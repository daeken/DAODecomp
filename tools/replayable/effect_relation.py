"""Bounded straight-line typed-effect checks; no arbitrary-IR acceptance.

The caller must bind complete CFGs, original inputs and the solver. This module
compares ordered memory events and live boundary values, never assumes disjoint
addresses or valid memory. Fault-register context is separately reported.
"""
from pathlib import Path
import hashlib
import subprocess
from rapid_object.encoding_equivalence import need,Refusal

FLAGS=(0,2,4,6,7,11)
def tag(n):return n.get('type','').split('+')[-1].split('.')[-1]
def bits(n):
 t=n.get('Ty',{});w=t.get('Bits');need(t.get('type')=='LiftIl.IlType+I' and type(w)is int and 1<=w<=64,'effect_integer_width');return w

def bv(n,w):return f'(_ bv{n% (1<<w)} {w})'
def sort(w):return f'(_ BitVec {w})'

class Terms:
 def __init__(self):
  self.lines=['(set-logic QF_AUFBV)','(set-option :timeout 3000)','(declare-fun memory () (Array (_ BitVec 32) (_ BitVec 8)))'];self.serial=0;self.event_arrays=set()
  for i in range(8):self.lines.append(f'(declare-fun R{i} () (_ BitVec 32))')
  for i in FLAGS:self.lines.append(f'(declare-fun F{i} () (_ BitVec 1))')
 # Shared event-indexed arrays overapproximate arbitrary external memory
 # changes between accesses. Stores are still compared as ordered events;
 # this cannot authorize read elimination or infer stable repeated reads.
 def event_memory(self,index):
  name=f'event_memory_{index}'
  if index not in self.event_arrays:self.lines.append(f'(declare-fun {name} () (Array (_ BitVec 32) (_ BitVec 8)))');self.event_arrays.add(index)
  return name
 def bind(self,term,w):
  name=f'v{self.serial}';self.serial+=1;self.lines.append(f'(define-fun {name} () {sort(w)} {term})');return name
 def array(self,term):
  name=f'm{self.serial}';self.serial+=1;self.lines.append(f'(define-fun {name} () (Array (_ BitVec 32) (_ BitVec 8)) {term})');return name

