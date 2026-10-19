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

extern "C" undefined1 g_00813234;

// FUNCTION: DAO 0x00838a20
void __fastcall fn_00438a20(int param_1)
{
  char cVar1;
  
  cVar1 = ((unsigned int (__thiscall *)(void *))((**(code **)(**(int **)(param_1 + 4) + 0x74))))((void *)(*(int **)(param_1 + 4)));
  if ((cVar1 == '\0') && (*(char *)(param_1 + 0x39) != '\0')) {
    g_00813234 = 0;
  }
  return;
}

