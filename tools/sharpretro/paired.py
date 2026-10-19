"""Private diagnostic CLI: attested COFF/original -> lossless typed SharpRetro IL.
No semantic acceptance, synthesis, compilation, instruction dropping or normalization.
"""
from pathlib import Path
import argparse, collections, hashlib, json, re, subprocess, sys, time, tempfile, os
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rapid_object import compare
from tools import export_native_sources as exporter
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_GRP_JUMP, CS_GRP_CALL
from capstone.x86 import X86_OP_IMM, X86_OP_REG, X86_OP_MEM
ROOT=Path(__file__).resolve().parent
CONFIG=None

def configure(config_path):
 global CONFIG
 path=Path(config_path).resolve(); data=json.loads(path.read_text())
 def resolved(key):
  p=Path(data[key]); return p.resolve() if p.is_absolute() else (path.parent/p).resolve()
 CONFIG={k:resolved(k) for k in ('sharp_retro_checkout','adapter_dll','build_manifest','original_binary')}
 return CONFIG

def config():
 require(CONFIG is not None,'explicit_config_required'); return CONFIG
REVISION='685b7578457cad325226aa8923b45ded35098fa3'

def atomic(path,value):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
 try:
  with os.fdopen(fd,'w') as out:json.dump(value,out,sort_keys=True,separators=(',',':'));out.write('\n')
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(value, reason):
 if not value: raise ValueError(reason)

def bound_function(summary_path, rva):
 """Recheck retained source/object/compiler/identity inputs, replay exact comparator."""
 path=Path(summary_path).resolve(); folder=path.parent
 report=json.loads(path.read_text()); build=json.loads((folder/'run.json').read_text()); compiler=json.loads((folder/'compiler.json').read_text(encoding='utf-8-sig'))
 source=(folder/'candidate.cpp').read_bytes(); obj=(folder/'candidate.obj').read_bytes()
 require(report['source_sha256']==build['source_sha256']==compare.sha(source),'source_hash')
 require(report['object_sha256']==build['object_sha256']==compare.sha(obj),'object_hash')
 require(report['build']==build and compiler==build['compiler']==report['compiler'],'build_compiler_binding')
 require(build['exit_code']==0 and compiler['sha256']==exporter.SELECTED_COMPILER_SHA256,'compiler_identity')
 require(build['flags']==exporter.SELECTED_FLAGS and build['linked'] is False,'compiler_flags')
 require(report['module_sha256']==build['module_sha256']==exporter.MODULE_SHA256,'module_binding')
 code={p.name:digest(p) for p in (Path(compare.__file__),Path(compare.__file__).with_name('coff.py'))}
 require(report['implementation_sha256']==code,'comparator_binding')
 identities=json.loads((folder/'identities.json').read_text())
 require(identities['requested']==report['requested'] and identities['symbols']==report['symbol_addresses'] and identities['module_sha256']==exporter.MODULE_SHA256,'requested_symbol_binding')
 registry={}
 for name,address in report['symbol_addresses'].items():
  match=re.search(r'(?:^|[?_])(fn|g)_([0-9a-fA-F]{8})(?=@|$)',name)
  require(match is not None and address==0x400000+int(match[2],16),'stable_symbol_identity')
  registry[match[1]+'_'+match[2].lower()]=address
 requested={int(k):v for k,v in report['requested'].items()}
 require(exporter.retained_symbol_bindings(folder/'candidate.obj',requested,registry)==report['symbol_addresses'],'retained_symbol_binding')
 original_path=config()['original_binary']; original=original_path.read_bytes()
 require(compare.sha(original)==exporter.MODULE_SHA256,'original_module_hash')
 replay=compare.compare_bytes(original,obj,requested,report['symbol_addresses'],compare.sha(source),compiler,exporter.MODULE_SHA256)
 require(not replay.get('error') and replay['functions']==report['functions'],'fresh_comparator_replay')
 fs=[f for f in replay['functions'] if f['rva']==rva]
 require(len(fs)==1,'unique_requested_function'); f=fs[0]
 require(f['status'] in ('nonmatch','exact_object_match') and 'relocated_bytes_hex' in f,'unsupported_comparison')
 paths=[path,folder/'candidate.cpp',folder/'candidate.obj',folder/'run.json',folder/'compiler.json',folder/'identities.json']
 binding={'module_sha256':exporter.MODULE_SHA256,'module_path':str(original_path),'module':'DAOrigins.exe','rva':rva,'compiler':compiler,'flags':build['flags'],'files':{str(p):digest(p) for p in paths},'comparator_implementation_sha256':code,'requested':requested[str(rva)] if str(rva) in requested else requested[rva],'symbol_addresses':report['symbol_addresses'],'relocations':f['relocations'],'candidate_raw_coff_bytes_sha256':compare.sha(bytes.fromhex(f['object_bytes_hex'])),'original_body_sha256':f['original_bytes_sha256'],'candidate_relocated_body_sha256':f['relocated_bytes_sha256'],'fresh_comparator_status':f['status']}
 return f,binding

