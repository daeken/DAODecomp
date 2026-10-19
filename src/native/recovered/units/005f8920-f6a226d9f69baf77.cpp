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

extern "C" unsigned int __cdecl fn_005f8580(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x009f8920
void fn_005f8920(int *param_1,int param_2,undefined1 param_3,undefined4 param_4,undefined4 param_5,
                 undefined4 param_6)
{
  int iVar1;
  undefined4 *puVar2;
  
  iVar1 = param_1[1];
  if (param_2 != 1) {
    *(undefined4 *)(*param_1 + 0x14) = 0xe;
    *(int *)(*param_1 + 0x18) = param_2;
    (**(code **)*param_1)(param_1);
  }
  puVar2 = (undefined4 *)fn_005f8580(param_1,param_2,0x78);
  puVar2[1] = param_5;
  puVar2[2] = param_4;
  *puVar2 = 0;
  puVar2[3] = param_6;
  *(undefined1 *)(puVar2 + 8) = param_3;
  *(undefined1 *)((int)puVar2 + 0x22) = 0;
  puVar2[9] = *(undefined4 *)(iVar1 + 0x48);
  *(undefined4 **)(iVar1 + 0x48) = puVar2;
  return;
}

