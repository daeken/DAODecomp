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

// FUNCTION: DAO 0x00a1ab10
void fn_0061ab10(undefined4 *param_1,undefined4 *param_2)
{
  for (; param_1 != param_2; param_1 = param_1 + 4) {
    if (param_1 != (undefined4 *)0x0) {
      fn_006085c0(*param_1,param_1[1]);
      *param_1 = 0;
      param_1[2] = 0;
      param_1[1] = 0;
    }
  }
  return;
}

