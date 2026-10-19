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



// FUNCTION: DAO 0x009b6050
void __fastcall fn_005b6050(int param_1)
{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = *(int *)(param_1 + 0x38) + -1;
  iVar4 = 0;
  if (0 < iVar3) {
    do {
      iVar1 = *(int *)(param_1 + 0x34);
      uVar2 = *(undefined4 *)(iVar1 + iVar4 * 4);
      *(undefined4 *)(iVar1 + iVar4 * 4) = *(undefined4 *)(iVar1 + iVar3 * 4);
      *(undefined4 *)(iVar1 + iVar3 * 4) = uVar2;
      iVar4 = iVar4 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar4 < iVar3);
  }
  return;
}

