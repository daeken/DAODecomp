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

extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00830240
void __fastcall fn_00430240(int param_1)
{
  if (*(undefined4 **)(param_1 + 8) != (undefined4 *)0x0) {
    fn_000136c0(**(undefined4 **)(param_1 + 8));
    fn_000136c0(*(undefined4 *)(*(int *)(param_1 + 8) + 0x14));
    fn_000136c0(*(undefined4 *)(*(int *)(param_1 + 8) + 0x18));
    fn_000136c0(*(undefined4 *)(*(int *)(param_1 + 8) + 0x24));
    fn_000136c0(*(undefined4 *)(*(int *)(param_1 + 8) + 0x28));
    fn_000136c0(*(undefined4 *)(*(int *)(param_1 + 8) + 0x34));
    fn_000136c0(*(undefined4 *)(param_1 + 8));
    *(undefined4 *)(param_1 + 8) = 0;
  }
  return;
}

