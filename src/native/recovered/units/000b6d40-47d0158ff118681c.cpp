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

extern "C" undefined * g_006eece4;
extern "C" unsigned int __cdecl fn_000b5c40(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000b6d40 { undefined4 * __thiscall fn_000b6d40(byte param_2); };

// FUNCTION: DAO 0x004b6d40
undefined4 * __thiscall Seed_000b6d40::fn_000b6d40(byte param_2)
{
  *((undefined4 *)this) = (undefined4)(&g_006eece4);
  fn_000b5c40();
  if ((param_2 & 1) != 0) {
    fn_000136c0(((undefined4 *)this));
  }
  return ((undefined4 *)this);
}