def lift_raw(data,pc=0x401000,identity='synthetic'):
 req={'hex':data.hex(),'pc':pc,'id':identity}
 start=time.perf_counter();run=subprocess.run(['dotnet',str(config()['adapter_dll'])],input=json.dumps(req)+'\n',text=True,capture_output=True,timeout=60)
 require(run.returncode==0,'lifter_process:'+run.stderr)
 result=json.loads(run.stdout);require('adapter_error' not in result,'lifter_error:'+str(result.get('adapter_error')))
 result['elapsed_seconds']=time.perf_counter()-start
 md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True
 decoded=list(md.disasm(data,pc)); cap=[]
 for ins in decoded:
  reads,writes=ins.regs_access(); ops=[]
  for op in ins.operands:
   d={'type':op.type,'size_bytes':op.size,'access':op.access}
   if op.type==X86_OP_IMM:d['immediate']=op.imm
   if op.type==X86_OP_REG:d['register']=ins.reg_name(op.reg)
   if op.type==X86_OP_MEM:d['memory']={'segment':ins.reg_name(op.mem.segment),'base':ins.reg_name(op.mem.base),'index':ins.reg_name(op.mem.index),'scale':op.mem.scale,'displacement':op.mem.disp}
   ops.append(d)
  cap.append({'offset':ins.address-pc,'pc':ins.address,'length':ins.size,'raw_hex':ins.bytes.hex(),'mnemonic':ins.mnemonic,'op_str':ins.op_str,'groups':list(ins.groups),'register_reads':[ins.reg_name(r) for r in reads],'register_writes':[ins.reg_name(r) for r in writes],'eflags':ins.eflags,'operands':ops,'edge':{'kind':'call' if CS_GRP_CALL in ins.groups else 'jump','target_va':ins.operands[0].imm if ins.operands and ins.operands[0].type==X86_OP_IMM else None,'indirect':not(ins.operands and ins.operands[0].type==X86_OP_IMM)} if CS_GRP_CALL in ins.groups or CS_GRP_JUMP in ins.groups else None})
 boundaries=[(i['offset'],i['length']) for i in result['instructions']];cap_boundaries=[(i['offset'],i['length']) for i in cap]
 cap_end=sum(i.size for i in decoded)
 result.update(capstone=cap,capstone_complete=cap_end==len(data),capstone_decoded_bytes=cap_end,decoder_boundaries_agree=boundaries==cap_boundaries)
 # Upstream has no lock/atomic IL node; retain and conservatively mark context.
 context=[]
 for i in result['instructions']:
  prefix=i['decoded']['P']
  if prefix['Lock']:context.append({'offset':i['offset'],'reason':'lock_atomicity_not_explicit_in_lift_il'})
  if (prefix['Rep'] or prefix['RepNz']) and not i['opaque_markers']:context.append({'offset':i['offset'],'reason':'repeat_prefix_without_explicit_intrinsic_model'})
 result['architectural_context_markers']=context
 starts={i['pc'] for i in cap};bad=[]
 for i in cap:
  e=i['edge']
  if e and e['target_va'] is not None and pc<=e['target_va']<pc+len(data) and e['target_va'] not in starts:bad.append({'instruction_pc':i['pc'],'target_va':e['target_va']})
 result['nonboundary_internal_edges']=bad
 result['complete_supported']=bool(result['decode_complete'] and result['capstone_complete'] and result['decoder_boundaries_agree'] and not bad and result['lift_errors']==0 and result['opaque_instructions']==0 and not context)
 return result

