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

extern "C" undefined4 g_0083f940;
extern "C" undefined4 g_0083f944;
extern "C" undefined4 g_0083f948;
extern "C" undefined4 g_0083f94c;

// FUNCTION: DAO 0x008fc42d
/* Library Function - Single Match
    __initp_misc_winsig
   
   Library: Visual Studio 2005 Release */

void fn_004fc42d(undefined4 param_1)
{
  g_0083f940 = param_1;
  g_0083f944 = param_1;
  g_0083f948 = param_1;
  g_0083f94c = param_1;
  return;
}

