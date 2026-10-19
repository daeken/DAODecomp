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
extern "C" size_t __cdecl fn_004e2964(void * _Str, size_t _Size, size_t _Count, FILE * _File);
extern "C" unsigned int __cdecl fn_0001c590(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0001c6b0 { size_t __thiscall fn_0001c6b0(void *param_2,size_t param_3); };

// FUNCTION: DAO 0x0041c6b0
size_t __thiscall Seed_0001c6b0::fn_0001c6b0(void *param_2,size_t param_3)
{
  size_t sVar1;
  undefined4 uVar2;
  
  if ((*(int *)(((int)this) + 0x24) != 0) && (*(int *)(((int)this) + 0x24) != 2)) {
    fn_004e3b7e(*(FILE **)(((int)this) + 0x18));
  }
  *(undefined4 *)(((int)this) + 0x24) = 2;
  sVar1 = fn_004e2964(param_2,1,param_3,*(FILE **)(((int)this) + 0x18));
  if ((int)sVar1 < (int)param_3) {
    uVar2 = fn_0001c590();
    *(undefined4 *)(((int)this) + 0x20) = uVar2;
  }
  return sVar1;
}

