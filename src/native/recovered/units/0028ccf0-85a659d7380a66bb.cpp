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

struct Seed_0028ccf0 { undefined4 __thiscall fn_0028ccf0(float *param_2); };

// FUNCTION: DAO 0x0068ccf0
undefined4 __thiscall Seed_0028ccf0::fn_0028ccf0(float *param_2)
{
  if ((((*(float *)(((int)this) + 0x2d0) < *param_2) && (*param_2 < *(float *)(((int)this) + 0x2e0))) &&
      (*(float *)(((int)this) + 0x2d4) < param_2[1])) && (param_2[1] < *(float *)(((int)this) + 0x2e4))) {
    return 1;
  }
  return 0;
}