def diff_paths(a,b,path='$'):
 if type(a)!=type(b): yield {'path':path,'original':a,'candidate':b};return
 if isinstance(a,dict):
  for key in sorted(a.keys()|b.keys()):
   if key not in a or key not in b:yield {'path':path+'.'+key,'original':a.get(key),'candidate':b.get(key)}
   else:yield from diff_paths(a[key],b[key],path+'.'+key)
 elif isinstance(a,list):
  if len(a)!=len(b):yield {'path':path+'.length','original':len(a),'candidate':len(b)}
  for n,(x,y) in enumerate(zip(a,b)):yield from diff_paths(x,y,f'{path}[{n}]')
 elif a!=b:yield {'path':path,'original':a,'candidate':b}

def diagnose(a,b):
 trees_a=[i['tree'] for i in a['instructions']];trees_b=[i['tree'] for i in b['instructions']]
 diffs=list(diff_paths(trees_a,trees_b));agree=trees_a==trees_b
 incomplete=any(not s['decode_complete'] or not s['capstone_complete'] or not s['decoder_boundaries_agree'] or s['nonboundary_internal_edges'] or s['lift_errors'] for s in (a,b))
 opaque=any(s['opaque_instructions'] or s['architectural_context_markers'] for s in (a,b))
 state='incomplete_lift' if incomplete else 'opaque_or_unsupported' if opaque else 'exact_lift_tree_agreement' if agree else 'differing_supported_il'
 return {'state':state,'raw_lift_trees_agree':agree,'tree_difference_count':len(diffs),'first_tree_differences':diffs[:24],'instruction_counts':[len(a['instructions']),len(b['instructions'])],'comparison':'ordered per-instruction typed trees, all fields; no address/temp normalization, no instruction dropping or semantic equivalence claim','acceptance':False,'proof':False}

def capstone_binding():
 import capstone
 package=Path(capstone.__file__).resolve().parent
 native=Path(capstone._cs._name).resolve()
 require(native.is_file(),'capstone_native_library_unresolved')
 return {'version':capstone.__version__,'wrapper_sha256':{p.name:digest(p) for p in sorted(package.glob('*.py'))},'native_library':str(native),'native_library_sha256':digest(native)}

def upstream_binding():
 checkout=config()['sharp_retro_checkout']
 dll=config()['adapter_dll']
 rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip();require(rev==REVISION,'upstream_revision')
 require(not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=checkout,text=True).strip(),'upstream_tracked_modifications')
 assemblies={p.name:digest(p) for p in sorted(dll.parent.glob('*.dll'))}
 manifest=json.loads(config()['build_manifest'].read_text())
 require(manifest['revision']==rev and manifest['assemblies_sha256']==assemblies,'lifter_build_assemblies')
 require(manifest['runtime_files_sha256']=={p.name:digest(p) for p in sorted(dll.parent.glob('*.json'))},'lifter_runtime_files')
 require(manifest['adapter_source_sha256']==digest(ROOT/'adapter/Program.cs') and manifest['adapter_project_sha256']==digest(ROOT/'adapter/PairedLift.csproj'),'lifter_build_source')
 for name,expected in manifest['upstream_tracked_source_sha256'].items():require(digest(checkout/name)==expected,'upstream_source_hash:'+name)
 return {'revision':rev,'build_manifest_sha256':digest(config()['build_manifest']),'mode':'Bits32','dotnet_version':subprocess.check_output(['dotnet','--version'],text=True).strip(),'assemblies_sha256':assemblies,'adapter_source_sha256':digest(ROOT/'adapter/Program.cs'),'adapter_project_sha256':digest(ROOT/'adapter/PairedLift.csproj'),'python_adapter_sha256':digest(__file__),'capstone':capstone_binding()}

