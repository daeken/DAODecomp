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
struct Seed_000a4a70 { void __thiscall fn_000a4a70(void *param_2,size_t param_3); };

// FUNCTION: DAO 0x004a4a70
void __thiscall Seed_000a4a70::fn_000a4a70(void *param_2,size_t param_3)
{
  fn_004e24a0(*(void **)(((int)this) + 4),param_2,param_3);
  *(int *)(((int)this) + 4) = *(int *)(((int)this) + 4) + param_3;
  *(int *)(((int)this) + 0xc) = *(int *)(((int)this) + 0xc) + param_3;
  return;
}

