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


extern "C" char * __cdecl fn_004e29f0(char * _Dest, char * _Source, size_t _Count);
struct Seed_0001e130 { char * __thiscall fn_0001e130(char *param_2); };

// FUNCTION: DAO 0x0041e130
char * __thiscall Seed_0001e130::fn_0001e130(char *param_2)
{
  if (((char *)this) != param_2) {
    if (param_2 == (char *)0x0) {
      *((char *)this) = '\0';
      return ((char *)this);
    }
    fn_004e29f0(((char *)this),param_2,0x40);
  }
  return ((char *)this);
}

