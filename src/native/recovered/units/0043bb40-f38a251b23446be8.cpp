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



// FUNCTION: DAO 0x0083bb40
uint fn_0043bb40(int param_1)
{
  int iVar1;
  int iVar2;
  
  if ((param_1 == 0) || (iVar1 = *(int *)(param_1 + 0x1c), iVar1 == 0)) {
    return 0xfffffffe;
  }
  iVar2 = *(int *)(iVar1 + 4);
  if ((((iVar2 != 0x2a) && (iVar2 != 0x45)) && (iVar2 != 0x49)) &&
     (((iVar2 != 0x5b && (iVar2 != 0x67)) && ((iVar2 != 0x71 && (iVar2 != 0x29a)))))) {
    return 0xfffffffe;
  }
  if (*(int *)(iVar1 + 8) != 0) {
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),*(int *)(iVar1 + 8));
  }
  iVar1 = *(int *)(*(int *)(param_1 + 0x1c) + 0x44);
  if (iVar1 != 0) {
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),iVar1);
  }
  iVar1 = *(int *)(*(int *)(param_1 + 0x1c) + 0x40);
  if (iVar1 != 0) {
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),iVar1);
  }
  iVar1 = *(int *)(*(int *)(param_1 + 0x1c) + 0x38);
  if (iVar1 != 0) {
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),iVar1);
  }
  (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),*(undefined4 *)(param_1 + 0x1c));
  *(undefined4 *)(param_1 + 0x1c) = 0;
  return (iVar2 != 0x71) - 1 & 0xfffffffd;
}

