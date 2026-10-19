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

extern "C" unsigned int __cdecl fn_001c5ca0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_006f6588;
extern "C" undefined * g_006f6578;
extern "C" undefined * g_006f651c;
extern "C" undefined * g_006f6504;

// FUNCTION: DAO 0x005229c0
undefined4 * __fastcall fn_001229c0(undefined4 *param_1)
{
  fn_001c5ca0();
  *param_1 = (undefined4)(&g_006f6588);
  param_1[2] = (undefined4)(&g_006f6578);
  param_1[7] = (undefined4)(&g_006f651c);
  param_1[8] = (undefined4)(&g_006f6504);
  return param_1;
}

