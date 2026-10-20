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

unsigned int __cdecl fn_000b5410(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_000b51e0(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_000b5cd0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000b63f0 { void __thiscall fn_000b63f0(int param_2); };

// FUNCTION: DAO 0x004b63f0
void __thiscall Seed_000b63f0::fn_000b63f0(int param_2)
{
  int *piVar1;
  undefined4 uVar2;
  
  ((uint(__thiscall*)(void*,unsigned int))&fn_000b5410)(this,param_2);
  *(undefined1 *)((uint)param_2 + 0x2cu) = *(undefined1 *)((uint)this + 0x2cu);
  *(undefined4 *)((uint)param_2 + 0x30u) = *(undefined4 *)((uint)this + 0x30u);
  ((uint(__thiscall*)(void*,void*,unsigned int))&fn_000b51e0)((void*)((uint)param_2 + 0x34u),*(undefined4 **)((uint)this + 0x34u) + 2,**(undefined4 **)((uint)this + 0x34u));
  *(undefined4 *)((uint)param_2 + 0x38u) = *(undefined4 *)((uint)this + 0x38u);
  *(undefined4 *)((uint)param_2 + 0x3cu) = *(undefined4 *)((uint)this + 0x3cu);
  *(undefined4 *)((uint)param_2 + 0x40u) = *(undefined4 *)((uint)this + 0x40u);
  *(undefined1 *)((uint)param_2 + 0x44u) = *(undefined1 *)((uint)this + 0x44u);
  for (piVar1 = *(int **)((uint)this + 0x18u); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[10]) {
    uVar2 = ((uint(__thiscall*)(void*))(**(code **)(*(uint*)piVar1 + 0x3cu)))(piVar1);
    ((uint(__thiscall*)(void*,unsigned int))&fn_000b5cd0)((void*)param_2,uVar2);
  }
  return;
}

