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

// FUNCTION: DAO 0x00a3d220
void __fastcall fn_0063d220(int *param_1)
{
  if (param_1[2] != 0) {
    fn_000136c0(param_1[2]);
    param_1[2] = 0;
  }
  if (param_1[4] != 0) {
    fn_000136c0(param_1[4]);
    param_1[4] = 0;
  }
                    /* WARNING: Could not recover jumptable at 0x00a3d25f. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(**(int **)(*param_1 + 0x1968) + 0x58))();
  return;
}

