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
extern "C" unsigned int __cdecl fn_0001c590(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0041c600
long __fastcall fn_0001c600(int param_1)
{
  long lVar1;
  undefined4 uVar2;
  
  lVar1 = fn_004e3992(*(FILE **)(param_1 + 0x18));
  if (lVar1 < 0) {
    uVar2 = fn_0001c590();
    *(undefined4 *)(param_1 + 0x20) = uVar2;
  }
  return lVar1;
}

