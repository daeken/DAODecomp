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

extern "C" int g_008327ec;

// FUNCTION: DAO 0x006c2930
void fn_002c2930(void)
{
  int iVar1;
  
  iVar1 = *(int *)(*(int *)(g_008327ec + 0x114) + 0x60);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 0x26) = 1;
  }
  return;
}

