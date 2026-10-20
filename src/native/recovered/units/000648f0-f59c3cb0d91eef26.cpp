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

extern "C" unsigned long __readfsdword(unsigned long);
extern "C" void __writefsdword(unsigned long,unsigned long);
#pragma intrinsic(__readfsdword)
#pragma intrinsic(__writefsdword)

extern "C" undefined g_006718b8;

// FUNCTION: DAO 0x004648f0
unsigned int fn_00062970(...);
struct fn_00062cc0 { unsigned word; unsigned char flag; fn_00062cc0(int); fn_00062cc0(const fn_00062cc0&); ~fn_00062cc0(); };
struct ConstructionBase_000648f0 {
 unsigned unknown,begin,end,capacity;
 void __thiscall fn_00063c30(unsigned,fn_00062cc0);
 __forceinline ConstructionBase_000648f0() {begin=0;end=0;capacity=0;}
 __forceinline ~ConstructionBase_000648f0() {((void(__thiscall*)(void*))&fn_00062970)(this);}
};
struct fn_000648f0:ConstructionBase_000648f0 {fn_000648f0(int);};
fn_000648f0::fn_000648f0(int param_2) {
 if((unsigned)param_2>0) this->fn_00063c30(param_2,fn_00062cc0(0));
}

