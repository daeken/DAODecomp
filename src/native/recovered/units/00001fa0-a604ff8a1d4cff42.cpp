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

extern "C" int * g_00831650;

// FUNCTION: DAO 0x00401fa0
void fn_00001fa0(void)
{
                    /* WARNING: Could not recover jumptable at 0x00401fab. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  ((unsigned int (__thiscall *)(void *))((**(code **)(*g_00831650 + 0x10))))((void *)(g_00831650));
  return;
}

