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



// FUNCTION: DAO 0x00966c20
uint __fastcall fn_00566c20(int param_1)
{
  uint uVar1;
  uint uVar2;
  int *piVar3;
  
  uVar1 = *(uint *)(*(int *)(param_1 + 0x9c) + 0xa90);
  if ((*(int *)(param_1 + 0x1bc) != 0) && (uVar2 = 0, ((unsigned int)(uVar1)) > 0u)) {
    piVar3 = *(int **)(*(int *)(param_1 + 0x9c) + 0xa8c);
    do {
      if (*piVar3 == param_1) {
        return uVar2;
      }
      uVar2 = uVar2 + 1;
      piVar3 = piVar3 + 1;
    } while (uVar2 < uVar1);
  }
  return 0xffffffff;
}

