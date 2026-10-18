"""Explicit same-database successor adoption and a read-only startup packet adapter.

This module never executes an original, a provider or model-supplied command.
Migration requires separate exact review and both established exclusive leases.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('continuation_dispatcher', HERE/'recovery_dispatcher.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
HISTORICAL = ('meta', 'tasks', 'ownership', 'requests', 'jobs', 'events', 'edges')
DDL = '''
CREATE TABLE supersessions(predecessor TEXT PRIMARY KEY,successor TEXT NOT NULL,reason TEXT NOT NULL);
CREATE TABLE ownership_successors(identity TEXT PRIMARY KEY,predecessor TEXT NOT NULL,successor TEXT NOT NULL);
CREATE TABLE runtime_tasks(id TEXT PRIMARY KEY);
CREATE TABLE input_blocks(id TEXT PRIMARY KEY,reason TEXT NOT NULL);
CREATE TABLE adoptions(id TEXT PRIMARY KEY,evidence TEXT NOT NULL);
CREATE TABLE migrations(id TEXT PRIMARY KEY,plan_sha256 TEXT NOT NULL,history_sha256 TEXT NOT NULL,installed REAL NOT NULL);
'''


def history(db):
    return {table: [list(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY '+','.join(
            str(i+1) for i in range(len(db.execute('PRAGMA table_info('+table+')').fetchall()))))]
            for table in HISTORICAL}


def value_sha(value):
    return hashlib.sha256(d.encoded(value)).hexdigest()


def bound_map(bindings):
    for path, expected in bindings.items():
        d.bound(path, expected)


def check_checkpoint(record):
    d.require(record.get('complete_checkpoint') is True and record.get('proof') is False,
              'incomplete external checkpoint')
    d.require(record.get('schema_version') == 2 and record.get('policy') == 'clean-build-local-groups-003'
              and record.get('fresh_clean_build') is True and record.get('native_windows_validated') is False,
              'external checkpoint policy differs')
    rows = record.get('records', [])
    d.require(type(rows) is list and len(rows)==165 and all(type(r.get('negative_control')) is bool for r in rows),
              'external inventory differs from93+72')
    identities = [(r.get('function_id'),r['negative_control']) for r in rows]
    d.require(len(set(identities))==165 and sum(not negative for _,negative in identities)==93,
              'external checkpoint has duplicate or wrong inventory')
    for row in rows:
        counts=row.get('case_counts',{})
        d.require(type(counts) is dict and counts and all(type(n) is int and n>=0 for n in counts.values()),
                  'external checkpoint missing measured counts')
        if row['negative_control']:
            d.require(row.get('status')=='failed' and set(counts)<={'corpus_pass','mismatch'} and counts.get('mismatch',0)>0,
                      'external control lacks measured mismatch')
        else:
            d.require(row.get('status')=='corpus_pass' and set(counts)=={'corpus_pass'} and counts['corpus_pass']>0,
                      'external positive did not pass')
    projection = dict(record)
    attestation = projection.pop('attestation_sha256', None)
    d.require(attestation == hashlib.sha256(json.dumps(projection,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),
              'external checkpoint self-binding changed')


def external_adoption(config, plan):
    """Require the single independently approved publication; never rerun its pair."""
    external = plan['external_adoption']
    bound_map(external['fixed_inputs'])
    descriptor = d.load(external['descriptor'])
    d.require(descriptor['package_sha256'] == external['package_sha256'] and
              descriptor['state'] == 'accepted-for-integration', 'accepted package differs')
    package = Path(descriptor['pair'])/'accepted/package.json'
    d.bound(package, external['package_sha256'])
    accepted = d.load(package)
    d.bound(Path(config['root'])/d.relative(accepted['candidate_target']),accepted['source_sha256'])
    d.require(len(set(accepted['functions']))==46 and accepted['proof'] is False and
              accepted['native_windows_validated'] is False, 'accepted package function scope differs')
    receipt = d.load(external['receipt'])
    published_path = Path(external['published'])
    published = d.load(published_path)
    d.require(receipt.get('state') == 'complete' and receipt.get('result',{}).get('state') == 'complete',
              'external publication incomplete or failed')
    d.require(receipt.get('review_packet_raw_sha256') == external['review_packet_sha256'] and
              receipt.get('approval_raw_sha256') == external['approval_sha256'] and
              receipt.get('published_raw_sha256') == d.digest(published_path), 'external approval/publication differs')
    head = published.get('commit')
    d.require(type(head) is str and receipt['result'].get('commit') == head, 'external publication head differs')
    runs = published.get('ci_runs', [])
    d.require(runs and all(r.get('headSha') == head and r.get('status') == 'completed' and r.get('conclusion') == 'success'
                          for r in runs), 'external exact-head CI incomplete')
    # Also query jobs: a single successful generic run is insufficient for the required three-host milestone.
    ci_jobs = []
    for run in runs:
        result = json.loads(d.output(['gh','run','view',str(run['databaseId']),'--json','headSha,status,conclusion,jobs'],config['root']))
        d.require(result.get('headSha') == head and result.get('status') == 'completed' and result.get('conclusion') == 'success',
                  'external exact-head CI no longer successful')
        ci_jobs += result.get('jobs',[])
    for host in ('ubuntu-latest','macos-latest','windows-latest'):
        d.require(any(j.get('name') == 'synthetic ('+host+')' and j.get('conclusion') == 'success' for j in ci_jobs),
                  'external three-host CI missing')
    record_path = Path(config['root'])/d.relative(published['record'])
    record = d.load(record_path)
    check_checkpoint(record)
    # Reuse existing current-input projection, rather than accepting old passing report metadata.
    sys.path.insert(0,config['root'])
    cache = d.module(Path(config['root'])/'tools/incremental_checkpoint.py','continuation_cache')
    source = cache.source_manifest(Path(config['root']))
    expected = dict(source, **{'analysis/functions.json':d.digest(Path(config['root'])/'analysis/functions.json')})
    d.require(all(r.get('artifacts_sha256')==expected and r.get('artifacts_unchanged') is True and
                  r.get('provenance_kind')=='fresh_clean_build_and_exact_execution_inputs' and
                  type(r.get('repeats_per_side')) is int and r['repeats_per_side']>=2 for r in record['records']),
              'external checkpoint current inputs stale')
    producer_path=Path(config['root'])/'reports/dispatcher-19527cacd0bd4f18a248d7e8a9296480/reuse-attestation.json'
    producer=d.load(producer_path)
    d.require(producer.get('status')=='passed' and producer.get('complete_checkpoint') is True and
              producer.get('usable_for_progress') is True and producer.get('source')==source and
              producer.get('registry_sha256')==expected['analysis/functions.json'], 'external producer differs')
    projected=cache.publication_document(producer)
    d.require(record['records']==projected['records'] and record.get('build_attestation',{})==projected.get('build_attestation',{}),
              'external publication differs from exact producer projection')
    return {'package_sha256':external['package_sha256'],'receipt':str(external['receipt']),
            'receipt_sha256':d.digest(external['receipt']),'published_sha256':d.digest(published_path),
            'checkpoint':str(record_path),'checkpoint_sha256':d.digest(record_path),'commit':head,
            'ci_jobs':ci_jobs,'accepted_increment':24,'proof':False,'native_windows_validated':False}


def install(plan_path, approval_path, release_path):
    plan = d.load(plan_path)
    config_path = Path(plan['config'])
    config = d.load(config_path)
    bound_map(plan['fixed_inputs'])
    d.bound(config_path, plan['config_sha256'])
    approval = d.load(approval_path)
    d.require(approval.get('decision') == 'approve' and approval.get('plan_sha256') == d.digest(plan_path)
              and approval.get('runtime_code') == config['runtime_code'] and
              approval.get('scope') == 'same-lineage-migration-external-adoption-and-bounded-startup-preparation'
              and not approval.get('blocking_issues'), 'exact independent continuation approval missing')
    release = d.load(release_path)
    d.require(release.get('released') is True and release.get('plan_sha256') == d.digest(plan_path),
              'shared mutation ownership not released')
    root = Path(config['root'])
    with d.exclusive(root/'local/providers/recovery-controller'):
        with d.exclusive(root/'local/providers/recovery-integration'):
            d.require(d.output(['git','status','--porcelain'],root) == '', 'shared checkout not clean')
            d.require(d.output(['git','rev-parse','HEAD'],root) == release.get('head'), 'released HEAD moved')
            # No write, including new tables, until all active/ambiguity/evidence checks pass.
            lineage = Path(config['lineage_state'])
            db = sqlite3.connect('file:'+str(lineage/'state.sqlite3')+'?mode=rw',uri=True)
            try:
                db.row_factory = sqlite3.Row
                d.require(not db.execute("SELECT 1 FROM jobs WHERE state='running'").fetchone(), 'active or unreconciled worker')
                d.require(not db.execute("SELECT 1 FROM meta WHERE key='successor-config'").fetchone(), 'migration already installed; no replay')
                before = history(db)
                d.require(dict(before['meta'])['config'] == plan['original_config_sha256'], 'original config identity differs')
                # Freeze the pre-existing record set, while allowing only additive later director debits/events.
                frozen = plan.get('historical_records', {})
                for table, rows in frozen.items():
                    for row in rows:
                        if table=='meta' and row[0]=='clock':
                            d.require(float(dict(before['meta'])['clock']) >= float(row[1]), 'historical clock regressed')
                        else:
                            d.require(row in before[table], 'historical record changed: '+table)
                dispositions = plan['request_dispositions']
                ambiguous = {r['id'] for r in db.execute("SELECT * FROM requests WHERE state='in-flight'")}
                d.require(ambiguous == set(dispositions), 'ambiguous external requests require exact disposition')
                for request, disposition in dispositions.items():
                    bound_map(disposition['evidence'])
                    d.require(disposition['disposition'] == 'failed-transport-retained-no-replay', 'unsupported request disposition')
                    # An independently reviewed disposition may resolve scheduling ambiguity but never rewrite/refund it.
                    status_paths=[p for p in disposition['evidence'] if p.endswith('/status.json')]
                    d.require(len(status_paths)==1,'missing failed transport status')
                    failed=d.load(status_paths[0])
                    reviews=[m for m in failed.get('model_requests',[]) if m.get('kind')=='review']
                    d.require(failed.get('status')=='needs-evidence' and len(reviews)==1 and
                              reviews[0].get('exit_code')==1 and reviews[0].get('usage')==[] and
                              reviews[0].get('tool_items')==[], 'historical failed transport not established')
                # Ensure queued stale history and every function claim are exactly the reviewed predecessors.
                for successor in config['tasks']:
                    d.verify_inputs(successor)
                for predecessor, entry in plan['supersessions'].items():
                    row = db.execute('SELECT payload,state,job FROM tasks WHERE id=?',(predecessor,)).fetchone()
                    d.require(row and value_sha(dict(row)) == entry['predecessor_sha256'], 'predecessor changed')
                adoption = external_adoption(config,plan)
                # Existing director requests after freeze are allowed as debits only; never reset clock/anchor.
                d.require(dict(before['meta'])['anchor'] == plan['anchor'], 'request cycle anchor differs')
                for key,value in plan['historical_meta'].items():
                    d.require(dict(before['meta']).get(key) == value, 'historical lineage changed')
                d.verify_controller(config)
                # executescript commits implicitly; use individual DDL statements in one FULL transaction.
                db.execute('PRAGMA synchronous=FULL')
                db.execute('BEGIN IMMEDIATE')
                for statement in DDL.split(';'):
                    if statement.strip(): db.execute(statement)
                db.execute("INSERT INTO meta VALUES('successor-config',?)",(plan['config_sha256'],))
                for predecessor, entry in plan['supersessions'].items():
                    db.execute('INSERT INTO supersessions VALUES(?,?,?)',(predecessor,entry['successor'],entry['reason']))
                db.execute('INSERT INTO adoptions VALUES(?,?)',('external-ready24-v2',d.encoded(adoption).decode()))
                db.execute('INSERT INTO adoptions VALUES(?,?)',('historical-request-dispositions',d.encoded(dispositions).decode()))
                db.execute('INSERT INTO migrations VALUES(?,?,?,?)',(plan['id'],d.digest(plan_path),value_sha(before),time.time()))
                # Original historical rows are byte/value preserved; only one new metadata row is expected.
                after = history(db)
                d.require([r for r in after['meta'] if r[0]!='successor-config'] == before['meta']
                          and all(after[t] == before[t] for t in HISTORICAL if t!='meta'), 'historical rows changed')
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
            # A crash after DB commit is fail-closed: replay refuses and requires receipt reconciliation.
            d.atomic(Path(plan['runtime'])/'migration-receipt.json',{'state':'installed','plan_sha256':d.digest(plan_path),
                'history_sha256':value_sha(before),'adoption':adoption,'same_database':str(lineage/'state.sqlite3'),
                'anchor':plan['anchor'],'ledger':config['ledger'],'no_model_calls':True,'no_original_execution':True})
            # Preserve approval bytes. The original approval/config remain in their original directory.
            d.atomic(Path(plan['runtime'])/'approval.json',{'decision':'approve','config_sha256':plan['config_sha256'],
                'trusted_code':config['trusted_code'],'continuation_review_sha256':d.digest(approval_path),
                'plan_sha256':d.digest(plan_path),'continuation_review_path':str(approval_path.absolute())})
            d.atomic(lineage/'successor.json',{'runtime':plan['runtime'],'config_sha256':plan['config_sha256'],
                'plan_sha256':d.digest(plan_path)})


def read_rva(binary, sections, rva, size):
    matches = [s for s in sections if s['rva'] <= rva and rva+size <= s['rva']+s['file_size']]
    d.require(len(matches)==1,'unmapped/ambiguous bounded static range')
    section = matches[0]
    return binary[section['file_offset']+rva-section['rva']:section['file_offset']+rva-section['rva']+size]


def prepare_static(config, task):
    """Build a frozen hypothesis packet from exact bytes, never a valid implementation contract."""
    d.verify_inputs(task)
    metadata = d.load(task['observation'])
    d.require(metadata['identity']['sha256']==config['reference']['sha256']
              and metadata['observed_control_flow']['target_rva']=='0x00016ad0'
              and metadata['observed_control_flow']['target_body_executed'] is False
              and metadata['termination']['approval_permanently_consumed'] is True, 'observation scope differs')
    root = Path(config['root'])
    for binding in metadata['bindings'].values():
        d.bound(root/d.relative(binding['private_path']),binding['sha256'])
    # Existing read-only PE intake, exact range checks and byte-backed direct edge checks.
    sys.path.insert(0,str(root))
    from tools.daodecomp.pe import fingerprint
    original = d.bound(config['reference']['path'],config['reference']['sha256'])
    pe = fingerprint(original)
    binary = original.read_bytes()
    frontier = d.load(task['frontier'])
    unit = next(u for u in frontier['units_in_priority_order'] if u['id']=='application-envelope')
    edges = []
    for edge in unit['observed_edges']:
        callsite = int(edge['callsite_rva'],16)
        if not 0x16ad0 <= callsite <= 0x16c00: continue
        instruction = bytes.fromhex(edge['bytes'])
        actual = read_rva(binary,pe['sections'],callsite,len(instruction))
        d.require(actual == instruction, 'static edge instruction changed')
        if edge.get('kind')=='call':
            d.require(len(actual)==5 and actual[0]==0xe8 and
                (callsite+5+int.from_bytes(actual[1:],'little',signed=True)) & 0xffffffff == int(edge['target_rva'],16),
                'direct target is not byte-backed')
        edges.append(edge)
    expected = {'000c2480','004e19e0','004e2d29','004e2da2'}
    d.require({e['target_rva'] for e in edges if e.get('kind')=='call' and e['callsite_rva']!='00016c00'}==expected,
              'envelope direct dependency set differs')
    body = read_rva(binary,pe['sections'],0x16ad0,0x16c00-0x16ad0)
    dependency_packets = []
    for rva in sorted(expected):
        # A 32-byte intake prefix does not establish a callee extent or ABI.
        prefix = read_rva(binary,pe['sections'],int(rva,16),32)
        characterized = [f for u in frontier['units_in_priority_order'] for f in u['functions'] if f.get('rva')==rva]
        d.require(len(characterized)==1,'dependency range characterization missing or ambiguous')
        function = characterized[0]
        ranges = function['body_ranges_hypothesis']
        d.require(ranges and len(ranges)<=8,'unbounded dependency range hypothesis')
        ranged = b''.join(read_rva(binary,pe['sections'],r['start_rva'],r['end_rva_inclusive']-r['start_rva']+1) for r in ranges)
        d.require(len(ranged)<=8192 and hashlib.sha256(ranged).hexdigest()==function['concatenated_body_ranges_sha256'],
                  'dependency body-range binding differs')
        dependency_packets.append({'body_ranges_hypothesis':ranges,'body_ranges_sha256':hashlib.sha256(ranged).hexdigest(),
            'range_status':'byte-checked static boundary hypothesis, not measured complete reachable body',
            'id':'envelope-dependency-'+rva,'kind':'characterization-required',
            'identity':config['reference']['module']+':'+config['reference']['sha256']+':rva-'+rva,
            'prefix_size':32,'prefix_sha256':hashlib.sha256(prefix).hexdigest(),
            'contract_status':'unknown','required':['exact reachable body ranges','caller argument/return and preserved state',
                'memory/global/TLS footprints','normal/failure/exception outcomes','effect dependencies','reproducible acceptance adapter']})
    return {'schema_version':1,'kind':'byte-backed-startup-preparation-packet','identity':unit['functions'][0]['id'],
        'observation_sha256':d.digest(task['observation']),'frontier_sha256':d.digest(task['frontier']),
        'range':{'start_rva':'00016ad0','stop_before_rva':'00016c00','bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()},
        'byte_checked_edges':edges,'dependency_queue':dependency_packets,
        'contract':{'status':'unfrozen-hypothesis','ABI':'unknown','initial_state':'retained measured entry, not complete ABI',
            'effects':'path/current-directory/mutex/wait hypotheses from static imports; no measured body effects',
            'early_cleanup_paths':'unknown; branches beyond linear interval require complete path closure',
            'normal_return':'unobserved','implementation_eligible':False},
        'windows_milestone':{'checkpoint':'measured entry only','body_execution':'requires separately reviewed bounded profile/effect capture',
            'adapter_gap':'Existing checkpoint debugger stops immediately on target entry; it does not record path/mutex effect boundaries or all early cleanup paths.',
            'required_evidence':['new exact target-body stop/failure profile','bounded effect capture for path, directory, mutex, wait and cleanup',
                'dependency/ABI contracts for four direct dependencies','fresh independent one-attempt setup approval'],
            'old_approval_consumed':True,'execute_permitted':False},
        'accepted_functions':0,'proof':False,'native_windows_validated':False}


def static_job(config, claim, store, directory):
    store.phase(claim['job'],'byte-checked-startup-contract-packet-preparation')
    result = prepare_static(config,claim['task'])
    d.atomic(directory/'startup-packet.json',result)
    expected = claim['task']['expected_packet_sha256']
    d.bound(directory/'startup-packet.json',expected)
    return {'state':'complete','reason':'byte-backed dependency/contract preparation complete; implementation and body execution remain blocked',
        'stage':'preparation','packet':str(directory/'startup-packet.json'),'packet_sha256':expected,
        'implementation_accepted':False,'windows_executable_milestone':False,'new_original_execution':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--approval',type=Path,required=True)
    parser.add_argument('--ownership-release',type=Path,required=True)
    args=parser.parse_args()
    install(args.plan,args.approval,args.ownership_release)

if __name__=='__main__': main()
