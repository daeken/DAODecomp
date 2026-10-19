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

extern "C" unsigned int __cdecl fn_0061e260(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0061e480(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0061e3d0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00a1e6d0
int fn_0061e6d0(void)
{
  int iVar1;
  int local_4;
  
  iVar1 = fn_0061e260();
  if (iVar1 == 1) {
    iVar1 = fn_0061e480(&local_4);
  }
  else {
    iVar1 = fn_0061e3d0(&local_4);
  }
  if ((iVar1 == 0) || (local_4 == 0)) {
    local_4 = 1;
  }
  return local_4;
}

