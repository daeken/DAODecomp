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

extern "C" unsigned int __cdecl fn_0039b0b0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_0072083c;
extern "C" undefined * g_00720820;
extern "C" undefined * g_00720810;
extern "C" undefined * g_007207b4;
extern "C" undefined * g_007207a0;
extern "C" undefined * g_00720714;

// FUNCTION: DAO 0x0079b2c0
undefined4 * __fastcall fn_0039b2c0(undefined4 *param_1)
{
  fn_0039b0b0();
  *param_1 = (undefined4)(&g_0072083c);
  param_1[6] = (undefined4)(&g_00720820);
  param_1[8] = (undefined4)(&g_00720810);
  param_1[0xd] = (undefined4)(&g_007207b4);
  param_1[0xe] = (undefined4)(&g_007207a0);
  param_1[0x1c] = (undefined4)(&g_00720714);
  *(undefined2 *)(param_1 + 0x144) = 0;
  return param_1;
}

