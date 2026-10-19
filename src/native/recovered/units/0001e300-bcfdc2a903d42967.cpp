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

struct Seed_0001e300 { void __thiscall fn_0001e300(int param_2); };

// FUNCTION: DAO 0x0041e300
void __thiscall Seed_0001e300::fn_0001e300(int param_2)
{
  int iVar1;
  int *piVar2;
  
  iVar1 = 0;
  piVar2 = (int *)(((int)this) + 8);
  do {
    if (*piVar2 == param_2) {
      *(undefined4 *)(((int)this) + 8 + iVar1 * 4) = 0;
      return;
    }
    iVar1 = iVar1 + 1;
    piVar2 = piVar2 + 1;
  } while (iVar1 < 0x10);
  return;
}

