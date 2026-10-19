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

extern "C" unsigned int __cdecl fn_00044aa0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_007f1ea0;
extern "C" unsigned int __cdecl fn_00044b30(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0044c160
void fn_0004c160(void)
{
  fn_00044aa0(g_007f1ea0);
  fn_00044b30(g_007f1ea0);
  return;
}

