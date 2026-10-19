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

extern "C" undefined4 g_0081dab8;

// FUNCTION: DAO 0x004481b0
void fn_000481b0(void)
{
  int *piVar1;
  
  piVar1 = (int *)(&g_0081dab8);
  do {
    if (*piVar1 != 0) {
      *piVar1 = 0;
      piVar1[1] = 0;
    }
    piVar1 = piVar1 + 2;
  } while ((int)piVar1 < 0xc1dbb8);
  return;
}