class State:
 def __init__(self,terms,arbitrary_event_memory=False):
  self.arbitrary_event_memory=arbitrary_event_memory;self.t=terms;self.reg={i:f'((_ zero_extend 32) R{i})' for i in range(8)};self.flag={i:f'F{i}' for i in FLAGS};self.mem='memory';self.events=[];self.tmp={};self.writes=set();self.flag_writes=set();self.faults=[];self.budget=12000
 def value(self,n):
  self.budget-=1;need(self.budget>=0,'effect_expression_budget');k=tag(n);w=bits(n)
  if k=='IlConst':
   v=n.get('Bits',{}).get('decimal');need(isinstance(v,str) and v.isdecimal() and int(v)<1<<w,'effect_constant');return bv(int(v),w),w
  if k=='IlTmp':need(n['Id'] in self.tmp and self.tmp[n['Id']][1]==w,'effect_temporary_before_definition_or_width');return self.tmp[n['Id']]
  if k=='IlReadReg':
   kind=n['Kind']['name'];i=n['Idx'];need(type(i)is int,'effect_register_index')
   if kind=='X86':need(i in self.reg and w==64,'effect_register_width');return self.reg[i],w
   if kind=='Eflags':need(i in self.flag and w==1,'effect_flag_domain');return self.flag[i],w
   need(kind=='X86Seg' and i in (2,3) and w==64,'effect_flat_segments_only');return bv(0,64),64
  if k=='IlCast':
   v,old=self.value(n['X']);op=n['Kind']['name'];need(op in ('Zext','Sext','Trunc'),'effect_cast')
   if w==old:return v,w
   if op=='Trunc':need(w<old,'effect_truncation');return f'((_ extract {w-1} 0) {v})',w
   need(w>old,'effect_extension');return f'((_ {"zero_extend" if op=="Zext" else "sign_extend"} {w-old}) {v})',w
  if k=='IlBin':
   a,aw=self.value(n['L']);b,bw=self.value(n['R']);op=n['Op']['name']
   if op in ('Shr','Shl'):
    count=n['R'];bound=int(count['Bits']['decimal']) if tag(count)=='IlConst' else int(count['R']['Bits']['decimal']) if tag(count)=='IlBin' and count['Op']['name']=='And' and tag(count['R'])=='IlConst' else None
    need(bound is not None and bound<aw and bw<=aw,'effect_shift_count_domain')
    if bw<aw:b=f'((_ zero_extend {aw-bw}) {b})';bw=aw
   need(aw==bw,'effect_operand_width');ops=dict(Add='bvadd',Sub='bvsub',And='bvand',Or='bvor',Xor='bvxor',Shr='bvlshr',Shl='bvshl');comparisons=dict(Eq='=',Ne='distinct',Ult='bvult',Ule='bvule')
   if op in comparisons:need(w==1,'effect_predicate_width');return f'(ite ({comparisons[op]} {a} {b}) #b1 #b0)',w
   need(op in ops and w==aw,'effect_binary_domain');return f'({ops[op]} {a} {b})',w
  if k=='IlLoad':
   need(w in (8,16,32),'effect_memory_width')
   if self.arbitrary_event_memory:self.mem=self.t.event_memory(len(self.events))
   address=self.address(n['Addr']);values=[f'(select {self.mem} (bvadd {address} {bv(i,32)}))' for i in reversed(range(w//8))];term=values[0] if len(values)==1 else '(concat '+' '.join(values)+')';value=self.t.bind(term,w);self.events.append(('read',address,w,value,self.segments['read']));self.faults.append(dict(registers=dict(self.reg),flags=dict(self.flag)));return value,w
  raise Refusal('effect_unsupported_expression:'+k)
 def wrapped(self,x):
  if tag(x)=='IlTmp':return x['Id'] in self.wrapped_temps and bits(x)==64
  if tag(x)=='IlCast' and x['Kind']['name']=='Zext' and bits(x)==64 and bits(x['X'])==32:return True
  if tag(x)=='IlBin' and x['Op']['name']=='Add' and bits(x)==64:
   for a,b in ((x['L'],x['R']),(x['R'],x['L'])):
    if tag(a)=='IlReadReg' and a['Kind']['name']=='X86Seg' and a['Idx'] in (2,3) and bits(a)==64 and self.wrapped(b):return True
  return False
 def address(self,n):
  need(self.wrapped(n),'effect_explicit_flat32_wrapped_address');v,w=self.value(n);need(w==64,'effect_address_width');return self.t.bind(f'((_ extract 31 0) {v})',32)
 def run(self,rows):
  need(0<len(rows)<=24,'effect_window_budget')
  for row in rows:
   self.tmp={};self.wrapped_temps=set()
   if 'raw_hex' in row:
    import capstone
    from rapid_object.encoding_equivalence import decode
    ins=decode(bytes.fromhex(row['raw_hex']),row['pc']);need(len(ins)==1,'effect_row_instruction_binding');i=ins[0];memory=[o for o in i.operands if o.type==capstone.x86.X86_OP_MEM];need(len(memory)<=1,'effect_multiple_memory_operands');segment='DS'
    if memory:
     m=memory[0].mem;segment=i.reg_name(m.segment).upper() if m.segment else 'SS' if i.reg_name(m.base) in ('esp','ebp') else 'DS'
    self.segments=dict(read='SS' if i.mnemonic=='pop' else segment,write='SS' if i.mnemonic=='push' else segment)
   else:self.segments=row.get('effect_segments',{})
   need(set(self.segments)=={'read','write'} and all(x in ('DS','SS') for x in self.segments.values()),'effect_explicit_memory_segment_context')
   body=row['tree']['Body'];need(isinstance(body,list) and len(body)<=32,'effect_tree_budget')
   for n in body:
    k=tag(n)
    if k=='IlLet':need(type(n['Id'])is int and n['Id'] not in self.tmp,'effect_temporary_identity');v,w=self.value(n['Val']);self.tmp[n['Id']]=(self.t.bind(v,w),w);self.wrapped_temps.update([n['Id']] if self.wrapped(n['Val']) else [])
    elif k=='IlWriteReg':
     v,w=self.value(n['Val']);kind=n['Kind']['name'];i=n['Idx']
     if kind=='X86':need(i in self.reg and w==64,'effect_write_register');self.reg[i]=self.t.bind(v,w);self.writes.add(i)
     else:need(kind=='Eflags' and i in self.flag and w==1,'effect_write_flag');self.flag[i]=self.t.bind(v,w);self.flag_writes.add(i)
    elif k=='IlStore':
     if self.arbitrary_event_memory:self.mem=self.t.event_memory(len(self.events))
     a=self.address(n['Addr']);v,w=self.value(n['Val']);need(w in (8,16,32),'effect_store_width');value=self.t.bind(v,w);self.events.append(('write',a,w,value,self.segments['write']));self.faults.append(dict(registers=dict(self.reg),flags=dict(self.flag)))
     for i in range(w//8):self.mem=self.t.array(f'(store {self.mem} (bvadd {a} {bv(i,32)}) ((_ extract {i*8+7} {i*8}) {value}))')
    else:raise Refusal('effect_unsupported_statement:'+k)
  return self

def prove_window(left,right,live_registers,solver,*,fault_context='full-registers',fault_live_registers=None,arbitrary_event_memory=False):
 """Return a fresh solver receipt. Only UNSAT succeeds; uncertainty refuses.

 full-registers includes register/flag context at each possibly faulting event.
 abi-event-only is diagnostic until the outer profile explicitly authorizes its
 narrower observation boundary; it still preserves every ordered memory access.
 """
 need(fault_context in ('full-registers','abi-event-only'),'effect_fault_observation_profile');need(fault_context=='full-registers' or fault_live_registers is not None,'effect_explicit_fault_register_contract_required');fault_live=list(range(8)) if fault_context=='full-registers' else sorted(set(fault_live_registers));need(set(fault_live)<=set(range(8)),'effect_fault_live_registers');need(set(live_registers)<=set(range(8)),'effect_live_registers');t=Terms();a=State(t,arbitrary_event_memory).run(left);b=State(t,arbitrary_event_memory).run(right);need(len(a.events)==len(b.events),'effect_memory_event_count');equal=[]
 for i,(x,y) in enumerate(zip(a.events,b.events)):
  need(x[:1]==y[:1] and x[2]==y[2],'effect_memory_event_order_or_width');need(x[4]==y[4],'effect_memory_segment_difference');equal.extend([f'(= {x[1]} {y[1]})',f'(= {x[3]} {y[3]})'])
  equal.extend(f'(= {a.faults[i]["registers"][r]} {b.faults[i]["registers"][r]})' for r in fault_live)
  if fault_context=='full-registers':
   equal.extend(f'(= {a.faults[i]["flags"][f]} {b.faults[i]["flags"][f]})' for f in FLAGS)
 equal.extend(f'(= {a.reg[r]} {b.reg[r]})' for r in live_registers);equal.extend(f'(= {a.flag[f]} {b.flag[f]})' for f in FLAGS);equal.append(f'(= {a.mem} {b.mem})');query='\n'.join(t.lines+[f'(assert (not (and {" ".join(equal)})))','(check-sat)'])+'\n';path=Path(solver).resolve();need(path.is_file(),'effect_solver_unavailable');run=subprocess.run([str(path),'-in','-smt2'],input=query,text=True,capture_output=True,timeout=6,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'});need(run.returncode==0 and not run.stderr and run.stdout.strip() in ('sat','unsat','unknown'),'effect_solver_protocol');return dict(status=run.stdout.strip(),query=query,query_sha256=hashlib.sha256(query.encode()).hexdigest(),solver_path=str(path),solver_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),live_registers=sorted(live_registers),flags_checked=list(FLAGS),ordered_memory_events=len(a.events),fault_observation_profile=fault_context,fault_preserved_registers=fault_live,arbitrary_external_memory_between_events=arbitrary_event_memory,full_fault_register_context_checked=fault_context=='full-registers',whole_function_equivalence_proven=False)

# Complete direct CFG pairing limits the local solver obligation to changed
# blocks. Unchanged instructions remain byte-identical, apart from their bound
# direct control displacements. No path, unrecognized instruction or byte drops.
def pair_cfg(original,candidate,pc,exit_live_registers):
 import capstone
 from capstone.x86_const import X86_OP_IMM
 from rapid_object.encoding_equivalence import decode
 need(len(original)<=4096 and len(candidate)<=4096,'effect_function_budget')
 conditionals={'ja','jae','jb','jbe','je','jne','jg','jge','jl','jle','jo','jno','jp','jnp','js','jns'}
 def graph(raw):
  ins=decode(raw,pc);need(0<len(ins)<=256,'effect_instruction_budget');at={i.address:i for i in ins};leaders={pc}
  def term(i):
   if i.mnemonic=='ret':need(list(i.prefix)==[0,0,0,0] and i.bytes[0] in (0xc2,0xc3) and len(i.operands)<=1 and all(o.type==X86_OP_IMM for o in i.operands),'effect_RET_domain');return ('ret',int(i.operands[0].imm) if i.operands else 0)
   if i.group(capstone.CS_GRP_CALL) or i.group(capstone.CS_GRP_JUMP):
    need(len(i.operands)==1 and i.operands[0].type==X86_OP_IMM and list(i.prefix)==[0,0,0,0],'effect_direct_control_only');target=i.operands[0].imm
    if i.group(capstone.CS_GRP_CALL):need(i.mnemonic=='call' and i.bytes[0]==0xe8,'effect_direct_near_call');return ('call',target)
    need(i.mnemonic=='jmp' or i.mnemonic in conditionals,'effect_branch_domain');need(target in at,'effect_external_or_interior_branch');return (i.mnemonic,target)
   need(not i.group(capstone.CS_GRP_RET) and not i.group(capstone.CS_GRP_IRET),'effect_return_domain');return None
  for i in ins:
   need(i.mnemonic in {'mov','lea','add','sub','cmp','test','push','pop','call','jmp','ret'}|conditionals,'effect_function_instruction_domain')
   need(i.addr_size==4 and list(i.prefix)==[0,0,0,0],'effect_function_prefix_domain')
   for operand in i.operands:
    if operand.type==capstone.x86.X86_OP_REG:need(i.reg_name(operand.reg) in {'eax','ecx','edx','ebx','esp','ebp','esi','edi','ax','cx','dx','bx','sp','bp','si','di','al','cl','dl','bl','ah','ch','dh','bh'},'effect_special_register_operand')
    if operand.type==capstone.x86.X86_OP_MEM:need(operand.mem.segment==0,'effect_segment_operand')
   t=term(i)
   if t:
    if t[0] not in ('call','ret'):leaders.add(t[1])
    if i.address+i.size<pc+len(raw):leaders.add(i.address+i.size)
  need(len(leaders)<=48,'effect_CFG_budget');blocks={}
  for start in sorted(leaders):
   body=[];here=start
   while True:
    i=at[here];t=term(i);nxt=here+i.size
    if t:
     edges=[] if t[0]=='ret' else [nxt] if t[0]=='call' else [t[1]] if t[0]=='jmp' else [nxt,t[1]]
     need(all(x in at for x in edges),'effect_control_falls_out');blocks[start]=dict(body=body,term=i,kind=t,edges=edges);break
    body.append(i)
    if nxt in leaders:blocks[start]=dict(body=body,term=None,kind=('fallthrough',),edges=[nxt]);break
    need(nxt in at,'effect_body_falls_out');here=nxt
  return blocks
 left,right=graph(original),graph(candidate);mapping={};reverse={};todo=[(pc,pc)]
 while todo:
  a,b=todo.pop()
  if a in mapping:need(mapping[a]==b,'effect_inconsistent_join');continue
  need(b not in reverse,'effect_nonbijective_CFG');mapping[a]=b;reverse[b]=a;x,y=left[a],right[b];need(x['kind'][0]==y['kind'][0] and len(x['edges'])==len(y['edges']),'effect_control_shape_difference')
  if x['kind'][0] in ('call','ret'):need(x['kind']==y['kind'],'effect_call_target_or_return_cleanup_difference')
  todo.extend(zip(x['edges'],y['edges']))
 need(set(mapping)==set(left) and set(reverse)==set(right),'effect_unreachable_bytes_or_blocks')
 # Conservative GPR liveness: partial writes never kill a full register.
 aliases={name:i for i,names in enumerate((('eax','ax','al','ah'),('ecx','cx','cl','ch'),('edx','dx','dl','dh'),('ebx','bx','bl','bh'),('esp','sp'),('ebp','bp'),('esi','si'),('edi','di'))) for name in names}
 def uses(i):
  read,write=i.regs_access();reads={aliases[i.reg_name(r)] for r in read if i.reg_name(r) in aliases};kills={aliases[i.reg_name(r)] for r in write if i.reg_name(r) in aliases and i.reg_name(r).startswith('e')};return reads,kills
 def liveness(g):
  live={p:set() for p in g};out={p:set() for p in g}
  for _ in range(256):
   changed=False
   for p,b in g.items():
    end=set(range(8)) if b['kind'][0]=='call' else set(exit_live_registers)|{4} if b['kind'][0]=='ret' else set().union(*(live[e] for e in b['edges']));v=set(end)
    for i in reversed(b['body']):reads,kills=uses(i);v=(v-kills)|reads
    if v!=live[p] or end!=out[p]:live[p]=v;out[p]=end;changed=True
   if not changed:return out
  raise Refusal('effect_liveness_budget')
 la,lb=liveness(left),liveness(right);pairs=[]
 for a,b in sorted(mapping.items()):
  x,y=left[a],right[b];unchanged=[bytes(i.bytes) for i in x['body']]==[bytes(i.bytes) for i in y['body']]
  if not unchanged:
   for i in x['body']+y['body']:need(i.mnemonic in ('mov','lea','add','sub','cmp','push') and i.addr_size==4 and list(i.prefix)==[0,0,0,0],'effect_changed_instruction_domain')
  pairs.append(dict(left_pc=a,right_pc=b,left=x['body'],right=y['body'],unchanged=unchanged,live_registers=sorted(la[a]|lb[b]),terminator=x['kind'][0]))
 need(0<sum(not p['unchanged'] for p in pairs)<=2,'effect_changed_block_budget');return pairs,mapping

def certify_typed_effects(original,candidate,*,pc,lifts,solver,exit_live_registers,fault_context='full-registers',fault_live_registers=None,boundary_live_registers=(),arbitrary_event_memory=False):
 """Complete direct-CFG obligation; caller still owns artifacts/relocations/EH.

 This function has no queue side effects. An event-only diagnostic must not be
 treated as a full fault-context or universal function-contract proof.
 """
 import json
 need(isinstance(lifts,list) and len(lifts)==2,'effect_missing_typed_pair');lookups=[]
 for raw,lift in zip((original,candidate),lifts):
  need(lift.get('schema')=='sharpretro_instruction_lift_v1' and lift.get('mode')=='Bits32' and lift.get('pc')==pc and lift.get('byte_length')==len(raw) and lift.get('decoded_bytes')==len(raw) and lift.get('decode_complete')is True and lift.get('unprocessed_hex')=='' and lift.get('lift_errors')==0 and lift.get('opaque_instructions')==0,'effect_incomplete_or_unknown_lift')
  rows=lift.get('instructions');need(isinstance(rows,list) and len(rows)<=256,'effect_typed_instruction_budget');offset=0;lookup={}
  for row in rows:
   size=row.get('length');need(type(size)is int and size>0 and row.get('pc')==pc+offset and row.get('offset')==offset and row.get('raw_hex')==raw[offset:offset+size].hex() and row.get('lift_error')is None and row.get('opaque_markers')==[] and row.get('tree',{}).get('type')=='LiftIl.IlBlock','effect_typed_byte_binding');lookup[pc+offset]=row;offset+=size
  need(offset==len(raw),'effect_typed_range_coverage');lookups.append(lookup)
 pairs,mapping=pair_cfg(original,candidate,pc,exit_live_registers);proofs=[]
 for pair in pairs:
  if pair['unchanged']:continue
  need(set(boundary_live_registers)<=set(range(8)),'effect_boundary_register_domain')
  live=sorted(set(pair['live_registers'])|set(boundary_live_registers))
  proof=prove_window([lookups[0][i.address] for i in pair['left']],[lookups[1][i.address] for i in pair['right']],live,solver,fault_context=fault_context,fault_live_registers=fault_live_registers,arbitrary_event_memory=arbitrary_event_memory)
  need(proof['status']=='unsat','effect_window_not_proved:'+proof['status']);proof.update(original_block_pc=pair['left_pc'],candidate_block_pc=pair['right_pc'],original_instruction_count=len(pair['left']),candidate_instruction_count=len(pair['right']));proofs.append(proof)
 return dict(rule='x86-flat32-direct-CFG-ordered-ABI-effects-v1',effect_windows=proofs,control_bijection={str(a):b for a,b in mapping.items()},complete_original_bytes=len(original),complete_candidate_bytes=len(candidate),unchanged_blocks=sum(p['unchanged'] for p in pairs),typed_pair_sha256=hashlib.sha256(json.dumps(lifts,sort_keys=True,separators=(',',':')).encode()).hexdigest(),fault_observation_profile=fault_context,exit_live_registers=sorted(exit_live_registers),strict_byte_match=False,whole_function_equivalence_proven=False,proof=False)
