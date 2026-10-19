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


extern "C" unsigned int __cdecl fn_0004c270(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0001cdf0(...); /* ABI/return type unknown, provisional declaration */
extern "C" void * __cdecl fn_004e19e0(void * _Dst, int _Val, size_t _Size);

// FUNCTION: DAO 0x0044db90
void * fn_0004db90(void)
{
  undefined4 uVar1;
  void *_Dst;
  
  uVar1 = fn_0004c270();
  _Dst = (void *)fn_0001cdf0(0x128,0x7073736c,uVar1);
  if (_Dst == (void *)0x0) {
    return (void *)0x0;
  }
  fn_004e19e0(_Dst,0,0x128);
  *(undefined4 *)((int)_Dst + 8) = uVar1;
  return _Dst;
}

