"""Byte-checked internal-entry proposals from whole-module instruction maps.

Static disassembly remains a hypothesis. This never widens function ownership,
changes annotations, or grants function/game acceptance.
"""
import argparse
import copy
import gzip
import json
from pathlib import Path
import tempfile
import time
import capstone
from tools import recomp, recomp_bulk, recomp_bulk_build
from tools.daodecomp.pe import fingerprint


def instruction_map(path, binary_sha, image_base):
    functions=set();count=0;complete=False
    with gzip.open(path,'rt') as stream:
        header=json.loads(next(stream))
        if (header.get('record')!='module' or header.get('schema_version')!=1 or
                header.get('module_sha256')!=binary_sha or header.get('image_base')!=image_base):
            raise ValueError('instruction map module identity differs from pinned original')
        for line in stream:
            row=json.loads(line)
            if complete:raise ValueError('instruction map has records after completion')
            if row.get('record')=='complete':
                if (row.get('functions')!=len(functions) or row.get('instructions')!=count or
                        row.get('behavioral_acceptance') is not False):
                    raise ValueError('instruction map completion counts differ')
                complete=True
            elif row.get('record')=='function':
                if type(row.get('rva')) is not int or not 0<=row['rva']<2**32 or row['rva'] in functions:
                    raise ValueError('duplicate/invalid instruction-map function identity')
                functions.add(row['rva']);end=-1
                for instruction in row['instructions']:
                    rva=instruction['rva'];data=bytes.fromhex(instruction['bytes'])
                    if type(rva) is not int or not 0<=rva<2**32 or not 0<len(data)<=15 or rva<end:
                        raise ValueError('invalid/overlapping static instruction boundaries')
                    end=rva+len(data);count+=1
                yield row
            else:raise ValueError('unknown instruction-map record')
    if not complete:raise ValueError('incomplete instruction map; no proposals can be published')


def extra_entries(row,selection,covered,image,pe):
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    additions=[];outside=0;spans=selection['ranges']
    for instruction in row['instructions']:
        rva=instruction['rva']
        if rva in covered:continue
        data=bytes.fromhex(instruction['bytes'])
        if not any(span['rva']<=rva<span['rva']+span['size'] for span in spans):
            outside+=1;continue
        if not any(span['rva']<=rva and rva+len(data)<=span['rva']+span['size'] for span in spans):
            raise ValueError('static instruction crosses existing function ownership boundary')
        if recomp_bulk.read_rva(image,pe,rva,len(data))!=data:
            raise ValueError('static instruction bytes differ from pinned original')
        decoded=list(decoder.disasm(data,pe['image_base']+rva,count=1))
        if len(decoded)!=1 or decoded[0].size!=len(data):
            raise ValueError('independent decoder disagrees with proposed instruction boundary')
        additions.append(rva)
    current=set(selection.get('extra_entries',[]))
    return sorted(set(additions)-current),outside


def prepare(generation,maps,output):
    report=recomp.load(generation/'report.json');recomp_bulk_build.require_whole_inventory(report)
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.coverage-',dir=output) as temporary:
        staging=Path(temporary);roles={};artifacts={};summary={}
        for role in ('main','umbra'):
            context=recomp.load(generation/role/'context.json');project=Path(context['project']);state=recomp.state(project)
            if recomp.digest(recomp.encoded(state))!=context['project_sha256']:
                raise ValueError('project annotations changed since generation; regenerate before proposing entries')
            binary=recomp.checked_binary(state);image=binary.read_bytes();pe=fingerprint(binary)
            catalog={row['rva']:row for row in map(json.loads,(generation/role/'catalog.jsonl').open())}
            results={row['rva']:row for row in map(json.loads,(generation/role/'results.jsonl').open())}
            startup=json.loads(gzip.decompress((generation/role/'startup-role.json.gz').read_bytes()))
            reviewed={row['rva']:copy.deepcopy(row) for row in startup.get('functions',[])}
            for rva,entry in catalog.items():
                if 'selection' in entry:reviewed.setdefault(rva,{}).update(copy.deepcopy(entry['selection']))
            wanted={rva for rva,row in results.items() if row['status']=='generated_only' and row['coverage']['uncovered_inventory_bytes']}
            seen=set();changes=[];rejected=[];outside=0;seeds=0
            for row in instruction_map(maps[role],state['binary_sha256'],state['image_base']):
                rva=row['rva']
                if rva not in wanted:continue
                seen.add(rva);entry=catalog[rva];selection=entry['selection']
                marker=recomp_bulk.load_shard(generation.parent.parent/'cache',entry['key'],state['binary_sha256'],rva)
                shard=generation.parent.parent/'cache'/entry['key']/'function.json.gz'
                function=json.loads(gzip.decompress(shard.read_bytes()))
                covered={item['rva'] for item in function['instructions']}
                try:added,ignored=extra_entries(row,selection,covered,image,pe)
                except ValueError as error:
                    rejected.append(dict(rva=rva,error=str(error),status='seed_preparation_failed; original selection retained'))
                    continue
                outside+=ignored
                if added:
                    reviewed[rva]['extra_entries']=sorted(set(selection.get('extra_entries',[]))|set(added))
                    changes.append(dict(rva=rva,added_extra_entries=added,original_shard_key=entry['key'],
                        metadata_sha256=marker['files']['function.json.gz'],
                        provenance='Ghidra static instruction boundary; pinned bytes and independent Capstone length checked; inside existing ranges'))
                    seeds+=len(added)
            startup['functions']=[reviewed[rva] for rva in sorted(reviewed)]
            recomp.atomic_json(staging/(role+'-role.json'),startup)
            recomp.atomic_json(staging/(role+'-changes.json'),dict(changes=changes,rejected=rejected,missing_static_functions=sorted(wanted-seen)))
            roles[role]=dict(project=str(project),inventory=context['inventory'],module=context['module'],binary_sha256=state['binary_sha256'],
                             project_sha256=context['project_sha256'],map_sha256=recomp.digest(maps[role].read_bytes()))
            summary[role]=dict(partial_generated_functions=len(wanted),functions_with_proposed_entries=len(changes),
                proposed_entries=seeds,rejected_functions=len(rejected),missing_static_functions=len(wanted-seen),ignored_outside_owned_ranges=outside)
            for path in (maps[role],generation/role/'catalog.jsonl',generation/role/'results.jsonl',generation/role/'context.json'):
                artifacts[str(path)]=recomp.digest(path.read_bytes())
        (staging/'controller.py').write_bytes(Path(__file__).read_bytes())
        descriptor=dict(status='prepared internal-entry hypotheses; regeneration/compilation/execution required',roles=roles,summary=summary,
            generation_run=str(generation),generation_report_sha256=recomp.digest((generation/'report.json').read_bytes()),
            input_artifacts=artifacts,behavioral_acceptance=False,game_acceptance=False)
        descriptor['files']={p.name:recomp.digest(p.read_bytes()) for p in staging.iterdir() if p.is_file()}
        recomp.atomic_json(staging/'overlay.json',descriptor)
        final=output/str(time.time_ns());staging.rename(final)
    return final,descriptor


