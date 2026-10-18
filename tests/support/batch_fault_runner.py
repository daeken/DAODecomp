"""Real subprocess fixtures for the fresh-child batch runtime tests."""
import os
from pathlib import Path
import signal
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.daodecomp.batch import serve
from tools.daodecomp.harness import canonical, digest, parse_json, validate_cases

MODE=sys.argv[1]
PATH=Path(sys.argv[2]) if len(sys.argv)>2 else None
CONTRACT={'schema_version':1,'function_id':'test:batch','kind':'synthetic','inputs':{'value':'u32'},'return_type':'u32','memory':{'bytes':4},'calls':[],'preconditions':'Test-only small integer'}
COUNTER=0

def validate(request):
    if type(request) is not dict or set(request)!={'schema_version','function_id','case'} or type(request['schema_version']) is not int or request['schema_version']!=1 or request['function_id']!=CONTRACT['function_id']:
        raise ValueError('bad fixture request')
    validate_cases([request['case']],CONTRACT)

def observation(request):
    global COUNTER
    COUNTER+=1
    value=request['case']['inputs']['value']
    if MODE=='stateful': value=COUNTER
    if MODE=='pid': value=os.getpid()
    if MODE=='mismatch': value=(value+1)&0xffffffff
    return {'schema_version':1,'case_id':request['case']['id'],'termination':'return','return':value,'memory':{'bytes':'00000000'},'calls':[]}

def handler(request):
    if MODE=='raise': raise RuntimeError('actual child exception')
    if MODE=='crash': os.kill(os.getpid(),signal.SIGKILL)
    if MODE=='hang': time.sleep(30)
    if MODE=='missing': os._exit(0)
    if MODE=='stdout-cap': os.write(1,b'x'*131072)
    if MODE=='stderr-cap': os.write(2,b'x'*8192)
    if MODE=='duplicate-json': os.write(1,canonical(observation(request)).encode())
    if MODE=='artifact': PATH.write_text('changed')
    if MODE in ('descendant-success','descendant-hang','worker-crash'):
        child=os.fork()
        if child==0:
            PATH.write_text(str(os.getpid()))
            time.sleep(30);os._exit(0)
        # Ensure the sentinel was published before the leader finishes/crashes.
        deadline=time.monotonic()+1
        while not PATH.exists():
            if time.monotonic()>deadline: raise RuntimeError('descendant did not start')
            time.sleep(.001)
        if MODE=='descendant-hang': time.sleep(30)
        if MODE=='worker-crash':
            os.kill(os.getppid(),signal.SIGKILL); time.sleep(30)
    result=observation(request)
    if MODE=='wrong-id': result['case_id']='foreign'
    if MODE=='bool-return': result['return']=True
    if MODE=='memory-corrupt': result['memory']['bytes']='01000000'
    return result

if MODE.startswith('frame-'):
    frames=[parse_json(line) for line in sys.stdin]
    responses=[]
    for frame in frames:
        results=[{'request_sha256':digest(r),'run':{'observation':observation(r)}} for r in frame['requests']]
        response={'schema_version':1,'batch_id':frame['batch_id'],'results':results,'child_processes':len(results)}
        if MODE=='frame-reorder': response['results'].reverse()
        if MODE=='frame-duplicate' and len(results)>1: response['results'][1]=response['results'][0]
        if MODE=='frame-wrong-batch': response['batch_id']+=1
        if MODE=='frame-count': response['results']=response['results'][:-1]
        if MODE=='frame-process-count': response['child_processes']=0
        responses.append(response)
    if MODE=='frame-missing': responses=[]
    if MODE=='frame-extra': responses+=responses
    if MODE=='frame-output-cap': print('x'*262144)
    else:
        for response in responses: print(canonical(response))
else:
    serve(handler,validate,timeout=float(os.environ.get('DAO_TEST_TIMEOUT','.15')))
