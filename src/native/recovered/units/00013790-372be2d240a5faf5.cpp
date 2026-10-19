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

extern "C" undefined * g_006e0084;
extern "C" undefined4 * g_0081d25c;

// FUNCTION: DAO 0x00413790
void __fastcall fn_00013790(undefined4 *param_1)
{
  *param_1 = (undefined4)(&g_006e0084);
  if (g_0081d25c == param_1) {
    g_0081d25c = (undefined4 *)0x0;
  }
  return;
}

