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

extern "C" unsigned int __cdecl fn_004da780(...); /* ABI/return type unknown, provisional declaration */
extern "C" int g_0083ec30;
extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x008dbf00
void fn_004dbf00(int param_1,int param_2)
{
  fn_004da780(param_1,param_2);
  if (param_1 != 0) {
    *(undefined4 *)(g_0083ec30 + *(int *)(param_1 + 0x18) * 4) = 0;
    fn_000136c0(param_1);
  }
  if (param_2 != 0) {
    *(undefined4 *)(g_0083ec30 + *(int *)(param_2 + 0x18) * 4) = 0;
    fn_000136c0(param_2);
  }
  return;
}

