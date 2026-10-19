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



// FUNCTION: DAO 0x0041c5e0
undefined4 __fastcall fn_0001c5e0(int *param_1)
{
  char cVar1;
  
  cVar1 = ((unsigned int (__thiscall *)(void *))((**(code **)(*param_1 + 8))))((void *)(param_1));
  if ((cVar1 != '\0') && ((*(byte *)(param_1 + 7) & 2) != 0)) {
    return 1;
  }
  return 0;
}

