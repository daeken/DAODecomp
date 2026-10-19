typedef unsigned char u8;
typedef unsigned int u32;
typedef void* PVOID;

extern "C" int __cdecl fn_00006a60(...);
extern "C" int __cdecl fn_000b8af0(...);
extern "C" int __cdecl fn_00173ed0(...);
extern "C" int __cdecl fn_000c0d90(...);
extern "C" int __cdecl fn_00008280(...);
extern "C" int __cdecl fn_000c9a90(...);
extern "C" int __cdecl fn_001389f0(...);
extern "C" int __cdecl fn_001d7080(...);
extern "C" int __cdecl fn_000c2ab0(...);
extern "C" int __cdecl fn_000c0a50(...);
extern "C" int __cdecl fn_00006030(...);
extern "C" int __cdecl fn_004714c0(...);
extern "C" int __cdecl fn_000c0db0(...);
extern "C" int __cdecl fn_00008320(...);
extern "C" int __cdecl fn_004e1613(...);
extern "C" int __cdecl fn_000bd560(...);
extern "C" int __cdecl fn_000bded0(...);
extern "C" int __cdecl fn_0007c870(...);
extern "C" int __cdecl fn_004e11f2(...);
extern "C" int __cdecl fn_000cb2b0(...);
extern "C" int __cdecl fn_000c3360(...);
extern "C" int __cdecl fn_000bf350(...);
extern "C" int __cdecl fn_000c3510(...);
extern "C" int __cdecl fn_000c3420(...);
extern "C" int __cdecl fn_00013660(...);
extern "C" int __cdecl fn_000c9170(...);
extern "C" int __cdecl fn_000c89f0(...);
extern "C" int __cdecl fn_004e2da2(...);
extern "C" int __cdecl fn_000c2510(...);
extern "C" int __cdecl fn_000c8b70(...);
extern "C" int __cdecl fn_004e21ac(...);
extern "C" int __cdecl fn_004e7ea0(...);
extern "C" int __cdecl fn_000c2ad0(...);
extern "C" int __cdecl fn_000c3250(...);
extern "C" int __cdecl fn_000c36c0(...);
extern "C" int __cdecl fn_000c9300(...);
extern "C" int __cdecl fn_004e47aa(...);
extern "C" int __cdecl fn_004e7e82(...);
extern "C" int __cdecl fn_004e1a5a(...);
extern "C" int __cdecl fn_000c8af0(...);
extern "C" int __cdecl fn_000cb300(...);
extern "C" int __cdecl fn_000c26b0(...);
extern "C" int __cdecl fn_000c1270(...);
extern "C" int __cdecl fn_000136c0(...);
extern "C" int __cdecl fn_000c0de0(...);
extern "C" int __cdecl fn_000c1240(...);
extern "C" int __cdecl fn_001b6e30(...);

typedef int (__cdecl *Fn3)(int, void*, void*);
extern "C" Fn3 g_006da17c;

struct C_4BE470 { unsigned char* __thiscall get(void* key); };
struct C_4BF3D0 { void __thiscall run(); };
struct C_4CA620 { unsigned char __thiscall insert(void* a, void* b); };
struct C_4E6530 { unsigned char __thiscall call(void* a); };

// FUNCTION: DAO 0x4072E0
extern "C" void __cdecl fn_000072e0(void)
{
    fn_00006a60();
}

// FUNCTION: DAO 0x409EA0
extern "C" unsigned char __stdcall fn_00009ea0(void* a0, void* a1, void* a2, void* a3, void* a4)
{
    struct L { int x0; int x1; int x2; u8 x3; } l = {0,0,0,0};
    void* v = 0;
    fn_000c0d90(&l);
    fn_00008280(&v);
    if (!fn_000c9a90(a1, &v, &l)) return 0;
    fn_001389f0(&v);
    fn_000c0d90(&v);
    fn_001d7080(&l, &v);
    fn_000c2ab0(&v, &l);
    fn_00006030(&v, a4);
    (void)a0; (void)a2; (void)a3;
    return 1;
}

