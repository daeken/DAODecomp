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

extern "C" unsigned int __cdecl fn_006085c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0060a8a0 { void __thiscall fn_0060a8a0(int param_2); };

// FUNCTION: DAO 0x00a0a8a0
void __thiscall Seed_0060a8a0::fn_0060a8a0(int param_2)
{
  if (param_2 != *((int *)this)) {
    *(undefined4 *)(*(int *)(param_2 + 8) + 4) = *(undefined4 *)(param_2 + 4);
    *(undefined4 *)(*(int *)(param_2 + 4) + 8) = *(undefined4 *)(param_2 + 8);
    fn_006085c0(param_2,0xc);
    ((int *)this)[1] = ((int *)this)[1] + -1;
  }
  return;
}

