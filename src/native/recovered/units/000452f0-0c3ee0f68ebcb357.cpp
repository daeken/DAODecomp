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

extern "C" unsigned int __cdecl fn_0004c230(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00046090(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0004c250(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x004452f0
undefined4 fn_000452f0(int *param_1)
{
  int iVar1;
  
  fn_0004c230(param_1[1]);
  iVar1 = fn_00046090(0x2000);
  *param_1 = iVar1;
  fn_0004c250();
  if (*param_1 == 0) {
    return 0;
  }
  param_1[0x24] = 1;
  return 1;
}