// FUNCTION: DAO 0x413670
extern "C" void __cdecl fn_00013670(void)
{
    fn_000b8af0();
}

// FUNCTION: DAO 0x4BE470
unsigned char* __thiscall C_4BE470::get(void* key)
{
    void* p = (void*)(u32)fn_000bd560(key);
    if (!p) { fn_004e11f2(); return 0; }
    void* q = (void*)(u32)fn_000bded0(this, p, key);
    if (!q) { fn_004e11f2(); return 0; }
    fn_0007c870((char*)q + 0x34);
    fn_0007c870((char*)q + 0x1c);
    return (unsigned char*)((char*)q + 0x10);
}

// FUNCTION: DAO 0x4BF3D0
void __thiscall C_4BF3D0::run()
{
    if (!*((u8*)this + 0x878)) return;
    void* obj = *((void**)((char*)this + 0x880));
    fn_000cb2b0(obj, -1);
    void* p38 = *((void**)((char*)this + 0x38));
    if (p38) {
        void** vt = *((void***)p38);
        typedef int (__thiscall *FnThisInt)(int);
        if (vt) ((FnThisInt)vt[0])(1);
        *((void**)((char*)this + 0x38)) = 0;
    }
    fn_000c3360((char*)this + 0x1c, this);
    fn_000bf350((char*)this + 0x1c, 0x5f, (char*)this + 0x44);
    fn_000c3510((char*)this + 0x1c, 0xaf01c8);
    void* n = (void*)(u32)fn_00013660(0x48);
    if (n) {
        fn_000c9170(n, &obj, 2);
        *((void**)((char*)this + 0x38)) = n;
        fn_000c89f0(n, 0, 0, *((u8*)0xaf0462));
    }
    fn_000c2510((char*)this + 0x90, 0xc2be00);
    if (*((u8*)this + 0x87c)) {
        fn_000c8b70(*((void**)((char*)this + 0x38)));
    }
    fn_004e21ac((char*)this + 0x18);
    fn_004e7ea0((char*)this + 0x1c);
    fn_000c2ad0((char*)this + 0x90, &obj);
    fn_000c3250((char*)this + 0x90, 0, obj);
    fn_000c36c0((char*)this + 0x90, 0xaf0120);
    fn_000c9300(*((void**)((char*)this + 0x38)), (char*)this + 0x90, 0);
    fn_000cb300(*((void**)((char*)this + 0x880)));
    fn_000c0db0((char*)this + 0xac);
}

// FUNCTION: DAO 0x4C35F0
extern "C" void* __cdecl fn_000c35f0(void* a0, void* a1, void* a2)
{
    void* local = 0;
    fn_000c0d90(&local);
    fn_000c26b0(&local, a1, a2);
    fn_000c1270(&local, 0, -1);
    fn_000136c0(&local);
    return a0;
}

// FUNCTION: DAO 0x4CA620
unsigned char __thiscall C_4CA620::insert(void* a, void* b)
{
    void* p = *((void**)this);
    void* prev = 0;
    while (p) {
        if (fn_000c0de0(p, a)) return 1;
        if (fn_000c1240(p, a)) break;
        prev = p;
        p = *((void**)((char*)p + 0x38));
    }
    if (!p) {
        void* n = (void*)(u32)fn_00013660(0x3c);
        if (!n) return 0;
        fn_001b6e30(n);
        fn_000c2ab0(n, a);
        fn_000c2ab0((char*)n + 0x1c, b);
        *((void**)((char*)n + 0x38)) = p;
        if (prev) *((void**)((char*)prev + 0x38)) = n;
        else *((void**)this) = n;
    }
    return 1;
}

// FUNCTION: DAO 0x4E6530
unsigned char __thiscall C_4E6530::call(void* a)
{
    void* p = *((void**)this);
    g_006da17c(0, a, p);
    return 1;
}

// FUNCTION: DAO 0x5744E0
extern "C" void __cdecl fn_001744e0(void)
{
    fn_00173ed0();
}
