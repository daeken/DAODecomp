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
typedef uint size_t;


extern "C" char * __cdecl fn_004e29f0(char * _Dest, char * _Source, size_t _Count);

// FUNCTION: DAO 0x0044b9b0
char * fn_0004b9b0(char *param_1,char *param_2,size_t param_3)
{
  fn_004e29f0(param_1,param_2,param_3);
  param_1[param_3 - 1] = '\0';
  return param_1;
}

