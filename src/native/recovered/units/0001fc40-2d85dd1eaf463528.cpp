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

extern "C" unsigned int __cdecl fn_000441a0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0001fc40 { int __thiscall fn_0001fc40(undefined4 param_2); };

// FUNCTION: DAO 0x0041fc40
int __thiscall Seed_0001fc40::fn_0001fc40(undefined4 param_2)
{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(((int)this) + 0x30);
  if (iVar2 == 0) {
    iVar2 = fn_000441a0(*(undefined4 *)(((int)this) + 0xc),param_2);
    if (iVar2 != 0) {
      return iVar2;
    }
  }
  else {
    do {
      iVar1 = *(int *)(iVar2 + 8);
      iVar2 = fn_000441a0(iVar2 + 0xc,param_2);
      if (iVar2 != 0) {
        return iVar2;
      }
      iVar2 = iVar1;
    } while (iVar1 != 0);
  }
  return 0;
}

