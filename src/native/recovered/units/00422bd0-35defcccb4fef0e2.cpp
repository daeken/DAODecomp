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

extern "C" unsigned int __cdecl fn_004e11f2(...); /* ABI/return type unknown, provisional declaration */
struct Seed_00422bd0 { int * __thiscall fn_00422bd0(int *param_2); };

// FUNCTION: DAO 0x00822bd0
int * __thiscall Seed_00422bd0::fn_00422bd0(int *param_2)
{
  *((int *)this) = 0;
  ((int *)this)[1] = param_2[1];
  ((int *)this)[2] = param_2[2];
  if (*param_2 == 0) {
    fn_004e11f2();
  }
  *((int *)this) = *param_2;
  return ((int *)this);
}

