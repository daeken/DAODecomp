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

unsigned int __cdecl fn_00112a10(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_004e11f2(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_001b7c50(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000e6f50 { void __thiscall fn_000e6f50(undefined4 param_2); };

// FUNCTION: DAO 0x004e6f50
void __thiscall Seed_000e6f50::fn_000e6f50(undefined4 param_2)
{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  undefined1 local_8 [8];
  
  piVar4 = (int *)((uint(__thiscall*)(void*,void*,undefined4))&fn_00112a10)(this,local_8,param_2);
  iVar1 = *piVar4;
  iVar2 = piVar4[1];
  iVar3 = *(int *)((uint)this + 4u);
  if ((iVar1 == 0) || (iVar1 != ((int)this))) {
    fn_004e11f2();
  }
  if (iVar2 != iVar3) {
    if (iVar1 == 0) {
      fn_004e11f2();
    }
    if (iVar2 == *(int *)((uint)iVar1 + 4u)) {
      fn_004e11f2();
    }
    undefined4* observed_receiver = *(undefined4 **)((uint)iVar2 + 0x28u);
    if (observed_receiver != (undefined4*)0) {
      ((uint(__thiscall*)(void*,uint))(**(code **)*observed_receiver))(observed_receiver,1u);
    }
    ((uint(__thiscall*)(void*,void*,int,int))&fn_001b7c50)(this,local_8,iVar1,iVar2);
  }
  return;
}

