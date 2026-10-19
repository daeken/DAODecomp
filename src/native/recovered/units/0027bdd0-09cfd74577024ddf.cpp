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



// FUNCTION: DAO 0x0067bdd0
void fn_0027bdd0(int *param_1,int *param_2,int *param_3)
{
  int iVar1;
  
  iVar1 = *param_2;
  if (*(float *)(*(int *)(iVar1 + 4) + 0x120) < *(float *)(*(int *)(*param_1 + 4) + 0x120)) {
    *param_2 = *param_1;
    *param_1 = iVar1;
  }
  iVar1 = *param_3;
  if (*(float *)(*(int *)(iVar1 + 4) + 0x120) < *(float *)(*(int *)(*param_2 + 4) + 0x120)) {
    *param_3 = *param_2;
    *param_2 = iVar1;
  }
  iVar1 = *param_2;
  if (*(float *)(*(int *)(iVar1 + 4) + 0x120) < *(float *)(*(int *)(*param_1 + 4) + 0x120)) {
    *param_2 = *param_1;
    *param_1 = iVar1;
  }
  return;
}

