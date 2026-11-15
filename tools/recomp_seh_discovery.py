"""Authenticate canonical MSVC x86 SEH4 table references and internal roots.

This discovers original-byte hypotheses, never exception behavior or acceptance.
Other prolog variants, C++ EH tables and nonlocal unwinding remain outside scope.
"""
import argparse
import copy
import json
from pathlib import Path
import struct
import time
import capstone
from tools import recomp
from tools.recomp_native import PE32
from tools.recomp_pointer_discovery import highlow_sites
from tools.recomp_bulk_build import require_whole_inventory

PROLOG_MIDDLE=bytes.fromhex('64ff35000000008b442410896c24108d6c24102be0535657')
PROLOG_END=bytes.fromhex('3145fc33c5508965e8ff75f88b45fcc745fcfeffffff8945f88d45f064a300000000c3')


def executable(pe,rva,size=1):
    return any(s['rva']<=rva and rva+size<=s['rva']+min(s['virtual_size'],s['file_size']) and
        struct.unpack_from('<I',pe.data,pe.section_table+i*40+36)[0]&0x20000000 for i,s in enumerate(pe.sections))


def ordinary_data(pe,rva,size):
    return any(s['rva']<=rva and rva+size<=s['rva']+min(s['virtual_size'],s['file_size']) and
        s['name'] not in ('.rsrc','.reloc') and not struct.unpack_from('<I',pe.data,pe.section_table+i*40+36)[0]&0x20000000
        for i,s in enumerate(pe.sections))


def prolog4(pe,rva,relocations):
    if not executable(pe,rva,69):return None
    raw=pe.read(rva,69)
    if raw[0]!=0x68 or raw[5:29]!=PROLOG_MIDDLE or raw[29]!=0xa1 or raw[34:]!=PROLOG_END:return None
    if rva+1 not in relocations or rva+30 not in relocations:
        raise ValueError('canonical SEH4 prolog lacks pointer relocation evidence')
    handler=int.from_bytes(raw[1:5],'little')-pe.info['image_base']
    cookie=int.from_bytes(raw[30:34],'little')-pe.info['image_base']
    if not executable(pe,handler):raise ValueError('SEH4 dispatcher is not module code')
    pe.read(cookie,4)
    return dict(rva=rva,bytes=raw.hex(),sha256=recomp.digest(raw),dispatcher_rva=handler,cookie_rva=cookie)


