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



// FUNCTION: DAO 0x005d44f0
void __fastcall fn_001d44f0(int param_1)
{
                    /* WARNING: Could not recover jumptable at 0x005d44fb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  ((unsigned int (__thiscall *)(void *))((**(code **)(**(int **)(param_1 + 0x158) + 0x18))))((void *)(*(int **)(param_1 + 0x158)));
  return;
}

