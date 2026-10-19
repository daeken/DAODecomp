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

extern "C" undefined * g_00720b54;
extern "C" undefined * g_00720b38;
extern "C" undefined * g_00720b28;
extern "C" undefined * g_00720acc;
extern "C" undefined * g_00720ab8;
extern "C" undefined * g_00720a2c;
extern "C" unsigned int __cdecl fn_0039add0(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_000136c0(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0039b500 { undefined4 * __thiscall fn_0039b500(byte param_2); };

// FUNCTION: DAO 0x0079b500
undefined4 * __thiscall Seed_0039b500::fn_0039b500(byte param_2)
{
  *((undefined4 *)this) = (undefined4)(&g_00720b54);
  ((undefined4 *)this)[6] = (undefined4)(&g_00720b38);
  ((undefined4 *)this)[8] = (undefined4)(&g_00720b28);
  ((undefined4 *)this)[0xd] = (undefined4)(&g_00720acc);
  ((undefined4 *)this)[0xe] = (undefined4)(&g_00720ab8);
  ((undefined4 *)this)[0x1c] = (undefined4)(&g_00720a2c);
  fn_0039add0();
  if ((param_2 & 1) != 0) {
    fn_000136c0(((undefined4 *)this));
  }
  return ((undefined4 *)this);
}