def paired(summary,rva):
 start=time.perf_counter();f,binding=bound_function(summary,rva)
 a=lift_raw(bytes.fromhex(f['original_bytes_hex']),f['original_va'],f'{rva:08x}:original')
 b=lift_raw(bytes.fromhex(f['relocated_bytes_hex']),f['original_va'],f'{rva:08x}:candidate')
 return {'schema':'sharpretro_paired_diagnostic_v1','identity':{'module_sha256':exporter.MODULE_SHA256,'module':'DAOrigins.exe','rva':rva},'binding':binding,'lifter':upstream_binding(),'original':a,'candidate':b,'diagnostic':diagnose(a,b),'elapsed_seconds':time.perf_counter()-start,'scope':'linear lift of complete attested ranges, including bytes beyond returns; not reachability, dependency semantics, whole-game proof or an acceptance path','vm_builds':0,'provider_calls':0}

def record_build_manifest(output):
 cfg=config(); checkout=cfg['sharp_retro_checkout']; dll=cfg['adapter_dll']
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
 require(revision==REVISION,'upstream_revision')
 require(not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=checkout,text=True).strip(),'upstream_tracked_modifications')
 tracked=subprocess.check_output(['git','ls-files'],cwd=checkout,text=True).splitlines()
 value={'revision':revision,'configuration':'Release','target':'net10.0','adapter_source_sha256':digest(ROOT/'adapter/Program.cs'),'adapter_project_sha256':digest(ROOT/'adapter/PairedLift.csproj'),'upstream_tracked_source_sha256':{p:digest(checkout/p) for p in tracked if p.endswith(('.cs','.csproj','.props','.targets'))},'assemblies_sha256':{p.name:digest(p) for p in sorted(dll.parent.glob('*.dll'))},'runtime_files_sha256':{p.name:digest(p) for p in sorted(dll.parent.glob('*.json'))},'build_command':['dotnet','build',str(ROOT/'adapter/PairedLift.csproj'),'-c','Release','-p:SharpRetroRoot='+str(checkout)],'dotnet_info':subprocess.check_output(['dotnet','--info'],text=True),'nuget_assets_sha256':{p:digest(checkout/p) for p in ('XFusionCpu/obj/project.assets.json','CoreArchCompiler/obj/project.assets.json','LibSharpRetro/obj/project.assets.json','LiftIl/obj/project.assets.json')}}
 require(dll.is_file() and value['assemblies_sha256'],'missing_adapter_build')
 atomic(Path(output),value)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--config',type=Path,required=True,help='JSON: sharp_retro_checkout, adapter_dll, build_manifest, original_binary (relative to config file or absolute)')
 p.add_argument('--record-build-manifest',type=Path,help='Explicitly capture a freshly built pinned dependency snapshot; review before use')
 p.add_argument('--summary',type=Path);p.add_argument('--rva',type=lambda s:int(s,0));p.add_argument('--output',type=Path);args=p.parse_args()
 configure(args.config)
 if args.record_build_manifest:
  record_build_manifest(args.record_build_manifest);return
 if args.summary is None or args.rva is None or args.output is None:p.error('--summary, --rva and --output required for paired lift')
 result=paired(args.summary,args.rva);atomic(args.output,result);print(json.dumps({'output':str(args.output),'diagnostic':result['diagnostic']['state'],'elapsed_seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
