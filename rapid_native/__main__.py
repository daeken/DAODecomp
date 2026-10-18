import argparse
import json
from pathlib import Path
from .pipeline import compare,VM_ORIGINAL
from .propose import propose
p=argparse.ArgumentParser(description='Native C++ source and pinned original -> compiler/reccmp loop')
s=p.add_subparsers(dest='command',required=True)
a=s.add_parser('compare');a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--vcvars',required=True);a.add_argument('--vm',default='Windows 11');a.add_argument('--vm-original',default=VM_ORIGINAL);a.add_argument('--optimization',choices=['/O1','/O2','/Ox','/Od'],default='/O2')
a=s.add_parser('propose');a.add_argument('--root',type=Path,required=True);a.add_argument('--rva',type=lambda v:int(v,0),action='append',required=True);a.add_argument('--feedback',type=Path)
a=s.add_parser('prepare');a.add_argument('--root',type=Path);a.add_argument('--max-groups',type=int,default=0)
a=s.add_parser('run');a.add_argument('--root',type=Path);a.add_argument('--vcvars',default=r'C:\Users\daeken\tools\VC8-SP1\vcvars.cmd');a.add_argument('--lanes',type=int,default=4);a.add_argument('--request-ceiling',type=int,default=120);a.add_argument('--max-repairs',type=int,default=6);a.add_argument('--stagnation-limit',type=int,default=3);a.add_argument('--max-dispatches',type=int,default=0);a.add_argument('--batch')
a=s.add_parser('continue-retained');a.add_argument('--root',type=Path);a.add_argument('--receipt',type=Path);a.add_argument('--max-repairs',type=int,default=6)
a=s.add_parser('status');a.add_argument('--root',type=Path)
a=s.add_parser('pause');a.add_argument('--root',type=Path);a.add_argument('--resume',action='store_true')
a=p.parse_args()
if a.command=='compare':value=compare(a.source,a.output,a.vcvars,a.vm,a.vm_original,optimization=a.optimization)
elif a.command=='propose':value=str(propose(a.root,a.rva,a.feedback.read_text() if a.feedback else None))
else:
    from .queue import ROOT,prepare,run,status,native_store,continue_retained
    root=a.root or ROOT
    if a.command=='prepare':value=prepare(root,a.max_groups)
    elif a.command=='run':run(root,a.vcvars,lanes=a.lanes,request_ceiling=a.request_ceiling,max_repairs=a.max_repairs,stagnation_limit=a.stagnation_limit,max_dispatches=a.max_dispatches,only_batch=a.batch);value=status(root)
    elif a.command=='continue-retained':value=continue_retained(root,a.receipt,a.max_repairs)
    elif a.command=='status':value=status(root)
    else:
        store=native_store(root);store.pause(not a.resume);value=status(root)
print(json.dumps(value,indent=2))

if type(value) is dict and value.get('exit_code'): raise SystemExit(1)
