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

extern "C" unsigned int __cdecl fn_000d2710(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000d29a0 { undefined4 __thiscall fn_000d29a0(short *param_2); };

// FUNCTION: DAO 0x004d29a0
undefined4 __thiscall Seed_000d29a0::fn_000d29a0(short *param_2)
{
  short sVar1;
  
  sVar1 = fn_000d2710();
  if (sVar1 != -1) {
    *param_2 = sVar1;
  }
  return ((undefined4)this);
}

