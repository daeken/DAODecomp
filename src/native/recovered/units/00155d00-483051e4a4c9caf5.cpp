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
typedef int errno_t;

typedef uint size_t;

typedef size_t rsize_t;


extern "C" errno_t __cdecl fn_004e0e8b(void * _Dst, rsize_t _DstSize, void * _Src, rsize_t _MaxCount);

// FUNCTION: DAO 0x00555d00
void * fn_00155d00(void *param_1,int param_2,int param_3)
{
  int iVar1;
  void *_Dst;
  
  iVar1 = param_2 - (int)param_1 >> 1;
  _Dst = (void *)(param_3 + iVar1 * -2);
  if (0 < iVar1) {
    fn_004e0e8b(_Dst,iVar1 * 2,param_1,iVar1 * 2);
  }
  return _Dst;
}

