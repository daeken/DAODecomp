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

typedef int errno_t;


extern "C" errno_t __cdecl fn_004e2cd9(FILE * * _File, char * _Filename, char * _Mode);

// FUNCTION: DAO 0x004b53e0
FILE * fn_000b53e0(char *param_1,char *param_2)
{
  errno_t eVar1;
  FILE *local_4;
  
  local_4 = (FILE *)0x0;
  eVar1 = fn_004e2cd9(&local_4,param_1,param_2);
  if ((eVar1 != 0) || (local_4 == (FILE *)0x0)) {
    local_4 = (FILE *)0x0;
  }
  return local_4;
}

