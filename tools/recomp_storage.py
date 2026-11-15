"""Share immutable generated payloads through independent APFS clones."""
import ctypes
import os
from pathlib import Path
import sys
from tools import recomp


def content_index(cache):
    if sys.platform!='darwin':return None
    result={}
    for directory in cache.iterdir():
        marker=directory/'complete.json'
        if not directory.is_dir() or not marker.is_file():continue
        value=recomp.load(marker)
        if value.get('status')!='generated_only':continue
        if set(value['files'])!={'function.cpp','function.json.gz'}:raise ValueError('invalid completed generated payload set')
        for name,identity in value['files'].items():result.setdefault(identity,directory/name)
    return result


def share_payload(source,target,identity):
    if recomp.digest(source.read_bytes())!=identity or recomp.digest(target.read_bytes())!=identity:
        raise ValueError('generated cache bytes changed before sharing')
    temporary=target.with_name('.share-'+str(os.getpid()))
    if temporary.exists():raise ValueError('unexpected cache sharing temporary')
    clone=ctypes.CDLL(None,use_errno=True).clonefile
    clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];clone.restype=ctypes.c_int
    try:
        if clone(os.fsencode(source),os.fsencode(temporary),0):return False
        if recomp.digest(temporary.read_bytes())!=identity or temporary.stat().st_ino==source.stat().st_ino:
            raise ValueError('independent cache clone changed')
        os.replace(temporary,target)
        return True
    finally:temporary.unlink(missing_ok=True)


def share_completed(cache,items,index):
    if index is None:return 0
    count=0
    for item in items:
        directory=cache/item['key'];marker=directory/'complete.json'
        if not marker.exists():continue # An interrupted attempt stays unknown.
        value=recomp.load(marker)
        if value['status']!='generated_only':continue
        for name,identity in value['files'].items():
            if name not in ('function.cpp','function.json.gz'):raise ValueError('invalid cache payload name')
            target=directory/name;source=index.setdefault(identity,target)
            if source!=target:count+=int(share_payload(source,target,identity))
    return count
