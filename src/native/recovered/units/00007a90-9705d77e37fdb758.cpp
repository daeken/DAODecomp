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

extern "C" void * _AddressOfReturnAddress(void);
#pragma intrinsic(_AddressOfReturnAddress)

extern "C" unsigned long __readfsdword(unsigned long);
extern "C" void __writefsdword(unsigned long,unsigned long);
#pragma intrinsic(__readfsdword)
#pragma intrinsic(__writefsdword)

extern "C" undefined g_00686b3b;
extern "C" uint g_00815234;
extern "C" unsigned int __cdecl fn_00013660(...); /* ABI/return type unknown, provisional declaration */
 /* ABI/return type unknown, provisional declaration */

// FUNCTION: DAO 0x00407a90
extern "C" void __cdecl fn_000b9080(void*);
struct fn_000075f0 {
 char opaque[32];
 __forceinline static void *operator new(unsigned n) {return (void*)fn_00013660(n);}
 __forceinline static void operator delete(void*p) {fn_000b9080(p);}
 fn_000075f0(int);
};
undefined4 fn_00007a90(int *param_1)
{
 if(param_1 && !*param_1) *param_1=(int)new fn_000075f0(0);
 return 2;
}

