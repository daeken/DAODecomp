"""Open typed loop graphs: order/aliasing observations, never game proof."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,binary,write,tmp
from test_replayable_stackargs import row,ret
from test_replayable_byvalue import push,load

def binary(op,left,right,bits=32):return node("IlBin",Op=dict(name=op),L=left,R=right,Ty=ty(bits))

def reg32(i):return node("IlCast",Kind=dict(name="Trunc"),X=reg(i),Ty=ty(32))

def fixture(stride=8,words=2):
 base=0x502000
 def branch(target,condition=None):return node('IlBranch',Kind=dict(name='Jmp' if condition is None else 'CondJmp'),Target=const(base+target,64),Cond=condition)
 rows=[row(base,[write(1,load(binary('Add',reg(4),const(8,64)))),branch(11,binary('Eq',reg32(1),const(0),1))]),
 row(base+1,[write(2,load(binary('Add',reg(4),const(12,64)))),write(0,load(binary('Add',reg(4),const(4,64)))),*push(reg32(6))]),
 row(base+2,[branch(8,binary('Eq',reg32(0),const(0),1))])]
 body=[]
 for i in range(words):body.extend([write(6,load(binary('Add',reg(2),const(i*4,64)))),node('IlStore',Addr=binary('Add',reg(0),const(i*4,64)),Val=reg32(6))])
 rows.extend([row(base+3,body),row(base+4,[]),row(base+5,[]),row(base+6,[]),row(base+7,[branch(8)]),row(base+8,[write(1,binary('Sub',reg32(1),const(1))),write(0,binary('Add',reg32(0),const(stride))),branch(2,binary('Ne',reg32(1),const(0),1))]),row(base+9,[node('IlLet',Id=0,Val=load(reg(4))),write(4,binary('Add',reg(4),const(4,64))),write(6,tmp(0,32))]),row(base+10,[]),row(base+11,ret(0),'c3')])
 # Empty rows above are open no-effect instructions, still fully covered.
 return dict(lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),counted_loops=True,rva=0x2000,image_base=0x500000,module='open.exe')

@unittest.skipUnless(DLL.exists(),'build changed component first')
class LoopTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_ordered_graph_retains_aliasable_stack_return_and_loop(self):
  r=self.recover(fixture());self.assertEqual(r['status'],'generated',r);g=r['ir']['graph'];self.assertEqual(len(g['loops']),1);self.assertEqual(r['ir']['destination_stride'],8);self.assertEqual(len(r['ir']['transfers']),2);self.assertIn('no forwarding',g['memory_model']);self.assertEqual(g['blocks'][-1]['return_target']['kind'],'memory_read');body=g['blocks'][3];self.assertEqual([e['kind'] for e in body['effects'] if e['kind'].startswith('memory_')],['memory_read','memory_store']*2);self.assertNotIn('memmove',r['source']);self.assertEqual(r['source'].count(' = read_word('),2)
 def test_zero_one_wrap_and_overlapping_memory_observations(self):
  r=self.recover(fixture());self.assertEqual(r['status'],'generated',r)
  # Execute the recovered CFG with a deliberately aliasable byte memory, not
  # the source recognizer. Bounds exhaustion is a test failure, never success.
  graph=r['ir']['graph'];blocks={b['pc']:b for b in graph['blocks']}
  def execute(count,destination,source):
   regs={i:0x3000+i for i in range(16)};regs[4]=0x1000;memory={};reads={};trace=[]
   def store(a,v):
    for j in range(4):memory[(a+j)&0xffffffff]=(v>>(j*8))&255
   for a,v in [(0x1000,0xdeadbeef),(0x1004,destination),(0x1008,count),(0x100c,source),(source,0x12345678),((source+4)&0xffffffff,0xabcdef01)]:store(a,v)
   pc=graph['blocks'][0]['pc']
   for budget in range(64):
    b=blocks[pc];entry=dict(regs)
    def val(x):
     k=x['kind']
     if k=='constant':return x['value']
     if k=='block_register':return entry[x['register']]
     if k=='register_input':return 0x1000 if x['index']==4 else 0x3000+x['index']
     if k=='wrapped_stack_address':return (0x1000+x['offset'])&0xffffffff
     if k=='add':return (val(x['left'])+x['offset'])&0xffffffff
     if k=='memory_read':return reads[(x['pc'],x['read_ordinal'])]
     if k=='bit_operation':
      vs=[val(v) for v in x['operands']];op=x['operation'];a=vs[0];z=vs[-1];return ({'Add':lambda:a+z,'Sub':lambda:a-z,'Eq':lambda:int(a==z),'Ne':lambda:int(a!=z),'Trunc':lambda:a,'Zext':lambda:a}[op]() & ((1<<x['bits'])-1))
     raise AssertionError(x)
    for e in b['effects']:
     if e['kind']=='memory_read':
      a=val(e['address']);v=sum(memory.get((a+j)&0xffffffff,0)<<(8*j) for j in range(4));reads[(e['pc'],e['value']['read_ordinal'])]=v;trace.append(('read',a,v))
     elif e['kind']=='memory_store':a=val(e['address']);v=val(e['value']);store(a,v);trace.append(('store',a,v))
    regs.update({int(k):val(v) for k,v in b['registers'].items()})
    if b['return_cleanup'] is not None:return trace,val(b['return_target'])
    condition=bool(val(b['predicate'])) if b['predicate'] else None;edge=next(e for e in b['edges'] if e['taken'] is None or e['taken']==condition);pc=edge['target']
   raise TimeoutError('test interpreter budget exhausted; outcome unknown')
  zero,_=execute(0,0,0x2000);self.assertEqual(len(zero),2) # count then RET, no pointer/source reads
  one,_=execute(1,0x2100,0x2000);self.assertEqual([x[:2] for x in one if x[1]>=0x2000],[('read',0x2000),('store',0x2100),('read',0x2004),('store',0x2104)])
  overlap,_=execute(1,0x2004,0x2000);self.assertEqual([x[2] for x in overlap if x[0]=='store' and x[1]>=0x2000],[0x12345678,0x12345678])
  wrap,_=execute(2,0xfffffff8,0x2000);self.assertEqual([x[1] for x in wrap if x[0]=='store' and x[1] in (0xfffffff8,0xfffffffc,0,4)],[0xfffffff8,0xfffffffc]) # next destination wraps to null: guarded
  with self.assertRaises(TimeoutError):execute(0xffffffff,0x2100,0x2000)
  alias,returned=execute(1,0x1000,0x2000);self.assertEqual(returned,0x12345678) # RET is not stale abstract entry_return_address
 def test_stride_and_word_count_are_derived_not_fixed(self):
  for stride,words in ((4,1),(16,4),(4096,3)):
   r=self.recover(fixture(stride,words));self.assertEqual(r['status'],'generated',r);self.assertEqual(len(r['ir']['transfers']),words);self.assertEqual(r['ir']['destination_stride'],stride)
 def test_count_step_or_backedge_refuses(self):
  for edit in ('step','edge','guard'):
   p=fixture();l=p['lift']['instructions'][8]['tree']['Body']
   if edit=='step':l[0]['Val']['R']=const(2)
   elif edit=='edge':l[-1]['Target']=const(0x502001,64)
   else:l[-1]['Cond']=binary('Eq',reg32(1),const(0),1)
   self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_intervening_read_or_store_cannot_be_dropped_or_grouped(self):
  p=fixture();b=p['lift']['instructions'][3]['tree']['Body'];b[1],b[2]=b[2],b[1];self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_unknown_predicate_external_effect_and_unreachable_bytes_refuse(self):
  for mode in ('unknown','call','unreachable','escape'):
   p=fixture()
   if mode=='unknown':p['lift']['instructions'][2]['tree']['Body'][0]['Cond']=node('IlUndefined',Ty=ty(1),Reason='open unknown')
   elif mode=='call':p['lift']['instructions'][7]['tree']['Body'][0]['Kind']['name']='Call'
   elif mode=='unreachable':p['lift']['instructions'][7]['tree']['Body'][0]['Target']=const(0x50200b,64)
   else:p['lift']['instructions'][3]['tree']['Body'][1]['Val']=reg32(4)
   self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_stack_join_mismatch_and_unaligned_save_refuse(self):
  p=fixture();p['lift']['instructions'][3]['tree']['Body'].append(write(4,binary('Sub',reg(4),const(4,64))));self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['lift']['instructions'][1]['tree']['Body'][-2]['Val']['R']=const(3,64);self.assertEqual(self.recover(p)['status'],'unsupported')

 def test_wide_carry_is_not_truncated_before_shift(self):
  p=fixture();p.pop('counted_loops');p['graph_paths']=True
  wide=binary('Add',const(0xffffffff,64),const(1,64),64)
  carry=binary('Shr',wide,const(32,64),64)
  p['lift']['instructions'][3]['tree']['Body'][0]['Val']=node('IlCast',Kind=dict(name='Trunc'),X=carry,Ty=ty(32))
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);stores=[e for b in r['ir']['blocks'] for e in b['effects'] if e['kind']=='memory_store' and e['pc']==0x502003];self.assertEqual(stores[0]['value'],dict(kind='constant',value=1,bits=32))
 def test_direct_branch_form_and_prefix_are_required(self):
  for mode in ('register','lock','width'):
   p=fixture()
   if mode=='register':p['lift']['instructions'][2]['tree']['Body'][0]['Target']=reg(0)
   elif mode=='lock':p['lift']['instructions'][1]['decoded']['P']['Lock']=True
   else:p['lift']['instructions'][3]['tree']['Body'][0]['Val']['Ty']=ty(16)
   self.assertEqual(self.recover(p)['status'],'unsupported')

 def test_generated_open_loop_has_distinct_temporary_names_and_valid_cpp(self):
  import shutil,tempfile
  from pathlib import Path
  r=self.recover(fixture(words=4));self.assertEqual(r['status'],'generated',r)
  for i in range(4):self.assertIn('unsigned int word_%d =' % i,r['source'])
  compiler=shutil.which('clang++')
  if not compiler:self.skipTest('optional host source syntax check compiler unavailable')
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'open.cpp';p.write_text(r['source']);result=subprocess.run([compiler,'-m32','-fms-extensions','-fsyntax-only','-Wno-ignored-pragmas',str(p)],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)

 def test_independent_undefined_occurrences_never_become_equal(self):
  for shared_reason in (True,False):
   p=fixture();p.pop('counted_loops');p['graph_paths']=True
   undefined=lambda reason:node('IlUndefined',Ty=ty(1),Reason=reason)
   p['lift']['instructions'][0]['tree']['Body']=[node('IlWriteReg',Kind=dict(name='Eflags'),Idx=2,Val=undefined('IMUL1 flag 2')),write(0,node('IlReadReg',Kind=dict(name='Eflags'),Idx=2,Ty=ty(1))),node('IlWriteReg',Kind=dict(name='Eflags'),Idx=2,Val=undefined('IMUL1 flag 2' if shared_reason else 'different diagnostic')),write(1,node('IlReadReg',Kind=dict(name='Eflags'),Idx=2,Ty=ty(1))),write(2,binary('Eq',reg32(0),reg32(1),1)),*p['lift']['instructions'][0]['tree']['Body']]
   r=self.recover(p);self.assertEqual(r['status'],'unsupported',r);self.assertIn('graph_undefined_architectural_value',r['blocker'])
 def test_even_unused_or_once_captured_undefined_is_conservatively_refused(self):
  p=fixture();p.pop('counted_loops');p['graph_paths']=True;p['lift']['instructions'][3]['tree']['Body'].insert(0,node('IlLet',Id=88,Val=node('IlUndefined',Ty=ty(1),Reason='open unused value')));r=self.recover(p);self.assertEqual(r['status'],'unsupported',r);self.assertIn('graph_undefined_architectural_value',r['blocker'])
