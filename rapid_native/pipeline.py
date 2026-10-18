"""C++ source -> isolated VC8 DLL/PDB -> complete-range reccmp diagnostics."""
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid
from rapid.factory import MAIN,REPO
from rapid.packets import PIN
from workers.deepseek_packet import atomic

VM_ROOT=r'C:\Users\daeken\DAOReccmpPilot'
VM_PYTHON=VM_ROOT+r'\.venv\Scripts\python.exe'
VM_ORIGINAL=r'C:\Users\daeken\DAODecompNativeProposal\local\windows-native-proposal\DAOrigins.exe'
RECCMP_PIN='435b00e6ba65f76aee2dd793fcc7d0f5139de749'


def sha(data):return hashlib.sha256(data).hexdigest()

def ps_quote(value):return "'"+str(value).replace("'","''")+"'"

def vm(script,vm_name='Windows 11',timeout=300):
    script="$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8\n"+script
    argv=['prlctl','exec',vm_name,'--current-user','powershell.exe','-NoProfile','-EncodedCommand',base64.b64encode(script.encode('utf-16-le')).decode()]
    return subprocess.run(argv,capture_output=True,timeout=timeout)


def selection(source,original,inventory):
    import pefile
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32
    data=Path(original).read_bytes()
    if sha(data)!=PIN:raise ValueError('original_pin')
    inv_raw=Path(inventory).read_bytes();inv=json.loads(inv_raw)
    if inv['module_sha256']!=PIN:raise ValueError('inventory_pin')
    markers=[int(v,16) for v in re.findall(r'^\s*//\s*FUNCTION:\s+DAO\s+(0x[0-9a-fA-F]+)\s*$',source,re.M)]
    if not markers or len(markers)!=len(set(markers)):raise ValueError('missing_or_duplicate_annotations')
    if markers!=sorted(markers):raise ValueError('annotations_not_address_order')
    pe=pefile.PE(data=data);md=Cs(CS_ARCH_X86,CS_MODE_32);index={f['rva']:f for f in inv['functions']};functions=[]
    all_ranges=sorted((r['start_rva'],r['end_rva_inclusive'],f['rva']) for f in inv['functions'] for r in f['body_ranges'])
    for va in markers:
        rva=va-pe.OPTIONAL_HEADER.ImageBase;f=index[rva];rr=f['body_ranges']
        if len(rr)!=1 or rr[0]['start_rva']!=rva:raise ValueError('noncontiguous_inventory_boundary')
        end=rr[0]['end_rva_inclusive'];size=end-rva+1
        if any(other!=rva and start<=end and stop>=rva for start,stop,other in all_ranges):raise ValueError('overlapping_inventory_boundary')
        section=pe.get_section_by_rva(rva)
        if not section or not section.Characteristics&0x20000000:raise ValueError('nonexecutable_range')
        raw=pe.get_data(rva,size);ins=list(md.disasm(raw,va))
        if not raw or len(raw)!=size or sum(i.size for i in ins)!=size:raise ValueError('incomplete_original_bytes')
        functions.append({'rva':rva,'original_va':va,'size':size,'bytes_sha256':sha(raw),'boundary_provenance':'existing_static_inventory_hypothesis'})
    return {'schema_version':1,'module_sha256':PIN,'image_base':pe.OPTIONAL_HEADER.ImageBase,'inventory_sha256':sha(inv_raw),'functions':functions}


