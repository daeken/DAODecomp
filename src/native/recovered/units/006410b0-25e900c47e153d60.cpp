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
typedef ulong DWORD;


extern "C" DWORD __stdcall fn_0001e870(void);
struct Seed_006410b0 { undefined4 __thiscall fn_006410b0(uint param_2); };

// FUNCTION: DAO 0x00a410b0
undefined4 __thiscall Seed_006410b0::fn_006410b0(uint param_2)
{
  DWORD DVar1;
  
  if ((param_2 < *(uint *)(((int)this) + 0x30)) &&
     (*(char *)(param_2 + *(int *)(((int)this) + 0x34)) != '\0')) {
    DVar1 = fn_0001e870();
    *(DWORD *)(*(int *)(((int)this) + 0x38) + param_2 * 4) = DVar1;
    return 1;
  }
  return 0;
}

