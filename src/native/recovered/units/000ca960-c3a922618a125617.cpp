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

extern "C" undefined g_006f07e0;

// FUNCTION: DAO 0x004ca960
uint fn_000ca960(int param_1,uint param_2)
{
  uint uVar1;
  uint uVar2;
  
  uVar1 = 0xffffffff;
  uVar2 = 0;
  if (((unsigned int)(param_2)) > 0u) {
    do {
      uVar1 = uVar1 >> 8 ^
              *(uint *)(&g_006f07e0 + ((uint)*(byte *)(uVar2 + param_1) ^ uVar1 & 0xff) * 4);
      uVar2 = uVar2 + 1;
    } while (uVar2 < param_2);
  }
  return ~uVar1;
}

