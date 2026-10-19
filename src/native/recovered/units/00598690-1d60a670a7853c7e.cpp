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

struct Seed_00598690 { void __thiscall fn_00598690(undefined4 *param_2); };

// FUNCTION: DAO 0x00998690
void __thiscall Seed_00598690::fn_00598690(undefined4 *param_2)
{
  if ((*(byte *)(param_2 + 0x14) & 1) != 0) {
    *(byte *)(((undefined4 *)this) + 0x14) = *(byte *)(((undefined4 *)this) + 0x14) | 1;
    *((undefined4 *)this) = *param_2;
    ((undefined4 *)this)[1] = param_2[1];
    ((undefined4 *)this)[2] = param_2[2];
    *(undefined1 *)(((undefined4 *)this) + 3) = *(undefined1 *)(param_2 + 3);
  }
  if ((*(byte *)(param_2 + 0x14) & 2) != 0) {
    *(byte *)(((undefined4 *)this) + 0x14) = *(byte *)(((undefined4 *)this) + 0x14) | 2;
    ((undefined4 *)this)[4] = param_2[4];
    ((undefined4 *)this)[5] = param_2[5];
    ((undefined4 *)this)[6] = param_2[6];
    *(undefined1 *)(((undefined4 *)this) + 7) = *(undefined1 *)(param_2 + 7);
  }
  if ((*(byte *)(param_2 + 0x14) & 4) != 0) {
    *(byte *)(((undefined4 *)this) + 0x14) = *(byte *)(((undefined4 *)this) + 0x14) | 4;
    ((undefined4 *)this)[8] = param_2[8];
    ((undefined4 *)this)[9] = param_2[9];
    ((undefined4 *)this)[10] = param_2[10];
    *(undefined1 *)(((undefined4 *)this) + 0xb) = *(undefined1 *)(param_2 + 0xb);
  }
  if ((*(byte *)(param_2 + 0x14) & 8) != 0) {
    *(byte *)(((undefined4 *)this) + 0x14) = *(byte *)(((undefined4 *)this) + 0x14) | 8;
    ((undefined4 *)this)[0xc] = param_2[0xc];
    ((undefined4 *)this)[0xd] = param_2[0xd];
    ((undefined4 *)this)[0xe] = param_2[0xe];
    *(undefined1 *)(((undefined4 *)this) + 0xf) = *(undefined1 *)(param_2 + 0xf);
  }
  if ((*(byte *)(param_2 + 0x14) & 0x10) != 0) {
    *(byte *)(((undefined4 *)this) + 0x14) = *(byte *)(((undefined4 *)this) + 0x14) | 0x10;
    ((undefined4 *)this)[0x10] = param_2[0x10];
    ((undefined4 *)this)[0x11] = param_2[0x11];
    ((undefined4 *)this)[0x12] = param_2[0x12];
    *(undefined1 *)(((undefined4 *)this) + 0x13) = *(undefined1 *)(param_2 + 0x13);
  }
  return;
}

