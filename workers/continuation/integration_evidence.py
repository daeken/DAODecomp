"""Hash-bound integration materials. No inference, execution or acceptance."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def bound(path, expected):
    path = Path(path).absolute()
    if path.resolve() != path or not path.is_file() or sha(path) != expected:
        raise ValueError('integration evidence binding differs: ' + str(path))
    return path


def imported(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def assemble(config, plan, accepted):
    """Resolve source and validate existing records against their actual producer.

    Historical checkpoint rows support preservation review only. A fresh complete
    checkpoint remains the publication gate. Source/contract acceptance is never
    inferred here.
    """
    root = Path(config['root'])
    pair = Path(accepted['pair'])
    package = read(bound(pair/'accepted/package.json', accepted['package_sha256']))
    bound(pair/'accepted/candidate.cpp', package['source_sha256'])
    status = read(pair/'status.json')
    source_review = read(pair/'review-response.json')
    if not status.get('accepted') or source_review.get('decision') != 'approve':
        raise ValueError('deterministic and independent source acceptance required')
    if sha(pair/'review-response.json') != package['review_sha256']:
        raise ValueError('source approval differs from accepted package')
    effective = copy.deepcopy(plan)
    candidate = effective['files'][package['candidate_target']]
    if candidate['source'] != 'accepted-candidate' or candidate['sha256'] not in (None, package['source_sha256']):
        raise ValueError('candidate plan binding differs')
    candidate['sha256'] = package['source_sha256']
    approval_path = bound(plan['review'], plan['review_sha256'])
    approval = read(approval_path)
    if approval.get('decision') != 'approve' or any(approval.get('reviewed_artifacts_sha256', {}).get(n) != h for n,h in plan['support_review_artifacts'].items()):
        raise ValueError('exact support promotion approval required')
    # These are trusted existing consumers, not an alternative acceptance policy.
    consumers = {}
    for name, expected in config['publication_code'].items():
        source = bound(root/name, expected)
        consumers[name] = {'path':str(source), 'sha256':expected, 'content':source.read_text()}
    cache = imported(root/'tools/incremental_checkpoint.py', '_integration_checkpoint_consumer')
    progress = imported(root/'tools/update_progress.py', '_integration_progress_consumer')
    source = cache.source_manifest(root)
    registry_sha = sha(root/'analysis/functions.json')
    expected = {**source, 'analysis/functions.json':registry_sha}
    inventory = progress.checkpoint_inventory(read(root/'analysis/functions.json'))
    checkpoints = []
    for name, expected_raw in plan.get('archive_records', {}).items():
        record_path = bound(root/name, expected_raw)
        record = read(record_path)
        unsigned = dict(record); attestation = unsigned.pop('attestation_sha256',None)
        if attestation != cache.digest(unsigned) or not record.get('complete_checkpoint') or not record.get('fresh_clean_build') or record.get('proof') is not False:
            raise ValueError('existing checkpoint attestation invalid')
        rows = record['records']
        actual = {(r['function_id'],r['negative_control']) for r in rows}
        if len(actual) != len(rows) or actual != inventory:
            raise ValueError('existing checkpoint inventory differs')
        if any(r['artifacts_sha256'] != expected or not r['artifacts_unchanged'] or r['provenance_kind'] != 'fresh_clean_build_and_exact_execution_inputs' or r['repeats_per_side'] < 2 for r in rows):
            raise ValueError('existing checkpoint current artifact binding differs')
        producer_name = 'reports/'+Path(name).stem+'/reuse-attestation.json'
        producer_path = root/producer_name
        producer = read(producer_path)
        if producer.get('status') != 'passed' or not producer.get('complete_checkpoint') or not producer.get('usable_for_progress') or producer.get('source') != source or producer.get('registry_sha256') != registry_sha:
            raise ValueError('existing checkpoint producer differs')
        projected = cache.publication_document(producer)
        if projected['records'] != rows or projected['build_attestation'] != record['build_attestation']:
            raise ValueError('checkpoint differs from producer projection')
        summaries = []
        for row in rows:
            counts = row['case_counts']
            valid = (row['status']=='failed' and counts.get('mismatch',0)>0 and set(counts)<={'mismatch','corpus_pass'}) if row['negative_control'] else (row['status']=='corpus_pass' and set(counts)=={'corpus_pass'} and counts['corpus_pass']>0)
            if not valid: raise ValueError('existing checkpoint case outcome invalid')
            summaries.append({k:row[k] for k in ('function_id','negative_control','status','case_counts','repeats_per_side','current_identity_sha256','report_sha256')})
        checkpoints.append({'path':str(record_path),'raw_sha256':expected_raw,'attestation_sha256':attestation,'producer_path':str(producer_path),'producer_raw_sha256':sha(producer_path),'producer_projection_records_and_build_match':True,'current_artifacts_sha256':expected,'records':summaries,'positive_reports':sum(not r['negative_control'] for r in rows),'negative_reports':sum(r['negative_control'] for r in rows),'historical_execution_not_rerun':True,'fresh_full_checkpoint_still_required':True})
    return {'effective_plan':effective,'package':package,'package_raw_sha256':accepted['package_sha256'],'source_review':{'path':str(pair/'review-response.json'),'sha256':sha(pair/'review-response.json'),'content':source_review},'exact_promotion_approval':{'path':str(approval_path),'sha256':sha(approval_path),'content':approval},'existing_checkpoints':checkpoints,'trusted_publication_consumers':consumers,'controller_reviewed_overrides':config.get('controller_reviewed_overrides',{}),'proof':False,'native_windows_validated':False}
