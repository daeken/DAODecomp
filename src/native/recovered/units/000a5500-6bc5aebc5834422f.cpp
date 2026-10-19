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

extern "C" unsigned int __cdecl fn_000c7990(...); /* ABI/return type unknown, provisional declaration */
struct Seed_000a5500 { void __thiscall fn_000a5500(char param_2); };

// FUNCTION: DAO 0x004a5500
void __thiscall Seed_000a5500::fn_000a5500(char param_2)
{
  int iVar1;
  int *piVar2;
  
  iVar1 = fn_000c7990();
  if (iVar1 != 0) {
    piVar2 = (int *)fn_000c7990();
    *piVar2 = *piVar2 + 1;
  }
  if (param_2 == '\0') {
    *(undefined1 *)(((int)this) + 0x162) = 1;
  }
  return;
}

