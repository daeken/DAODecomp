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

extern "C" unsigned int __cdecl fn_00583360(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0051f9f0 { void __thiscall fn_0051f9f0(undefined1 param_2); };

// FUNCTION: DAO 0x0091f9f0
void __thiscall Seed_0051f9f0::fn_0051f9f0(undefined1 param_2)
{
  fn_00583360();
  *((undefined1 *)this) = 2;
  ((undefined1 *)this)[4] = param_2;
  return;
}

