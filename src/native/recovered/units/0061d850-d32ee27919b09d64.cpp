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

extern "C" unsigned int __cdecl fn_000480e0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined g_0061d5f0;
extern "C" unsigned int __cdecl fn_00047330(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0061e240(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0001ce30(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00a1d850
void fn_0061d850(undefined4 *param_1)
{
  fn_000480e0(&g_0061d5f0,param_1);
  fn_00047330(*param_1);
  fn_0061e240(param_1[1]);
  fn_0001ce30(param_1,0x6c636b72,param_1[2]);
  return;
}

