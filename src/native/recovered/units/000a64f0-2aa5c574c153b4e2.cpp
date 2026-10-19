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

extern "C" undefined4 g_0082b2c0;
extern "C" unsigned int __cdecl fn_000a6380(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x004a64f0
undefined4 __fastcall fn_000a64f0(int param_1)
{
  undefined4 *puVar1;
  int iVar2;
  
  if (*(int *)(param_1 + 0x10) == 0) {
    return g_0082b2c0;
  }
  puVar1 = (undefined4 *)fn_000a6380();
  if (*(int *)(param_1 + 0x10) != 0) {
    *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + 1;
    if ((uint)(*(int *)(param_1 + 8) * 4) <= *(uint *)(param_1 + 0xc)) {
      *(undefined4 *)(param_1 + 0xc) = 0;
    }
    iVar2 = *(int *)(param_1 + 0x10) + -1;
    *(int *)(param_1 + 0x10) = iVar2;
    if (iVar2 == 0) {
      *(undefined4 *)(param_1 + 0xc) = 0;
    }
  }
  return *puVar1;
}

