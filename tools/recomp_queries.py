"""Read-only, pinned static program index for generated recovery workspaces.

Rows preserve original-byte identities and generated observations. They are not
behavioral acceptance or proof of reachability.
"""
import argparse
from contextlib import contextmanager
import gzip
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import tempfile
import os

from tools import recomp, recomp_bulk

SCHEMA = 2
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inputs(root):
    p = Path(root) / 'baseline/inputs.json'
    return recomp.load(p), _sha(p)


def _module_sources(inputs, report, generation):
    result = {}
    for role in report['modules']:
        context = recomp.load(generation / role / 'context.json')
        module_path=generation/role/'module.json.gz'
        module_data=json.loads(gzip.decompress(module_path.read_bytes()))
        if module_data.get('binary_sha256')!=context.get('binary_sha256'):
            raise ValueError(f'{role} generated module metadata identity mismatch')
        # Binary paths are pinned by each project's identity, not by generated metadata.
        project = recomp.ROOT / ('local/recomp/project' if role == 'main' else 'local/recomp/umbra') / 'project.json'
        state = recomp.state(project.parent)
        if state['binary_sha256'] != context['binary_sha256'] or state['module'] != context['module']:
            raise ValueError(f'{role} project/context identity mismatch')
        binary = recomp.checked_binary(state)
        image = binary.read_bytes()
        # Authenticated PE map and original header bounds keep non-code data unmapped.
        from tools.daodecomp.pe import fingerprint
        pe = fingerprint(binary)
        result[role] = dict(context=context, state=state, image=image, pe=pe)
    return result


def _entry_address_map(rows, modules):
    entries = {}
    for row in rows:
        m = modules[row['module']]
        address = m['state']['image_base'] + row['rva']
        if address in entries:
            entries[address] = None
        else:
            entries[address] = row['id']
    return entries


def _transfers(metadata):
    abi = metadata.get('abi', {})
    return abi.get('transfers', [])


