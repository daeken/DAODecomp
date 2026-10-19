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

extern "C" uint g_0084c364;
extern "C" int g_0081cec8;
extern "C" int g_0081cec4;

// FUNCTION: DAO 0x00a62ae0
int fn_00662ae0(void)
{
  g_0084c364 = g_0084c364 * 0x343fd + 0x269ec3;
  return (g_0084c364 >> 0x10 & 0x7fff) % (uint)(g_0081cec8 - g_0081cec4) + g_0081cec4;
}

