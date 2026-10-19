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

struct Seed_00545810 { void __thiscall fn_00545810(float *param_2,float *param_3); };

// FUNCTION: DAO 0x00945810
void __thiscall Seed_00545810::fn_00545810(float *param_2,float *param_3)
{
  int iVar1;
  
  iVar1 = *((int *)this);
  *param_2 = (float)*(int *)(iVar1 + 0x2c);
  *param_3 = (float)*(int *)(iVar1 + 0x30);
  if ((*(byte *)(iVar1 + 0x70) & 0x80) != 0) {
    *param_2 = *param_2 * *(float *)(iVar1 + 0x6c);
    *param_3 = *(float *)(iVar1 + 0x6c) * *param_3;
  }
  return;
}

