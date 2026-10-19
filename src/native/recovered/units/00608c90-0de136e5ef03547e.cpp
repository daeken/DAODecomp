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


extern "C" unsigned int __cdecl fn_00608ac0(...); /* ABI/return type unknown, provisional declaration */
extern "C" void * __cdecl fn_004e24a0(void * _Dst, void * _Src, size_t _Size);
struct Seed_00608c90 { int * __thiscall fn_00608c90(undefined4 *param_2); };

// FUNCTION: DAO 0x00a08c90
int * __thiscall Seed_00608c90::fn_00608c90(undefined4 *param_2)
{
  void *_Dst;
  int iVar1;
  
  if (param_2[2] == 0) {
    _Dst = (void *)0x0;
    iVar1 = 0;
  }
  else {
    iVar1 = param_2[2] + 1;
    if (iVar1 == 0) {
      _Dst = (void *)0x0;
    }
    else {
      _Dst = (void *)fn_00608ac0(iVar1);
    }
  }
  *((int *)this) = (int)_Dst;
  ((int *)this)[1] = iVar1;
  ((int *)this)[2] = 0;
  fn_004e24a0(_Dst,(void *)*param_2,param_2[2]);
  iVar1 = param_2[2];
  ((int *)this)[2] = iVar1;
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + *((int *)this)) = 0;
  }
  return ((int *)this);
}

