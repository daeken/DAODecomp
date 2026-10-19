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

struct Seed_00018390 { void __thiscall fn_00018390(int param_2); };

// FUNCTION: DAO 0x00418390
void __thiscall Seed_00018390::fn_00018390(int param_2)
{
  if (*(int *)(((int)this) + 0x1c) != 0) {
    *(int *)(param_2 + 8) = *(int *)(((int)this) + 0x1c);
    *(int *)(*(int *)(((int)this) + 0x1c) + 4) = param_2;
    *(undefined4 *)(param_2 + 4) = 0;
    *(int *)(((int)this) + 0x1c) = param_2;
    return;
  }
  *(undefined4 *)(param_2 + 8) = 0;
  *(undefined4 *)(param_2 + 4) = 0;
  *(int *)(((int)this) + 0x18) = param_2;
  *(int *)(((int)this) + 0x1c) = param_2;
  return;
}

