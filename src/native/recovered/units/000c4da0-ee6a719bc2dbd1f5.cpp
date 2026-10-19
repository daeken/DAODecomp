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

extern "C" undefined * g_006ddc9c;
extern "C" unsigned int __cdecl fn_00013670(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00013770(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000c4da0 { undefined4 * __thiscall fn_000c4da0(undefined4 param_2); };

// FUNCTION: DAO 0x004c4da0
undefined4 * __thiscall Seed_000c4da0::fn_000c4da0(undefined4 param_2)
{
  undefined4 uVar1;
  
  *((undefined4 *)this) = (undefined4)(&g_006ddc9c);
  ((undefined4 *)this)[1] = 100;
  ((undefined4 *)this)[2] = 0;
  ((undefined4 *)this)[3] = param_2;
  uVar1 = fn_00013670();
  ((undefined4 *)this)[4] = uVar1;
  uVar1 = fn_00013770();
  ((undefined4 *)this)[5] = uVar1;
  return ((undefined4 *)this);
}

