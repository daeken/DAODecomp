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

extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_00163630 { void __thiscall fn_00163630(int *param_2); };

// FUNCTION: DAO 0x00563630
void __thiscall Seed_00163630::fn_00163630(int *param_2)
{
  if (param_2 != (int *)0x0) {
    if (*param_2 != 0) {
      fn_000136c0(*param_2);
      *param_2 = 0;
    }
    if (param_2[5] != 0) {
      fn_000136c0(param_2[5]);
      param_2[5] = 0;
    }
    if (param_2[6] != 0) {
      fn_000136c0(param_2[6]);
      param_2[6] = 0;
    }
    if (param_2[9] != 0) {
      fn_000136c0(param_2[9]);
      param_2[9] = 0;
    }
    if (param_2[10] != 0) {
      fn_000136c0(param_2[10]);
      param_2[10] = 0;
    }
    if (param_2[0xd] != 0) {
      fn_000136c0(param_2[0xd]);
      param_2[0xd] = 0;
    }
    fn_000136c0(param_2);
    *(undefined4 *)(((int)this) + 0x480) = 0;
    *(undefined1 *)(((int)this) + 0x445) = 0;
  }
  return;
}

