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

struct Seed_00065a60 { void __thiscall fn_00065a60(float *param_2); };

// FUNCTION: DAO 0x00465a60
void __thiscall Seed_00065a60::fn_00065a60(float *param_2)
{
  float fVar1;
  float fVar2;
  
  fVar1 = *(float *)(((int)this) + 0xe8);
  fVar2 = *(float *)(((int)this) + 0xd8);
  *param_2 = -*(float *)(((int)this) + 200);
  param_2[1] = -fVar2;
  param_2[2] = -fVar1;
  return;
}

