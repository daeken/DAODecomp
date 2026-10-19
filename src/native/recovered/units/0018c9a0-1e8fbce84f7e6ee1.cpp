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



// FUNCTION: DAO 0x0058c9a0
void fn_0018c9a0(undefined4 *param_1,undefined4 *param_2,undefined4 *param_3)
{
  for (; param_1 != param_2; param_1 = (undefined4 *)((int)param_1 + 6)) {
    *param_1 = *param_3;
    *(undefined2 *)(param_1 + 1) = *(undefined2 *)(param_3 + 1);
  }
  return;
}

