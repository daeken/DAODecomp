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

extern "C" unsigned int __cdecl fn_0008bb70(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0048c9b0
void __fastcall fn_0008c9b0(int param_1)
{
  *(undefined1 *)(param_1 + 0xe4) = 1;
  *(undefined1 *)(param_1 + 0xe5) = 1;
  fn_0008bb70();
  return;
}

