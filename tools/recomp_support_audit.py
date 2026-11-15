"""Audit independently decoded instructions in incomplete or all catalog selections.

Diagnostics bypass whole-function boundary requirements, never the production
generator. A successful instruction emission is not a compiled/accepted function.
Linear decode tails and invalid selections remain explicit unknowns.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import subprocess
import time
import capstone
from tools import recomp
from tools.recomp_bulk_build import require_whole_inventory
from tools.recomp_native import PE32

PROJECT=recomp.ROOT/'recompiler/SupportAudit/Support.Audit.csproj'


def collect_candidates(pe, catalog, results, instruction_limit=500_000, diagnostic_ranges=None, scope='incomplete'):
    if scope not in ('incomplete','catalog'):
        raise ValueError('invalid instruction audit scope')
    if type(instruction_limit) is not int or not 1<=instruction_limit<=10_000_000:
        raise ValueError('invalid instruction audit budget')
    if (len({r['rva'] for r in catalog})!=len(catalog) or
            len({r['rva'] for r in results})!=len(results) or
            {r['rva'] for r in catalog}!={r['rva'] for r in results}):
        raise ValueError('instruction audit requires a complete unique catalog/result roster')
    owners={row['rva']:row for row in catalog};candidates={};unknown=[];count=0;inspected=0;diagnostic_count=0;diagnostic_selections=0
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    for result in results:
        if scope=='incomplete' and result['status']=='generated_only' and not result.get('coverage',{}).get('uncovered_inventory_bytes',0):continue
        owner=owners[result['rva']];selection=owner.get('selection');inspected+=1
        diagnostic=not selection
        if diagnostic:
            unknown.append(dict(rva=owner['rva'],reason='no valid selection; original preparation failure retained'))
            spans=(diagnostic_ranges or {}).get(owner['rva'],[])
            if not spans:continue
            diagnostic_selections+=1
        else:spans=selection['ranges']
        previous=0 if diagnostic else owner['rva']
        for span in spans:
            start,size=span['rva'],span['size']
            if type(start) is not int or type(size) is not int or size<=0 or start<previous:
                raise ValueError('invalid/overlapping original audit selection')
            previous=start+size;raw=pe.read(start,size);end=start
            for instruction in decoder.disasm(raw,pe.info['image_base']+start):
                rva=instruction.address-pe.info['image_base'];code=instruction.bytes.hex();count+=1
                if diagnostic:diagnostic_count+=1
                if count>instruction_limit:raise ValueError('instruction audit budget exhausted; no completed report')
                candidate=candidates.setdefault(code,dict(rva=rva,bytes=code,mnemonic=instruction.mnemonic,
                    operands=instruction.op_str,origins=[]))
                candidate['origins'].append(dict(rva=rva,owner_rva=owner['rva'],**({'source_kind':'invalid_selection_inventory_range_diagnostic'} if diagnostic else {})))
                end=rva+instruction.size
            if end<start+size:
                unknown.append(dict(rva=end,size=start+size-end,owner_rva=owner['rva'],
                    reason='linear decode stopped; remaining boundary/tail unknown'))
    return list(candidates.values()),unknown,dict(inspected_selections=inspected,instruction_occurrences=count,
        unique_encodings=len(candidates),diagnostic_invalid_selections=diagnostic_selections,invalid_selection_instruction_occurrences=diagnostic_count,audit_scope=scope,scope='deduplicated exact bytes inside existing selections or authenticated invalid-selection inventory ranges; linear candidates, never complete CFG or valid-ownership evidence')


def freeze_backend(out):
    with recomp.locked(recomp.ROOT/'local/recomp/bridge-build'):
        command=['dotnet','build',str(PROJECT),'-c','Release','--nologo',
                 '-p:SharpRetroRoot='+str(recomp.ROOT.parent/'SharpRetro')]
        built=subprocess.run(command,capture_output=True,text=True,timeout=180)
        (out/'build.log').write_text(built.stdout+built.stderr)
        if built.returncode:raise RuntimeError('support audit build failed; see build.log')
        target=out/'backend';target.mkdir()
        for path in (PROJECT.parent/'bin/Release/net10.0').iterdir():
            if path.is_file() and path.suffix in ('.dll','.json','.hpp'):(target/path.name).write_bytes(path.read_bytes())
        producers=out/'producers';producers.mkdir()
        sources=[(Path(__file__),'controller.py'),(PROJECT,'support-audit.csproj'),
            (PROJECT.parent/'Program.cs','support-audit-program.cs')]
        sources.extend((p,'sharp-retro-'+p.name) for pattern in ('*.cs','*.hpp')
            for p in (recomp.ROOT.parent/'SharpRetro/Decompiler').glob(pattern))
        if len({name for path,name in sources})!=len(sources):raise ValueError('colliding producer snapshot names')
        for path,name in sources:(producers/name).write_bytes(path.read_bytes())
        bindings={str(p.relative_to(out)):recomp.digest(p.read_bytes()) for folder in (target,producers) for p in folder.iterdir()}
        recomp.atomic_json(out/'producer-bindings.json',bindings)
        return target


def audit_instructions(binary, binary_sha256, candidates, backend, directory):
    request=dict(schema_version=1,binary=str(binary),binary_sha256=binary_sha256,
        instructions=[dict(rva=r['rva'],bytes=r['bytes']) for r in candidates])
    recomp.atomic_json(directory/'request.json',request)
    if not candidates:
        return []
    command=['dotnet',str(backend/'Support.Audit.dll')]
    with (directory/'stdout.json').open('wb') as stdout,(directory/'stderr').open('wb') as stderr:
        run=subprocess.run(command,input=json.dumps(request).encode(),stdout=stdout,stderr=stderr,timeout=300)
    if run.returncode:
        raise RuntimeError('instruction audit process failed; no completed publication: '+(directory/'stderr').read_text(errors='replace')[-2000:])
    response=recomp.load(directory/'stdout.json')
    if response['schema_version']!=1 or response['binary_sha256']!=binary_sha256 or response['game_acceptance'] is not False:
        raise ValueError('wrong instruction audit identity')
    expected={(r['rva'],r['bytes']) for r in candidates};observed=[(r['rva'],r['bytes']) for r in response['results']]
    if len(observed)!=len(expected) or set(observed)!=expected:raise ValueError('incomplete/duplicate instruction audit results')
    known={r['bytes']:r for r in candidates}
    return [dict(known[row['bytes']],**{k:v for k,v in row.items() if k not in ('rva','bytes')}) for row in response['results']]


def audit_in_batches(binary, binary_sha256, candidates, backend, directory, batch_size=5000):
    if type(batch_size) is not int or not 1<=batch_size<=500_000:
        raise ValueError('invalid instruction audit batch size')
    results=[]
    for offset in range(0,len(candidates),batch_size):
        batch=directory/f'batch-{offset//batch_size:06d}';batch.mkdir()
        results.extend(audit_instructions(binary,binary_sha256,candidates[offset:offset+batch_size],backend,batch))
        print(dict(module=directory.name,audited_encodings=len(results),total_encodings=len(candidates)),flush=True)
    return results


def prepare(generation, output, scope='incomplete', instruction_limit=500_000, batch_size=5000):
    generation=generation.absolute();report=recomp.load(generation/'report.json');require_whole_inventory(report)
    out=output.absolute()/str(time.time_ns());out.mkdir(parents=True);backend=freeze_backend(out);modules={}
    for role in ('main','umbra'):
        directory=out/role;directory.mkdir();context=recomp.load(generation/role/'context.json');state=recomp.state(Path(context['project']))
        if recomp.digest(recomp.encoded(state))!=context['project_sha256']:raise ValueError('project changed since generation')
        binary=recomp.checked_binary(state);pe=PE32(binary)
        catalog=list(map(json.loads,(generation/role/'catalog.jsonl').open()));previous=list(map(json.loads,(generation/role/'results.jsonl').open()))
        inventory_path=Path(context['inventory'])
        if recomp.digest(inventory_path.read_bytes())!=context['inventory_sha256']:raise ValueError('inventory changed since generation')
        inventory=recomp.load(inventory_path)
        if inventory['module_sha256'].lower()!=state['binary_sha256']:raise ValueError('inventory binary identity changed')
        invalid={r['rva'] for r in catalog if not r.get('selection')}
        diagnostic_ranges={r['rva']:[dict(rva=b['start_rva'],size=b['end_rva_inclusive']-b['start_rva']+1) for b in r['body_ranges']]
            for r in inventory['functions'] if r['rva'] in invalid}
        recomp.atomic_json(directory/'invalid-selection-inventory-ranges.json',dict(inventory=str(inventory_path),inventory_sha256=context['inventory_sha256'],binary_sha256=state['binary_sha256'],ranges=diagnostic_ranges,scope='diagnostic raw ranges only; original invalid selections remain unknown'))
        candidates,unknown,summary=collect_candidates(pe,catalog,previous,instruction_limit=instruction_limit,diagnostic_ranges=diagnostic_ranges,scope=scope)
        print(dict(role=role,phase='collected',**summary),flush=True)
        results=audit_in_batches(binary,state['binary_sha256'],candidates,backend,directory,batch_size)
        recomp.checked_binary(state);groups=defaultdict(list)
        for row in results:
            if row['status']=='instruction_support_unresolved':groups[(row['mnemonic'],row['stage'])].append(row)
            elif row['status']!='instruction_emission_available':raise ValueError('unknown instruction audit outcome')
        payload=dict(binary_sha256=state['binary_sha256'],module=state['module'],
            summary=summary,unknown_selections_or_tails=unknown,results=results,game_acceptance=False)
        if scope=='catalog':
            # Whole-catalog origin lists are large; retain every origin losslessly.
            temporary=directory/'results.json.gz.tmp'
            with gzip.open(temporary,'wt') as stream:json.dump(payload,stream,separators=(',',':'))
            temporary.rename(directory/'results.json.gz')
        else:recomp.atomic_json(directory/'results.json',payload)
        modules[role]=dict(**summary,status_counts=dict(Counter(r['status'] for r in results)),unknown_ranges=len(unknown),
            unresolved_groups=[dict(mnemonic=key[0],stage=key[1],unique_encodings=len(rows),
                occurrences=sum(len(r['origins']) for r in rows)) for key,rows in sorted(groups.items())])
        print(dict(role=role,**modules[role]),flush=True)
    final=dict(status='completed scoped instruction diagnostics; full-function compilation and runtime remain separate',
        generation_run=str(generation),generation_report_sha256=recomp.digest((generation/'report.json').read_bytes()),
        decoder_version=capstone.__version__,modules=modules,game_acceptance=False,audit_scope=scope,
        scope=('every catalog selection' if scope=='catalog' else 'previously failed/partial selections')+'; linear instruction candidates only; repeated byte encodings share a representative; undecodable tails stay unknown')
    recomp.atomic_json(out/'report.json',final)
    recomp.atomic_json(recomp.ROOT/'local/recomp/startup/support-instruction-audit-latest.json',dict(directory=str(out),**final))
    return out,final


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--generation',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/support-instruction-audits')
    parser.add_argument('--scope',choices=('incomplete','catalog'),default='incomplete')
    parser.add_argument('--instruction-limit',type=int,default=None)
    parser.add_argument('--batch-size',type=int,default=5000)
    args=parser.parse_args();limit=args.instruction_limit if args.instruction_limit is not None else (10_000_000 if args.scope=='catalog' else 500_000)
    out,report=prepare(args.generation,args.output,args.scope,limit,args.batch_size);print(json.dumps(dict(directory=str(out),modules=report['modules'])))

if __name__=='__main__':main()
