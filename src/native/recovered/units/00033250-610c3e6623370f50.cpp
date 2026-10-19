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



// FUNCTION: DAO 0x00433250
int __fastcall fn_00033250(int param_1)
{
  int iVar1;
  int iVar2;
  
  iVar1 = 0;
  for (iVar2 = *(int *)(param_1 + 4); iVar2 != *(int *)(param_1 + 8); iVar2 = iVar2 + 4) {
    iVar1 = iVar1 + 1;
  }
  return iVar1;
}

