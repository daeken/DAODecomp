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

extern "C" unsigned int __cdecl fn_004630a0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x008638b0
void fn_004638b0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)
{
  int iVar1;
  
  iVar1 = fn_004630a0(param_1,param_2,param_3,param_4);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 0x86) = 0x17;
  }
  return;
}

