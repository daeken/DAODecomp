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

struct Seed_0046bcc0 { void __thiscall fn_0046bcc0(undefined1 param_2,undefined1 param_3,undefined1 param_4,undefined1 param_5); };

// FUNCTION: DAO 0x0086bcc0
void __thiscall Seed_0046bcc0::fn_0046bcc0(undefined1 param_2,undefined1 param_3,undefined1 param_4,undefined1 param_5)
{
  *(undefined1 *)(((int)this) + 0x39) = param_2;
  *(undefined1 *)(((int)this) + 0x3a) = param_3;
  *(undefined1 *)(((int)this) + 0x3b) = param_4;
  *(undefined1 *)(((int)this) + 0x3c) = param_5;
  return;
}

