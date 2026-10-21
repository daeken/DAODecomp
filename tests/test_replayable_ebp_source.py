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
 graph=dict(handler=dict(va=HANDLER,profile=dict(cookie_checked=True)),FuncInfo=dict(states=4,flags=1,bytes_hex="22059319"+"00000000"*7+"01000000"),unwind_map=dict(transitions=[dict(to_state=v,action_va=0)for v in(-1,-1,1,1)]),try_map=dict(entries=[dict(try_low=state,try_high=state,catch_high=3,handlers=dict(entries=[dict(type_va=0,entry_va=entry)]))for state,entry in[(2,INNER),(0,OUTER)]]))
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

def comparison_fixture(other_zero_bound=7):
 p=fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];a=tmp(101,32);diff=tmp(102,32)
 rows[16]['tree']['Body'] += [node('IlLet',Id=101,Val=node('IlCast',Kind=dict(name='Trunc'),X=reg(1),Ty=ty(32))),node('IlLet',Id=102,Val=node('IlBin',Op=dict(name='Sub'),L=a,R=const(other_zero_bound,32),Ty=ty(32))),node('IlWriteReg',Kind=dict(name='Eflags'),Idx=0,Val=node('IlBin',Op=dict(name='Ult'),L=a,R=const(7,32),Ty=ty(1))),node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=node('IlBin',Op=dict(name='Eq'),L=diff,R=const(0,32),Ty=ty(1)))]
 cf=node('IlReadReg',Kind=dict(name='Eflags'),Idx=0,Ty=ty(1));zf=node('IlReadReg',Kind=dict(name='Eflags'),Idx=6,Ty=ty(1));condition=node('IlBin',Op=dict(name='Or'),L=cf,R=zf,Ty=ty(1));rows[17]['tree']['Body'] += [write(1,const(999)),node('IlBranch',Kind=dict(name='CondJmp'),Target=const(rows[18]['pc'],32),Cond=condition)]
 return p

