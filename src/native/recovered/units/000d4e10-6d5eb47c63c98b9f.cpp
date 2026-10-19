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



// FUNCTION: DAO 0x004d4e10
float * __fastcall fn_000d4e10(float *param_1)
{
  float fVar1;
  
  if (param_1[3] != 0.0) {
    fVar1 = 1.0 / param_1[3];
    *param_1 = fVar1 * *param_1;
    param_1[1] = param_1[1] * fVar1;
    param_1[2] = fVar1 * param_1[2];
    param_1[3] = 1.0;
  }
  return param_1;
}

