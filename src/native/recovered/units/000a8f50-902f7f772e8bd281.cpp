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

extern "C" unsigned int __cdecl fn_000a8c30(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x004a8f50
void __fastcall fn_000a8f50(int param_1)
{
  if ((*(char *)(param_1 + 0x15b) == '\0') && (*(char *)(param_1 + 0x15c) == '\0')) {
    return;
  }
  fn_000a8c30();
  return;
}

