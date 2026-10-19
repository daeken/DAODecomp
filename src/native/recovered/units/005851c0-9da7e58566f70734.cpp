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
typedef ushort wint_t;


extern "C" int __cdecl fn_004e1b5c(wint_t _C);

// FUNCTION: DAO 0x009851c0
bool fn_005851c0(wint_t param_1)
{
  int iVar1;
  
  iVar1 = fn_004e1b5c(param_1);
  return iVar1 != 0;
}

