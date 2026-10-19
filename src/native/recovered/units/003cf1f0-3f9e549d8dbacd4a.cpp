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



// FUNCTION: DAO 0x007cf1f0
void fn_003cf1f0(float *param_1,float *param_2,float *param_3)
{
  float fVar1;
  
  if (*param_2 < *param_1) {
    fVar1 = *param_2;
    *param_2 = *param_1;
    *param_1 = fVar1;
  }
  if (*param_3 < *param_2) {
    fVar1 = *param_3;
    *param_3 = *param_2;
    *param_2 = fVar1;
  }
  if (*param_2 < *param_1) {
    fVar1 = *param_2;
    *param_2 = *param_1;
    *param_1 = fVar1;
  }
  return;
}

