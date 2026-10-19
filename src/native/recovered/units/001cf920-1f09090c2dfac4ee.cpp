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

extern "C" undefined g_0082be00;
struct Seed_001cf920 { undefined * __thiscall fn_001cf920(int param_2); };

// FUNCTION: DAO 0x005cf920
undefined * __thiscall Seed_001cf920::fn_001cf920(int param_2)
{
  if ((param_2 <= *(int *)(((int)this) + 0x84)) && (*(int *)(((int)this) + 0x80) != 0)) {
    return (undefined *)(*(int *)(((int)this) + 0x80) + param_2 * 0x1c);
  }
  return &g_0082be00;
}

