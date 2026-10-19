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


extern "C" unsigned int __cdecl fn_00048e30(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0004db90(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00048c20(...); /* ABI/return type unknown, provisional declaration */
extern "C" void * __cdecl fn_004e24a0(void * _Dst, void * _Src, size_t _Size);

// FUNCTION: DAO 0x0044dc00
int * fn_0004dc00(undefined4 *param_1,int param_2,void *param_3,size_t *param_4)
{
  int iVar1;
  int *piVar2;
  
  if (param_2 != 0) {
    return (int *)0x0;
  }
  iVar1 = fn_00048e30(*param_1,param_3,param_4);
  if (iVar1 == 0) {
    return (int *)0x0;
  }
  piVar2 = (int *)fn_0004db90();
  if (piVar2 == (int *)0x0) {
    fn_00048c20(iVar1);
    return (int *)0x0;
  }
  *piVar2 = iVar1;
  fn_004e24a0(piVar2 + 0x43,param_3,*param_4);
  piVar2[0x47] = 0x1f;
  return piVar2;
}