def generate(overlay,output,args):
    descriptor=recomp.load(overlay/'overlay.json')
    for name,identity in descriptor['files'].items():
        if recomp.digest((overlay/name).read_bytes())!=identity:raise ValueError('prepared entry overlay changed')
    with recomp.locked(output):
        pipeline,backend,policy=recomp_bulk.freeze_backend(output,args.dispatch)
        run=output/'runs'/str(time.time_ns());run.mkdir(parents=True)
        report=dict(status='running',directory=str(run),pipeline=pipeline,modules={},
                    entry_overlay=str(overlay),entry_overlay_sha256=recomp.digest((overlay/'overlay.json').read_bytes()),
                    behavioral_acceptance=False,game_acceptance=False)
        (run/'entry-overlay.json').write_bytes((overlay/'overlay.json').read_bytes())
        (run/'coverage-controller.py').write_bytes(Path(__file__).read_bytes())
        report['coverage_controller_sha256']=recomp.digest((run/'coverage-controller.py').read_bytes())
        try:
            for role,identity in descriptor['roles'].items():
                project=Path(identity['project'])
                if recomp.digest(recomp.encoded(recomp.state(project)))!=identity['project_sha256']:
                    raise ValueError('project changed after entry proposals')
                startup=recomp.load(overlay/(role+'-role.json'))
                report['modules'][role]=recomp_bulk.generate_module(role,project,Path(identity['inventory']),startup,output,
                    pipeline,backend,policy,args,run)
                # An entirely cached module makes no bridge request. Retain its
                # same-pipeline PE metadata so downstream linking stays possible.
                metadata=run/role/'module.json.gz'
                if not metadata.exists():
                    base=Path(descriptor['generation_run']);base_report=recomp.load(base/'report.json')
                    if base_report['pipeline']!=pipeline:
                        raise ValueError('cached module metadata requires the same generation pipeline')
                    payload=(base/role/'module.json.gz').read_bytes();decoded=json.loads(gzip.decompress(payload))
                    if decoded['binary_sha256']!=identity['binary_sha256']:
                        raise ValueError('cached module metadata identity changed')
                    metadata.write_bytes(payload)
                    report['modules'][role]['cached_module_metadata_source']=dict(path=str(base/role/'module.json.gz'),sha256=recomp.digest(payload))
                    recomp.atomic_json(run/role/'report.json',report['modules'][role])
                recomp.atomic_json(output/'latest.json',report)
            report['status']='completed inventory generation attempt; compilation/runtime remain separate'
        except BaseException as error:
            report.update(status='stopped; incomplete attempt',error=str(error));raise
        finally:
            recomp.atomic_json(run/'report.json',report);recomp.atomic_json(output/'latest.json',report)
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('--generation',type=Path,required=True)
    prep.add_argument('--maps',type=Path,default=recomp.ROOT/'local/recomp/instruction-maps')
    prep.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/coverage-overlays')
    gen=sub.add_parser('generate');gen.add_argument('--overlay',type=Path,required=True)
    gen.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/bulk')
    gen.add_argument('--batch-size',type=int,default=64);gen.add_argument('--batch-timeout',type=int,default=180)
    gen.add_argument('--min-free-mb',type=int,default=256);gen.add_argument('--dispatch',action='store_true')
    args=parser.parse_args(argv)
    if args.action=='prepare':
        path,result=prepare(args.generation.absolute(),{role:args.maps.absolute()/(role+'.jsonl.gz') for role in ('main','umbra')},args.output.absolute())
        print(json.dumps(dict(overlay=str(path),summary=result['summary']),indent=2))
    else:
        if not 1<=args.batch_size<=512 or args.batch_timeout<=0 or args.min_free_mb<0:parser.error('invalid batch/budget settings')
        args.limit=None;args.output.mkdir(parents=True,exist_ok=True)
        result=generate(args.overlay.absolute(),args.output.absolute(),args)
        print(json.dumps(dict(status=result['status'],directory=result['directory']),indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
