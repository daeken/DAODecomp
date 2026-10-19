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

extern "C" unsigned int __cdecl fn_00585fe0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined g_0083fb72;
struct Seed_00587a30 { int * __thiscall fn_00587a30(int *param_2,int param_3,int *param_4); };

// FUNCTION: DAO 0x00987a30
int * __thiscall Seed_00587a30::fn_00587a30(int *param_2,int param_3,int *param_4)
{
  int *piVar1;
  int iVar2;
  
  piVar1 = (int *)(((int)this) + 0x14);
  iVar2 = fn_00585fe0(piVar1,&param_3,&g_0083fb72);
  if (iVar2 != -1) {
    if (param_4 != (int *)0x0) {
      *param_4 = param_3 - *(int *)(*(int *)(*piVar1 + iVar2 * 4) + 0x1c);
    }
    *param_2 = (int)piVar1;
    param_2[1] = iVar2;
    return param_2;
  }
  *param_2 = 0;
  param_2[1] = -1;
  return param_2;
}

