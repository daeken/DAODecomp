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

unsigned int __cdecl fn_000d9f10(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_000d5230(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_00074e10(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000783b0 { void __thiscall fn_000783b0(undefined4 param_2,undefined4 param_3); };

// FUNCTION: DAO 0x004783b0
void __thiscall Seed_000783b0::fn_000783b0(undefined4 param_2,undefined4 param_3)
{
  uint uVar1;
  int iVar2;
  undefined1 local_10 [16];
  
  ((unsigned int(__thiscall*)(void*,void*,unsigned int))&fn_000d9f10)((void*)**(unsigned int**)this,local_10,*(undefined4 *)(((int)this) + 8));
  iVar2 = ((unsigned int(__thiscall*)(void*,unsigned int))&fn_000d5230)(local_10,param_2);
  if ((((iVar2 != 0) && (uVar1 = *(uint *)(iVar2 + 4), (((byte)(uVar1 >> 0x1f) & 1) == 0))) &&
      (((byte)(uVar1 >> 0x1d) & 1) == 0)) && ((((byte)(uVar1 >> 0x1e) & 1) == 0 && ((uVar1 & 0xffff) == 5)))) {
    ((unsigned int(__thiscall*)(void*,unsigned int,unsigned int))&fn_00074e10)(*(void**)this,*(uint *)(iVar2 + 8) + *(uint *)(((int)this) + 4),param_3);
  }
  return;
}

