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

extern "C" unsigned int __cdecl fn_00045900(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00046220(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00046110(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0001ce30(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00445cc0
void fn_00045cc0(int *param_1)
{
  if (*param_1 != 0) {
    param_1[0x12d] = 0;
    fn_00045900(param_1);
    param_1[0x24] = 0;
    if (*param_1 != 0) {
      fn_00046220(*param_1);
      fn_00046110(*param_1);
      *param_1 = 0;
    }
  }
  fn_0001ce30(param_1,0x74656c6d,param_1[1]);
  return;
}