def compare(source,output,vcvars,vm_name='Windows 11',vm_original=VM_ORIGINAL,original=MAIN/'gamedata/bin_ship/DAOrigins.exe',inventory=MAIN/'local/analysis/functions.json',optimization='/O2'):
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False,mode=0o700)
    text=source.read_text();selected=selection(text,original,inventory)
    # Physical transfer is necessary: Parallels denies worktree/symlink shares.
    bridge=Path.home()/'Downloads/DAOReccmpPilotTransfer';bridge.mkdir(exist_ok=True)
    job='job-'+uuid.uuid4().hex;transfer=bridge/job;transfer.mkdir(mode=0o700)
    (transfer/'candidate.cpp').write_text(text);atomic(transfer/'selection.json',selected);shutil.copy2(REPO/'rapid_native/audit.py',transfer/'audit.py');shutil.copy2(REPO/'rapid_native/status_rules.py',transfer/'status_rules.py')
    original_name=Path(str(vm_original).replace('\\','/')).name
    project={'targets':{'DAO':{'filename':original_name,'source-root':'.','hash':{'sha256':PIN},'data-sources':['sizes.csv']}}}
    guest=VM_ROOT+'\\'+job
    (transfer/'reccmp-project.yml').write_text(json.dumps(project))
    (transfer/'reccmp-user.yml').write_text(json.dumps({'targets':{'DAO':{'path':str(vm_original)}}}))
    (transfer/'reccmp-build.yml').write_text(json.dumps({'project':'.','targets':{'DAO':{'path':'candidate.dll','pdb':'candidate.pdb'}}}))
    (transfer/'sizes.csv').write_text('address|type|size\n'+''.join(f"{f['original_va']:x}|function|{f['size']}\n" for f in selected['functions']))
    batch='@echo off\r\ncall "'+str(vcvars)+'"\r\nif errorlevel 1 exit /b %errorlevel%\r\ncl\r\nwhere cl\r\nwhere link\r\ncl /nologo /c '+optimization+' /Ob1 /Oy /Zi /Zl /GS- /GR- /EHsc /Focandidate.obj /Fdcompiler.pdb candidate.cpp\r\nif errorlevel 1 exit /b %errorlevel%\r\nlink /NOLOGO /NODEFAULTLIB /DLL /NOENTRY /DEBUG /OPT:NOREF /OPT:NOICF /MACHINE:X86 /OUT:candidate.dll /PDB:candidate.pdb candidate.obj\r\nexit /b %errorlevel%\r\n'
    (transfer/'build.cmd').write_bytes(batch.encode('ascii'))
    shared='\\\\Mac\\Home\\Downloads\\DAOReccmpPilotTransfer\\'+job;started=time.time()
    script=f'''$guest={ps_quote(guest)}
Copy-Item -Recurse -Force {ps_quote(shared)} $guest
Set-Location $guest
$compilerRoot=Split-Path {ps_quote(vcvars)}
@('cl.exe','link.exe') | ForEach-Object {{ $p=Join-Path $compilerRoot ('bin\\'+$_); $i=Get-Item $p; [PSCustomObject]@{{path=$p;sha256=(Get-FileHash -Algorithm SHA256 $p).Hash.ToLower();file_version=$i.VersionInfo.FileVersion}} }} | ConvertTo-Json | Set-Content -Encoding UTF8 compiler.json
$expected={ps_quote(PIN)}
if ((Get-FileHash -Algorithm SHA256 {ps_quote(vm_original)}).Hash.ToLower() -ne $expected) {{throw 'original_pin'}}
& cmd.exe /d /c 'build.cmd > build.log 2>&1'
$buildExit=$LASTEXITCODE
$buildExit | Set-Content build-exit.txt
if ($buildExit -eq 0) {{
  & cmd.exe /d /c {ps_quote(chr(34)+VM_PYTHON+chr(34)+' audit.py . > compare.log 2>&1')}
  $compareExit=$LASTEXITCODE
  $compareExit | Set-Content compare-exit.txt
}}
Copy-Item -Recurse -Force ($guest+'\\*') {ps_quote(shared)}
if ($buildExit -ne 0) {{exit $buildExit}}
if ($compareExit -ne 0) {{exit $compareExit}}
'''
    (output/'vm-invocation.ps1').write_text(script)
    (transfer/'run.ps1').write_text(script)
    launcher='& ([scriptblock]::Create([System.IO.File]::ReadAllText('+ps_quote(shared+'\\run.ps1')+')))';
    try:
        run=vm(launcher,vm_name,timeout=300)
        (output/'transport.stdout').write_bytes(run.stdout);(output/'transport.stderr').write_bytes(run.stderr)
        for file in transfer.iterdir():
            if file.is_file():shutil.copy2(file,output/file.name)
        receipt={'schema_version':1,'source_sha256':sha(source.read_bytes()),'module_sha256':PIN,'reccmp_commit':RECCMP_PIN,'vcvars':str(vcvars),'vm':vm_name,'vm_workspace':guest,'optimization':optimization,'elapsed_seconds':round(time.time()-started,3),'exit_code':run.returncode,'original_compiler_patch':'unknown; VC8 SP1 is a hypothesis','original_executed':False}
        atomic(output/'run.json',receipt)
        return json.loads((output/'summary.json').read_text()) if (output/'summary.json').exists() else receipt
    finally:
        # Only this job's temporary public/candidate transfer, never original data.
        shutil.rmtree(transfer)
