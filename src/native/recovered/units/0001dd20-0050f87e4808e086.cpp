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

extern "C" unsigned int __cdecl fn_0001d960(...); /* ABI/return type unknown, provisional declaration */
struct Seed_0001dd20 { undefined4 __thiscall fn_0001dd20(int param_2); };

// FUNCTION: DAO 0x0041dd20
undefined4 __thiscall Seed_0001dd20::fn_0001dd20(int param_2)
{
  char cVar1;
  
  if (param_2 == 0) {
    return 2;
  }
  if (((*((byte *)this) & 1) != 0) &&
     ((*(short *)(param_2 + 6) < *(short *)(((byte *)this) + 10) ||
      ((*(short *)(param_2 + 6) == *(short *)(((byte *)this) + 10) &&
       (((char)*(byte *)(param_2 + 4) < (char)((byte *)this)[8] ||
        ((*(byte *)(param_2 + 4) == ((byte *)this)[8] && (*(char *)(param_2 + 5) < (char)((byte *)this)[9]))))))))
     )) {
    return 0xffffffff;
  }
  if ((*((byte *)this) & 2) != 0) {
    cVar1 = fn_0001d960(param_2,((byte *)this) + 0x10);
    if (cVar1 != '\0') {
      return 1;
    }
  }
  return 0;
}

