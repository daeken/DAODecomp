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

extern "C" unsigned int __cdecl fn_000e99e0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00a2a5b0
void __fastcall fn_0062a5b0(int param_1)
{
  int iVar1;
  
  iVar1 = 3;
  do {
    fn_000e99e0(param_1);
    param_1 = param_1 + 4;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  return;
}

