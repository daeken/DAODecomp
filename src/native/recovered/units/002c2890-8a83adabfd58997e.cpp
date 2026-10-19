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

extern "C" unsigned int __cdecl fn_002c2350(...); /* ABI/return type unknown, provisional declaration */
struct Seed_002c2890 { void __thiscall fn_002c2890(undefined4 param_2,char param_3); };

// FUNCTION: DAO 0x006c2890
void __thiscall Seed_002c2890::fn_002c2890(undefined4 param_2,char param_3)
{
  *(undefined4 *)(((int)this) + 0x30) = param_2;
  if (param_3 != '\0') {
    fn_002c2350();
  }
  return;
}

