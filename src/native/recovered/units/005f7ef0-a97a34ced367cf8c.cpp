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

extern "C" unsigned int __cdecl fn_005f7780(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_005f7e70(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x009f7ef0
void fn_005f7ef0(int *param_1,undefined4 param_2)
{
  if (param_1[5] != 100) {
    *(undefined4 *)(*param_1 + 0x14) = 0x14;
    *(int *)(*param_1 + 0x18) = param_1[5];
    (**(code **)*param_1)(param_1);
  }
  fn_005f7780(param_1,0);
  (**(code **)(*param_1 + 0x10))(param_1);
  (**(code **)(param_1[6] + 8))(param_1);
  fn_005f7e70(param_2);
  param_1[0x34] = 0;
  param_1[5] = 0x67;
  return;
}

