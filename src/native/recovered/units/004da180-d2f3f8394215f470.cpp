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


extern "C" void * __cdecl fn_004e47aa(size_t _Size);
extern "C" void __cdecl fn_004e1a5a(void * _Memory);
struct Seed_004da180 { void __thiscall fn_004da180(int param_2); };

// FUNCTION: DAO 0x008da180
void __thiscall Seed_004da180::fn_004da180(int param_2)
{
  void *_Memory;
  void *pvVar1;
  int iVar2;
  
  ((int *)this)[2] = param_2;
  _Memory = (void *)*((int *)this);
  pvVar1 = fn_004e47aa(param_2 * 4);
  *((int *)this) = (int)pvVar1;
  iVar2 = 0;
  if (0 < ((int *)this)[1]) {
    do {
      *(undefined4 *)(*((int *)this) + iVar2 * 4) = *(undefined4 *)((int)_Memory + iVar2 * 4);
      iVar2 = iVar2 + 1;
    } while (iVar2 < ((int *)this)[1]);
  }
  if (_Memory != (void *)0x0) {
    fn_004e1a5a(_Memory);
  }
  return;
}

