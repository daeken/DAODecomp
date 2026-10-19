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

extern "C" unsigned int __cdecl fn_006133a0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_006085c0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00a13940
void __fastcall fn_00613940(int *param_1)
{
  fn_006133a0(*param_1,*param_1 + param_1[2] * 0xc);
  fn_006085c0(*param_1,param_1[1] * 0xc);
  *param_1 = 0;
  param_1[2] = 0;
  param_1[1] = 0;
  return;
}

