"""Run frozen whole-program replacement images on the existing composed Wine host.

FEX executes the game; corrected QEMU executes the identical Wine 8 i386 server.
This records startup observations, not native Windows or game acceptance.
"""
import argparse
import gzip
import json
import re
from pathlib import Path
import subprocess
import time
from tools import recomp, recomp_native


def freeze(output, directory):
    build_bytes=(output/'build-report.json').read_bytes();build=json.loads(build_bytes)
    if build['game_acceptance'] is not False or not all(
            build['modules'][role]['original_sections_executable'] is False for role in ('main','umbra')):
        raise ValueError('replacement must retain original instruction pages as nonexecutable data')
    prepared_bytes=(output/'prepared.json').read_bytes();prepared=json.loads(prepared_bytes)
    if recomp.digest(prepared_bytes)!=build['prepared_sha256']:
        raise ValueError('prepared inputs changed after link')
    stage=output/('frozen-'+str(time.time_ns()))
    subprocess.run(['/bin/cp','-cR',str(output/'bin_ship'),str(stage)],check=True)
    (directory/'build-report.json').write_bytes(build_bytes)
    (directory/'prepared.json').write_bytes(prepared_bytes)
    expected={'DAOrigins.exe':build['modules']['main']['output_sha256'],
              'umbra.dll':build['modules']['umbra']['output_sha256'],
              'recomp_runtime.dll':build['runtime_sha256']}
    images={};artifacts=output/'artifacts';artifacts.mkdir(exist_ok=True)
    for path in sorted(stage.iterdir()):
        if not path.is_file():continue
        data=path.read_bytes();identity=recomp.digest(data)
        if path.name in expected and identity!=expected[path.name]:
            raise ValueError('linked image changed before execution')
        if path.name in build['retained_providers'] and identity!=build['retained_providers'][path.name]['sha256']:
            raise ValueError('retained provider changed before execution')
        blob=artifacts/(identity+'.gz')
        if blob.exists():
            if recomp.digest(gzip.decompress(blob.read_bytes()))!=identity:raise ValueError('retained artifact changed')
        else:blob.write_bytes(gzip.compress(data,compresslevel=3,mtime=0))
        images[path.name]=dict(sha256=identity,compressed_blob=str(blob))
    if not set(expected)<=set(images):raise ValueError('replacement image missing')
    sources={}
    for name,identity in prepared['sources'].items():
        data=(output/'source'/name).read_bytes()
        if recomp.digest(data)!=identity:raise ValueError('linked source changed')
        blob=artifacts/(identity+'.gz')
        if not blob.exists():blob.write_bytes(gzip.compress(data,compresslevel=3,mtime=0))
        elif recomp.digest(gzip.decompress(blob.read_bytes()))!=identity:raise ValueError('source archive changed')
        sources[name]=dict(sha256=identity,compressed_blob=str(blob))
    return stage,build,images,sources


def diagnostic_environment(values):
    reserved={'WINEPREFIX','WINELOADERNOEXEC','WINELOADER','WINESERVER','WINEDEBUG','LP_NUM_THREADS','RECOMP_INSTRUCTION_BUDGET'}
    result={}
    for item in values:
        name,separator,value=item.partition('=')
        if not separator or not re.fullmatch('[A-Z_][A-Z_0-9]*',name) or name in reserved or name in result or '\0' in value:
            raise ValueError('invalid, duplicate or reserved diagnostic environment setting')
        result[name]=value
    return result


