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

extern "C" unsigned int __cdecl fn_004282b0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_0072707c;

// FUNCTION: DAO 0x0082c1b0
void fn_0042c1b0(void)
{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)fn_004282b0();
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = (undefined4)(&g_0072707c);
    puVar1[1] = 0;
  }
  return;
}

