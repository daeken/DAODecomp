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

struct Seed_0054e080 { int __thiscall fn_0054e080(int param_2); };

// FUNCTION: DAO 0x0094e080
int __thiscall Seed_0054e080::fn_0054e080(int param_2)
{
  uint uVar1;
  int *piVar2;
  
  uVar1 = 0;
  if (((unsigned int)(*(uint *)(((int)this) + 0x1c))) > 0u) {
    piVar2 = *(int **)(((int)this) + 0x18);
    do {
      if (*piVar2 == param_2) {
        return (*(int **)(((int)this) + 0x18))[uVar1 * 2 + 1];
      }
      uVar1 = uVar1 + 1;
      piVar2 = piVar2 + 2;
    } while (uVar1 < *(uint *)(((int)this) + 0x1c));
  }
  return 0;
}

