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

extern "C" unsigned int __cdecl fn_001187f0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_00118cb0 { void __thiscall fn_00118cb0(char param_2); };

// FUNCTION: DAO 0x00518cb0
void __thiscall Seed_00118cb0::fn_00118cb0(char param_2)
{
  *(char *)(((int)this) + 0x28) = param_2;
  if (param_2 == '\0') {
    fn_001187f0();
  }
  return;
}

