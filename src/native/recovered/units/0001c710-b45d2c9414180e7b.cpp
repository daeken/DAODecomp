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


extern "C" int __cdecl fn_004e3b7e(FILE * _File);
extern "C" unsigned int __cdecl fn_004e2484(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0001c590(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0001c710 { int __thiscall fn_0001c710(undefined4 param_2,int param_3); };

// FUNCTION: DAO 0x0041c710
int __thiscall Seed_0001c710::fn_0001c710(undefined4 param_2,int param_3)
{
  int iVar1;
  undefined4 uVar2;
  
  if ((*(int *)(((int)this) + 0x24) != 0) && (*(int *)(((int)this) + 0x24) != 1)) {
    fn_004e3b7e(*(FILE **)(((int)this) + 0x18));
  }
  *(undefined4 *)(((int)this) + 0x24) = 1;
  iVar1 = fn_004e2484(param_2,1,param_3,*(undefined4 *)(((int)this) + 0x18));
  if (iVar1 < param_3) {
    uVar2 = fn_0001c590();
    *(undefined4 *)(((int)this) + 0x20) = uVar2;
  }
  return iVar1;
}

