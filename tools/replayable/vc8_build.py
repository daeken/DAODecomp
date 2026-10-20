"""Selected VC8 EH flags over the existing synchronous copy/compile protocol.

No queue, acceptance, retries or VM concurrency policy lives here. The caller
holds the same shared VM lock. Uncertain outcomes remain the durable job's barrier.
"""
import json
from pathlib import Path
import shutil
import time
import uuid
from rapid_native.pipeline import vm,ps_quote,VM_ROOT
from rapid_object.build import VCVARS
from rapid.packets import PIN
from workers.deepseek_packet import atomic,sha

EH_FLAGS=['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc']

def compile_object(source,output,flags,profile):
    from replayable_transport import rendered_scripts
    if flags!=EH_FLAGS:raise ValueError('unsupported_EH_compiler_flags')
    if profile['protocol']!='prlctl-sync-copy-v1' or profile['guest_root']!=VM_ROOT or profile['vcvars']!=VCVARS:
        raise ValueError('unsupported_EH_transport_profile')
    if Path(profile['build_helper']).resolve()!=Path(__file__).resolve() or profile['build_helper_sha256']!=sha(Path(__file__).read_bytes()):
        raise ValueError('unattested_EH_profile_helper')
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False,mode=0o700)
    bridge=Path.home()/'Downloads/DAOReccmpPilotTransfer';bridge.mkdir(exist_ok=True)
    if Path(profile['host_transfer_root'])!=bridge:raise ValueError('unsupported_EH_transfer_root')
    name='coff-job-'+uuid.uuid4().hex;transfer=bridge/name;transfer.mkdir(mode=0o700)
    guest,shared,batch,script=rendered_scripts(profile,name,flags);shutil.copy2(source,transfer/'candidate.cpp')
    (transfer/'build.cmd').write_bytes(batch);(transfer/'run.ps1').write_bytes(script);started=time.time()
    try:
        result=vm('& ([scriptblock]::Create([System.IO.File]::ReadAllText('+ps_quote(shared+'\\run.ps1')+')))',profile['vm_name'],timeout=300)
        (output/'transport.stdout').write_bytes(result.stdout);(output/'transport.stderr').write_bytes(result.stderr)
        for p in transfer.iterdir():
            if p.is_file():shutil.copy2(p,output/p.name)
        receipt=dict(schema_version=1,source_sha256=sha(source.read_bytes()),module_sha256=PIN,object_sha256=sha((output/'candidate.obj').read_bytes()) if (output/'candidate.obj').exists() else None,compiler=json.loads((output/'compiler.json').read_text(encoding='utf-8-sig')) if (output/'compiler.json').exists() else None,flags=flags,linked=False,original_executed=False,vm=profile['vm_name'],vm_workspace=guest,elapsed_seconds=round(time.time()-started,3),exit_code=result.returncode)
        atomic(output/'run.json',receipt);return receipt
    finally:shutil.rmtree(transfer)
