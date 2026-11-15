"""Original PE32 direct-edge and continuation discovery, without ABI guesses.

Direct targets and missing fallthroughs can lead outside inventory envelopes.
They become bounded continuation hypotheses; existing owners/contracts stay put.
"""
import struct
from pathlib import Path
import capstone
from capstone import x86
from tools.recomp_instruction_pointer_discovery import discover_closure, ClosureBudgetError


class DirectTransferScanner:
    def __init__(self, pe, include_switches=False):
        self.pe = pe
        self.decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); self.decoder.detail = True
        self.code = [(s['rva'],s['rva']+min(s['virtual_size'],s['file_size'])) for i,s in enumerate(pe.sections)
                     if struct.unpack_from('<I',pe.data,pe.section_table+i*40+36)[0] & 0x20000000]
        self.known_bytes = bytearray(max(b for a,b in self.code))
        self.include_switches = include_switches
        self.tables = {}
        if include_switches:
            from tools.recomp_pointer_discovery import highlow_sites
            self.relocation_sites = highlow_sites(pe)

    def executable(self, rva, size=1):
        return any(a <= rva and rva+size <= b for a,b in self.code)

    @staticmethod
    def rows(instructions):
        rows={}
        for row in instructions:
            rva,data=row['rva'],bytes.fromhex(row['bytes'])
            if type(rva) is not int or not 0 <= rva < 2**32 or not 1 <= len(data) <= 15 or rva in rows:
                raise ValueError('invalid/duplicate instruction metadata')
            rows[rva]=data
        return rows

    def record_generated(self, instructions):
        for rva,data in self.rows(instructions).items():
            if not self.executable(rva,len(data)):raise ValueError('generated instruction leaves executable storage')
            if self.known_bytes[rva]==2 or 1 in self.known_bytes[rva+1:rva+len(data)]:
                raise ValueError('generated instruction interiors overlap known code')
            self.known_bytes[rva:rva+len(data)]=bytes([2])*len(data);self.known_bytes[rva]=1

    def scan(self, instructions):
        rows=self.rows(instructions);origins,rejected=[],[]
        def add(target, rva, data, kind, operand_offset=None):
            if target in rows:return
            if not self.executable(target):
                rejected.append(dict(instruction_rva=rva,target_rva=target,kind=kind,
                                     reason='target is external or not file-backed module code'));return
            # Legacy closure helper uses this as an origin key only. Published
            # reports below name relative encodings/fallthroughs explicitly.
            origins.append(dict(rva=target,source_pointer_rva=rva+(operand_offset or 0),
                instruction_rva=rva,instruction_bytes=data.hex(),kind=kind,
                relative_operand_offset=operand_offset,behavioral_acceptance=False))
        for rva,data in rows.items():
            # Decode all possible transfer forms and any missing continuation.
            opcode=data[0];near=opcode in (0xe8,0xe9,0xeb,0xe0,0xe1,0xe2,0xe3) or 0x70<=opcode<=0x7f or opcode==0x0f and len(data)>1 and 0x80<=data[1]<=0x8f
            prefixed=opcode in (0x26,0x2e,0x36,0x3e,0x64,0x65,0x66,0x67,0xf0,0xf2,0xf3)
            if not near and not prefixed and rva+len(data) in rows:continue
            try:
                if not self.executable(rva,len(data)):raise ValueError('source instruction is not file-backed executable code')
                if self.pe.read(rva,len(data))!=data:raise ValueError('instruction bytes differ from pinned original')
                decoded=list(self.decoder.disasm(data,self.pe.info['image_base']+rva,count=1))
                if len(decoded)!=1 or decoded[0].size!=len(data):raise ValueError('independent instruction boundary differs')
                ins=decoded[0];jump=ins.group(capstone.CS_GRP_JUMP);call=ins.group(capstone.CS_GRP_CALL)
                if (jump or call) and len(ins.operands)==1 and ins.operands[0].type==x86.X86_OP_IMM:
                    if ins.imm_size not in (1,4) or 0x66 in ins.prefix:
                        raise ValueError('unsupported operand-size direct transfer')
                    raw=data[ins.imm_offset:ins.imm_offset+ins.imm_size]
                    if len(raw)!=ins.imm_size:raise ValueError('relative operand leaves instruction')
                    target=(self.pe.info['image_base']+rva+ins.size+int.from_bytes(raw,'little',signed=True))&0xffffffff
                    if target!=(ins.operands[0].imm&0xffffffff):raise ValueError('independent relative target differs')
                    add(target-self.pe.info['image_base'],rva,data,
                        'direct_call' if call else 'direct_jump' if ins.id==x86.X86_INS_JMP else 'direct_conditional',ins.imm_offset)
                elif jump or call:
                    rejected.append(dict(instruction_rva=rva,reason='indirect/non-near transfer has no static target'))
                terminal=(ins.group(capstone.CS_GRP_RET) or ins.group(capstone.CS_GRP_IRET) or ins.group(capstone.CS_GRP_INT) or
                          ins.id in (x86.X86_INS_JMP,x86.X86_INS_LJMP,x86.X86_INS_HLT,x86.X86_INS_UD2))
                if not terminal:
                    add(rva+ins.size,rva,data,'return_continuation' if call else 'conditional_fallthrough' if jump else 'fallthrough')
            except (ValueError,struct.error) as error:rejected.append(dict(instruction_rva=rva,reason=str(error)))
        if self.include_switches and any(len(data)==7 and data[:2]==b'\xff\x24' for data in rows.values()):
            from tools.recomp_switch_case_recovery import cfg_tables
            try:
                tables,refusals=cfg_tables(self.pe,instructions,self.relocation_sites)
                rejected.extend(dict(row,kind='guarded_switch_case') for row in refusals)
                for table in tables:
                    self.tables[table['jump_rva']]=table
                    for target in table['targets']:
                        if target['rva'] in rows:continue
                        origins.append(dict(rva=target['rva'],source_pointer_rva=target['source_pointer_rva'],
                            instruction_rva=table['jump_rva'],instruction_bytes=rows[table['jump_rva']].hex(),
                            kind='guarded_switch_case',table_entry_rva=target['source_pointer_rva'],
                            table_index=target['index'],table_rva=table['table_rva'],
                            behavioral_acceptance=False))
            except (ValueError,struct.error) as error:
                rejected.append(dict(kind='guarded_switch_case',reason=str(error)))
        return origins,rejected

    def validate_table_separation(self, proposals):
        """A decoded hypothesis cannot consume authenticated switch literals."""
        from tools.recomp_switch_case_recovery import table_data
        data=table_data(list(self.tables.values()))
        for a,b in data:
            if any(self.known_bytes[a:b]):
                raise ValueError('authenticated switch data overlaps emitted instructions')
        for proposal in proposals:
            if any(span['rva']<b and a<span['rva']+span['size']
                   for span in proposal['ranges'] for a,b in data):
                raise ValueError('continuation proposal overlaps authenticated switch data')


