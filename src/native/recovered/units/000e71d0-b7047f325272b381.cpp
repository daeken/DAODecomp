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


extern "C" void * __cdecl fn_004e24a0(void * _Dst, void * _Src, size_t _Size);
struct Seed_000e71d0 { void __thiscall fn_000e71d0(void *param_2,size_t param_3); };

// FUNCTION: DAO 0x004e71d0
void __thiscall Seed_000e71d0::fn_000e71d0(void *param_2,size_t param_3)
{
  uint uVar1;
  
  uVar1 = (uint)*(ushort *)(((int)this) + 0x68);
  if ((int)(uVar1 + param_3) < 0x80) {
    fn_004e24a0((void *)(*(int *)(((int)this) + 100) + uVar1),param_2,param_3);
    *(short *)(((int)this) + 0x68) = *(short *)(((int)this) + 0x68) + (short)param_3;
    return;
  }
  fn_004e24a0((void *)(*(int *)(((int)this) + 100) + uVar1),param_2,0x80 - uVar1);
  fn_004e24a0(*(void **)(((int)this) + 100),
          (void *)((int)param_2 + (0x80 - (uint)*(ushort *)(((int)this) + 0x68))),
          (*(ushort *)(((int)this) + 0x68) - 0x80) + param_3);
  *(short *)(((int)this) + 0x68) = *(short *)(((int)this) + 0x68) + (short)param_3 + -0x80;
  return;
}

