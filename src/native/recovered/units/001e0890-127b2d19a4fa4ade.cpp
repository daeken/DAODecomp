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

extern "C" unsigned int __cdecl fn_001e0800(...); /* ABI/return type unknown, provisional declaration */
struct Seed_001e0890 { void __thiscall fn_001e0890(undefined4 param_2); };

// FUNCTION: DAO 0x005e0890
void __thiscall Seed_001e0890::fn_001e0890(undefined4 param_2)
{
  fn_001e0800(((undefined4)this),param_2);
  return;
}

