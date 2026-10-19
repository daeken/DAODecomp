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

extern "C" unsigned int __cdecl fn_00610e50(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_006085c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_00611ba0 { undefined4 __thiscall fn_00611ba0(byte param_2); };

// FUNCTION: DAO 0x00a11ba0
undefined4 __thiscall Seed_00611ba0::fn_00611ba0(byte param_2)
{
  fn_00610e50();
  if ((param_2 & 1) != 0) {
    fn_006085c0(((undefined4)this),0x3c);
  }
  return ((undefined4)this);
}

