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

struct Seed_000213e0 { void __thiscall fn_000213e0(undefined4 param_2,undefined4 param_3); };

// FUNCTION: DAO 0x004213e0
void __thiscall Seed_000213e0::fn_000213e0(undefined4 param_2,undefined4 param_3)
{
  if ((code *)*((undefined4 *)this) != (code *)0x0) {
    (*(code *)*((undefined4 *)this))(((undefined4 *)this),param_2,param_3);
    return;
  }
  if ((code *)((undefined4 *)this)[2] != (code *)0x0) {
    (*(code *)((undefined4 *)this)[2])(param_2,param_3);
  }
  return;
}

