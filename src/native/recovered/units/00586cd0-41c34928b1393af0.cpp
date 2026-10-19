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

extern "C" unsigned int __cdecl fn_005866a0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00986cd0
void __fastcall fn_00586cd0(undefined4 *param_1)
{
  ushort *puVar1;
  
  puVar1 = (ushort *)param_1[1];
  *param_1 = (undefined4)(puVar1);
  if ((*(char *)(param_1 + 4) != '\0') && (*puVar1 == 0x26)) {
    fn_005866a0();
    return;
  }
  if (puVar1 < (ushort *)param_1[2]) {
    param_1[3] = (uint)*puVar1;
    param_1[1] = (undefined4)(puVar1 + 1);
  }
  return;
}

