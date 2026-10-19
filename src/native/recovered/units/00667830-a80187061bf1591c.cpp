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

extern "C" unsigned int __cdecl fn_00660b50(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_007597fc;

// FUNCTION: DAO 0x00a67830
undefined4 * __fastcall fn_00667830(undefined4 *param_1)
{
  fn_00660b50();
  *param_1 = (undefined4)(&g_007597fc);
  *(undefined1 *)(param_1 + 4) = 0x10;
  return param_1;
}

