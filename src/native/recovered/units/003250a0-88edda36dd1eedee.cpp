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

extern "C" undefined * g_00718210;
extern "C" undefined * g_00718200;
extern "C" undefined * g_007181a4;
extern "C" undefined * g_00718190;
extern "C" unsigned int __cdecl fn_006559e0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_003250a0 { undefined4 * __thiscall fn_003250a0(byte param_2); };

// FUNCTION: DAO 0x007250a0
undefined4 * __thiscall Seed_003250a0::fn_003250a0(byte param_2)
{
  *((undefined4 *)this) = (undefined4)(&g_00718210);
  ((undefined4 *)this)[2] = (undefined4)(&g_00718200);
  ((undefined4 *)this)[7] = (undefined4)(&g_007181a4);
  ((undefined4 *)this)[8] = (undefined4)(&g_00718190);
  fn_006559e0();
  if ((param_2 & 1) != 0) {
    fn_000136c0(((undefined4 *)this));
  }
  return ((undefined4 *)this);
}

