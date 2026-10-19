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

extern "C" unsigned int __cdecl fn_004e11f2(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000cd610 { int __thiscall fn_000cd610(int *param_2); };

// FUNCTION: DAO 0x004cd610
int __thiscall Seed_000cd610::fn_000cd610(int *param_2)
{
  if ((char)param_2[2] != '\0') {
    if (*param_2 == 0) {
      fn_004e11f2();
    }
    if (param_2[1] == *(int *)(*param_2 + 4)) {
      fn_004e11f2();
    }
    return param_2[1] + 0xc;
  }
  return ((int)this) + 0x2c;
}

