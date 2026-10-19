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

struct Seed_005724f0 { undefined4 __thiscall fn_005724f0(int *param_2); };

// FUNCTION: DAO 0x009724f0
undefined4 __thiscall Seed_005724f0::fn_005724f0(int *param_2)
{
  if (((((*((int *)this) == *param_2) && ((short)((int *)this)[1] == (short)param_2[1])) &&
       (*(char *)((int)((int *)this) + 6) == *(char *)((int)param_2 + 6))) &&
      ((*(char *)((int)((int *)this) + 7) == *(char *)((int)param_2 + 7) &&
       ((char)((int *)this)[2] == (char)param_2[2])))) &&
     ((*(char *)((int)((int *)this) + 9) == *(char *)((int)param_2 + 9) &&
      ((*(char *)((int)((int *)this) + 10) == *(char *)((int)param_2 + 10) &&
       (*(char *)((int)((int *)this) + 0xb) == *(char *)((int)param_2 + 0xb))))))) {
    return 1;
  }
  return 0;
}

