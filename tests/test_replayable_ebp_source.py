"""Synthetic compiler-frame source proposals, not original/game equivalence."""
import copy,json,struct,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,tmp,binary
from test_replayable_stackargs import ret,row
from test_replayable_frame_flow import push as frame_push
from test_replayable_terminal_calls import fixture as terminal

BASE=0x501000;ALLOC=0x502000;LATER=0x502100;HANDLER=0x503000;COOKIE=0x504000;OUTER=0x505000;INNER=0x505100;RESUME=0x505200

def push(v):return frame_push(v if v['Ty']['Bits']==32 else node('IlCast',Kind=dict(name='Trunc'),X=v,Ty=ty(32)))
def addr(off):return binary('Add',reg(5),const(off&0xffffffffffffffff,64))
def store(off,v):return node('IlStore',Addr=addr(off),Val=v if v['Ty']['Bits'] in (8,32) else node('IlCast',Kind=dict(name='Trunc'),X=v,Ty=ty(32)))
def load(off):return node('IlLoad',Addr=addr(off),Ty=ty(32))
def call(target):return [node('IlLet',Id=0,Val=const(target,32)),node('IlBranch',Kind=dict(name='Call'),Target=tmp(0,32),Cond=None)]
def jump(target):return [node('IlBranch',Kind=dict(name='Jmp'),Target=const(target,32),Cond=None)]
def stackadd(n):return [write(4,binary('Add',reg(4),const(n,64)))]
def fixture():
 runtime=terminal()['runtime_terminal_evidence'];throw=runtime['target']
 def rows(start,parts):
  result=[]
  for raw,effects in parts:
   if raw=='e800000000':
    target=int(effects[0]['Val']['Bits']['decimal']);raw='e8'+struct.pack('<i',target-start-5).hex();effects=[effects[0],node('IlLet',Id=1,Val=const(start+5,32)),write(4,binary('Sub',reg(4),const(4,64))),node('IlStore',Addr=reg(4),Val=tmp(1,32)),effects[-1]]
   result.append(row(start,effects,raw));start+=len(bytes.fromhex(raw))
  return result
 prologue=['55','8bec','6aff','68'+struct.pack('<I',HANDLER).hex(),'64a100000000','50','83ec0c','53','56','57','a1'+struct.pack('<I',COOKIE).hex(),'33c5','50','8d45f4','64a300000000','8965f0']
 first=rows(BASE,[(raw,[store(-16,reg(4))] if i==15 else [])for i,raw in enumerate(prologue)])
 at=first[-1]['pc']+first[-1]['length'];join=BASE+0x100
 first+=rows(at,[('8bf9',[write(7,reg(1))]),('897dec',[store(-20,reg(7))]),('8b7508',[write(6,load(8))]),('6a00',push(const(0))),('56',push(reg(6))),('c745fc00000000',[store(-4,const(0))]),('e800000000',call(ALLOC)),('83c408',stackadd(8)),('894508',[store(8,reg(0))]),('eb00',jump(join))])
 suffix=rows(join,[('57',push(reg(7))),('e800000000',call(LATER)),('83c404',stackadd(4))])
 end=suffix[-1]['pc']+suffix[-1]['length'];suffix+=rows(end,[(raw,ret(8) if raw=='c20800'else [])for raw in ['8b4df4','64890d00000000','59','5f','5e','5b','8be5','5d','c20800']])
 outer=rows(OUTER,[('8b4508',[write(0,load(8))]),('8965f0',[store(-16,reg(4))]),('8945e8',[store(-24,reg(0))]),('6a00',push(const(0))),('50',push(reg(0))),('c645fc02',[store(-4,const(2,8))]),('e800000000',call(ALLOC)),('894508',[store(8,reg(0))]),('83c408',stackadd(8)),('b8'+struct.pack('<I',RESUME).hex(),[write(0,const(RESUME))]),('c3',ret(0))])
 inner=rows(INNER,[('8b75ec',[write(6,load(-20))]),('6a00',push(const(0))),('6a00',push(const(0))),('e800000000',call(throw)),('cc',[])])
 trap=inner[-1]['pc'];inner[-1]['tree']['Body']=[node('IlTrap',Architecture='x86',Vector=3,InstructionPc=const(trap,64),ContinuationPc=const(trap+1,64))]
 resume=rows(RESUME,[('8b7dec',[write(7,load(-20))]),('8b75e8',[write(6,load(-24))])])
 def dep(code,role,continuations):return dict(role=role,graph=dict(entry_va=code[0]['pc'],continuation_candidates=continuations),typed_instructions=[dict(lift=dict(instructions=code))])
 graph=dict(handler=dict(va=HANDLER,profile=dict(cookie_checked=True)),FuncInfo=dict(states=4),unwind_map=dict(transitions=[dict(to_state=v,action_va=0)for v in(-1,-1,1,1)]),try_map=dict(entries=[dict(try_low=state,try_high=state,catch_high=3,handlers=dict(entries=[dict(type_va=0,entry_va=entry)]))for state,entry in[(2,INNER),(0,OUTER)]]))
 frame=dict(normal_paths=[],incoming=dict(required_bytes=8,frame_escaped=False),return_cleanup_bytes=[8],instruction_origins=[r['pc']for r in first+suffix],normal_continuation_contract='synthetic candidate source fixture',exceptional_semantics_unknown=True)
 deps=[dict(target=t,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(t,ret(0),'c3')]))for t in (ALLOC,LATER)]
 return dict(ebp_try_source=True,rva=BASE-0x500000,image_base=0x500000,image_end=0xa00000,module='open.exe',lift=dict(schema='sharpretro_owned_ranges_v1',ranges=[dict(lift=dict(instructions=first)),dict(lift=dict(instructions=suffix))]),frame=frame,eh=dict(graph=graph,dependencies=[dep(inner,'catch_entry',[]),dep(outer,'catch_entry',[RESUME]),dep(resume,'literal_return_continuation_candidate',[])],typed_lift_errors=0,typed_opaque_instructions=0,security_cookie_va=COOKIE),callees=dict(callees=deps,runtime_terminal_evidence=runtime))

