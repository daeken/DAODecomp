"""Typed #BP must be retained by its source profile or refused elsewhere."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,const,ty
from test_replayable_fault_paths import guarded
from test_replayable_owned_ranges import envelope
from test_replayable_terminal_calls import fixture as terminal

def trap(pc):return node('IlTrap',Architecture='x86',Vector=3,InstructionPc=const(pc,64),ContinuationPc=const(pc+1,64))

@unittest.skipUnless(DLL.exists(),'build changed component first')
class TrapConsumerTests(unittest.TestCase):
 def run_ir(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_normal_cleanup_does_not_treat_trap_as_fallthrough_or_return(self):
  p=guarded();row=p['lift']['instructions'][0];row['tree']['Body']=[trap(row['pc'])];p=dict(normal_return_evidence=True,target=row['pc'],lift=p['lift']);self.assertEqual(self.run_ir(p)['status'],'unsupported')
 def test_nested_trap_cannot_hide_inside_noncontrol_effect(self):
  for wrap in (lambda t:node('IlLet',Id=0,Val=t),lambda t:node('IlIf',Cond=const(1,1),Then=[t],Else=[])):
   p=guarded();row=p['lift']['instructions'][0];row['tree']['Body']=[wrap(trap(row['pc']))];p=dict(normal_return_evidence=True,target=row['pc'],lift=p['lift']);self.assertEqual(self.run_ir(p)['status'],'unsupported')
 def test_terminal_owned_and_flow_consumers_refuse_unknown_resumption(self):
  p=terminal();r=p['lift']['instructions'][0];r['tree']['Body'].insert(0,trap(r['pc']));self.assertEqual(self.run_ir(p)['status'],'unsupported')
  p=envelope();r=p['ranges'][0]['lift']['instructions'][0];r['tree']['Body'].insert(0,trap(r['pc']));self.assertEqual(self.run_ir(dict(owned_ranges=True,lift=p))['status'],'unsupported')
  p=guarded();r=p['lift']['instructions'][0];r['tree']['Body']=[trap(r['pc'])];self.assertEqual(self.run_ir(p)['status'],'unsupported')
