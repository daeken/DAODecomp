"""Fresh attested SharpRetro crosscheck for the bounded encoding relation.

No compiler dispatch, queue mutation, cached proof loading, or broad IL matcher.
Callers retain the strict comparator report and full native/EH binding gates.
"""
import hashlib
import json
from pathlib import Path
import subprocess
from rapid_object.encoding_equivalence import certify_range, Relocation, Refusal, need
from rapid_object import encoding_equivalence
from tools.replayable.guest_batch import unique_object


def digest(data): return hashlib.sha256(data).hexdigest()
def parse(data): return json.loads(data, object_pairs_hook=unique_object)


def attested_lifter(project, inputs):
    def read(path):
        p=Path(path)
        need(p.is_absolute() and not any(x.is_symlink() for x in (p,*p.parents)),'encoding_lifter_path')
        need(any(p.is_relative_to(Path(root)) and p!=Path(root) for root in project['allowed_roots']),'encoding_lifter_path_outside_roots')
        raw=p.read_bytes();need(inputs.get(str(p))==digest(raw),'encoding_lifter_unbound_or_changed_input');return raw
    config_path=Path(project['replayable']['lifter_config']);config=parse(read(config_path))
    def resolve(value):
        p=Path(value);return p if p.is_absolute() else config_path.parent/p
    manifest_path=resolve(config['build_manifest']);manifest=parse(read(manifest_path));dll=resolve(config['adapter_dll']);checkout=resolve(config['sharp_retro_checkout'])
    need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True,timeout=10).strip()==manifest['revision'],'encoding_lifter_revision_changed')
    for name,expected in manifest['upstream_tracked_source_sha256'].items():need(digest(read(checkout/name))==expected,'encoding_lifter_source_changed')
    for extension,key in (('*.dll','assemblies_sha256'),('*.json','runtime_files_sha256')):
        actual={p.name:digest(read(p)) for p in dll.parent.glob(extension)};need(actual==manifest[key],'encoding_lifter_runtime_changed')
    bindings=dict(config_sha256=digest(read(config_path)),manifest_sha256=digest(read(manifest_path)),adapter_sha256=digest(read(dll)),revision=manifest['revision'])
    def lift_pair(left,right,pc):
        requests=[dict(id=name,pc=pc,hex=raw.hex()) for name,raw in (('original',left),('candidate',right))]
        result=subprocess.run([config.get('dotnet','dotnet'),str(dll)],input=''.join(json.dumps(x)+'\n' for x in requests),text=True,capture_output=True,timeout=30)
        need(result.returncode==0 and len(result.stdout)<=262144,'encoding_lifter_process_failure')
        rows=[parse(line) for line in result.stdout.splitlines()]
        need(len(rows)==2 and [r.get('id') for r in rows]==['original','candidate'],'encoding_lifter_response_identity')
        return rows
    return lift_pair,bindings


def certify_report(report,project,inputs):
    """Only a fresh exact-comparator report may be supplied by the bound caller.

    Never accept caller-authored certificate JSON. The returned deterministic
    certificate is recomputed from full range bytes and fresh actual typed IL.
    """
    implementation={}
    for path in (Path(__file__),Path(encoding_equivalence.__file__)):
        raw=path.read_bytes();need(inputs.get(str(path))==digest(raw),'encoding_checker_unbound_or_changed');implementation[path.name]=digest(raw)
    need(report.get('backend')=='i386_coff_exact_v1' and not report.get('error'),'encoding_requires_ordinary_complete_comparison')
    need(report.get('module_sha256')==project['module_sha256'],'encoding_module_binding')
    rows=report.get('functions');requested=report.get('requested')
    need(isinstance(rows,list) and len(rows)==1 and isinstance(requested,dict) and len(requested)==1,'encoding_single_complete_function')
    row=rows[0];spec=requested.get(str(row['rva']),requested.get(row['rva']));need(isinstance(spec,dict),'encoding_requested_identity')
    ranges=spec['ranges'];need(len(ranges)==1 and ranges[0]['start_rva']==row['rva'],'encoding_contiguous_entry_range')
    size=ranges[0]['end_rva_inclusive']-ranges[0]['start_rva']+1
    need(row.get('status')=='nonmatch' and row.get('diagnostics')==['full_function_bytes_differ'] and row.get('original_size')==row.get('object_size')==size and spec['original_va']==row['original_va'],'encoding_strict_comparison_domain')
    original=bytes.fromhex(row['original_bytes_hex']);candidate=bytes.fromhex(row['object_bytes_hex'])
    need(digest(original)==row['original_bytes_sha256'],'encoding_original_range_hash')
    relocs=[Relocation(r['offset'],r['kind'],r['target_va'],r['addend_u32']) for r in row['relocations']]
    lift,bindings=attested_lifter(project,inputs)
    certificate=certify_range(original,candidate,pc=row['original_va'],complete_length=size,relocations=relocs,lift_pair=lift)
    certificate.update(implementation_sha256=implementation,rva=row['rva'],module_sha256=report['module_sha256'],source_sha256=report['source_sha256'],object_sha256=report['object_sha256'],compiler_sha256=project['compiler_sha256'],strict_status='nonmatch',lifter=bindings,original_range_sha256=digest(original),candidate_raw_range_sha256=digest(candidate),candidate_relocated_range_sha256=row['relocated_bytes_sha256'],proof=False)
    return certificate
