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

struct Seed_0063ba80 { undefined4 __thiscall fn_0063ba80(ushort param_2,ushort param_3); };

// FUNCTION: DAO 0x00a3ba80
undefined4 __thiscall Seed_0063ba80::fn_0063ba80(ushort param_2,ushort param_3)
{
  if (param_3 == 0xffff) {
    param_3 = param_2;
  }
  if (((int)(uint)param_2 < *(int *)(((int)this) + 0x20)) &&
     ((int)(uint)param_3 < *(int *)(((int)this) + 0x20))) {
    return *(undefined4 *)
            (*(int *)(*(int *)(((int)this) + 0x24) + (uint)param_2 * 0x14) + (uint)param_3 * 4);
  }
  return 0;
}

