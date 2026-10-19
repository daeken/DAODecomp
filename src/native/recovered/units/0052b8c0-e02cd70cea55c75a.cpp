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

extern "C" unsigned int __cdecl fn_00520760(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0052b8c0 { void __thiscall fn_0052b8c0(char param_2); };

// FUNCTION: DAO 0x0092b8c0
void __thiscall Seed_0052b8c0::fn_0052b8c0(char param_2)
{
  ushort *puVar1;
  int iVar2;
  
  iVar2 = *(int *)(*(int *)(((int)this) + 0x9c) + 0x11c);
  if (param_2 != '\0') {
    iVar2 = fn_00520760();
    *(ushort *)(iVar2 + 100) = *(ushort *)(iVar2 + 100) | 2;
    return;
  }
  if (iVar2 != 0) {
    puVar1 = (ushort *)(iVar2 + 100);
    *puVar1 = *puVar1 & 0xfffd;
  }
  return;
}