@unittest.skipUnless(DLL.exists(),'build changed component first')
class EbpSourceTests(unittest.TestCase):
 def run_source(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_shared_suffix_keeps_normal_and_catch_exception_regions(self):
  r=self.run_source(fixture());self.assertEqual(r['status'],'generated',r);s=r['source'];self.assertEqual(s.count('= fn_00002100('),2);self.assertLess(s.index('= fn_00002100('),s.index('} catch (...)'));self.assertIn('throw;',s);self.assertIn('__debugbreak();',s);self.assertFalse(r['proof']);self.assertEqual(len(r['ir']['traps']),1);self.assertTrue(r['ir']['traps'][0]['delivery_and_resumption_unknown'])
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

 def test_source_contexts_share_only_explicit_parent_words(self):
  r=self.run_source(fixture());self.assertEqual(r['status'],'generated',r);s=r['source'];self.assertIn('r_main_0 = fn_00002100',s);self.assertIn('r_continuation_0 = fn_00002100',s);self.assertIn('r_allocation_catch_0 = fn_00002000',s);self.assertIn('r_cleanup_catch_6 =',s);self.assertIn('parent_m20 =',s);self.assertIn('parent_m24 =',s);self.assertNotIn('unsigned int r_0;',s);self.assertIn('push_main_',s);self.assertIn('push_continuation_',s)

 def test_zero_extended_capture_uses_word_storage_but_wide_product_stays_wide(self):
  p=fixture();r=p['lift']['ranges'][0]['lift']['instructions'][16];narrow=node('IlCast',Kind=dict(name='Zext'),X=node('IlCast',Kind=dict(name='Trunc'),X=reg(1),Ty=ty(32)),Ty=ty(64));r['tree']['Body'].insert(0,node('IlLet',Id=101,Val=narrow));r['tree']['Body'].append(write(0,tmp(101,64)));wide=node('IlBin',Op=dict(name='Mul'),L=narrow,R=narrow,Ty=ty(64));r['tree']['Body'].append(node('IlLet',Id=102,Val=wide));r['tree']['Body'].append(write(0,node('IlCast',Kind=dict(name='Trunc'),X=tmp(102,64),Ty=ty(32))));result=self.run_source(p);self.assertEqual(result['status'],'generated',result);source=result['source'];self.assertIn(f"unsigned int t_main_{r['pc']:x}_101;",source);self.assertIn(f"unsigned __int64 t_main_{r['pc']:x}_102;",source)

 def test_unsigned_condition_uses_same_captured_operands_after_register_write(self):
  result=self.run_source(comparison_fixture());self.assertEqual(result['status'],'generated',result);source=result['source'];condition=next(line for line in source.splitlines()if 'goto L_main_'in line);self.assertIn(' <= ',condition);self.assertIn('t_main_',condition);self.assertNotIn('r_main_1',condition)
 def test_different_subtraction_bound_does_not_fuse_flags(self):
  result=self.run_source(comparison_fixture(8));self.assertEqual(result['status'],'generated',result);condition=next(line for line in result['source'].splitlines()if 'goto L_main_'in line);self.assertNotIn(' <= ',condition);self.assertIn(' | ',condition)

 def test_wide_product_of_captured_words_keeps_value_without_wide_local(self):
  p=fixture();r=p['lift']['ranges'][0]['lift']['instructions'][16];body=r['tree']['Body'];body.insert(0,node('IlLet',Id=101,Val=node('IlCast',Kind=dict(name='Trunc'),X=reg(1),Ty=ty(32))));operand=node('IlCast',Kind=dict(name='Zext'),X=tmp(101,32),Ty=ty(64));body.append(node('IlLet',Id=102,Val=node('IlBin',Op=dict(name='Mul'),L=operand,R=operand,Ty=ty(64))));body.append(write(1,const(9)));body.append(write(0,node('IlCast',Kind=dict(name='Trunc'),X=tmp(102,64),Ty=ty(32))));result=self.run_source(p);self.assertEqual(result['status'],'generated',result);source=result['source'];self.assertNotIn(f"t_main_{r['pc']:x}_102",source);self.assertIn(f"t_main_{r['pc']:x}_101",source);self.assertIn(' * ',source)

 def test_flag_operand_load_is_captured_once_across_aliasable_store(self):
  p=comparison_fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];next(n for n in rows[16]['tree']['Body']if n.get('Id')==101)['Val']=node('IlLoad',Addr=reg(1),Ty=ty(32));rows[17]['tree']['Body'].insert(0,node('IlStore',Addr=reg(1),Val=const(99,32)));result=self.run_source(p);self.assertEqual(result['status'],'generated',result);source=result['source'];self.assertEqual(source.count('read_word('),2);condition=next(line for line in source.splitlines()if 'goto L_main_'in line);self.assertIn('t_main_',condition);self.assertNotIn('read_word',condition)
 def test_flag_facts_do_not_cross_a_join_with_different_initial_values(self):
  p=comparison_fixture();initial=[write(7,reg(1))]+[node('IlWriteReg',Kind=dict(name='Eflags'),Idx=i,Val=const(0,1))for i in (0,6)];p=bypass(p,16,17,initial=initial);result=self.run_source(p);self.assertEqual(result['status'],'generated',result);condition=[line for line in result['source'].splitlines()if 'goto L_main_'in line][1];self.assertIn('flag_main_0',condition);self.assertIn('flag_main_6',condition);self.assertNotIn(' <= ',condition)
 def test_mistyped_capture_does_not_acquire_unsigned_comparison_fact(self):
  p=comparison_fixture();rows=p['lift']['ranges'][0]['lift']['instructions'];next(n for n in rows[16]['tree']['Body']if n.get('Id')==101)['Val']=reg(1);result=self.run_source(p);self.assertEqual(result['status'],'generated',result);condition=next(line for line in result['source'].splitlines()if 'goto L_main_'in line);self.assertNotIn(' <= ',condition)
 def test_capture_word_narrowing_preserves_arbitrary_high_bits(self):
  p=fixture();r=p['lift']['ranges'][0]['lift']['instructions'][16];r['tree']['Body'].insert(0,node('IlLet',Id=200,Val=node('IlBin',Op=dict(name='Add'),L=reg(1),R=const(0x100000000,64),Ty=ty(64))));r['tree']['Body'].append(write(0,node('IlCast',Kind=dict(name='Trunc'),X=tmp(200,64),Ty=ty(32))));result=self.run_source(p);self.assertEqual(result['status'],'generated',result);self.assertIn(f"unsigned __int64 t_main_{r['pc']:x}_200;",result['source'])


 def test_lexical_shared_suffix_retains_machine_regions_as_unproved_obligations(self):
  p=fixture();p['shared_tail']=True;r=self.run_source(p);self.assertEqual(r['status'],'generated',r);s=r['source'];self.assertEqual(s.count('= fn_00002100('),1);self.assertEqual(s.count('= fn_00002000('),2);self.assertNotIn('cleanup_active',s);self.assertIn('if (retry_completed)',s);self.assertNotIn('for (;;)',s);self.assertNotIn('resumed',s);self.assertNotIn('goto ',s);self.assertEqual(r['ir']['shared_input_registers'],[6,7]);self.assertEqual(r['ir']['continuation_lowering'],'lexical_catch_shared_continuation_v4');self.assertGreater(s.index('= fn_00002100('),s.rindex('} catch (...)'));self.assertIn('__debugbreak();',s);self.assertFalse(r['proof']);self.assertTrue(any('NOT established' in h for h in r['ir']['hypotheses']))
 def test_shared_tail_requires_both_register_inputs(self):
  p=fixture();p['shared_tail']=True;p['eh']['dependencies'][2]['typed_instructions'][0]['lift']['instructions'][0]['tree']['Body']=[];self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_register_7')
 def test_shared_tail_retains_parent_and_stack_dominance_guards(self):
  for index,target in [(17,18),(19,20)]:
   p=bypass(fixture(),index,target);p['shared_tail']=True;self.assertEqual(self.run_source(p)['status'],'unsupported')
 def test_shared_tail_does_not_invent_caller_saved_registers(self):
  p=fixture();p['shared_tail']=True;p['lift']['ranges'][1]['lift']['instructions'][0]['tree']['Body']=push(reg(1));self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_register_1')

 def test_shared_tail_private_parent_must_exist_on_both_paths(self):
  p=fixture();p['shared_tail']=True;p['lift']['ranges'][1]['lift']['instructions'][0]['tree']['Body']=push(load(-24));self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_parent_word')
 def test_shared_tail_retains_aliasable_memory_and_call_order(self):
  p=fixture();p['shared_tail']=True;rows=p['lift']['ranges'][1]['lift']['instructions'];rows[0]['tree']['Body'].insert(0,node('IlStore',Addr=reg(7),Val=const(99,32)));r=self.run_source(p);self.assertEqual(r['status'],'generated',r);s=r['source'];self.assertEqual(s.count('= fn_00002100('),1);self.assertLess(s.index('write_word(static_cast'),s.index('= fn_00002100('));self.assertIn('99u',s)

 def test_resumed_parent_reads_follow_outer_catch_completion(self):
  p=fixture();p['shared_tail']=True;r=self.run_source(p);self.assertEqual(r['status'],'generated',r);s=r['source'];completion=s.index('\n    }',s.index('retry_completed = true;'));resume=s.index('if (retry_completed)',completion)
  for register,parent in [(7,20),(6,24)]:
   assignment='r_continuation_'+str(register)+' = static_cast<unsigned int>(parent_m'+str(parent)+');'
   self.assertEqual(s.count(assignment),1);self.assertLess(resume,s.index(assignment));self.assertGreater(s.index(assignment),completion)
  self.assertLess(s.rindex('} catch (...)'),completion)
 def test_continuation_memory_effect_occurs_outside_allocation_catch(self):
  p=fixture();p['shared_tail']=True;rows=p['eh']['dependencies'][2]['typed_instructions'][0]['lift']['instructions'];rows[1]['tree']['Body'].append(node('IlStore',Addr=reg(7),Val=const(99,32)))
  r=self.run_source(p);self.assertEqual(r['status'],'generated',r);s=r['source'];a=s.index('write_word(static_cast');self.assertLess(s.index('if (retry_completed)'),a);self.assertGreater(a,s.rindex('} catch (...)'));self.assertEqual(s.count('write_word(static_cast'),1)

 def dispatch(self,plan,state,category='eligible_cpp',unchanged=True):
  return self.run_source(dict(ebp_region_dispatch=plan,state=state,category=category,runtime_state_unchanged=unchanged))
 def test_saved_esp_and_state_are_distinct_and_completion_retains_retry_state(self):
  p=fixture();p['shared_tail']=True;r=self.run_source(p);plan=r['ir']['exception_regions'];self.assertEqual(plan['registration_parent_offset'],-12);self.assertEqual(plan['saved_esp_parent_offset'],-16);self.assertEqual(plan['state_parent_offset'],-4)
  regions={x['role']:x for x in plan['regions']};self.assertEqual(regions['catch_preparation']['state'],1)
  for name in ('retry_allocation','catch_completion','literal_continuation','resumed_suffix'):
   self.assertEqual(regions[name]['state'],2);self.assertEqual(regions[name]['handler'],INNER)
  self.assertTrue(regions['literal_continuation']['after_catch_completion']);self.assertFalse(plan['proof'])
 def test_initial_and_resumed_suffix_dispatch_differ(self):
  plan=self.run_source(fixture())['ir']['exception_regions'];self.assertEqual(self.dispatch(plan,0)['handler'],OUTER);self.assertEqual(self.dispatch(plan,2)['handler'],INNER)
 def test_preparation_and_cleanup_failure_cannot_reenter_cleanup(self):
  plan=self.run_source(fixture())['ir']['exception_regions']
  for state in (-1,1,3):self.assertEqual(self.dispatch(plan,state)['status'],'propagate')
 def test_runtime_mutation_and_fault_categories_stay_unknown(self):
  plan=self.run_source(fixture())['ir']['exception_regions']
  for state,category,unchanged in [(None,'eligible_cpp',True),(2,'eligible_cpp',False),(2,'access_fault',True),(2,'foreign',True),(99,'eligible_cpp',True)]:
   r=self.dispatch(plan,state,category,unchanged);self.assertEqual(r['status'],'unknown');self.assertIsNone(r['handler'])
 def test_state_word_cannot_be_confused_with_saved_esp_store(self):
  p=fixture();p['eh']['dependencies'][1]['typed_instructions'][0]['lift']['instructions'][1]['tree']['Body']=[store(-4,reg(4))];self.assertEqual(self.run_source(p)['blocker'],'EBP_try_catch_SP_role')
 def test_unknown_or_changed_state_and_category_profile_refuse(self):
  for value in (reg(0),const(1,8)):
   p=fixture();p['eh']['dependencies'][1]['typed_instructions'][0]['lift']['instructions'][5]['tree']['Body']=[store(-4,value)];self.assertEqual(self.run_source(p)['status'],'unsupported')
  for key,value in [('flags',0),('bytes_hex','21059319'+'00000000'*7+'01000000')]:
   p=fixture();p['eh']['graph']['FuncInfo'][key]=value;self.assertEqual(self.run_source(p)['blocker'],'EBP_regions_exception_category_profile')

 def test_resume_load_cannot_bypass_its_only_definition(self):
  p=fixture();p['shared_tail']=True;rows=p['eh']['dependencies'][2]['typed_instructions'][0]['lift']['instructions'];rows[0]['tree']['Body']=[node('IlBranch',Kind=dict(name='CondJmp'),Target=const(rows[1]['pc'],32),Cond=const(1,1))]
  self.assertEqual(self.run_source(p)['blocker'],'EBP_try_undefined_register_7')
