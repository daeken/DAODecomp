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

struct Seed_00578fc0 { void __thiscall fn_00578fc0(float *param_2); };

// FUNCTION: DAO 0x00978fc0
void __thiscall Seed_00578fc0::fn_00578fc0(float *param_2)
{
  ((float *)this)[1] = param_2[1] * *((float *)this) + ((float *)this)[1];
  ((float *)this)[3] = param_2[3] * ((float *)this)[2] + ((float *)this)[3];
  ((float *)this)[5] = param_2[5] * ((float *)this)[4] + ((float *)this)[5];
  ((float *)this)[7] = param_2[7] * ((float *)this)[6] + ((float *)this)[7];
  *((float *)this) = *param_2 * *((float *)this);
  ((float *)this)[2] = param_2[2] * ((float *)this)[2];
  ((float *)this)[4] = param_2[4] * ((float *)this)[4];
  ((float *)this)[6] = param_2[6] * ((float *)this)[6];
  return;
}

