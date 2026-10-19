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

extern "C" char g_0081cfac;
struct Seed_00669ba0 { int __thiscall fn_00669ba0(char param_2); };

// FUNCTION: DAO 0x00a69ba0
int __thiscall Seed_00669ba0::fn_00669ba0(char param_2)
{
  int iVar1;
  
  iVar1 = 0;
  if ((g_0081cfac != '\0') && (*(char *)(((int)this) + 0x6f) == '\0')) {
    if ((param_2 != '\0') ||
       ((*(int *)(((int)this) + 0x54) != 8 || (iVar1 = *(int *)(((int)this) + 0x5c), iVar1 == 0)))) {
      iVar1 = *(int *)(((int)this) + 0x60);
    }
    if (iVar1 == 1) {
      iVar1 = 0;
    }
  }
  return iVar1;
}