def build(workspace):
    root = Path(workspace).resolve()
    inputs, inputs_sha = _inputs(root)
    generation = Path(inputs['generation_run']).resolve()
    report_path = generation / 'report.json'
    report_sha = _sha(report_path)
    if inputs.get('generation_report_sha256') != report_sha:
        raise ValueError('generation report changed')
    report = recomp.load(report_path)
    modules = _module_sources(inputs, report, generation)
    rows = inputs['functions']
    if len({r['id'] for r in rows}) != len(rows) or len({(r['module'], r['rva']) for r in rows}) != len(rows):
        raise ValueError('duplicate function inventory identity')
    for role, summary in report['modules'].items():
        expected=summary.get('counts',{}).get('generated_only')
        actual=sum(r['module']==role for r in rows)
        if expected is None or expected!=actual:
            raise ValueError(f'incomplete generated-function baseline for {role}: expected {expected}, got {actual}')
    cache = generation.parent.parent / 'cache'
    loaded = []
    seen = set()
    for row in rows:
        if row['module'] not in modules or row['module'] not in ('main', 'umbra'):
            raise ValueError('unknown module role')
        module = modules[row['module']]
        marker = recomp_bulk.load_shard(cache, row['artifact_key'], module['context']['binary_sha256'], row['rva'])
        if marker['status'] != 'generated_only' or marker['files']['function.cpp'] != row['source_sha256']:
            raise ValueError('baseline source identity/status changed')
        shard = cache / row['artifact_key']
        source_sha = _sha(shard / 'function.cpp')
        rawmeta = (shard / 'function.json.gz').read_bytes()
        meta = json.loads(gzip.decompress(rawmeta))
        symbol = Path(row['source_file']).stem
        if meta.get('rva') != row['rva'] or meta.get('name') != symbol or row['source_sha256'] != source_sha:
            raise ValueError('function source/metadata identity mismatch')
        key = (row['module'], row['rva'])
        if key in seen:
            raise ValueError('duplicate function inventory identity')
        seen.add(key)
        loaded.append((row, module, meta, rawmeta, source_sha, _sha(shard / 'function.json.gz')))
    addrmap = _entry_address_map(rows, modules)
    target_rows = {r['id']: r for r in rows}
    dbpath = root / 'program.sqlite'
    root.mkdir(parents=True, exist_ok=True)
    fd, tempname = tempfile.mkstemp(prefix='.program-', suffix='.sqlite', dir=root)
    os.close(fd)
    try:
        db = sqlite3.connect(tempname)
        db.executescript('''
        PRAGMA journal_mode=DELETE;
        PRAGMA synchronous=FULL;
        CREATE TABLE functions(id TEXT PRIMARY KEY,module TEXT,rva INTEGER,binary_sha256 TEXT,module_name TEXT,symbol TEXT,artifact_key TEXT,source_sha256 TEXT,metadata_sha256 TEXT,instructions INTEGER,metadata_json TEXT);
        CREATE TABLE edges(caller TEXT,site INTEGER,kind TEXT,target INTEGER,import_slot INTEGER,callee TEXT,classification TEXT,library TEXT,symbol TEXT);
        CREATE TABLE fields(function_id TEXT,object_origin TEXT,field_origin TEXT,offset INTEGER,width INTEGER,read INTEGER,write INTEGER,base_origin TEXT,sites_json TEXT);
        CREATE TABLE refs(function_id TEXT,site INTEGER,address INTEGER,kind TEXT);
        CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);
        ''')
        for row, module, meta, rawmeta, source_sha, meta_sha in loaded:
            context=module['context']
            local_addresses={module['state']['image_base']+i['rva'] for i in meta.get('instructions',[])}
            compact={k:v for k,v in meta.items() if k not in ('source','cpp','instructions','instructions_bytes')}
            db.execute('INSERT INTO functions VALUES(?,?,?,?,?,?,?,?,?,?,?)', (row['id'],row['module'],row['rva'],context['binary_sha256'],context['module'],meta['name'],row['artifact_key'],source_sha,meta_sha,len(meta.get('instructions',[])),json.dumps(compact,separators=(',',':'))))
            for transfer in _transfers(meta):
                kind=transfer.get('kind','unknown'); target=transfer.get('direct_target'); slot=transfer.get('import_slot')
                callee=addrmap.get(target) if target is not None else None
                if kind in ('Jmp','CondJmp') and target in local_addresses:
                    classification='local';callee=None
                elif callee:
                    classification='recursive' if callee==row['id'] else 'direct'
                elif slot is not None:
                    classification='import'
                elif target is None:
                    classification='indirect'
                else:
                    classification='unresolved'
                db.execute('INSERT INTO edges VALUES(?,?,?,?,?,?,?,?,?)',(row['id'],transfer.get('instruction_rva',transfer.get('rva',row['rva'])),kind,target,slot,callee,classification,transfer.get('library'),transfer.get('symbol')))
            for structure in meta.get('structures',[]):
                for field in structure.get('fields',[]):
                    db.execute('INSERT INTO fields VALUES(?,?,?,?,?,?,?,?,?)',(row['id'],structure.get('origin'),field.get('origin'),field.get('offset'),field.get('width'),int(bool(field.get('read'))),int(bool(field.get('write'))),field.get('base_origin'),json.dumps(field.get('sites',[]))))
            # Explicit hex operands are candidates, including scalar immediates.
            # The query deliberately does not assert pointer/reference semantics.
            for ins in meta.get('instructions',[]):
                text=ins.get('text','')
                for token in re.findall(r'\b0x([0-9a-fA-F]{1,8})\b', text):
                    address=int(token,16)
                    db.execute('INSERT INTO refs VALUES(?,?,?,?)',(row['id'],ins['rva'],address,'syntactic_address_candidate'))
        exclusions={role:{'initial_inventory_functions':summary.get('inventory_functions'),'catalog_functions':summary.get('catalog_functions'),'generated_only':summary.get('counts',{}).get('generated_only',0),'excluded_or_unresolved':summary.get('catalog_functions',0)-summary.get('counts',{}).get('generated_only',0)} for role,summary in report['modules'].items()}
        meta_values={'schema_version':str(SCHEMA),'baseline_sha256':inputs_sha,'generation_report_sha256':report_sha,'scope':'generated_only compilation baseline; excludes failed/unsupported catalog functions; static hypotheses, not accepted behavior or complete reachability','generation_exclusions_json':json.dumps(exclusions,sort_keys=True)}
        db.executemany('INSERT INTO meta VALUES(?,?)',meta_values.items())
        db.executescript('''
        CREATE UNIQUE INDEX function_by_module_rva ON functions(module,rva);
        CREATE INDEX edge_caller ON edges(caller,site);
        CREATE INDEX edge_callee ON edges(callee);
        CREATE INDEX field_offset ON fields(offset,width);
        CREATE INDEX refs_address ON refs(address);
        CREATE INDEX function_search ON functions(symbol,module);
        ''')
        db.commit(); db.close()
        os.replace(tempname,dbpath)
    except BaseException:
        try: os.unlink(tempname)
        except FileNotFoundError: pass
        raise
    return {'index':str(dbpath),'functions':len(rows),'baseline_sha256':inputs_sha,'generation_report_sha256':report_sha,'scope':'generated_only compilation baseline; excludes failed/unsupported catalog functions; static hypotheses, not accepted behavior or complete reachability','generation_exclusions':exclusions}


