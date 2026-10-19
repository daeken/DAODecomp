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



// FUNCTION: DAO 0x009790a0
undefined4 __fastcall fn_005790a0(float *param_1)
{
  if (((((*param_1 == 1.0) && (param_1[2] == 1.0)) && (param_1[4] == 1.0)) &&
      ((param_1[6] == 1.0 && (param_1[1] == 0.0)))) &&
     ((param_1[3] == 0.0 && ((param_1[5] == 0.0 && (param_1[7] == 0.0)))))) {
    return 1;
  }
  return 0;
}

