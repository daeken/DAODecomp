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

extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_007592b8;

// FUNCTION: DAO 0x00a45ea0
void __fastcall fn_00645ea0(undefined4 *param_1)
{
  if (param_1[5] != 0) {
    fn_000136c0(param_1[5]);
  }
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  *param_1 = (undefined4)(&g_007592b8);
  return;
}

