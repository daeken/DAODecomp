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

extern "C" int __cdecl fn_004e55d7(int _C);
struct Seed_00629f90 { undefined4 __thiscall fn_00629f90(int param_2); };

// FUNCTION: DAO 0x00a29f90
undefined4 __thiscall Seed_00629f90::fn_00629f90(int param_2)
{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = fn_004e55d7((int)*(char *)(uVar3 + param_2));
    iVar2 = fn_004e55d7((uint)*(byte *)(((int)this) + 0x21 + uVar3));
    if (iVar1 != iVar2) {
      return 1;
    }
  } while ((iVar1 != 0) && (uVar3 = uVar3 + 1, uVar3 < 0x20));
  return 0;
}

