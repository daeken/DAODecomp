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



// FUNCTION: DAO 0x009d6a40
void __fastcall fn_005d6a40(int *param_1)
{
  int *piVar1;
  
  piVar1 = param_1 + 0x11;
  *piVar1 = *piVar1 + -1;
  if (*piVar1 == 0) {
    (**(code **)(**(int **)(*param_1 + 0x14) + 0x70))();
    param_1[0x10] = 0;
  }
  return;
}

