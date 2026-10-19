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

extern "C" int g_0081dab4;
extern "C" unsigned int __cdecl fn_0004adb0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00444de0
undefined4 fn_00044de0(void)
{
  int iVar1;
  
  iVar1 = g_0081dab4;
  if (*(int *)(g_0081dab4 + 4) == 0) {
    *(undefined4 *)(g_0081dab4 + 4) = 1;
    if (*(int *)(iVar1 + 8) != 0) {
      fn_0004adb0(*(int *)(iVar1 + 8),0x6d616372,0x64736367,0,0);
    }
  }
  return 0;
}

