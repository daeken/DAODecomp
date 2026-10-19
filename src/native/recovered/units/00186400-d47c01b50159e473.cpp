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

struct Seed_00186400 { void __thiscall fn_00186400(float param_2); };

// FUNCTION: DAO 0x00586400
void __thiscall Seed_00186400::fn_00186400(float param_2)
{
  *(float *)(((int)this) + 0x18) = param_2;
  *(float *)(((int)this) + 0x60) = param_2;
  if (*(char *)(((int)this) + 0x52) != '\0') {
    *(float *)(((int)this) + 0x60) = param_2 * *(float *)(((int)this) + 0x58);
    return;
  }
  return;
}

