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

extern "C" unsigned int __cdecl fn_005a0320(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x009a0650
void __fastcall fn_005a0650(int param_1)
{
  *(undefined4 *)(param_1 + 0x20) = 0;
  *(undefined2 *)(param_1 + 0x14) = 0;
  *(undefined1 *)(param_1 + 0x28) = 0;
  *(undefined2 *)(param_1 + 0x16) = 0;
  *(undefined2 *)(param_1 + 0x18) = 0;
  *(undefined2 *)(param_1 + 0x1a) = 0;
  *(undefined2 *)(param_1 + 0x1c) = 0;
  *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xff41 | 1;
  fn_005a0320();
  *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xffbf;
  return;
}

