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

extern "C" unsigned int __cdecl fn_00013660(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_0071b194;

// FUNCTION: DAO 0x007380d0
undefined4 * fn_003380d0(undefined4 param_1,undefined4 param_2,undefined4 param_3)
{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)fn_00013660(0x10);
  if (puVar1 != (undefined4 *)0x0) {
    puVar1[1] = param_1;
    *puVar1 = (undefined4)(&g_0071b194);
    puVar1[2] = param_2;
    puVar1[3] = param_3;
    return puVar1;
  }
  return (undefined4 *)0x0;
}

