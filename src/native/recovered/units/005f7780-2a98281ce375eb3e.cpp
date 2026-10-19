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



// FUNCTION: DAO 0x009f7780
void fn_005f7780(int param_1,undefined1 param_2)
{
  int *piVar1;
  int iVar2;
  
  if (*(int *)(param_1 + 0x48) != 0) {
    *(undefined1 *)(*(int *)(param_1 + 0x48) + 0x80) = param_2;
  }
  if (*(int *)(param_1 + 0x4c) != 0) {
    *(undefined1 *)(*(int *)(param_1 + 0x4c) + 0x80) = param_2;
  }
  if (*(int *)(param_1 + 0x50) != 0) {
    *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x80) = param_2;
  }
  if (*(int *)(param_1 + 0x54) != 0) {
    *(undefined1 *)(*(int *)(param_1 + 0x54) + 0x80) = param_2;
  }
  piVar1 = (int *)(param_1 + 0x68);
  iVar2 = 4;
  do {
    if (piVar1[-4] != 0) {
      *(undefined1 *)(piVar1[-4] + 0x111) = param_2;
    }
    if (*piVar1 != 0) {
      *(undefined1 *)(*piVar1 + 0x111) = param_2;
    }
    piVar1 = piVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}

