"""Run inside the isolated Windows reccmp environment. No game code executes."""
import contextlib
import hashlib
import io
import inspect
import struct
import reccmp
import json
from pathlib import Path
import sys
from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
from reccmp.compare import Compare
from reccmp.compare.report import serialize_reccmp_report
from reccmp.project.detect import RecCmpProject
from reccmp.tools.asmcmp import print_match_verbose
from reccmp.types import ImageId
from status_rules import classify
from operands import scope_reason,strict_operand_match,descriptors,instruction_keys


def sha(data): return hashlib.sha256(data).hexdigest()



def _mapped(image,value):
    try:image.read(value,1);return True
    except Exception:return False

def analyze(root):
    root=Path(root); selection=json.loads((root/'selection.json').read_text()); target=RecCmpProject.from_directory(root).get('DAO')
    original_data=target.original_path.read_bytes(); candidate_data=target.recompiled_path.read_bytes()
    for image in (original_data,candidate_data):
        pe=struct.unpack_from('<I',image,0x3c)[0]
        if image[pe:pe+4]!=b'PE\0\0' or struct.unpack_from('<H',image,pe+4)[0]!=0x14c or struct.unpack_from('<H',image,pe+24)[0]!=0x10b: raise ValueError('requires_native_x86_PE32')
    original_hash=sha(original_data)
    if original_hash!=selection['module_sha256']: raise ValueError('vm_original_pin_mismatch')
    compare=Compare.from_target(target); report=compare.to_report(target.original_path.name)
    (root/'reccmp.json').write_text(serialize_reccmp_report(report,diff_included=True),encoding='utf-8')
    matches={m.orig_addr:m for m in compare.get_functions()}; md=Cs(CS_ARCH_X86,CS_MODE_32); md.detail=True
    summary={'schema_version':1,'module_sha256':original_hash,'source_sha256':sha((root/'candidate.cpp').read_bytes()),
        'recompiled_sha256':sha((root/'candidate.dll').read_bytes()),'pdb_sha256':sha((root/'candidate.pdb').read_bytes()),
        'compiler_patch_identity':'recorded build.log and compiler hashes; exact original compiler patch unknown',
        'evidence_kind':'reccmp_normalized_assembly_match_for_pinned_compiled_artifact','pe_machine':'I386','optional_header':'PE32','reccmp_version':reccmp.VERSION,'operand_check':'typed-instruction-v1','operand_guard_sha256':sha(Path(__file__).with_name('operands.py').read_bytes()),'tool_module_sha256':{},'functions':[]}
    for module in ('reccmp.compare.core','reccmp.compare.functions','reccmp.compare.asm.parse','reccmp.compare.asm.instgen','reccmp.compare.report'):
        loaded=__import__(module,fromlist=['_']);summary['tool_module_sha256'][module]=sha(Path(inspect.getfile(loaded)).read_bytes())
    for expected in selection['functions']:
        va=expected['original_va']; ent=report.entities.get(va); mapping=matches.get(va); unknown=[]; details={**expected}
        orig_size=mapping.size(ImageId.ORIG) if mapping else None
        recomp_size=mapping.size(ImageId.RECOMP) if mapping else None
        details.update(original_size_used=orig_size,recompiled_size=recomp_size,recompiled_va=mapping.recomp_addr if mapping else None,
            score=ent.accuracy if ent else None,effective_heuristic=ent.is_effective_match if ent else None)
        if orig_size!=expected['size'] or orig_size is None or orig_size<=0: unknown.append('complete_original_size_not_used')
        if mapping is None or mapping.recomp_addr is None or not recomp_size: unknown.append('missing_nonempty_native_mapping')
        if ent is None or ent.rdiff is None: unknown.append('missing_comparison')
        if not unknown:
            original=compare.orig_bin.read(va,orig_size); recomp=compare.recomp_bin.read(mapping.recomp_addr,recomp_size)
            if sha(original)!=expected['bytes_sha256']: unknown.append('original_slice_hash_mismatch')
            normalized=[line for _,line in ent.rdiff.orig_inst+ent.rdiff.recomp_inst]
            if any('<OFFSET' in line for line in normalized): unknown.append('unresolved_normalized_target')
            for side,raw,start,lines in [('original',original,va,ent.rdiff.orig_inst),('recompiled',recomp,mapping.recomp_addr,ent.rdiff.recomp_inst)]:
                instructions=list(md.disasm(raw,start)); addresses={int(a,16) for a,_ in lines if a}
                if sum(i.size for i in instructions)!=len(raw): unknown.append(side+'_incomplete_decode')
                if not instructions or not {i.address for i in instructions}.issubset(addresses): unknown.append(side+'_instructions_missing_from_comparison')
                reason=scope_reason(instructions,start,len(raw),lambda value: _mapped(compare.orig_bin,value) or _mapped(compare.recomp_bin,value))
                if reason:unknown.append(side+'_'+reason)
                for instruction in instructions:
                    if instruction.mnemonic in ('call','lcall'):
                        unknown.append(side+'_external_call_not_in_pilot_scope')
                    if instruction.group(CS_GRP_JUMP):
                        if not instruction.operands or instruction.operands[0].type!=CS_OP_IMM or not start<=instruction.operands[0].imm<start+len(raw): unknown.append(side+'_external_or_indirect_branch')
            try:
                left=descriptors(list(md.disasm(original,va)));right=descriptors(list(md.disasm(recomp,mapping.recomp_addr)))
                if instruction_keys(left)!=instruction_keys(right):
                    unknown.append('typed_instruction_or_operand_mismatch')
                    details['operand_differences']=[{'instruction_index':n,'original':left[n] if n<len(left) else None,'recompiled':right[n] if n<len(right) else None} for n in range(max(len(left),len(right))) if n>=len(left) or n>=len(right) or instruction_keys([left[n]])!=instruction_keys([right[n]])][:16]
            except ValueError:unknown.append('unmapped_typed_branch_target')
            output=io.StringIO()
            with contextlib.redirect_stdout(output): print_match_verbose(ent,show_both_addrs=True)
            (root/f'diff-{va:08x}.txt').write_text(output.getvalue(),encoding='utf-8')
        details['unknowns']=sorted(set(unknown)); details['complete_range_compared']=not unknown
        details['status']=classify(ent.accuracy if ent else None,original_size=orig_size,expected_size=expected['size'],recompiled_size=recomp_size,mapped=mapping is not None and mapping.recomp_addr is not None,unknowns=unknown,is_stub=ent.is_stub if ent else False)
        summary['functions'].append(details)
    summary['requested_count']=len(selection['functions']); summary['reccmp_matched_count']=sum(f['status']=='reccmp_matched' for f in summary['functions'])
    summary['retained_unmatched_count']=summary['requested_count']-summary['reccmp_matched_count']
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return summary
if __name__=='__main__': print(json.dumps(analyze(sys.argv[1]),indent=2))