def discover(pe,registered,record_limit=128):
    if type(record_limit) is not int or not 1<=record_limit<=4096:raise ValueError('invalid SEH record budget')
    relocations=set(highlow_sites(pe));helpers={};sources=[];rejected=[]
    for site in sorted(relocations):
        if site<1 or not executable(pe,site-1,10):continue
        raw=pe.read(site-1,10)
        if raw[0]!=0x68 or raw[5]!=0xe8:continue
        helper=site+9+int.from_bytes(raw[6:10],'little',signed=True)
        if helper not in helpers:helpers[helper]=prolog4(pe,helper,relocations)
        if helpers[helper] is None:continue
        # Both opcodes must be starts in the input-bound compiled registry.
        if site-1 not in registered or site+4 not in registered:
            rejected.append(dict(rva=site-1,reason='SEH4-looking source lacks registered push/call boundaries'));continue
        table=int.from_bytes(raw[1:5],'little')-pe.info['image_base']
        if not ordinary_data(pe,table,16):
            rejected.append(dict(rva=site-1,table_rva=table,reason='scope table is not file-backed ordinary data'));continue
        sources.append(dict(push_rva=site-1,call_rva=site+4,bytes=raw.hex(),table_rva=table,prolog_rva=helper))
    tables=[];bases=sorted({s['table_rva'] for s in sources})
    for index,base in enumerate(bases):
        try:header=pe.read(base,16);offsets=struct.unpack('<iiii',header)
        except ValueError as error:
            rejected.append(dict(table_rva=base,reason=str(error)));continue
        if (offsets[0]!=-2 and (offsets[0]>=0 or offsets[0]%4)) or offsets[2]>=0 or offsets[2]%4:
            rejected.append(dict(table_rva=base,reason='unrecognized SEH4 cookie offset header'));continue
        bound=bases[index+1] if index+1<len(bases) else None
        records=[];stop=None;trailing=None
        for number in range(record_limit):
            cell=base+16+number*12
            if bound is not None and cell+12>bound:
                stop='next independently referenced canonical scope table';break
            if not ordinary_data(pe,cell,12):stop='record leaves file-backed ordinary data';break
            try:raw=pe.read(cell,12)
            except ValueError as error:stop=str(error);break
            enclosing,filter_va,handler_va=struct.unpack('<iII',raw)
            filter_rva=filter_va-pe.info['image_base'] if filter_va else None
            handler_rva=handler_va-pe.info['image_base']
            reason=None
            if enclosing!=-2 and not 0<=enclosing<number:reason='invalid enclosing level for canonical SEH4 record'
            elif cell+8 not in relocations or not executable(pe,handler_rva):reason='handler lacks executable HIGHLOW reference'
            elif filter_va and (cell+4 not in relocations or not executable(pe,filter_rva)):reason='filter lacks executable HIGHLOW reference'
            if reason:
                stop='record prefix ended; subsequent bytes remain unclassified'
                trailing=dict(rva=cell,bytes=raw.hex(),reason=reason);break
            records.append(dict(index=number,rva=cell,bytes=raw.hex(),enclosing_level=enclosing,
                filter_rva=filter_rva,handler_rva=handler_rva,
                pointer_sites=[cell+8]+([cell+4] if filter_va else [])))
        else:raise ValueError('SEH table record budget exhausted; no completed discovery')
        if not records:
            rejected.append(dict(table_rva=base,reason='no authenticated SEH4 record',trailing=trailing));continue
        tables.append(dict(rva=base,header_bytes=header.hex(),cookie_offsets=list(offsets),records=records,
            sources=[s for s in sources if s['table_rva']==base],boundary_observation=stop,trailing_unknown=trailing,
            scope='authenticated record prefix; total table extent and dynamic try levels are not proven'))
    return dict(prologs=[v for v in helpers.values() if v is not None],tables=tables,rejected=rejected,
        scope='canonical SEH4 prolog references only; other prolog variants/C++ EH and execution/unwind behavior remain unknown')


def internal_roots(pe,catalog,registered,discovery):
    proposals=[];unknown=[];decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    origins={}
    for table in discovery['tables']:
        for record in table['records']:
            for kind in ('filter','handler'):
                target=record[kind+'_rva']
                if target is None or target in registered:continue
                origins.setdefault(target,[]).append(dict(table_rva=table['rva'],record_rva=record['rva'],kind=kind,
                    pointer_rva=record['rva']+(4 if kind=='filter' else 8)))
    for target,evidence in sorted(origins.items()):
        interior=False
        for start in range(max(0,target-14),target):
            if start not in registered:continue
            known=next(decoder.disasm(pe.read(start,15),pe.info['image_base']+start,count=1),None)
            if known is None:raise ValueError('registered code is independently undecodable')
            if start+known.size>target:interior=True;break
        if interior:
            unknown.append(dict(rva=target,origins=evidence,reason='SEH reference enters a registered instruction interior'));continue
        owners=[r for r in catalog if any(b['rva']<=target<b['rva']+b['size'] for b in r.get('selection',{}).get('ranges',[]))]
        if not owners:
            unknown.append(dict(rva=target,origins=evidence,reason='SEH entry outside existing selections; bounds remain unknown'));continue
        # Preserve every overlapping envelope. No new ownership or ABI is inferred.
        instruction=next(decoder.disasm(pe.read(target,15),pe.info['image_base']+target,count=1),None)
        if instruction is None:
            unknown.append(dict(rva=target,origins=evidence,reason='SEH target is undecodable'));continue
        valid=[r for r in owners if any(b['rva']<=target and target+instruction.size<=b['rva']+b['size'] for b in r['selection']['ranges'])]
        if not valid:
            unknown.append(dict(rva=target,origins=evidence,reason='SEH instruction crosses existing ownership'));continue
        proposals.append(dict(rva=target,bytes=instruction.bytes.hex(),origins=evidence,owner_rvas=[r['rva'] for r in valid],
            contract_status='exception entry state and nonlocal continuation remain unknown; not accepted'))
    return proposals,unknown


