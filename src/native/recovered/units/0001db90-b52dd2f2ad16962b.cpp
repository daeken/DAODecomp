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
typedef longlong __time64_t;

typedef struct tm tm, *Ptm;

struct tm {
    int tm_sec;
    int tm_min;
    int tm_hour;
    int tm_mday;
    int tm_mon;
    int tm_year;
    int tm_wday;
    int tm_yday;
    int tm_isdst;
};


extern "C" __time64_t __cdecl fn_004e4e3a(tm * _Tm);

// FUNCTION: DAO 0x0041db90
__time64_t __fastcall fn_0001db90(int param_1)
{
  __time64_t _Var1;
  tm local_24;
  
  local_24.tm_year = *(short *)(param_1 + 6) + -0x76c;
  local_24.tm_mon = *(char *)(param_1 + 4) + -1;
  local_24.tm_mday = (int)*(char *)(param_1 + 5);
  local_24.tm_hour = (int)*(char *)(param_1 + 8);
  local_24.tm_min = (int)*(char *)(param_1 + 9);
  local_24.tm_sec = (int)*(char *)(param_1 + 10);
  local_24.tm_isdst = 0;
  _Var1 = fn_004e4e3a(&local_24);
  return _Var1;
}

