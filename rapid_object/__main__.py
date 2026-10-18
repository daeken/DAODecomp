import argparse
import json
from pathlib import Path
from .catalog import ROOT,prepare,open_store
from .queue import run,status
from .build import VCVARS
p=argparse.ArgumentParser(description='All-inventory C++ -> historical VC8 COFF -> exact original comparison')
s=p.add_subparsers(dest='command',required=True)
a=s.add_parser('prepare');a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--group-functions',type=int,default=12)
a=s.add_parser('run');a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--vcvars',default=VCVARS);a.add_argument('--lanes',type=int,default=16);a.add_argument('--request-ceiling',type=int,default=120);a.add_argument('--max-repairs',type=int,default=6);a.add_argument('--stagnation-limit',type=int,default=3);a.add_argument('--max-dispatches',type=int,default=0);a.add_argument('--batch')
a=s.add_parser('status');a.add_argument('--root',type=Path,default=ROOT)
a=s.add_parser('pause');a.add_argument('--root',type=Path,default=ROOT)
a=p.parse_args()
if a.command=='prepare':value=prepare(a.root,a.group_functions)
elif a.command=='run':run(a.root,a.vcvars,lanes=a.lanes,request_ceiling=a.request_ceiling,max_repairs=a.max_repairs,stagnation_limit=a.stagnation_limit,max_dispatches=a.max_dispatches,only_batch=a.batch);value=status(a.root)
elif a.command=='pause':open_store(a.root).pause(True);value=status(a.root)
else:value=status(a.root)
print(json.dumps(value,indent=2))
