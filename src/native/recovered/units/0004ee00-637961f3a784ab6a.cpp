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

extern "C" unsigned int __cdecl fn_0004f0b0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0044ee00
void fn_0004ee00(int *param_1,undefined4 param_2,undefined4 param_3)
{
  if (*param_1 != 0) {
    fn_0004f0b0(param_1 + 2,param_2,param_3);
    param_1[1] = 1;
  }
  return;
}

