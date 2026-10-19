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


extern "C" unsigned int __cdecl fn_0061e150(...); /* ABI/return type unknown, provisional declaration */
extern "C" unsigned int __cdecl fn_00047470(...); /* ABI/return type unknown, provisional declaration */
extern "C" void * __cdecl fn_004e19e0(void * _Dst, int _Val, size_t _Size);

// FUNCTION: DAO 0x00a1dee0
void fn_0061dee0(undefined4 *param_1)
{
  if ((param_1[0x18bb8] == 6) || (param_1[0x18bb8] == 3)) {
    fn_0061e150(param_1[1],param_1[0x18b9c]);
  }
  fn_00047470(*param_1);
  param_1[0x18bb8] = 0;
  fn_004e19e0(param_1 + 0x18b33,0,0x194);
  param_1[0x18ba0] = 0;
  param_1[0x18ba1] = 0;
  param_1[0x18ba2] = 0;
  param_1[0x18ba3] = 0;
  param_1[0x18b98] = 0xffffffff;
  return;
}

