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

extern "C" uint g_0084bf74;

// FUNCTION: DAO 0x00a3c9e0
int __fastcall fn_0063c9e0(int *param_1)
{
  g_0084bf74 = g_0084bf74 * 0x343fd + 0x269ec3;
  return ((g_0084bf74 >> 0x10 & 0x7fff) % (uint)param_1[1]) * 0x10 + *param_1;
}

