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

extern "C" unsigned int __cdecl fn_004e37b6(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0041c590
int fn_0001c590(void)
{
  int *piVar1;
  
  piVar1 = (int *)fn_004e37b6();
  if (*piVar1 == 2) {
    return 0x1001;
  }
  piVar1 = (int *)fn_004e37b6();
  if (*piVar1 != 0xd) {
    piVar1 = (int *)fn_004e37b6();
    if (*piVar1 != 1) {
      piVar1 = (int *)fn_004e37b6();
      return (*piVar1 == 0x1c) + 0x1003;
    }
  }
  return 0x1002;
}

