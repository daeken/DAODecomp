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

extern "C" unsigned int __cdecl fn_0001b560(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0041b5c0
undefined4 * fn_0001b5c0(int param_1,undefined4 *param_2,int param_3,int param_4,undefined4 param_5,
            undefined4 param_6,undefined4 param_7)
{
  undefined4 *puVar1;
  
  if (param_4 == 0) {
    *param_2 = 0;
    return param_2 + 2;
  }
  if (param_1 == 0) {
    puVar1 = (undefined4 *)fn_0001b560(param_2,param_3,param_4,param_5,param_6,param_7);
    return puVar1;
  }
  *(undefined4 **)(param_1 + 8) = param_2;
  *(int *)(param_1 + 0xc) = param_3;
  param_2[1] = 0xcccccccc;
  *(undefined4 *)((int)param_2 + param_3 + 8) = 0xcccccccc;
  return param_2 + 2;
}

