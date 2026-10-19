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

extern "C" unsigned int __cdecl fn_005b03a0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_005b0470 { void __thiscall fn_005b0470(int *param_2); };

// FUNCTION: DAO 0x009b0470
void __thiscall Seed_005b0470::fn_005b0470(int *param_2)
{
  if (((uint)param_2[2] < (uint)((int *)this)[2]) && (((unsigned int)(((int *)this)[3])) > 0u)) {
    fn_005b03a0(*param_2 + param_2[2] * 8,((int *)this)[2] - param_2[2],param_2[1] + param_2[4] * 4);
  }
  *((int *)this) = *param_2;
  ((int *)this)[1] = param_2[1];
  ((int *)this)[2] = param_2[2];
  ((int *)this)[3] = param_2[3];
  ((int *)this)[4] = param_2[4];
  return;
}

