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

extern "C" unsigned int __cdecl fn_004e11f2(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_003cfff0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_003d4bf0 { void __thiscall fn_003d4bf0(int *param_2,int param_3,int param_4,int param_5,int param_6); };

// FUNCTION: DAO 0x007d4bf0
void __thiscall Seed_003d4bf0::fn_003d4bf0(int *param_2,int param_3,int param_4,int param_5,int param_6)
{
  undefined4 uVar1;
  
  if ((param_3 == 0) || (param_3 != param_5)) {
    fn_004e11f2();
  }
  if (param_4 != param_6) {
    uVar1 = fn_003cfff0(param_6,*(undefined4 *)(((int)this) + 8),param_4);
    *(undefined4 *)(((int)this) + 8) = uVar1;
  }
  param_2[1] = param_4;
  *param_2 = param_3;
  return;
}

