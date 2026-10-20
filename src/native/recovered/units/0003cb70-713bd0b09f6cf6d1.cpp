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

unsigned int __cdecl fn_0001ce70(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_00033270(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_0003c3a0(...); /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x0043cb70
int * fn_0003cb70(int *param_1,undefined4 *param_2,undefined4 *param_3,int param_4)
{
  undefined4 *puVar1;
  
  *param_1 = param_4;
  for (; param_2 != param_3; param_2 = param_2 + 0x22) {
    puVar1 = (undefined4 *)*param_1;
    if (puVar1 != (undefined4 *)0x0) {
      *puVar1 = 0;
      puVar1[1] = 0;
      puVar1[2] = 0;
      ((unsigned int(__thiscall*)(void*,void*))&fn_0001ce70)(puVar1 + 3,param_2 + 3);
      ((unsigned int(__thiscall*)(void*,unsigned int,unsigned int))&fn_00033270)(puVar1,*param_2,param_2[1]);
      ((unsigned int(__thiscall*)(void*,void*))&fn_0003c3a0)(puVar1 + 4,param_2 + 4);
    }
    *param_1 = (int)((uint)*param_1 + 0x88u);
  }
  return param_1;
}

