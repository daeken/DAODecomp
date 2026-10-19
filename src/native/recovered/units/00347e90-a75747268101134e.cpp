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

struct Seed_00347e90 { undefined1 __thiscall fn_00347e90(byte param_2); };

// FUNCTION: DAO 0x00747e90
undefined1 __thiscall Seed_00347e90::fn_00347e90(byte param_2)
{
  if (param_2 < 6) {
    return *(undefined1 *)(param_2 + 0x1a8 + ((int)this));
  }
  return 0xff;
}

