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



// FUNCTION: DAO 0x00930cd0
undefined1 __fastcall fn_00530cd0(int param_1)
{
  int iVar1;
  
  iVar1 = ((unsigned int (__thiscall *)(void *))((**(code **)(**(int **)(param_1 + 0x74) + 0x40))))((void *)(*(int **)(param_1 + 0x74)));
  return *(undefined1 *)(iVar1 + 0xe4);
}

