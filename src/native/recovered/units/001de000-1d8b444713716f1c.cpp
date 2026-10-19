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



// FUNCTION: DAO 0x005de000
void fn_001de000(undefined4 *param_1,undefined4 *param_2,undefined4 *param_3,code *param_4)
{
  undefined4 uVar1;
  undefined4 uVar2;
  char cVar3;
  
  cVar3 = (*param_4)(param_2,param_1);
  if (cVar3 != '\0') {
    uVar1 = *param_2;
    uVar2 = param_2[1];
    *param_2 = *param_1;
    param_2[1] = param_1[1];
    *param_1 = uVar1;
    param_1[1] = uVar2;
  }
  cVar3 = (*param_4)(param_3,param_2);
  if (cVar3 != '\0') {
    uVar1 = *param_3;
    uVar2 = param_3[1];
    *param_3 = *param_2;
    param_3[1] = param_2[1];
    *param_2 = uVar1;
    param_2[1] = uVar2;
  }
  cVar3 = (*param_4)(param_2,param_1);
  if (cVar3 != '\0') {
    uVar1 = *param_2;
    uVar2 = param_2[1];
    *param_2 = *param_1;
    param_2[1] = param_1[1];
    *param_1 = uVar1;
    param_1[1] = uVar2;
  }
  return;
}

