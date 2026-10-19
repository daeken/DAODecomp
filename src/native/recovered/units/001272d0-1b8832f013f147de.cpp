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
typedef int BOOL;


extern "C" BOOL __stdcall fn_000e6160(void);

// FUNCTION: DAO 0x005272d0
void __fastcall fn_001272d0(int param_1)
{
  char cVar1;
  
  cVar1 = *(char *)(param_1 + 0x18);
  while (cVar1 == '\0') {
    fn_000e6160();
    cVar1 = *(char *)(param_1 + 0x18);
  }
  return;
}

