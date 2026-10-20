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
struct Seed_00091960 { size_t __thiscall fn_00091960(int param_2,int param_3); };

// FUNCTION: DAO 0x00491960
size_t __thiscall Seed_00091960::fn_00091960(int param_2,int param_3)
{
  int iVar1;
  size_t _Size;
  
  *(uint *)((uint)param_2 + 0x28ccu) = *(uint *)((uint)param_2 + 0x28ccu) + (uint)param_3;
  iVar1 = *(int *)((uint)param_2 + 0x28ccu);
  _Size = 0x1000;
  if ((int)((uint)iVar1 + 0x1000u) > *(int *)((uint)param_2 + 0x28d0u)) {
    _Size = *(uint *)((uint)param_2 + 0x28d0u) - (uint)iVar1;
    if ((int)_Size < 0) return _Size;
  }
  if (*(uint *)((uint)this + 0x28fcu) != 0) {
    if (_Size == 0) {
      return 0;
    }
    fn_004e24a0((void *)(*(uint *)((uint)param_2 + 0x28c8u) * 0x1000u + 0x8c8u + (uint)param_2),
            (void *)(*(uint *)((uint)this + 0x28fcu) + (uint)iVar1),_Size);
  }
  return _Size;
}

