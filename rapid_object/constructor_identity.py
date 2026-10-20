"""Recognize a deliberately narrow native C++ constructor source identifier.

MSVC x86 public __thiscall constructors of an unqualified class fn_<RVA>, taking
zero arguments or one signed int, are authored source identities. Other special members and
compiler generated names are not aliases for that class's constructor.
"""
import re
_CONSTRUCTOR = re.compile(r'^\?\?0fn_([0-9a-fA-F]{8})@@QAE@(?:XZ|H@Z)$')

def constructor_identity(name):
    if not isinstance(name, str):
        return None
    found = _CONSTRUCTOR.fullmatch(name)
    return ('fn', int(found[1], 16)) if found else None