def bypass(p,index,target,*,initial=None):
 rows=p['lift']['ranges'][0]['lift']['instructions'];start=rows[index]['pc'];targetpc=rows[target]['pc'];extra=2+(2 if initial is not None else 0)
 for r in rows[index:]:
  r['pc']+=extra
  if r['raw_hex'].startswith('e8'):
   dest=int(r['tree']['Body'][0]['Val']['Bits']['decimal']);r['raw_hex']='e8'+struct.pack('<i',dest-r['pc']-5).hex();r['tree']['Body'][1]['Val']=const(r['pc']+5,32)
  branch=r['tree']['Body'][-1] if r['tree']['Body'] else {}
  if branch.get('type')=='LiftIl.IlBranch' and branch['Kind']['name'] in ('Jmp','CondJmp'):
   dest=int(branch['Target']['Bits']['decimal'])
   if start<=dest<BASE+0x100:branch['Target']=const(dest+extra,32)
 condition=node('IlBin',Op=dict(name='Eq'),L=load(8),R=const(0,32),Ty=ty(1));branch=node('IlBranch',Kind=dict(name='CondJmp'),Target=const(targetpc+extra,32),Cond=condition)
 prefix=[] if initial is None else [row(start,initial,'8bf9')]
 prefix.append(row(start+len(prefix)*2,[branch],'7400'));rows[index:index]=prefix;p['frame']['instruction_origins']=[r['pc']for part in p['lift']['ranges']for r in part['lift']['instructions']]
 return p

