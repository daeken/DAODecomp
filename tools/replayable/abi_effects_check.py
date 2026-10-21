"""Fresh typed ABI-event diagnostics and explicit bounded behavioral relation.

The legacy profile remains nonaccepting. The new opt-in policy additionally
checks inherited ordinary x86 unwind structure, ESP/nonvolatile state at all
accesses/boundaries, and independently varying ordered memory observations.
Neither profile claims full temporary fault CONTEXT or game equivalence.
"""
from pathlib import Path
import json,struct,subprocess
from tools.replayable.encoding_check import digest,parse,attested_lifter
from tools.replayable import effect_relation,encoding_check
from rapid_object.encoding_equivalence import need,decode

PROFILE='abi-ordered-fault-events-v1'
ARCHITECTURE='x86-bits32-terminal-aware-abi-effects-v1'
BEHAVIORAL_PROFILE='windows-x86-inherited-unwind-ordered-events-v1'
BEHAVIORAL_ARCHITECTURE='x86-bits32-scalar-behavioral-events-v1'

def bound_read(project,inputs,path):
 p=Path(path);need(p.is_absolute() and not any(x.is_symlink() for x in (p,*p.parents)),'abi_effects_input_path');need(any(p.is_relative_to(Path(root)) and p!=Path(root) for root in project['allowed_roots']),'abi_effects_input_outside_roots');raw=p.read_bytes();need(inputs.get(str(p))==digest(raw),'abi_effects_unbound_or_changed_input');return raw

