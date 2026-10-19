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



// FUNCTION: DAO 0x00420960
undefined1 * __fastcall fn_00020960(int param_1)
{
  undefined1 *puVar1;
  char *pcVar2;
  int iVar3;
  
  iVar3 = 0;
  pcVar2 = (char *)(param_1 + 0x2e40);
  do {
    if (*pcVar2 == '\0') {
      puVar1 = (undefined1 *)(iVar3 * 0x2c + 0x2e40 + param_1);
      *puVar1 = 1;
      if (iVar3 + 1 <= *(int *)(param_1 + 0x14)) {
        return puVar1;
      }
      *(int *)(param_1 + 0x14) = iVar3 + 1;
      return puVar1;
    }
    iVar3 = iVar3 + 1;
    pcVar2 = pcVar2 + 0x2c;
  } while (iVar3 < 0x20);
  return (undefined1 *)0x0;
}