def run(output,budget,timeout,environment=()):
    diagnostics=diagnostic_environment(environment)
    directory=output/'runs'/str(time.time_ns());directory.mkdir(parents=True)
    with recomp.locked(output/'build-lock'):
        stage,build,images,sources=freeze(output,directory)
    loader='/workspace/local/tools/recomp/fex-linux/wine-loader.sh'
    server='/workspace/local/tools/recomp/fex-linux/wineserver-qemu.sh'
    env=['-e','WINEPREFIX=/home/daeken/wineprefix-fex','-e','WINELOADERNOEXEC=1',
         '-e','WINELOADER='+loader,'-e','WINESERVER='+server,'-e','WINEDEBUG=-all',
         '-e','LP_NUM_THREADS=2','-e','RECOMP_INSTRUCTION_BUDGET='+str(budget)]
    for name,value in diagnostics.items():env+=['-e',name+'='+value]
    base=['docker','exec',*env,'daodecomp-fex-host'];stop=base+[server,'-k']
    # Serialize access to this task's dedicated Wine prefix; never touch the
    # user's separate original-game/Alkyhol process or its Wine prefix.
    with recomp.locked(recomp.ROOT/'local/recomp/startup/fex-host/host-lock'):
        for label,command in [('host-components',['docker','exec','daodecomp-fex-host','sha256sum',
                '/usr/bin/FEX','/guest/usr/lib/wine/wineserver32',
                '/workspace/local/tools/recomp/qemu-i386-signal-control/out/qemu-i386-envfix']),
                ('server-version',base+[server,'--version'])]:
            result=subprocess.run(command,capture_output=True)
            (directory/(label+'.stdout')).write_bytes(result.stdout);(directory/(label+'.stderr')).write_bytes(result.stderr)
            if result.returncode:raise RuntimeError('composed host unavailable: '+label)
        previous=subprocess.run(stop,capture_output=True)
        (directory/'stop-before.stdout').write_bytes(previous.stdout);(directory/'stop-before.stderr').write_bytes(previous.stderr)
        if previous.returncode not in (0,1):raise RuntimeError('owned Wine prefix cleanup failed')
        server_argv=base+[server,'-f','-p']
        with (directory/'server.stdout').open('wb') as server_out,(directory/'server.stderr').open('wb') as server_err:
            process=subprocess.Popen(server_argv,stdout=server_out,stderr=server_err)
            try:
                time.sleep(0.5)
                if process.poll() is not None:raise RuntimeError('Wine server exited before game launch')
                argv=['docker','exec',*env,'-w','/workspace/'+str(stage.relative_to(recomp.ROOT)),
                      'daodecomp-fex-host','timeout','--kill-after=5s',str(timeout)+'s',loader,'DAOrigins.exe']
                recomp.atomic_json(directory/'launch.json',dict(argv=argv,server_argv=server_argv,stage=str(stage),
                    executed_images=images,source_archives=sources,functions=build['functions'],budget=budget,game_acceptance=False))
                started=time.time()
                with (directory/'stdout').open('wb') as stdout,(directory/'stderr').open('wb') as stderr:
                    result=subprocess.run(argv,stdout=stdout,stderr=stderr)
                elapsed=time.time()-started
            finally:
                before_stop=process.poll();cleanup=subprocess.run(stop,capture_output=True)
                (directory/'stop-after.stdout').write_bytes(cleanup.stdout);(directory/'stop-after.stderr').write_bytes(cleanup.stderr)
                try:server_exit=process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.terminate();server_exit=process.wait(timeout=10)
    events,index=recomp_native.read_native_events(directory/'stderr')
    report=dict(status='incomplete; whole-program replacement startup observation',game_acceptance=False,
        functions=build['functions'],generation_excluded=build['generation_excluded'],executed_images=images,
        frozen_stage=str(stage),source_archives=sources,argv=argv,server_argv=server_argv,
        host='macOS ARM64 -> Docker ARM64 Ubuntu24.04 -> FEX2611 game + corrected QEMU i386 Wine8 server',
        exit_code=result.returncode,timed_out=result.returncode in (124,137),elapsed_seconds=elapsed,
        events=events,native_abi_trace=index,budget=budget,diagnostic_environment=diagnostics,server_before_stop=before_stop,server_final=server_exit,
        initial_state_note='Existing owned Wine prefix; no identical initialized-state original/replacement comparison.',
        scope='Original main/Umbra execution forbidden; permanent DEP enforced before translated entry. No successful missing-code stubs.')
    report['observation']=recomp_native.native_observation(report)
    for name,item in images.items():
        if recomp.digest((stage/name).read_bytes())!=item['sha256']:raise ValueError('executed image changed during run')
    report['artifacts']={str(p):recomp.digest(p.read_bytes()) for p in directory.iterdir() if p.is_file()}
    controller=Path(__file__).read_bytes();(directory/'runner.py').write_bytes(controller)
    report['artifacts'][str(directory/'runner.py')]=recomp.digest(controller)
    recomp.atomic_json(directory/'report.json',report);recomp.atomic_json(output/'run-report.json',report)
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/bulk-native')
    parser.add_argument('--budget',type=int,default=1000000000);parser.add_argument('--timeout',type=int,default=180)
    parser.add_argument('--environment',action='append',default=[],metavar='NAME=VALUE',help='recorded host diagnostic setting; runner-owned settings cannot be overridden')
    args=parser.parse_args(argv)
    if not 0<args.budget<=2**64-1 or args.timeout<=0:parser.error('positive bounded budget and timeout required')
    report=run(args.output.absolute(),args.budget,args.timeout,args.environment)
    print(json.dumps({k:report[k] for k in ('status','functions','exit_code','elapsed_seconds','observation')},indent=2))
    return 3


if __name__=='__main__':raise SystemExit(main())
