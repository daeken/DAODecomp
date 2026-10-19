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

extern "C" undefined g_0081eb20;
extern "C" undefined4 g_0081eb18;

// FUNCTION: DAO 0x004560d0
undefined4 * fn_000560d0(void)
{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)&g_0081eb20;
  if (g_0081eb18 != 0) {
    puVar1 = &g_0081eb18;
  }
  return puVar1;
}

