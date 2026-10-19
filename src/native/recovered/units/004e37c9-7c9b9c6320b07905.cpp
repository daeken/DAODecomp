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

extern "C" unsigned int __cdecl fn_004ee241(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined g_0081541c;

// FUNCTION: DAO 0x008e37c9
undefined * fn_004e37c9(void)
{
  int iVar1;
  
  iVar1 = fn_004ee241();
  if (iVar1 == 0) {
    return &g_0081541c;
  }
  return (undefined *)(iVar1 + 0xc);
}

