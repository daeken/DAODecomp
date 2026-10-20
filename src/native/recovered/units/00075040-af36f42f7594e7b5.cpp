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

extern "C" undefined g_006cbe5b;
extern "C" uint g_00815234;
extern "C" unsigned int __cdecl fn_00013660(...); /* ABI/return type unknown, provisional declaration */
unsigned int __cdecl fn_000d2070(...); /* ABI/return type unknown, provisional declaration */
extern "C" undefined * g_006e891c;

// FUNCTION: DAO 0x00475040
extern "C" void __cdecl fn_000b9080(void*);
struct EHConstruction_00075040 {unsigned int opaque_word;
__forceinline static void *operator new(unsigned int n){return (void*)fn_00013660(n);}
__forceinline static void operator delete(void*p){fn_000b9080(p);}
__forceinline EHConstruction_00075040() {
    ((unsigned int (__thiscall *)(void *))(&fn_000d2070))((void *)((undefined4*)this));
    *((undefined4*)this) = (undefined4)(&g_006e891c);
    }
};
typedef char EHConstruction_00075040_Size[(sizeof(EHConstruction_00075040)==4)?1:-1];
undefined4 * fn_00075040(void)
{ return (undefined4*)new EHConstruction_00075040(); }

