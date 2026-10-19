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

extern "C" unsigned int __cdecl fn_002336a0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_00233730 { void __thiscall fn_00233730(undefined4 param_2); };

// FUNCTION: DAO 0x00633730
void __thiscall Seed_00233730::fn_00233730(undefined4 param_2)
{
  fn_002336a0(((undefined4)this),param_2);
  return;
}

