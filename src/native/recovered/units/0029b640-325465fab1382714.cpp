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

extern "C" unsigned int __cdecl fn_0029a7a0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0029b640 { void __thiscall fn_0029b640(char param_2); };

// FUNCTION: DAO 0x0069b640
void __thiscall Seed_0029b640::fn_0029b640(char param_2)
{
  if (*(char *)(((int)this) + 0x23c) != param_2) {
    *(char *)(((int)this) + 0x23c) = param_2;
    fn_0029a7a0();
  }
  return;
}

