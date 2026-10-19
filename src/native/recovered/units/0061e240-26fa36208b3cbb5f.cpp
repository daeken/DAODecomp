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

extern "C" unsigned int __cdecl fn_0061e150(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0001ce30(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00a1e240
void fn_0061e240(undefined4 *param_1)
{
  fn_0061e150(param_1,0xffffffff);
  fn_0001ce30(param_1,0x70666c74,*param_1);
  return;
}