def prepare(generation,linked,output):
    generation=generation.absolute();linked=linked.absolute();report=recomp.load(generation/'report.json');require_whole_inventory(report)
    prepared=recomp.load(linked/'prepared.json');compiled=recomp.load(Path(prepared['compilation_run'])/'inputs.json')
    if Path(compiled['generation_run'])!=generation or compiled['generation_report_sha256']!=recomp.digest((generation/'report.json').read_bytes()):
        raise ValueError('linked registry does not belong to this generation')
    registry=linked/'source/registry.S'
    if recomp.digest(registry.read_bytes())!=prepared['sources']['registry.S']:raise ValueError('compiled registry source changed')
    addresses={int(line[6:],16) for line in registry.open() if line.startswith('.long 0x')}
    if len(addresses)!=prepared['instruction_entries']:raise ValueError('compiled registry entry count differs')
    prior=Path(report['entry_overlay']);descriptor=recomp.load(prior/'overlay.json')
    if recomp.digest((prior/'overlay.json').read_bytes())!=report['entry_overlay_sha256']:raise ValueError('base overlay changed')
    for name,sha in descriptor['files'].items():
        if Path(name).name!=name or recomp.digest((prior/name).read_bytes())!=sha:raise ValueError('base overlay member changed')
    out=output.absolute()/str(time.time_ns());out.mkdir(parents=True);summary={}
    for role in ('main','umbra'):
        context=recomp.load(generation/role/'context.json');state=recomp.state(Path(context['project']))
        if recomp.digest(recomp.encoded(state))!=context['project_sha256']:raise ValueError('project changed after generation')
        pe=PE32(recomp.checked_binary(state));registered={a-pe.info['image_base'] for a in addresses if executable(pe,a-pe.info['image_base'])}
        catalog=list(map(json.loads,(generation/role/'catalog.jsonl').open()))
        discovery=discover(pe,registered);proposals,unknown=internal_roots(pe,catalog,registered,discovery)
        selected=recomp.load(prior/(role+'-role.json'));entries={f['rva']:f for f in selected['functions']};by_rva={r['rva']:r for r in catalog}
        for proposal in proposals:
            for owner in proposal['owner_rvas']:
                if owner not in entries:
                    entry=copy.deepcopy(by_rva[owner]['selection']);selected['functions'].append(entry);entries[owner]=entry
                entry=entries[owner];entry['extra_entries']=sorted(set(entry.get('extra_entries',[]))|{proposal['rva']})
        selected['functions'].sort(key=lambda r:r['rva']);recomp.atomic_json(out/(role+'-role.json'),selected)
        evidence=dict(binary_sha256=state['binary_sha256'],module=state['module'],discovery=discovery,proposals=proposals,unknown=unknown,
            catalog_sha256=recomp.digest((generation/role/'catalog.jsonl').read_bytes()),registry_sha256=prepared['sources']['registry.S'],game_acceptance=False)
        recomp.atomic_json(out/(role+'-seh.json'),evidence);recomp.checked_binary(state)
        summary[role]=dict(prologs=len(discovery['prologs']),tables=len(discovery['tables']),records=sum(len(t['records']) for t in discovery['tables']),
            proposed_internal_entries=len(proposals),changed_owners=len({o for p in proposals for o in p['owner_rvas']}),unknown_targets=len(unknown),rejected=len(discovery['rejected']))
    (out/'controller.py').write_bytes(Path(__file__).read_bytes())
    descriptor.update(status='SEH4 internal-entry hypotheses; contracts, bounds and acceptance preserved',generation_run=str(generation),
        generation_report_sha256=recomp.digest((generation/'report.json').read_bytes()),base_overlay=dict(path=str(prior),sha256=report['entry_overlay_sha256']),
        linked_input=str(linked),prepared_sha256=recomp.digest((linked/'prepared.json').read_bytes()),seh_discovery=summary,game_acceptance=False,behavioral_acceptance=False)
    descriptor['files']={p.name:recomp.digest(p.read_bytes()) for p in out.iterdir() if p.is_file()};recomp.atomic_json(out/'overlay.json',descriptor)
    recomp.atomic_json(recomp.ROOT/'local/recomp/startup/seh-overlay-latest.json',dict(overlay=str(out),summary=summary,game_acceptance=False));return out,summary


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--generation',type=Path,required=True);parser.add_argument('--linked',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/seh-overlays');args=parser.parse_args()
    out,summary=prepare(args.generation,args.linked,args.output);print(json.dumps(dict(overlay=str(out),summary=summary)),flush=True)

if __name__=='__main__':main()
