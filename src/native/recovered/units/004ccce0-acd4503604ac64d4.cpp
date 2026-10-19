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

extern "C" unsigned int __cdecl fn_004d7f30(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined g_006e5538;
struct Seed_004ccce0 { void __thiscall fn_004ccce0(undefined4 param_2); };

// FUNCTION: DAO 0x008ccce0
void __thiscall Seed_004ccce0::fn_004ccce0(undefined4 param_2)
{
  fn_004d7f30(param_2,3,&g_006e5538,((int)this) + 0x2c);
  return;
}

