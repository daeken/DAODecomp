"""Derive native C++ from complete retained paid responses, without new requests."""
import fcntl
import json
from pathlib import Path
import time
from workers import deepseek_packet as provider
from rapid.packets import PIN
from .response import retained_response
from .queue import native_store,attempt_numbers,evaluate,best_functions,retained_evaluations,progress_decision,quality,ingest,ROOT,VCVARS


def recover(root=ROOT,receipt=None,vcvars=VCVARS):
    root=Path(root);store=native_store(root);lock=(root/'owner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    report={'schema_version':1,'action':'source_only_retained_response_recovery','at':time.time(),'provider_requests':0,'records':[]}
    for batch, in store.db.execute("SELECT id FROM batches WHERE state='error'").fetchall():
        folder=root/'batches'/batch;numbers=attempt_numbers(folder)
        if not numbers:continue
        attempt=numbers[-1];paid=folder/f'attempt-{attempt}';record={'batch':batch,'attempt':attempt,'provider_requests':0}
        try:
            historical=(paid/'result.json').read_bytes();metrics=provider.strict_json(historical)
            if metrics.get('http_status')!=200 or metrics.get('finish_reason')!='stop' or metrics.get('outcome')!='invalid_response' or 'charged_nanodollars' not in metrics:raise ValueError('not_known_complete_paid_response')
            packet_raw=(paid/'packet.json').read_bytes();packet=provider.strict_json(packet_raw)
            if packet.get('module_sha256')!=PIN or provider.sha(packet_raw)!=metrics['packet_sha256'] or provider.sha((paid/'request.json').read_bytes())!=metrics['request_sha256']:raise ValueError('historical_request_binding')
            raw=(paid/'raw-response.json').read_bytes();response,envelope=retained_response(raw,[f['original_va'] for f in packet['functions']])
            if provider.normalized_usage(envelope.get('usage'))!=metrics.get('usage'):raise ValueError('historical_usage_binding')
            source=response['source'].encode();candidate=paid/'candidate.cpp'
            if candidate.exists() and candidate.read_bytes()!=source:raise ValueError('retained_source_collision')
            record.update(outcome='source_recovered',historical_provider_result_sha256=provider.sha(historical),raw_response_sha256=provider.sha(raw),source_sha256=provider.sha(source),source_marker_domain=[f['original_va'] for f in packet['functions']])
            provider.atomic(paid/'parse-recovery.json',record);provider.atomic(paid/'native-response.json',response)
            if not candidate.exists():candidate.write_bytes(source)
            previous_raw=(folder/'result.json').read_bytes();previous=provider.strict_json(previous_raw)
            provider.atomic(paid/'batch-before-parse-recovery.json',previous)
            observed,error=evaluate(root,batch,attempt,vcvars)
            original=provider.strict_json((folder/'packet.json').read_bytes());requested={f['rva'] for f in original['functions']}
            best=best_functions(retained_evaluations(folder,attempt,requested))
            if observed and {f['rva'] for f in observed[2]['functions']}!={f['rva'] for f in packet['functions']}:raise ValueError('recovery_comparison_domain')
            decision=progress_decision(attempt,best,len(requested),previous,6,3,bool(error and error['transport_failure']))
            result={'schema_version':1,'packet_sha256':batch,'final_record':True,'outcome':'success','functions':best,'attempts':attempt,'matched':quality(best)[0],'requested':len(requested),'error':error,'parse_recovery':str(paid/'parse-recovery.json'),**decision}
            history=folder/'history';history.mkdir(exist_ok=True);provider.atomic(history/f'attempt-{attempt}-parse-recovery.json',result);provider.atomic(folder/'result.json',result)
            ingest(store,batch,best);store.finish(batch,'pending' if decision['needs_repair'] else 'complete','repair_pending' if decision['needs_repair'] else None)
            if (paid/'result.json').read_bytes()!=historical:raise ValueError('historical_provider_record_changed')
            record.update(outcome='compiled_recovered_source',matched=result['matched'],requested=result['requested'],needs_repair=result['needs_repair'],compiler_error=error)
        except Exception as exc:record.update(outcome='left_recorded',reason=str(exc) if type(exc) is ValueError else type(exc).__name__)
        report['records'].append(record)
        # Derived record only: historical provider outcome, usage and cost stay immutable.
        if record.get('source_sha256'):provider.atomic(paid/'parse-recovery.json',record)
    target=Path(receipt) if receipt else root/f'parse-recovery-{int(time.time())}.json';provider.atomic(target,report)
    fcntl.flock(lock,fcntl.LOCK_UN);lock.close();return report
