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

extern "C" unsigned int __cdecl fn_0060bfc0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_006085c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0060c5c0 { undefined4 __thiscall fn_0060c5c0(byte param_2); };

// FUNCTION: DAO 0x00a0c5c0
undefined4 __thiscall Seed_0060c5c0::fn_0060c5c0(byte param_2)
{
  fn_0060bfc0();
  if ((param_2 & 1) != 0) {
    fn_006085c0(((undefined4)this),0x48);
  }
  return ((undefined4)this);
}

