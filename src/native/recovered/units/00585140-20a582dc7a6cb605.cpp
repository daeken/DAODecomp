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

struct Seed_00585140 { int __thiscall fn_00585140(int *param_2); };

// FUNCTION: DAO 0x00985140
int __thiscall Seed_00585140::fn_00585140(int *param_2)
{
  uint uVar1;
  
  if (*(int *)(((int)this) + 0x18) != 0) {
    uVar1 = *(uint *)(*(int *)(((int)this) + 0x18) + 4);
    if (*(uint *)(((int)this) + 0x1c) < uVar1) {
      if (param_2 != (int *)0x0) {
        *param_2 = uVar1 - *(uint *)(((int)this) + 0x1c);
      }
      return **(int **)(((int)this) + 0x18) + *(int *)(((int)this) + 0x1c) * 2;
    }
  }
  *param_2 = 0;
  return 0;
}

