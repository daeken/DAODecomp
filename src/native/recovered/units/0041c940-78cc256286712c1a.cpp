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

extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0081c940
void fn_0041c940(int param_1)
{
  int *piVar1;
  
  if (((param_1 != 0) && (piVar1 = *(int **)(param_1 + 4), piVar1 != (int *)0x0)) && (*piVar1 != 0))
  {
    fn_000136c0(piVar1);
    *(undefined4 *)(param_1 + 4) = 0;
  }
  return;
}

