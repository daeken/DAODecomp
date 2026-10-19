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

extern "C" unsigned int __cdecl fn_000d2070(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_00707be0;
struct Seed_0024dc30 { undefined4 * __thiscall fn_0024dc30(undefined4 param_2); };

// FUNCTION: DAO 0x0064dc30
undefined4 * __thiscall Seed_0024dc30::fn_0024dc30(undefined4 param_2)
{
  fn_000d2070();
  ((undefined4 *)this)[1] = param_2;
  *((undefined4 *)this) = (undefined4)(&g_00707be0);
  return ((undefined4 *)this);
}

