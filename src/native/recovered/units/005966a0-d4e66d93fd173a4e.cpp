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

extern "C" unsigned int __cdecl fn_00595980(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x009966a0
undefined4 __fastcall fn_005966a0(int param_1)
{
  if ((*(byte *)(param_1 + 0x14e) & 3) != 0) {
    fn_00595980();
    *(byte *)(param_1 + 0x14e) = *(byte *)(param_1 + 0x14e) & 0xfc;
  }
  return *(undefined4 *)(param_1 + 0x30);
}

