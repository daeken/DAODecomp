"""Bounded architectural encoding relation over fresh complete relocated ranges.

The exact comparator stays separate. This rule recognizes one DS scale-one MOV
immediate-store base/index swap, and requires an independent typed lift of both
actual changed instructions. It does not compare arbitrary IR or certify calls,
whole-function contracts, code-byte observations, or game execution.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import capstone
from capstone.x86_const import X86_INS_MOV, X86_OP_MEM, X86_OP_IMM

class Refusal(ValueError): pass

def need(ok, why):
    if not ok: raise Refusal(why)

@dataclass(frozen=True)
class Relocation:
    offset: int
    kind: int
    target: int | None
    addend: int


def decode(code, pc):
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
    instructions=list(md.disasm(code,pc))
    need(sum(x.size for x in instructions)==len(code),'incomplete_instruction_range')
    return instructions


def relocate(raw, reference, pc, relocations):
    data=bytearray(raw);used=set()
    for rel in relocations:
        need(type(rel.offset)is int and 0<=rel.offset<=len(raw)-4,'relocation_bounds')
        need(rel.kind in (6,0x14),'unsupported_relocation')
        need(type(rel.target)is int and 0<=rel.target<=0xffffffff,'unresolved_relocation')
        fields=set(range(rel.offset,rel.offset+4));need(not fields&used,'duplicate_or_overlapping_relocations');used|=fields
        need(type(rel.addend)is int and 0<=rel.addend<=0xffffffff,'invalid_addend')
        need(struct.unpack_from('<I',raw,rel.offset)[0]==rel.addend,'relocation_raw_addend_mismatch')
        value=(rel.target+rel.addend-(pc+rel.offset+4 if rel.kind==0x14 else 0))&0xffffffff
        need(reference[rel.offset:rel.offset+4]==struct.pack('<I',value),'relocation_target_differs')
        struct.pack_into('<I',data,rel.offset,value)
    return bytes(data),used


def instruction_fields(insn):
    need(insn.addr_size==4,'requires_Bits32_address_size')
    need(insn.id==X86_INS_MOV and len(insn.operands)==2,'only_MOV_memory_immediate')
    memory,imm=insn.operands
    need(memory.type==X86_OP_MEM and imm.type==X86_OP_IMM and memory.access==capstone.CS_AC_WRITE,'requires_single_memory_write')
    need(memory.size in (1,2,4) and imm.size==memory.size,'unsupported_access_width')
    need(insn.eflags==0,'flags_effect_not_supported')
    # Only an optional single operand-size prefix. No segment, address, LOCK,
    # REP/REPNZ, duplicate or unusual prefix ordering assumptions.
    m=insn.modrm_offset;need(m>0,'missing_ModRM')
    need(list(insn.prefix) in ([0,0,0,0],[0,0,0x66,0]),'unsupported_prefix')
    prefix_len=1 if insn.prefix[2] else 0
    need(insn.bytes[:prefix_len]==(b'\x66' if prefix_len else b'') and m==prefix_len+1,'unsupported_opcode_or_prefix_encoding')
    modrm=insn.bytes[m];mod=modrm>>6
    need(mod!=3 and modrm&7==4 and (modrm>>3)&7==0,'not_memory_immediate_SIB')
    sib=insn.bytes[m+1];scale=1<<(sib>>6);index=(sib>>3)&7;base=sib&7
    need(scale==1,'nonunit_scale')
    need(index!=4 and not(mod==0 and base==5),'special_index_or_no_base')
    # Strict DS-only domain. EBP/ESP would require more segment-context rules.
    need(base not in (4,5) and index not in (4,5),'special_or_segment_sensitive_register')
    need(base!=index,'not_a_distinct_register_swap')
    need(memory.mem.segment==0,'segment_override')
    need(insn.reg_name(memory.mem.base)==['eax','ecx','edx','ebx','esp','ebp','esi','edi'][base]
         and insn.reg_name(memory.mem.index)==['eax','ecx','edx','ebx','esp','ebp','esi','edi'][index]
         and memory.mem.scale==scale,'decoder_field_disagreement')
    return dict(base=base,index=index,scale=scale,displacement=memory.mem.disp,
        width_bits=memory.size*8,immediate=imm.imm&((1<<(memory.size*8))-1),segment='DS',mod=mod,sib_offset=m+1,
        prefix=bytes(insn.bytes[:prefix_len]).hex(),opcode=insn.bytes[prefix_len],length=insn.size)


def ring_certificate(fields):
    # Canonical affine polynomial over Z/(2^32). Registers are arbitrary
    # 32-bit values; reduction modulo32 is built into each coefficient/constant.
    return dict(modulus=1<<32,coefficients={str(r):1 for r in sorted([fields['base'],fields['index']])},
                constant=fields['displacement']&0xffffffff)


def certify_range(reference, candidate_raw, *, pc, complete_length, relocations=(), lift_pair):
    need(type(pc)is int and 0<=pc<=0xffffffff,'invalid_PC')
    need(type(complete_length)is int and complete_length>0 and len(reference)==len(candidate_raw)==complete_length
         and pc+complete_length<=1<<32,'incomplete_or_conflicting_full_range')
    candidate,relocation_fields=relocate(candidate_raw,reference,pc,relocations)
    left,right=decode(reference,pc),decode(candidate,pc)
    need([(x.address,x.size)for x in left]==[(x.address,x.size)for x in right],'instruction_boundary_difference')
    differences=[i for i,(a,b)in enumerate(zip(reference,candidate))if a!=b]
    need(len(differences)==1,'requires_exactly_one_byte_difference')
    changed=differences[0];pair=[(a,b)for a,b in zip(left,right)if a.address-pc<=changed<a.address-pc+a.size]
    need(len(pair)==1,'changed_byte_not_unique_instruction')
    a,b=pair[0];fa,fb=instruction_fields(a),instruction_fields(b)
    need(changed==a.address-pc+fa['sib_offset']==b.address-pc+fb['sib_offset'],'difference_is_not_SIB')
    need(not (set(range(a.address-pc,a.address-pc+a.size))&relocation_fields),'relocation_overlaps_rewritten_instruction')
    need(fa['base']==fb['index'] and fa['index']==fb['base'],'not_a_base_index_swap')
    need({k:v for k,v in fa.items()if k not in ('base','index')}=={k:v for k,v in fb.items()if k not in ('base','index')},'other_instruction_field_difference')
    ca,cb=ring_certificate(fa),ring_certificate(fb);need(ca==cb,'affine_certificate_mismatch')
    # Direct branches into an instruction interior undermine even local rewriting
    # at a function's normal instruction boundaries. Refuse visible such edges.
    boundaries={x.address for x in left}
    for insn in left:
        if insn.group(capstone.CS_GRP_JUMP) or insn.group(capstone.CS_GRP_CALL):
            for operand in insn.operands:
                if operand.type==X86_OP_IMM and pc<=operand.imm<pc+complete_length:
                    need(operand.imm in boundaries,'interior_direct_control_target')
            need(len(insn.operands)==1 and insn.operands[0].type==X86_OP_IMM,'indirect_control_target_unknown')
    lifted=lift_pair(bytes(a.bytes),bytes(b.bytes),a.address)
    typed=check_typed_pair(lifted,a,b,fa,fb,ca)
    return dict(status='encoding_equivalent',rule='x86-flat32-MOV-immediate-DS-unit-SIB-swap-v1',typed_crosscheck=typed,typed_lifts=lifted,strict_byte_match=False,
        whole_function_equivalence_proven=False,mode='Bits32',changed_function_offset=changed,
        instruction_pc=a.address,original_instruction=a.bytes.hex(),candidate_instruction=b.bytes.hex(),
        original_fields=fa,candidate_fields=fb,affine_certificate=ca,relocations_checked=len(relocations),
        full_range_bytes_checked=complete_length,other_relocated_function_bytes_identical=True,
        effect=dict(kind='store_immediate',width_bits=fa['width_bits'],value=fa['immediate'],flags='unchanged',
                    segment='same DS descriptor/base/limit/rights in paired state',effective_offset='equal modulo2^32'),
        assumptions=['same pre-instruction registers/flags/memory/segment/control state',
            'supported ordinary Bits32 instruction semantics; same decode entry boundary and execution mode',
            'instruction encodings/code-byte reads, debugger/tracing/performance/fetch side channels are not observations',
            'no concurrent code modification or entry into instruction interiors',
            'unmodeled external calls/ABI/object validity and complete program behavior are not proved'])



def check_typed_pair(lifts,left,right,left_fields,right_fields,certificate):
    need(isinstance(lifts,list) and len(lifts)==2,'missing_or_duplicate_lift_pair')
    summaries=[]
    for lifted,insn,fields in zip(lifts,[left,right],[left_fields,right_fields]):
        need(isinstance(lifted,dict) and lifted.get('schema')=='sharpretro_instruction_lift_v1' and lifted.get('mode')=='Bits32','typed_lift_schema_mode')
        need(lifted.get('pc')==insn.address and lifted.get('byte_length')==insn.size and lifted.get('decoded_bytes')==insn.size and lifted.get('decode_complete') is True and lifted.get('unprocessed_hex')=='' and lifted.get('lift_errors')==0 and lifted.get('opaque_instructions')==0,'typed_lift_incomplete_or_unknown')
        rows=lifted.get('instructions');need(isinstance(rows,list) and len(rows)==1,'typed_lift_instruction_count');row=rows[0]
        need(row.get('pc')==insn.address and row.get('offset')==0 and row.get('length')==insn.size and row.get('raw_hex')==insn.bytes.hex() and row.get('lift_error') is None and row.get('opaque_markers')==[],'typed_lift_instruction_binding')
        decoded=row['decoded'];memory=decoded['M'];prefix=decoded['P']
        need(not any(prefix.get(k) for k in ('Lock','Rep','RepNz','AdSize','Rex','VexValid','EvexValid','Segment')),'typed_lift_prefix_unknown')
        need(memory['BaseReg']==fields['base'] and memory['IndexReg']==fields['index'] and memory['Scale']==1 and memory['Disp']==fields['displacement'] and memory['IsReg'] is False and memory['RipRelative'] is False,'typed_decode_disagreement')
        tree=row['tree'];need(tree.get('type')=='LiftIl.IlBlock' and isinstance(tree.get('Body'),list) and len(tree['Body'])==2,'typed_effect_shape');temporary,store=tree['Body']
        need(temporary.get('type')=='LiftIl.IlLet' and type(temporary.get('Id')) is int and temporary['Id']>=0 and store.get('type')=='LiftIl.IlStore','typed_store_capture_shape')
        def integer(node,bits):return node.get('Ty',{}).get('type')=='LiftIl.IlType+I' and node['Ty'].get('Bits')==bits and node['Ty'].get('Signed') is False
        address=temporary['Val'];need(address.get('type')=='LiftIl.IlCast' and address.get('Kind',{}).get('name')=='Zext' and integer(address,64),'typed_address_extension')
        offset=address['X'];need(offset.get('type')=='LiftIl.IlCast' and offset.get('Kind',{}).get('name')=='Trunc' and integer(offset,32),'typed_address_wrap')
        def affine(node,depth=0):
            need(depth<=16 and integer(node,64),'typed_affine_width_or_depth')
            if node.get('type')=='LiftIl.IlReadReg':
                need(node.get('Kind',{}).get('name')=='X86' and type(node.get('Idx')) is int and 0<=node['Idx']<=7,'typed_affine_register');return {str(node['Idx']):1},0
            if node.get('type')=='LiftIl.IlConst':
                text=node.get('Bits',{}).get('decimal');need(isinstance(text,str) and text.isdecimal() and len(text)<=20 and int(text)<1<<64,'typed_affine_constant');return {},int(text)&0xffffffff
            need(node.get('type')=='LiftIl.IlBin' and node.get('Op',{}).get('name')=='Add','typed_affine_unknown_effect')
            a,ac=affine(node['L'],depth+1);b,bc=affine(node['R'],depth+1);out=dict(a)
            for key,value in b.items():out[key]=(out.get(key,0)+value)&0xffffffff
            return out,(ac+bc)&0xffffffff
        coefficients,constant=affine(offset['X']);need(coefficients==certificate['coefficients'] and constant==certificate['constant'],'typed_affine_disagreement')
        destination=store['Addr'];value=store['Val']
        need(destination.get('type')=='LiftIl.IlTmp' and destination.get('Id')==temporary['Id'] and integer(destination,64),'typed_store_address_binding')
        need(value.get('type')=='LiftIl.IlConst' and integer(value,fields['width_bits']),'typed_store_immediate_width')
        text=value.get('Bits',{}).get('decimal');need(isinstance(text,str) and text.isdecimal() and len(text)<=10 and int(text)==fields['immediate'],'typed_store_immediate_value')
        summaries.append(dict(mode='Bits32',coefficients=coefficients,constant=constant,store_bits=fields['width_bits'],store_value=int(text),ordered_effects=['capture_wrapped_address','store_immediate'],flags_written=False,raw_sha256=hashlib.sha256(bytes(insn.bytes)).hexdigest()))
    return summaries
