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

extern "C" unsigned int __cdecl fn_00044e40(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00044d80(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00431f10
undefined4 __fastcall fn_00031f10(int param_1)
{
  int iVar1;
  undefined4 uVar2;
  
  if ((*(byte *)(*(int *)(param_1 + 4) + 300) & 1) == 0) {
    iVar1 = fn_00044e40(0x6f70656e,0,0,0);
    if (iVar1 == 0) {
      uVar2 = fn_00044d80(0);
      return uVar2;
    }
  }
  return 0;
}

