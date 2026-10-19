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

extern "C" unsigned int __cdecl fn_0011f0d0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000dc000 { int __thiscall fn_000dc000(undefined4 param_2); };

// FUNCTION: DAO 0x004dc000
int __thiscall Seed_000dc000::fn_000dc000(undefined4 param_2)
{
  int iVar1;
  
  iVar1 = fn_0011f0d0();
  *(int *)(((int)this) + 4) = iVar1;
  *(undefined1 *)(iVar1 + 0x15) = 1;
  *(int *)(*(int *)(((int)this) + 4) + 4) = *(int *)(((int)this) + 4);
  *(undefined4 *)*(undefined4 *)(((int)this) + 4) = *(undefined4 *)(((int)this) + 4);
  *(int *)(*(int *)(((int)this) + 4) + 8) = *(int *)(((int)this) + 4);
  *(undefined4 *)(((int)this) + 0x10) = param_2;
  *(undefined4 *)(((int)this) + 8) = 0;
  return ((int)this);
}

