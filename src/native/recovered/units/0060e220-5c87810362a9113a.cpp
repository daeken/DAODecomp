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

struct Seed_0060e220 { uint __thiscall fn_0060e220(int param_2); };

// FUNCTION: DAO 0x00a0e220
uint __thiscall Seed_0060e220::fn_0060e220(int param_2)
{
  uint uVar1;
  uint uVar2;
  int *piVar3;
  
  uVar1 = (*(undefined4 **)(((int)this) + 0x28))[2];
  uVar2 = 0;
  if (((unsigned int)(uVar1)) > 0u) {
    piVar3 = (int *)**(undefined4 **)(((int)this) + 0x28);
    do {
      if (param_2 == *piVar3) {
        return uVar2;
      }
      uVar2 = uVar2 + 1;
      piVar3 = piVar3 + 1;
    } while (uVar2 < uVar1);
  }
  return 0xffffffff;
}

