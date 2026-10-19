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
typedef struct _Ctypevec _Ctypevec, *P_Ctypevec;

struct _Ctypevec {
    uint _Page;
    short *_Table;
    int _Delfl;
    wchar_t *_LocaleName;
};


extern "C" int __cdecl fn_004e0a81(int param_1, _Ctypevec * param_2);
struct Seed_000e2030 { byte * __thiscall fn_000e2030(byte *param_2,byte *param_3); };

// FUNCTION: DAO 0x004e2030
byte * __thiscall Seed_000e2030::fn_000e2030(byte *param_2,byte *param_3)
{
  int iVar1;
  
  if (param_2 != param_3) {
    do {
      iVar1 = fn_004e0a81((uint)*param_2,(_Ctypevec *)(((int)this) + 8));
      *param_2 = (byte)iVar1;
      param_2 = param_2 + 1;
    } while (param_2 != param_3);
  }
  return param_2;
}

