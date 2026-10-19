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

extern "C" undefined * g_0071a9f8;
extern "C" undefined * g_0071a9e8;
extern "C" undefined * g_0071a98c;
extern "C" undefined * g_0071a974;
extern "C" unsigned int __cdecl fn_006559e0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00733940
void __fastcall fn_00333940(undefined4 *param_1)
{
  *param_1 = (undefined4)(&g_0071a9f8);
  param_1[2] = (undefined4)(&g_0071a9e8);
  param_1[7] = (undefined4)(&g_0071a98c);
  param_1[8] = (undefined4)(&g_0071a974);
  fn_006559e0();
  return;
}

