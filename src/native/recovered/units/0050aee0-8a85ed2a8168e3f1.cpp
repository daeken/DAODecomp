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

extern "C" undefined * g_00747f14;
extern "C" unsigned int __cdecl fn_005f4e90(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_005f76b0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_0050aeb0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_005f75b0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_005f7100(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_005f6d60(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0050aee0 { undefined4 * __thiscall fn_0050aee0(undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5); };

// FUNCTION: DAO 0x0090aee0
undefined4 * __thiscall Seed_0050aee0::fn_0050aee0(undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)
{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  *((undefined4 *)this) = (undefined4)(&g_00747f14);
  puVar1 = ((undefined4 *)this) + 2;
  uVar2 = fn_005f4e90(((undefined4 *)this) + 0x5c);
  *puVar1 = uVar2;
  fn_005f76b0(puVar1,0x3e,0x168);
  fn_0050aeb0(puVar1,param_2);
  ((undefined4 *)this)[9] = param_3;
  ((undefined4 *)this)[10] = param_4;
  ((undefined4 *)this)[0xb] = 3;
  ((undefined4 *)this)[0xc] = 2;
  fn_005f75b0(puVar1);
  fn_005f7100(puVar1,param_5,1);
  fn_005f6d60(puVar1,1);
  return ((undefined4 *)this);
}

