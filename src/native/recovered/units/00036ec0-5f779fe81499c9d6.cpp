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

struct Seed_00036ec0 { void __thiscall fn_00036ec0(undefined4 *param_2); };

// FUNCTION: DAO 0x00436ec0
void __thiscall Seed_00036ec0::fn_00036ec0(undefined4 *param_2)
{
  if (param_2 != (undefined4 *)0x0) {
    *(undefined4 *)(((int)this) + 0x48) = *param_2;
    *(undefined4 *)(((int)this) + 0x4c) = param_2[1];
    *(undefined4 *)(((int)this) + 0x50) = param_2[2];
    *(undefined4 *)(((int)this) + 0x54) = param_2[3];
  }
  return;
}

