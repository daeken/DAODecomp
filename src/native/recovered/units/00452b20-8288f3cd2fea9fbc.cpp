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

extern "C" unsigned int __cdecl fn_00456940(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00452a80(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00852b20
uint fn_00452b20(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)
{
  char cVar1;
  uint uVar2;
  
  uVar2 = fn_00456940(param_1,1,*(undefined4 *)(param_1 + 0x90),param_2,param_3,param_4);
  if (uVar2 == 0) {
    cVar1 = fn_00452a80(param_1);
    uVar2 = (uint)(cVar1 == '\0');
  }
  return uVar2;
}

