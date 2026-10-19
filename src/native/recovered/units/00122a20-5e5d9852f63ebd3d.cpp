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

extern "C" undefined * g_006f6588;
extern "C" undefined * g_006f6578;
extern "C" undefined * g_006f651c;
extern "C" undefined * g_006f6504;
extern "C" unsigned int __cdecl fn_001c5b30(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00522a20
void __fastcall fn_00122a20(undefined4 *param_1)
{
  *param_1 = (undefined4)(&g_006f6588);
  param_1[2] = (undefined4)(&g_006f6578);
  param_1[7] = (undefined4)(&g_006f651c);
  param_1[8] = (undefined4)(&g_006f6504);
  fn_001c5b30();
  return;
}

