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
typedef uint size_t;


extern "C" void * __cdecl fn_004e19e0(void * _Dst, int _Val, size_t _Size);

// FUNCTION: DAO 0x0086e580
void __fastcall fn_0046e580(undefined4 *param_1)
{
  *param_1 = 0;
  param_1[1] = 0;
  fn_004e19e0(param_1 + 2,0,0x348);
  fn_004e19e0(param_1 + 0xd4,0,0x40);
  fn_004e19e0(param_1 + 0xe4,0,0x840);
  fn_004e19e0(param_1 + 0x2f4,0,0x380);
  param_1[0x3d4] = 0;
  fn_004e19e0(param_1 + 0x3d5,0,0x40);
  fn_004e19e0(param_1 + 0x3e5,0,0x40);
  param_1[0x3f5] = 0;
  return;
}

