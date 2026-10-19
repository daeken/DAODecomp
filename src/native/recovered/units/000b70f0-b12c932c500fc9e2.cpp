// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.
typedef unsigned int pointer32;
typedef unsigned int code(...);
typedef unsigned char   undefined;
typedef unsigned char    byte;
typedef unsigned int    dword;
typedef unsigned __int64    GUID;
typedef pointer32 ImageBaseOffset32;

typedef __int64    longlong;
typedef unsigned char    uchar;
typedef unsigned int    uint;
typedef unsigned long    ulong;
typedef unsigned __int64    ulonglong;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned __int64    undefined6;
typedef unsigned __int64    undefined8;
typedef unsigned short    ushort;
typedef unsigned short    word;

extern "C" int __cdecl fn_004e58b3(int _C);

// FUNCTION: DAO 0x004b70f0
undefined4 fn_000b70f0(byte param_1)
{
  int iVar1;
  
  iVar1 = fn_004e58b3((uint)param_1);
  if (((iVar1 == 0) && (param_1 != 10)) && (param_1 != 0xd)) {
    return 0;
  }
  return 1;
}

