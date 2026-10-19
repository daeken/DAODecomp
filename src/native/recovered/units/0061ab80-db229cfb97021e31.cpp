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

extern "C" unsigned int __cdecl fn_006085c0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00a1ab80
void fn_0061ab80(int param_1,int param_2)
{
  int *piVar1;
  
  if (param_1 != param_2) {
    piVar1 = (int *)(param_1 + 0xc);
    do {
      if (param_1 != 0) {
        fn_006085c0(piVar1[-1],*piVar1 * 4);
        piVar1[-1] = 0;
        piVar1[1] = 0;
        *piVar1 = 0;
      }
      param_1 = param_1 + 0x14;
      piVar1 = piVar1 + 5;
    } while (param_1 != param_2);
  }
  return;
}