@unittest.skipUnless(DLL.exists(),'build changed component first')
class EbpSourceTests(unittest.TestCase):
 def run_source(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_shared_suffix_keeps_normal_and_catch_exception_regions(self):
  r=self.run_source(fixture());self.assertEqual(r['status'],'generated',r);s=r['source'];self.assertEqual(s.count('r_0 = fn_00002100('),2);self.assertLess(s.index('r_0 = fn_00002100('),s.index('} catch (...)'));self.assertIn('throw;',s);self.assertIn('__debugbreak();',s);self.assertFalse(r['proof']);self.assertEqual(len(r['ir']['traps']),1);self.assertTrue(r['ir']['traps'][0]['delivery_and_resumption_unknown'])
 def test_wrong_trap_vector_origin_or_continuation_refuses(self):
  for key,value in [('Vector',0),('Architecture','other'),('InstructionPc',const(7,64)),('ContinuationPc',const(7,64))]:
   p=fixture();p['eh']['dependencies'][0]['typed_instructions'][0]['lift']['instructions'][-1]['tree']['Body'][0][key]=value;self.assertEqual(self.run_source(p)['status'],'unsupported',key)
 def test_nonzero_rethrow_arguments_cannot_become_throw_expression(self):
  p=fixture();p['eh']['dependencies'][0]['typed_instructions'][0]['lift']['instructions'][1]['tree']['Body']=push(const(7));self.assertEqual(self.run_source(p)['blocker'],'EBP_try_rethrow_arguments')
 def test_extra_prologue_effect_or_unwind_action_refuses(self):
  p=fixture();p['lift']['ranges'][0]['lift']['instructions'][2]['raw_hex']='6a00';self.assertEqual(self.run_source(p)['blocker'],'EBP_try_complete_compiler_prologue')
  p=fixture();p['eh']['graph']['unwind_map']['transitions'][0]['action_va']=123;self.assertEqual(self.run_source(p)['blocker'],'EBP_try_two_try_zero_actions')
 def test_changed_state_or_missing_continuation_refuses(self):
  p=fixture();p['eh']['graph']['try_map']['entries'][0]['try_low']=1;self.assertEqual(self.run_source(p)['status'],'unsupported')
  p=fixture();p['eh']['dependencies'][1]['graph']['continuation_candidates']=[];self.assertEqual(self.run_source(p)['blocker'],'EBP_try_unique_catch_continuation')
 def test_opaque_handler_and_unknown_effect_refuse(self):
  p=fixture();p['eh']['typed_opaque_instructions']=1;self.assertEqual(self.run_source(p)['blocker'],'EBP_try_complete_typed_EH')
  p=fixture();p['eh']['dependencies'][0]['typed_instructions'][0]['lift']['instructions'][0]['tree']['Body']=[node('IlIntrin',Name='unknown',Args=[])];self.assertEqual(self.run_source(p)['status'],'unsupported')

 def test_small_unsigned_multiply_avoids_signed_integer_promotion(self):
  p=fixture();r=p['lift']['ranges'][0]['lift']['instructions'][16];small=lambda:node('IlCast',Kind=dict(name='Trunc'),X=reg(1),Ty=ty(16));r['tree']['Body'].append(write(0,node('IlBin',Op=dict(name='Mul'),L=small(),R=small(),Ty=ty(16))));result=self.run_source(p);self.assertEqual(result['status'],'generated',result);self.assertIn('static_cast<unsigned int>(static_cast<unsigned short>',result['source'])
 def test_signed_expression_and_source_name_injection_refuse(self):
  p=fixture();p['module']='open.exe\nunsigned injected;';self.assertEqual(self.run_source(p)['blocker'],'EBP_try_module_name')
  p=fixture();r=p['lift']['ranges'][0]['lift']['instructions'][16];value=const(7);value['Ty']['Signed']=True;r['tree']['Body'].append(write(0,value));self.assertEqual(self.run_source(p)['blocker'],'EBP_try_expression_width')

 def test_no_extra_effects_can_hide_in_call_frame_or_continuation(self):
  for dep,index in [(1,1),(1,5),(1,6),(1,9),(1,10)]:
   p=fixture();r=p['eh']['dependencies'][dep]['typed_instructions'][0]['lift']['instructions'][index];r['tree']['Body'].insert(0,node('IlIntrin',Name='hidden',Args=[]));self.assertEqual(self.run_source(p)['status'],'unsupported',(dep,index))
 def test_unexpected_return_and_nested_branch_refuse(self):
  p=fixture();r=p['eh']['dependencies'][2]['typed_instructions'][0]['lift']['instructions'][0];r['tree']['Body']=ret(0);r['raw_hex']='c3';self.assertEqual(self.run_source(p)['blocker'],'EBP_try_unexpected_return')
  p=fixture();r=p['eh']['dependencies'][2]['typed_instructions'][0]['lift']['instructions'][0];r['tree']['Body'].insert(0,jump(RESUME+1)[0]);self.assertEqual(self.run_source(p)['status'],'unsupported')
 def test_call_stack_width_and_return_address_refuse(self):
  for field in ['width','address']:
   p=fixture();r=p['eh']['dependencies'][1]['typed_instructions'][0]['lift']['instructions'][6]
   if field=='width':r['tree']['Body'][2]['Val']=binary('Sub',reg(4),const(8,64))
   else:r['tree']['Body'][1]['Val']=const(123,32)
   self.assertEqual(self.run_source(p)['status'],'unsupported',field)

 def test_forward_join_refuses_register_assignment_bypass(self):
  p=bypass(fixture(),16,17);self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_register_7')
 def test_prior_initialized_register_survives_forward_join(self):
  p=bypass(fixture(),16,17,initial=[write(7,reg(1))]);r=self.run_source(p);self.assertEqual(r['status'],'generated',r)
 def test_parent_word_assignment_bypass_and_catch_entry_refuse(self):
  p=bypass(fixture(),17,18);self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_parent_word')
  p=fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];rows[17]['tree']['Body']=[];rows[24]['tree']['Body'].append(store(-20,reg(7)));self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_parent_word')
 def test_prior_parent_word_survives_forward_join(self):
  p=bypass(fixture(),17,18,initial=[store(-20,reg(7))]);r=self.run_source(p);self.assertEqual(r['status'],'generated',r)
 def test_outgoing_stack_bypass_refuses_without_filling_missing_argument(self):
  p=bypass(fixture(),19,20);self.assertEqual(self.run_source(p)['blocker'],'EBP_try_incompatible_source_stack_join')
 def test_outgoing_capture_identity_must_agree_at_join(self):
  p=fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];rows[20]['tree']['Body']=stackadd(4)+push(const(0));p=bypass(p,20,21);self.assertEqual(self.run_source(p)['blocker'],'EBP_try_incompatible_source_stack_join')
 def test_flag_assignment_bypass_refuses(self):
  p=fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];rows[18]['tree']['Body'].append(node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(1,1)));rows[19]['tree']['Body'].insert(0,write(0,node('IlReadReg',Kind=dict(name='Eflags'),Idx=6,Ty=ty(1))));p=bypass(p,18,19);self.assertEqual(self.run_source(p)['blocker'],'EBP_try_region_entry_flags_unknown')
 def test_instruction_temporary_cannot_escape_a_skipped_row(self):
  p=fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];rows[16]['tree']['Body'].append(node('IlLet',Id=99,Val=const(1,32)));rows[17]['tree']['Body'].append(write(0,tmp(99,32)));self.assertEqual(self.run_source(p)['status'],'unsupported')

 def test_try_marker_and_literal_continuation_cannot_be_bypassed(self):
  p=bypass(fixture(),21,22);self.assertEqual(self.run_source(p)['blocker'],'EBP_try_outer_try_body')
  p=fixture();rows=p['eh']['dependencies'][1]['typed_instructions'][0]['lift']['instructions'];rows[9]['raw_hex']='7500000000';rows[9]['tree']['Body']=[node('IlBranch',Kind=dict(name='CondJmp'),Target=const(rows[10]['pc'],32),Cond=const(1,1))];self.assertEqual(self.run_source(p)['blocker'],'EBP_try_catch_continuation_not_definite')