def certify_report(report,project,inputs,*,behavioral=False):
 implementation={}
 if behavioral:
  from tools.replayable import unregistered_unwind
  implementation['unregistered_unwind.py']=digest(bound_read(project,inputs,str(Path(unregistered_unwind.__file__))))
 for path in (Path(__file__),Path(effect_relation.__file__),Path(encoding_check.__file__)):
  implementation[path.name]=digest(bound_read(project,inputs,str(path)))
 need(report.get('backend')=='i386_coff_exact_v1' and not report.get('error') and report.get('module_sha256')==project['module_sha256'],'abi_effects_complete_ordinary_comparison')
 rows=report.get('functions');requested=report.get('requested');need(isinstance(rows,list) and len(rows)==1 and isinstance(requested,dict) and len(requested)==1,'abi_effects_single_function')
 row=rows[0];spec=requested.get(str(row['rva']),requested.get(row['rva']));need(isinstance(spec,dict),'abi_effects_requested_identity');ranges=spec['ranges'];need(len(ranges)==1 and ranges[0]['start_rva']==row['rva'] and spec['original_va']==row['original_va'],'abi_effects_entry_range');size=ranges[0]['end_rva_inclusive']-ranges[0]['start_rva']+1
 original=bytes.fromhex(row['original_bytes_hex']);raw=bytes.fromhex(row['object_bytes_hex']);candidate=bytes.fromhex(row['relocated_bytes_hex']);diagnostics=['full_function_bytes_differ']+(['full_function_length_differs_no_prefix_acceptance'] if len(original)!=len(candidate) else [])
 need(row.get('status')=='nonmatch' and row.get('diagnostics')==diagnostics and row.get('boundary_evidence')=='entire_single_function_comdat' and row.get('original_size')==size==len(original) and row.get('object_size')==len(raw)==len(candidate) and 0<size<=512 and len(candidate)<=512,'abi_effects_full_native_ranges')
 need(digest(original)==row['original_bytes_sha256'] and digest(candidate)==row['relocated_bytes_sha256'],'abi_effects_range_hashes');insns=decode(candidate,row['original_va']);call_fields={i.address-row['original_va']+1:i for i in insns if i.mnemonic=='call' and i.bytes[0]==0xe8 and i.size==5};patched=bytearray(raw);used=set()
 for rel in row['relocations']:
  at=rel['offset'];need(type(at)is int and at in call_fields and at not in used and rel['kind']==0x14 and rel['addend_u32']==0 and type(rel['target_va'])is int and 0<=rel['target_va']<=0xffffffff,'abi_effects_direct_call_relocation_domain');used.add(at);need(raw[at:at+4]==b'\0'*4,'abi_effects_call_addend');value=(rel['target_va']-(row['original_va']+at+4))&0xffffffff;struct.pack_into('<I',patched,at,value);need(call_fields[at].operands[0].imm==rel['target_va'],'abi_effects_call_relocation_target')
 need(bytes(patched)==candidate,'abi_effects_relocation_coverage')
 config_path=project['replayable'].get('equivalence_solver_config');need(isinstance(config_path,str),'abi_effects_solver_not_registered');config=parse(bound_read(project,inputs,config_path));need(set(config)=={'schema_version','executable','sha256','observation_profile'} and config['schema_version']==1 and config['observation_profile']==(BEHAVIORAL_PROFILE if behavioral else PROFILE),'abi_effects_observation_profile');solver=config['executable'];need(digest(bound_read(project,inputs,solver))==config['sha256'],'abi_effects_solver_binding')
 # Verify the exact lifter closure with the existing attestation. Its old SIB
 # response budget stays unchanged; this additional whole-range request has a
 # separate bounded2MiB response for the explicit new profile only.
 _,lifter_binding=attested_lifter(project,inputs);lc=parse(bound_read(project,inputs,project['replayable']['lifter_config']));dll=Path(lc['adapter_dll']);dll=dll if dll.is_absolute() else Path(project['replayable']['lifter_config']).parent/dll
 requests=[dict(id=name,pc=row['original_va'],hex=data.hex()) for name,data in (('original',original),('candidate',candidate))];run=subprocess.run([lc.get('dotnet','dotnet'),str(dll)],input=''.join(json.dumps(x)+'\n' for x in requests),text=True,capture_output=True,timeout=30);need(run.returncode==0 and len(run.stdout)<=2*1024*1024,'abi_effects_lifter_failure_or_budget');lifts=[parse(line) for line in run.stdout.splitlines()];need(len(lifts)==2 and [x.get('id') for x in lifts]==['original','candidate'],'abi_effects_lifter_identity')
 # VC8 x86 profile: EAX result, ESP and nonvolatile EBX/EBP/ESI/EDI. All
 # registers are checked at every external call; live CFG uses are added.
 certificate=effect_relation.certify_typed_effects(original,candidate,pc=row['original_va'],lifts=lifts,solver=solver,exit_live_registers=[0,3,4,5,6,7],fault_context='abi-event-only',fault_live_registers=[3,4,5,6,7] if behavioral else [3,5,6,7],boundary_live_registers=[3,4,5,6,7] if behavioral else [],arbitrary_event_memory=behavioral)
 if behavioral:
  # Bind complete original/object bytes independently of the relocated report.
  pe=bound_read(project,inputs,project['original']);need(digest(pe)==project['module_sha256'],'behavioral_original_binding')
  candidates=[path for path,h in inputs.items() if Path(path).name=='candidate.obj' and h==report['object_sha256']]
  need(len(candidates)>=1,'behavioral_object_binding_missing');objects=[bound_read(project,inputs,path) for path in candidates];need(all(raw==objects[0] and digest(raw)==report['object_sha256'] for raw in objects),'behavioral_object_binding');obj=objects[0]
  mapping={int(a):b for a,b in certificate['control_bijection'].items()}
  unwind=unregistered_unwind.certify_structure(original,candidate,row['original_va'],mapping,pe,obj)
 for window in certificate['effect_windows']:window.pop('query')
 certificate.update(status='conditional_abi_trace_equivalence',acceptance_authorized=False,accepted=False,observation_profile=PROFILE,implementation_sha256=implementation,lifter=lifter_binding,solver_config_sha256=digest(bound_read(project,inputs,config_path)),module_sha256=report['module_sha256'],rva=row['rva'],source_sha256=report['source_sha256'],object_sha256=report['object_sha256'],compiler_sha256=project['compiler_sha256'],original_range_sha256=digest(original),candidate_raw_range_sha256=digest(raw),candidate_relocated_range_sha256=digest(candidate),strict_status='nonmatch',full_fault_register_context_equivalence_proven=False,ordinary_exception_propagation_equivalence_proven=False,ordinary_unwind_equivalence_proven=False,assumptions=['flat32 DS/SS with common segment context; synchronous instruction semantics','function ABI result/nonvolatile/stack obligations, all arithmetic flags at changed-block boundaries and all GPRs at calls are observed','same ordered memory accesses including faulting address/width and preceding memory/effect prefix; nonvolatile EBX/EBP/ESI/EDI equal at each access; accepting behavioral profile additionally checks ESP and retains ESP/nonvolatile at every changed boundary; no assumed valid memory, nonaliasing or object bounds','arbitrary fault-handler CONTEXT inspection/modification, debugger/tracing/concurrent observation and code/return-address identity observations excluded','direct external calls keep original targets and paired state under control-continuation mapping; unknown effects/results/termination are not implemented or proved'],proof=False)
 if behavioral:
  certificate.update(status='bounded_behavioral_equivalence',accepted=True,acceptance_authorized=True,observation_profile=BEHAVIORAL_PROFILE,ordinary_exception_propagation_equivalence_proven=True,ordinary_unwind_equivalence_proven=True,unwind_relation=unwind,validation_scope='Bounded compiled-artifact synchronous Windows IA-32 inherited-registration simulation; same actual callees, unknown outcomes paired, no local EH; excludes fault temporary CONTEXT/code-address introspection. Not universal C++/callee/game proof.')
 return certificate
