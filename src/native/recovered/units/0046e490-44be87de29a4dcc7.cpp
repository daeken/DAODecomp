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

// FUNCTION: DAO 0x0086e490
void __fastcall fn_0046e490(undefined4 *param_1)
{
  *param_1 = 0;
  fn_004e19e0(param_1 + 1,0,0x40);
  fn_004e19e0(param_1 + 0x11,0,0x1000);
  fn_004e19e0(param_1 + 0x411,0,0x100);
  param_1[0x451] = 0;
  fn_004e19e0(param_1 + 0x452,0,0x40);
  fn_004e19e0(param_1 + 0x462,0,0xe00);
  fn_004e19e0(param_1 + 0x7e2,0,0x100);
  fn_004e19e0(param_1 + 0x822,0,0x348);
  fn_004e19e0(param_1 + 0x8f4,0,0x40);
  fn_004e19e0(param_1 + 0x904,0,0x840);
  fn_004e19e0(param_1 + 0xb14,0,0x380);
  param_1[0xbf4] = 0;
  fn_004e19e0(param_1 + 0xc25,0,0x40);
  param_1[0xc35] = 0;
  return;
}

