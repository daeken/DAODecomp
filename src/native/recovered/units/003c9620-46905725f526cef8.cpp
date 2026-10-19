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
struct Seed_003c9620 { void __thiscall fn_003c9620(void *param_2,size_t param_3); };

// FUNCTION: DAO 0x007c9620
void __thiscall Seed_003c9620::fn_003c9620(void *param_2,size_t param_3)
{
  if (param_3 == *(size_t *)(((int)this) + 0x14)) {
    fn_004e24a0(*(void **)(((int)this) + 0x10),param_2,param_3);
  }
  return;
}

