"""Trusted intake and export bridge for the separate complete main/EH backend.

No stored verdict is authoritative. Every export reopens all inputs and recomputes
runtime recognition, graph derivation and every byte/relocation comparison.
Private paths are configuration; public policy contains hashes, never addresses.
"""
import json,re
from pathlib import Path
from rapid_object import eh_native
from rapid_object.static_crt_identity import canonical,require
from rapid_object.eh_graph import sha

BACKEND='i386_coff_eh_graph_v1'
STATUS='exact_eh_graph_match'
DAO_POLICY={
 'module_sha256':'2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3',
 'inventory_sha256':'3eec75966d23372e90dab28c07800cb8420057e7b226cd00477f472ce78feb99',
 'compiler_sha256':'5f6489b0d211b14ae09d93d3fb58a7bce84d070287f008e06416c9baa5564219',
 'libraries_sha256':{'libcmt.lib':'3bc6c5b90f8507964839fd0264d8565c3b766d01f9efcad336532a11e8f06ac3'},
 'toolchain_archive_sha256':'f544c8ec782921a64ffed4b41206aa3d6e16d0cf47c78a5bc26308ae0c2251ea',
 'compiler_flags':['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc']}

def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def recompute(folder,original,inputs):
 folder=Path(folder)
 require(set(inputs)=={'inventory','compiler','libraries'},'unsupported_EH_intake_fields')
 require(set(inputs['libraries'])==set(DAO_POLICY['libraries_sha256']),'EH_library_set')
 source=(folder/'candidate.cpp').read_bytes();obj=(folder/'candidate.obj').read_bytes();build=read_json(folder/'run.json');compiler_receipt=read_json(folder/'compiler.json')
 require(canonical(compiler_receipt)==canonical(build['compiler']),'EH_compiler_receipt_binding')
 return json.loads(canonical(eh_native.check(original,Path(inputs['inventory']).read_bytes(),Path(inputs['compiler']).read_bytes(),{n:Path(p).read_bytes() for n,p in inputs['libraries'].items()},source,obj,build,DAO_POLICY)))

def make_rows(folder,original,inputs,output):
 """Derive report/rows from a compiler artifact; no candidate-supplied placements."""
 folder=Path(folder).resolve();output=Path(output);require(not output.exists(),'EH_output_exists')
 report=recompute(folder,original,inputs);output.mkdir(parents=True)
 summary=output/'comparison.json';summary.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 rows=[]
 if report['status']==STATUS:
  for f in report['functions']:
   rows.append(dict(rva=f['rva'],source=str(folder/'candidate.cpp'),artifact_dir=str(folder),measurement=dict(status=STATUS,backend=BACKEND,summary=str(summary.resolve()),summary_sha256=sha(summary.read_bytes()))))
 result=dict(records=rows,computed_status=report['status']);(output/'report.json').write_text(json.dumps(result,indent=2)+'\n');return result

def retained_match(row,original,inputs):
 """Refuse stale/forged/partial reports; export only freshly complete exact rows."""
 require(type(row['rva']) is int and 0<=row['rva']<=0xffffffff,'EH_RVA_type');rva=row['rva'];measurement=row['measurement']
 require(measurement['status']==STATUS and measurement['backend']==BACKEND,'EH_backend_status')
 summary=Path(measurement['summary']);stored_raw=summary.read_bytes();require(sha(stored_raw)==measurement['summary_sha256'],'EH_summary_hash')
 stored=json.loads(stored_raw);folder=Path(row['artifact_dir']);source=Path(row['source']).read_bytes()
 require(Path(row['source']).resolve()==(folder/'candidate.cpp').resolve(),'EH_source_path')
 fresh=recompute(folder,original,inputs)
 require(canonical(fresh)==canonical(stored),'EH_fresh_recomparison_binding')
 require(fresh['backend']==BACKEND and fresh['status']==STATUS and not fresh['blockers'],'EH_not_complete_exact')
 require(fresh['inputs']['source_sha256']==sha(source),'EH_source_binding')
 functions=fresh['functions'];matches=[f for f in functions if type(f['rva']) is int and f['rva']==rva]
 require(len(matches)==1 and len({f['rva'] for f in functions})==len(functions),'EH_unique_function')
 evidence=matches[0];require(evidence['status']==STATUS and not evidence['blockers'] and evidence['all_bytes_accounted'] is True and set(evidence['counts'])=={'equal'} and set(evidence['nodes'])=={'main','handler','FuncInfo','unwind_map','action','delete_helper'},'EH_complete_nodes')
 text=source.decode('utf-8');require(not re.search(r'(?:/Users/|/home/|[A-Za-z]:\\)',text),'private_source_path')
 markers=[i for i,line in enumerate(text.splitlines(),1) if re.fullmatch(r'\s*//\s*FUNCTION:\s*DAO\s+0x%08x\s*'%(rva+0x400000),line,re.I)]
 require(len(markers)==1,'EH_source_annotation_identity')
 source_hash=sha(source);filename='units/%08x-%s.cpp'%(min(f['rva'] for f in functions),source_hash[:16]);unit_id=STATUS+':'+source_hash
 build=read_json(folder/'run.json');spec=fresh['requested'].get(str(rva),fresh['requested'].get(rva));require(spec is not None,'EH_requested_identity')
 unit=dict(id=unit_id,source=filename,source_sha256=source_hash,comparison_report_sha256=sha(stored_raw),compiled_artifact_sha256=fresh['inputs']['object_sha256'],matched_rvas=['0x%08x'%f['rva'] for f in functions],comparator_modules=fresh['inputs']['implementations'],compiler_version=build['compiler']['file_version'],compiler_sha256=fresh['inputs']['compiler_sha256'],compiler_flags=build['flags'],provenance='retained_compiler_artifact_full_main_EH_recompared',backend=BACKEND,input_key=fresh['input_key'],intake_hashes={k:v for k,v in fresh['inputs'].items() if k!='implementations'},trusted_policy=DAO_POLICY,graph_functions={('0x%08x'%f['rva']):{n:dict(original_size=d['original_size'],candidate_size=d['candidate_size'],original_sha256=d['original_sha256'],candidate_raw_sha256=d['candidate_raw_sha256']) for n,d in f['nodes'].items()} for f in functions},all_graph_bytes=sum(f['counts']['equal'] for f in functions),exporter_sha256=sha(Path(__file__).read_bytes()))
 function=dict(rva='0x%08x'%rva,status=STATUS,unit=unit_id,source=filename,source_sha256=source_hash,annotation_line=markers[0],original_ranges=[{k:r[k] for k in ('start_rva','end_rva_inclusive')} for r in spec['ranges']],original_bytes_sha256=spec['bytes_sha256'],backend=BACKEND)
 return function,unit,source
