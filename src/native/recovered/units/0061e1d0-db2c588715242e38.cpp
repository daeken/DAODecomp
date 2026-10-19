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

extern "C" unsigned int __cdecl fn_0004b9b0(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined g_00757de4;

// FUNCTION: DAO 0x00a1e1d0
void fn_0061e1d0(int param_1,int param_2,char *param_3)
{
  if (param_2 == 1) {
    if (*param_3 != '\0') {
      do {
        *param_3 = ((*param_3 != ' ') - 1U & 0xf6) + 0x2a;
        param_3 = param_3 + 1;
      } while (*param_3 != '\0');
      return;
    }
  }
  else if (param_2 == 2) {
    if (*(char *)(param_1 + 0xc) == '\0') {
      fn_0004b9b0(param_3,&g_00757de4,5);
      return;
    }
    fn_0004b9b0(param_3,(char *)(param_1 + 0xc),0x20);
  }
  return;
}

