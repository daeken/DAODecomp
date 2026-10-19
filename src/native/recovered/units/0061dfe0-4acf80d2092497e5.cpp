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

// FUNCTION: DAO 0x00a1dfe0
undefined4 * fn_0061dfe0(void)
{
  undefined4 uVar1;
  undefined4 *_Dst;
  
  uVar1 = fn_0004c270();
  _Dst = (undefined4 *)fn_0001cdf0(0x3c,0x70666c74,uVar1);
  if (_Dst == (undefined4 *)0x0) {
    return (undefined4 *)0x0;
  }
  fn_004e19e0(_Dst,0,0x3c);
  *_Dst = uVar1;
  *(undefined1 *)(_Dst + 3) = 0;
  return _Dst;
}

