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

extern "C" unsigned int __cdecl fn_0032aa00(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0032ac30 { undefined4 __thiscall fn_0032ac30(byte param_2); };

// FUNCTION: DAO 0x0072ac30
undefined4 __thiscall Seed_0032ac30::fn_0032ac30(byte param_2)
{
  fn_0032aa00();
  if ((param_2 & 1) != 0) {
    fn_000136c0(((undefined4)this));
  }
  return ((undefined4)this);
}

