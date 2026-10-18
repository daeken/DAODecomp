"""Historical x86 /c build, with no link or dependency stubs."""
import json
from pathlib import Path
import re
import shutil
import time
import uuid
from rapid_native.pipeline import vm,ps_quote,VM_ROOT
from workers.deepseek_packet import atomic,sha
from rapid.packets import PIN

VCVARS=r'C:\Users\daeken\tools\VC8-SP1\vcvars.cmd'


def compile_object(source,output,vcvars=VCVARS,vm_name='Windows 11'):
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False,mode=0o700)
    bridge=Path.home()/'Downloads/DAOReccmpPilotTransfer';bridge.mkdir(exist_ok=True)
    job='coff-job-'+uuid.uuid4().hex;transfer=bridge/job;transfer.mkdir(mode=0o700);shutil.copy2(source,transfer/'candidate.cpp')
    batch='@echo off\r\ncall "'+str(vcvars)+'"\r\nif errorlevel 1 exit /b %errorlevel%\r\ncl\r\nwhere cl\r\ncl /nologo /c /O2 /Ob1 /Oy /Gy /Z7 /Zl /GS- /GR- /EHsc /FAs /Facandidate.asm /Focandidate.obj candidate.cpp\r\nexit /b %errorlevel%\r\n'
    (transfer/'build.cmd').write_bytes(batch.encode('ascii'));guest=VM_ROOT+'\\'+job;shared='\\\\Mac\\Home\\Downloads\\DAOReccmpPilotTransfer\\'+job
    script=f'''$guest={ps_quote(guest)}
Copy-Item -Recurse -Force {ps_quote(shared)} $guest
Set-Location $guest
$p=Join-Path (Split-Path {ps_quote(vcvars)}) 'bin\\cl.exe'
$i=Get-Item $p
[PSCustomObject]@{{path=$p;sha256=(Get-FileHash -Algorithm SHA256 $p).Hash.ToLower();file_version=$i.VersionInfo.FileVersion}} | ConvertTo-Json | Set-Content -Encoding UTF8 compiler.json
& cmd.exe /d /c 'build.cmd > build.log 2>&1'
$buildExit=$LASTEXITCODE
$buildExit | Set-Content -Encoding ASCII build-exit.txt
Copy-Item -Force ($guest+'\\*') {ps_quote(shared)}
exit $buildExit
'''
    (transfer/'run.ps1').write_text(script);started=time.time()
    try:
        result=vm('& ([scriptblock]::Create([System.IO.File]::ReadAllText('+ps_quote(shared+'\\run.ps1')+')))',vm_name,timeout=300)
        (output/'transport.stdout').write_bytes(result.stdout);(output/'transport.stderr').write_bytes(result.stderr)
        for file in transfer.iterdir():
            if file.is_file():shutil.copy2(file,output/file.name)
        receipt={'schema_version':1,'source_sha256':sha(source.read_bytes()),'module_sha256':PIN,'object_sha256':sha((output/'candidate.obj').read_bytes()) if (output/'candidate.obj').exists() else None,'compiler':json.loads((output/'compiler.json').read_text(encoding='utf-8-sig')) if (output/'compiler.json').exists() else None,'flags':['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS-','/GR-','/EHsc'],'linked':False,'original_executed':False,'vm':vm_name,'vm_workspace':guest,'elapsed_seconds':round(time.time()-started,3),'exit_code':result.returncode}
        atomic(output/'run.json',receipt);return receipt
    finally:shutil.rmtree(transfer)


def symbol_bindings(object_path,requested,registry):
    from .coff import Coff
    obj=Coff(Path(object_path).read_bytes());addresses={};defined={}
    for symbol in obj.symbols.values():
        found=re.search(r'(?:^|[?_])(fn|g)_([0-9a-fA-F]{8})(?=@|$)',symbol.name)
        if found is None:continue
        name=found[1]+'_'+found[2].lower();record=registry.get(name)
        if record is None:continue
        address=record['original_va'] if type(record) is dict else record
        addresses[symbol.name]=address
        rva=int(found[2],16)
        if found[1]=='fn' and rva in requested and symbol.section>0:defined.setdefault(rva,[]).append(symbol.name)
    for rva,names in defined.items():
        if len(names)==1:requested[rva]['symbol']=names[0]
    return addresses


def build_and_compare(source,output,requested,registry,vcvars=VCVARS):
    from .compare import compare_object
    output=Path(output);receipt=compile_object(source,output,vcvars)
    if receipt['exit_code'] or not (output/'candidate.obj').exists():return {'schema_version':1,'build':receipt,'functions':[],'error':'object_compile_or_transport_failure'}
    symbols=symbol_bindings(output/'candidate.obj',requested,registry)
    atomic(output/'identities.json',{'requested':requested,'symbols':symbols,'module_sha256':PIN})
    from rapid.factory import MAIN
    summary=compare_object(MAIN/'gamedata/bin_ship/DAOrigins.exe',output/'candidate.obj',requested,symbols,receipt['source_sha256'],receipt['compiler'],module_sha256=PIN)
    summary['build']=receipt;atomic(output/'summary.json',summary);return summary
