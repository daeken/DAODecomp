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

extern "C" int g_00758e08;
struct Seed_00643040 { int __thiscall fn_00643040(byte param_2); };

// FUNCTION: DAO 0x00a43040
int __thiscall Seed_00643040::fn_00643040(byte param_2)
{
  if (param_2 < 0x40) {
    return (uint)param_2 * g_00758e08 + *(int *)(((int)this) + 0x304);
  }
  return 0;
}

