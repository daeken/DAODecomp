"""Bounded Windows IA-32 registration-chain simulation, not an OS executor.

Only frames without local registration or unwind metadata are supported. A
paired external call may return, throw, terminate or diverge; no result is
invented. Call return-PC bytes must be equal even under the observation
policy: an ordinary aliased callee read can otherwise expose them as data. Fault-site ESP/nonvolatile and ordered byte-memory equality are separate
solver obligations, not inferred from this structural check.
"""
import struct
from rapid_object.encoding_equivalence import decode,need
from rapid_object.coff import Coff

POLICY='windows-x86-inherited-registration-ordered-events-v1'

def certify_structure(original,candidate,pc,mapping,original_pe,object_bytes):
 import capstone
 peoff=struct.unpack_from('<I',original_pe,0x3c)[0];opt=peoff+24
 need(original_pe[:2]==b'MZ' and original_pe[peoff:peoff+4]==b'PE\0\0' and struct.unpack_from('<H',original_pe,peoff+4)[0]==0x14c and struct.unpack_from('<H',original_pe,opt)[0]==0x10b,'unwind_requires_PE32_i386')
 optsize=struct.unpack_from('<H',original_pe,peoff+20)[0];need(optsize>=96,'unwind_PE_optional_header')
 count=struct.unpack_from('<I',original_pe,opt+92)[0]
 if count>3:
  need(optsize>=128 and struct.unpack_from('<II',original_pe,opt+96+3*8)==(0,0),'unwind_original_function_table_unsupported')
 obj=Coff(object_bytes)
 need(not any(s.data and (s.name.startswith(('.pdata','.xdata')) or s.name.startswith('.sxdata')) for s in obj.sections),'unwind_candidate_metadata_unsupported')
 # No FS/GS accesses, segment writes, opaque transfers, floating point or
 # implicit exception machinery are admitted by the complete CFG domain.
 # Check it here too so this structural receipt cannot stand alone as a broad
 # "no FS prefix" heuristic.
 allowed={'mov','lea','add','sub','cmp','test','push','pop','call','jmp','ret','ja','jae','jb','jbe','je','jne','jg','jge','jl','jle','js','jns','jo','jno','jp','jnp'}
 sides=[]
 for raw in (original,candidate):
  instructions=decode(raw,pc);stack=[];calls=[]
  for i in instructions:
   need(i.mnemonic in allowed and i.addr_size==4 and list(i.prefix)==[0,0,0,0],'unwind_unregistered_instruction_domain')
   for operand in i.operands:
    if operand.type==capstone.x86.X86_OP_MEM:need(operand.mem.segment==0,'unwind_segment_or_registration_access')
    if operand.type==capstone.x86.X86_OP_REG:need(i.reg_name(operand.reg) in {'eax','ecx','edx','ebx','esp','ebp','esi','edi','ax','cx','dx','bx','sp','bp','si','di','al','cl','dl','bl','ah','ch','dh','bh'},'unwind_special_register')
   _,writes=i.regs_access()
   if capstone.x86.X86_REG_ESP in writes and i.mnemonic not in ('call','ret'):
    need(i.mnemonic in ('push','pop') or i.mnemonic in ('add','sub') and len(i.operands)==2 and i.operands[0].type==capstone.x86.X86_OP_REG and i.operands[0].reg==capstone.x86.X86_REG_ESP and i.operands[1].type==capstone.x86.X86_OP_IMM and i.operands[1].imm%4==0,'unwind_dynamic_or_rebased_stack')
    stack.append(bytes(i.bytes).hex())
   if i.mnemonic=='call':
    need(i.bytes[0]==0xe8 and i.size==5 and len(i.operands)==1 and i.operands[0].type==capstone.x86.X86_OP_IMM,'unwind_indirect_call')
    calls.append((i.address,i.address+i.size,i.operands[0].imm))
  sides.append((stack,calls))
 need(sides[0][0]==sides[1][0],'unwind_stack_protocol_difference')
 need(len(sides[0][1])==len(sides[1][1]),'unwind_call_count')
 calls=[]
 for (a,an,at),(b,bn,bt) in zip(sides[0][1],sides[1][1]):
  need(at==bt and mapping.get(an)==bn,'unwind_call_continuation_mapping')
  need(an==bn,'unwind_changed_return_pc_with_unmodeled_callee')
  calls.append(dict(original_call=a,candidate_call=b,target=at,original_return=an,candidate_return=bn))
 return dict(policy=POLICY,local_registration_frames=0,local_unwind_metadata=False,stack_protocol=sides[0][0],paired_calls=calls,required_fault_registers=[3,4,5,6,7],inherited_handler_chain='same initial chain and equal ordered memory effects; no FS/GS or local registration instruction',exceptional_transfer='same actual callee/fault and inherited registration chain; no inserted cleanup or catch; no callee outcome assumed',return_PC_observation='numeric call-return addresses equal; no assumed private-stack nonaliasing or unknown-callee invariance under changed return words',native_OS_execution=False,whole_game_proof=False)
