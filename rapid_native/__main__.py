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
a=s.add_parser('run');a.add_argument('--root',type=Path);a.add_argument('--vcvars',default=r'C:\Users\daeken\tools\VC8-SP1\vcvars.cmd')
a=s.add_parser('status');a.add_argument('--root',type=Path)
a=s.add_parser('pause');a.add_argument('--root',type=Path);a.add_argument('--resume',action='store_true')
a=p.parse_args()
if a.command=='compare':value=compare(a.source,a.output,a.vcvars,a.vm,a.vm_original,optimization=a.optimization)
elif a.command=='propose':value=str(propose(a.root,a.rva,a.feedback.read_text() if a.feedback else None))
else:
    from .queue import ROOT,prepare,run,status,native_store
    root=a.root or ROOT
    if a.command=='prepare':value=prepare(root,a.max_groups)
    elif a.command=='run':run(root,a.vcvars);value=status(root)
    elif a.command=='status':value=status(root)
    else:
        store=native_store(root);store.pause(not a.resume);value=status(root)
print(json.dumps(value,indent=2))

if type(value) is dict and value.get('exit_code'): raise SystemExit(1)
