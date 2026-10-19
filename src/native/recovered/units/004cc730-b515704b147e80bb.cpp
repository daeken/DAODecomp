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

extern "C" unsigned int __cdecl fn_004d7f30(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined g_006e5538;
struct Seed_004cc730 { void __thiscall fn_004cc730(undefined4 param_2,undefined4 param_3); };

// FUNCTION: DAO 0x008cc730
void __thiscall Seed_004cc730::fn_004cc730(undefined4 param_2,undefined4 param_3)
{
  undefined4 uVar1;
  
  if ((*(int *)(((int)this) + 0x14) != 0) && (*(int *)(((int)this) + 0x20) == 0)) {
    uVar1 = fn_004d7f30(param_3,*(int *)(((int)this) + 0x14),&g_006e5538,0);
    *(undefined4 *)(((int)this) + 0x20) = uVar1;
  }
  return;
}