@contextmanager
def open_index(workspace):
    root=Path(workspace).resolve(); inputs, digest=_inputs(root)
    report=Path(inputs['generation_run'])/'report.json'
    reportsha=_sha(report)
    db=sqlite3.connect(f'file:{(root / "program.sqlite").as_posix()}?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        meta=dict(db.execute('SELECT key,value FROM meta'))
        if meta.get('schema_version')!=str(SCHEMA) or meta.get('baseline_sha256')!=digest or meta.get('generation_report_sha256')!=reportsha or inputs.get('generation_report_sha256')!=reportsha:
            raise ValueError('stale or unsupported program index')
        yield db
    finally: db.close()


def _limit(value):
    if type(value) is not int or value < 1 or value > MAX_LIMIT: raise ValueError(f'limit must be 1..{MAX_LIMIT}')
    return value


def _address(value):
    return value if type(value) is int else int(value, 16)


def query(workspace, kind, **filters):
    limit=_limit(filters.get('limit',DEFAULT_LIMIT))
    start=filters.get('start',0)
    if type(start) is not int or start<0: raise ValueError('start must be a nonnegative row offset')
    with open_index(workspace) as db:
        sql,args=None,[]
        if kind=='function': sql='SELECT * FROM functions WHERE module=? AND rva=?';args=[filters['module'],_address(filters['rva'])]
        elif kind in ('callers','callees'):
            module=filters['module'];rva=_address(filters['rva'])
            row=db.execute('SELECT id FROM functions WHERE module=? AND rva=?',(module,rva)).fetchone()
            if not row: raise ValueError('function not found')
            sql=('SELECT * FROM edges WHERE callee=?' if kind=='callers' else 'SELECT * FROM edges WHERE caller=?');args=[row[0]]
        elif kind=='fields': sql='SELECT * FROM fields WHERE offset=?';args=[_address(filters['offset'])]
        elif kind=='references': sql='SELECT refs.* FROM refs JOIN functions ON functions.id=refs.function_id WHERE refs.address=? AND functions.module=?';args=[_address(filters['address']),filters['module']]
        elif kind=='search': sql='SELECT * FROM functions WHERE lower(metadata_json) LIKE ? OR lower(symbol) LIKE ?';pat='%'+filters['text'].lower()+'%';args=[pat,pat]
        elif kind=='walk':
            seed=db.execute('SELECT id FROM functions WHERE module=? AND rva=?',(filters['module'],_address(filters['rva']))).fetchone()
            if not seed: raise ValueError('function not found')
            depth=min(max(int(filters.get('depth',4)),0),32); seen={seed[0]};front=[seed[0]]
            for _ in range(depth):
                nxt=[]
                for caller in front:
                    for (callee,) in db.execute("SELECT callee FROM edges WHERE caller=? AND classification IN ('direct','recursive')",(caller,)):
                        if callee and callee not in seen:seen.add(callee);nxt.append(callee)
                front=nxt
                if not front:break
            rows=[db.execute('SELECT * FROM functions WHERE id=?',(i,)).fetchone() for i in sorted(seen)]
            total=len(rows); items=[dict(r) for r in rows[start:start+limit]]
            return {'kind':kind,'items':items,'total':total,'start':start,'truncated':total>start+limit,'scope':'static direct-entry graph; reachability incomplete'}
        else: raise ValueError('unknown query kind')
        if kind=='fields' and filters.get('width') is not None: sql+=' AND width=?';args.append(int(filters['width']))
        count=db.execute('SELECT count(*) FROM ('+sql+')',args).fetchone()[0]
        ordering={'function':'module,rva','callers':'caller,site','callees':'site,target',
            'fields':'function_id,object_origin,field_origin','references':'refs.function_id,refs.site,refs.address',
            'search':'module,rva'}[kind]
        records=db.execute(sql+' ORDER BY '+ordering+' LIMIT ? OFFSET ?',args+[limit,start]).fetchall()
        columns=[d[0] for d in db.execute(sql+' LIMIT 0',args).description]
        result={'kind':kind,'items':[dict(zip(columns,r)) for r in records],'total':count,'start':start,'truncated':count>start+limit}
    if kind=='function' and result['items']:
        item=result['items'][0]
        inputs,_=_inputs(workspace); cache=Path(inputs['generation_run']).parent.parent/'cache'
        record=next((r for r in inputs['functions'] if r['id']==item['id']),None)
        if record is None: raise ValueError('function record missing from pinned baseline')
        marker=recomp_bulk.load_shard(cache,record['artifact_key'],item['binary_sha256'],item['rva'])
        shard=cache/record['artifact_key'];source=shard/'function.cpp';md=shard/'function.json.gz'
        if marker['status']!='generated_only' or marker['files']['function.cpp']!=record['source_sha256'] or _sha(source)!=record['source_sha256'] or _sha(md)!=item['metadata_sha256']:
            raise ValueError('function shard evidence changed')
        item['metadata']=json.loads(gzip.decompress(md.read_bytes()))
        item['record']=record;item['source_path']=str(source);item['source_included']=False
        state=None
        if (Path(workspace)/'workbench.json').exists():
            from tools import recomp_workbench as w
            state=w.read(Path(workspace))
            current=state['functions'].get(item['id'])
            if current is not None:
                w.blob(Path(workspace),current['committed_source_sha256'])
                item['workspace_source']={
                    'path':str(Path(workspace)/current['source_path']),
                    'committed_blob':str(Path(workspace)/'blobs'/current['committed_source_sha256']),
                    'sha256':current['committed_source_sha256'],
                    'hypotheses':current['hypotheses'],
                    'scope':'Recorded edited source; source_path separately identifies the pinned generated original.'}
        if (Path(workspace)/'types.json').exists():
            from tools import recomp_types
            item['shared_types']=recomp_types.function_context(Path(workspace),item['id'],state)
        if filters.get('source'):
            cap=filters.get('source_max_bytes',65536)
            if type(cap) is not int or not 1<=cap<=262144: raise ValueError('source_max_bytes must be 1..262144')
            raw=source.read_bytes()
            if len(raw)>cap: raise ValueError('source exceeds requested bound; raise source_max_bytes (max 262144)')
            item['source']=raw.decode('utf-8');item['source_included']=True;item['source_bytes']=len(raw);item['source_truncated']=False
    return result


def get_function(workspace,module,rva):
    result=query(workspace,'function',module=module,rva=f'{int(rva):x}',limit=1)
    if result['total']!=1: raise ValueError('function not found or ambiguous')
    row=result['items'][0]
    return {'function':row,'record':row['record'],'metadata':row['metadata'],'source_path':row['source_path'],'source_sha256':row['record']['source_sha256'],'source_included':row['source_included'],'shared_types':row.get('shared_types'),'workspace_source':row.get('workspace_source')}


def binary_query(workspace, kind, module, rva, size=None, encoding='ascii', max_bytes=256):
    if kind not in ('bytes','string'):raise ValueError('unknown original-byte query')
    inputs,_=_inputs(workspace);generation=Path(inputs['generation_run']);report=recomp.load(generation/'report.json')
    sources=_module_sources(inputs,report,generation)
    if module not in sources: raise ValueError('module not in pinned generation')
    m=sources[module]
    rva=_address(rva)
    if kind=='bytes':
        if type(size) is not int or not 1<=size<=4096: raise ValueError('size must be 1..4096')
        length=size
    else:
        if encoding not in ('ascii','utf16'): raise ValueError('encoding must be ascii or utf16')
        if type(max_bytes) is not int or not 1<=max_bytes<=4096: raise ValueError('max_bytes must be 1..4096')
        length=max_bytes
    pe=m['pe']; spans=[s for s in pe['sections'] if s['rva']<=rva and rva+length<=s['rva']+s['file_size']]
    if len(spans)!=1: raise ValueError('requested range is not uniquely file-backed')
    section=spans[0];off=section['file_offset']+rva-section['rva'];data=m['image'][off:off+length]
    if len(data)!=length: raise ValueError('truncated original binary range')
    terminated=False
    if kind=='string':
        step=2 if encoding=='utf16' else 1; end=None
        for pos in range(0,len(data)-step+1,step):
            if data[pos:pos+step]==b'\0'*step:end=pos;terminated=True;break
        shown=data[:end] if end is not None else data
        text=shown.decode('ascii' if encoding=='ascii' else 'utf-16le',errors='replace')
        return {'kind':'string','module':module,'binary_sha256':m['context']['binary_sha256'],'rva':rva,'hex':shown.hex(),'text':text,'encoding':encoding,'truncated':not terminated,'terminated':terminated}
    return {'kind':'bytes','module':module,'binary_sha256':m['context']['binary_sha256'],'rva':rva,'size':size,'hex':data.hex(),'truncated':False}


def _cli():
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',default='.')
    sub=parser.add_subparsers(dest='cmd',required=True);sub.add_parser('build')
    for kind in ('function','callers','callees','walk'):
        p=sub.add_parser(kind);p.add_argument('--module',choices=('main','umbra'),required=True);p.add_argument('--rva',required=True)
        if kind=='walk':p.add_argument('--depth',type=int,default=4)
        p.add_argument('--limit',type=int,default=DEFAULT_LIMIT)
        if kind=='function':
            p.add_argument('--source',action='store_true');p.add_argument('--source-max-bytes',type=int,default=65536)
    p=sub.add_parser('fields');p.add_argument('--offset',required=True);p.add_argument('--width',type=int);p.add_argument('--limit',type=int,default=DEFAULT_LIMIT)
    p=sub.add_parser('references');p.add_argument('--module',choices=('main','umbra'),required=True);p.add_argument('--address',required=True);p.add_argument('--limit',type=int,default=DEFAULT_LIMIT)
    p=sub.add_parser('bytes');p.add_argument('--module',choices=('main','umbra'),required=True);p.add_argument('--rva',required=True);p.add_argument('--size',type=int,required=True)
    p=sub.add_parser('string');p.add_argument('--module',choices=('main','umbra'),required=True);p.add_argument('--rva',required=True);p.add_argument('--encoding',choices=('ascii','utf16'),default='ascii');p.add_argument('--max-bytes',type=int,default=256)
    p=sub.add_parser('search');p.add_argument('--text',required=True);p.add_argument('--limit',type=int,default=DEFAULT_LIMIT)
    for command, command_parser in sub.choices.items():
        if command not in ('build','bytes','string'):
            command_parser.add_argument('--start',type=int,default=0)
    a=parser.parse_args()
    try:
        filters={k:v for k,v in vars(a).items() if k not in ('cmd','workspace')}
        result=build(a.workspace) if a.cmd=='build' else (binary_query(a.workspace,a.cmd,a.module,a.rva,getattr(a,'size',None),getattr(a,'encoding','ascii'),getattr(a,'max_bytes',256)) if a.cmd in ('bytes','string') else query(a.workspace,a.cmd,**filters))
        print(json.dumps(result,sort_keys=True,default=str))
    except Exception as exc:
        parser.error(str(exc))

if __name__=='__main__': _cli()
