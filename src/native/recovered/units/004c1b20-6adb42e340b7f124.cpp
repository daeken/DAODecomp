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
typedef struct _iobuf _iobuf, *P_iobuf;

typedef struct _iobuf FILE;

struct _iobuf {
    char *_ptr;
    int _cnt;
    char *_base;
    int _flag;
    int _file;
    int _charbuf;
    int _bufsiz;
    char *_tmpfname;
};


extern "C" long __cdecl fn_004e3992(FILE * _File);

// FUNCTION: DAO 0x008c1b20
long fn_004c1b20(undefined4 *param_1)
{
  long lVar1;
  
  lVar1 = 0;
  if (param_1 != (undefined4 *)0x0) {
    if ((FILE *)*param_1 != (FILE *)0x0) {
      lVar1 = fn_004e3992((FILE *)*param_1);
      return lVar1;
    }
    lVar1 = param_1[3];
  }
  return lVar1;
}

