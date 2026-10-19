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

extern "C" undefined g_0074eff0;
extern "C" undefined g_006e4128;

// FUNCTION: DAO 0x00984f40
undefined * __fastcall fn_00584f40(int param_1)
{
  undefined *puVar1;
  
  puVar1 = &g_0074eff0;
  if ((*(byte *)(param_1 + 0x28) & 2) == 0) {
    puVar1 = &g_006e4128;
  }
  return puVar1;
}