def published_origin(row):
    result={k:v for k,v in row.items() if k!='source_pointer_rva'}
    if result.get('relative_operand_offset') is not None:
        result['relative_operand_rva']=row['instruction_rva']+row['relative_operand_offset']
    return result


def prepare(generation, output, max_rounds=32, include_switches=False):
    import gzip
    import json
    import time
    from tools import recomp,recomp_bulk,recomp_pointer_discovery,recomp_instruction_pointer_discovery
    from tools.recomp_bulk_build import require_whole_inventory
    from tools.recomp_native import PE32
    from tools.recomp_pointer_discovery import unowned_targets
    generation,output=generation.absolute(),output.absolute()
    report=recomp.load(generation/'report.json');require_whole_inventory(report)
    overlay=Path(report['entry_overlay']);descriptor=recomp.load(overlay/'overlay.json')
    overlay_sha=recomp.digest((overlay/'overlay.json').read_bytes())
    if overlay_sha!=report['entry_overlay_sha256']:raise ValueError('input overlay identity changed')
    for name,identity in descriptor['files'].items():
        if recomp.digest((overlay/name).read_bytes())!=identity:raise ValueError('input overlay file changed')
    out=output/str(time.time_ns());out.mkdir(parents=True)
    for name,path in [('direct-transfer-discovery.py',Path(__file__)),('pointer-discovery.py',Path(recomp_pointer_discovery.__file__)),
                      ('closure-controller.py',Path(recomp_instruction_pointer_discovery.__file__))]:
        (out/name).write_bytes(path.read_bytes())
    if include_switches:
        from tools import recomp_switch_case_recovery
        (out/'switch-case-recovery.py').write_bytes(Path(recomp_switch_case_recovery.__file__).read_bytes())
    summary={}
    for role in ('main','umbra'):
        context=recomp.load(generation/role/'context.json');state=recomp.state(Path(context['project']))
        if recomp.digest(recomp.encoded(state))!=context['project_sha256']:raise ValueError('project changed after generation')
        scanner=DirectTransferScanner(PE32(recomp.checked_binary(state)),include_switches=include_switches)
        catalog=list(map(json.loads,(generation/role/'catalog.jsonl').open()))
        initial,rejected,bindings=[],[],{};inspected=0
        for row in map(json.loads,(generation/role/'results.jsonl').open()):
            if row['status']!='generated_only':continue
            marker=recomp_bulk.load_shard(generation.parent.parent/'cache',row['key'],state['binary_sha256'],row['rva'])
            metadata=generation.parent.parent/'cache'/row['key']/'function.json.gz'
            function=json.loads(gzip.decompress(metadata.read_bytes()))
            if function['rva']!=row['rva']:raise ValueError('function metadata identity differs')
            scanner.record_generated(function['instructions']);found,refusals=scanner.scan(function['instructions'])
            if found:initial.append((row['rva'],found))
            inspected+=1;bindings[str(row['rva'])]=marker['files']['function.json.gz']
            rejected.extend(dict(r,function_rva=row['rva']) for r in refusals)
        try:closure=discover_closure(scanner,initial,catalog,max_rounds)
        except ClosureBudgetError as error:
            recomp.atomic_json(out/(role+'-closure-exhausted.json'),dict(status='direct-edge closure budget exhausted',
                rounds=error.rounds,targets=error.targets,game_acceptance=False));raise
        scanner.validate_table_separation(closure['proposals'])
        roots={r['rva'] for r in catalog};all_targets={rva:[r['instruction_rva'] for r in rows] for rva,rows in closure['origins'].items()}
        unowned,_=unowned_targets(all_targets,catalog)
        unresolved_owned=[dict(rva=rva,reason='known catalog entry has no emitted instruction' if rva in roots else
            'owned target is an instruction interior or uncovered byte; existing ownership retained',
            origins=[published_origin(r) for r in rows]) for rva,rows in closure['origins'].items()
            if rva not in unowned and scanner.known_bytes[rva]!=1]
        selected=recomp.load(overlay/(role+'-role.json'));selected_roots={f['rva'] for f in selected['functions']}
        _,occupied=unowned_targets({},catalog);spans=[]
        for proposal in closure['proposals']:
            if proposal['rva'] in selected_roots:raise ValueError('continuation proposal overrides existing selection')
            for span in proposal['ranges']:
                a,b=span['rva'],span['rva']+span['size']
                if any(a<y and x<b for x,y in occupied):raise ValueError('continuation proposal overlaps existing ownership')
                spans.append((a,b))
            proposal.pop('source_pointer_rvas',None)
            proposal['pointer_origins']=[published_origin(r) for r in proposal['pointer_origins']]
            proposal.update(discovery_kind='original_switch_and_direct_continuation' if include_switches else 'original_direct_control_flow_continuation',
                bounds_status='recursive original decode before known ownership and other direct-edge roots',
                contract_status='continuation/function entry ABI, behavior and CFG completeness unknown; not accepted',
                purpose='unaccepted direct-edge code continuation; no callable signature inferred',
                module_sha256=state['binary_sha256'],module=state['module'])
            selected['functions'].append(proposal)
        spans.sort()
        if any(b>c for (a,b),(c,d) in zip(spans,spans[1:])):raise ValueError('competing continuation ownership')
        selected['functions'].sort(key=lambda f:f['rva']);recomp.atomic_json(out/(role+'-role.json'),selected)
        closure['origins']={rva:[published_origin(r) for r in rows] for rva,rows in closure['origins'].items()}
        evidence=dict(binary_sha256=state['binary_sha256'],module=state['module'],inspected=inspected,
            known_catalog_sha256=recomp.digest((generation/role/'catalog.jsonl').read_bytes()),metadata_bindings=bindings,
            rejected_sources=rejected,owned_unregistered_targets=unresolved_owned,**closure,
            guarded_tables=list(scanner.tables.values()),
            scope='original direct-edge/missing-continuation hypotheses; nonemitted inputs and dynamic targets remain unresolved',game_acceptance=False)
        recomp.atomic_json(out/(role+'-direct-transfer-proposals.json'),evidence)
        summary[role]=dict(inspected=inspected,targets=len(closure['origins']),unowned_targets=closure['unowned_targets'],
            proposed=len(closure['proposals']),rejected_bounds=len(closure['rejected_bounds']),
            owned_unregistered_targets=len(unresolved_owned),rejected_sources=len(rejected),
            closure_rounds=closure['closure_rounds'],instructions=sum(p['instruction_count'] for p in closure['proposals']))
        if include_switches:
            summary[role].update(guarded_tables=len(scanner.tables),
                compressed_tables=sum(t['remap'] is not None for t in scanner.tables.values()))
        print(dict(role=role,**summary[role]),flush=True)
    descriptor.update(status='unaccepted original direct-edge continuation closure; existing ownership/contracts preserved',
        base_overlay=dict(path=str(overlay),sha256=overlay_sha),generation_run=str(generation),
        generation_report_sha256=recomp.digest((generation/'report.json').read_bytes()),decoder_version=capstone.__version__,
        direct_transfer_discovery=summary,include_guarded_switches=include_switches,behavioral_acceptance=False,game_acceptance=False)
    descriptor['files']={p.name:recomp.digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    recomp.atomic_json(out/'overlay.json',descriptor);return out,summary


def main():
    import argparse,json
    from tools import recomp
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--generation',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/direct-transfer-overlays')
    parser.add_argument('--max-rounds',type=int,default=32)
    parser.add_argument('--include-switches',action='store_true',help='also follow authenticated guarded/compressed switch cases outside existing ownership')
    args=parser.parse_args()
    out,summary=prepare(args.generation,args.output,args.max_rounds,args.include_switches)
    recomp.atomic_json(recomp.ROOT/'local/recomp/startup/direct-transfer-overlay-latest.json',
                       dict(overlay=str(out),summary=summary,game_acceptance=False))
    print(json.dumps(dict(overlay=str(out),summary=summary)),flush=True)


if __name__=='__main__':main()
