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
typedef ulong DWORD;


extern "C" DWORD __stdcall fn_000bbd40(void);
extern "C" DWORD g_0082b590;
extern "C" int g_00831650;

// FUNCTION: DAO 0x005278c0
undefined4 fn_001278c0(void)
{
  DWORD DVar1;
  
  DVar1 = fn_000bbd40();
  if (DVar1 == g_0082b590) {
    return *(undefined4 *)(g_00831650 + 0xbc);
  }
  return *(undefined4 *)(g_00831650 + 0xb4);
}

