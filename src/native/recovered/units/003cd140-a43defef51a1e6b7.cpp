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

struct Seed_003cd140 { void __thiscall fn_003cd140(undefined4 param_2); };

// FUNCTION: DAO 0x007cd140
void __thiscall Seed_003cd140::fn_003cd140(undefined4 param_2)
{
  *(undefined4 *)(((int)this) + 0x1c0) = param_2;
  *(undefined1 *)(((int)this) + 0x1b9) = 1;
  return;
}

