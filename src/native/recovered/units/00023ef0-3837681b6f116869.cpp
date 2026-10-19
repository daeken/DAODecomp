// Provisional VC8 C++98 reconstruction.
extern "C" {
extern void* g_0081d9e0;
extern void* g_0081da08;
extern unsigned char g_006e19f0[];
extern unsigned char g_006e2668[];
extern unsigned char g_006e5558[];
extern unsigned char g_006e3638[];
extern unsigned char g_006e1a1c[];
extern unsigned char g_006e19d0[];
extern unsigned char g_006dff52[];
extern void __cdecl fn_004e4696(void*);
extern void* __cdecl fn_004e47aa(unsigned int);
extern void __cdecl fn_000136c0(void*);
extern void __cdecl fn_000444f0(void*, void*, unsigned int, void*);
extern void __cdecl fn_004e4677(void*, void*, void*);
extern void __cdecl fn_00045e80(void*, void*, unsigned int);
extern void* __cdecl fn_0001fc40(void*);
extern void __cdecl fn_00020510(void*, void*, void*);
}
struct C_1efd0 { void __thiscall fn_0001efd0(); };
struct C_1f530 { void __thiscall fn_0001f530(void*); };
struct C_1f960 { void __thiscall fn_0001f960(); };
struct C_20170 { int __thiscall fn_00020170(void*, void*, void*); };
struct C_244d0 { void* __thiscall fn_000244d0(void*, void*); };
struct C_1f9c0 { void* __thiscall fn_0001f9c0(void*, void*); };
struct C_1fa20 { void __thiscall fn_0001fa20(void*); };
struct C_1fb30 { void __thiscall fn_0001fb30(); };
struct C_23ef0 { void __thiscall fn_00023ef0(int); };
struct C_24030 { void __thiscall fn_00024030(int); };
struct C_24050 { void __thiscall fn_00024050(int); };
struct C_24060 { int __thiscall fn_00024060(); };
struct C_24090 { void __thiscall fn_00024090(int); };
struct C_240c0 { void* __thiscall fn_000240c0(int); };
struct C_241f0 { void __thiscall fn_000241f0(); };
struct C_244c0 { void __thiscall fn_000244c0(); };
struct C_24530 { void* __thiscall fn_00024530(void*, unsigned int); };
struct C_248c0 { int __thiscall fn_000248c0(void*, void*, unsigned int); };
struct Node24ce0 { unsigned int cap; unsigned int len; void* data; };
struct C_24ce0 { bool __thiscall fn_00024ce0(void*, void*); };

// FUNCTION: DAO 0x00423EF0
void __thiscall C_23ef0::fn_00023ef0(int v)
{
    *(int*)((char*)this + 0x14) = v;
}

// FUNCTION: DAO 0x00424030
void __thiscall C_24030::fn_00024030(int v)
{
    *(int*)((char*)this + 0x48) = v;
}

// FUNCTION: DAO 0x00424050
void __thiscall C_24050::fn_00024050(int v)
{
    *(int*)((char*)this + 0x4c) = v;
}

// FUNCTION: DAO 0x00424060
int __thiscall C_24060::fn_00024060()
{
    return *(int*)((char*)this + 0x4c);
}

// FUNCTION: DAO 0x00424090
void __thiscall C_24090::fn_00024090(int v)
{
    *(int*)((char*)this + 0x54) = v;
}

// FUNCTION: DAO 0x004240C0
void* __thiscall C_240c0::fn_000240c0(int flags)
{
    ((C_1efd0*)this)->fn_0001efd0();
    if (flags & 1)
        fn_000136c0(this);
    return this;
}

// FUNCTION: DAO 0x004241F0
void __thiscall C_241f0::fn_000241f0()
{
    void* p;
    void* alloc = g_0081d9e0;
    if (!alloc) {
        fn_004e4696((void*)g_006e19f0);
        alloc = g_0081d9e0;
    }
    if (alloc) {
        typedef void* (__thiscall *FAlloc0)(void*, int, int);
        FAlloc0 f = *(FAlloc0*)((char*)*(void**)alloc + 0x1c);
        p = f(alloc, 0, 0xc);
    } else {
        p = fn_004e47aa(0xc);
    }
    if (p) {
        *(void**)((char*)p + 4) = 0;
        *(void**)((char*)p + 8) = 0;
        *(void**)p = (void*)g_006e2668;
        ((C_1f530*)this)->fn_0001f530(p);
    } else {
        ((C_1f530*)this)->fn_0001f530(0);
    }
}

// FUNCTION: DAO 0x004244C0
void __thiscall C_244c0::fn_000244c0()
{
    ((C_1f960*)this)->fn_0001f960();
    *(void**)this = (void*)g_006e5558;
}

// FUNCTION: DAO 0x00424530
void* __thiscall C_24530::fn_00024530(void* a, unsigned int b)
{
    unsigned char* node = *(unsigned char**)((char*)this + 0x30);
    if (!node)
        return 0;
    if (!a)
        return 0;
    if (b < *(unsigned int*)((char*)this + 0x14))
        return 0;
    do {
        void* edx = *(void**)(node + 4);
        void* esi = *(void**)(node + 8);
        fn_00020510(edx, node + 0xc, a);
        node = (unsigned char*)esi;
    } while (node);
    return a;
}

// FUNCTION: DAO 0x00424630
__int64 __cdecl fn_00024630(void* a, unsigned int b, unsigned int c)
{
    char buf[0x40];
    void* p = fn_0001fc40(a);
    if (p) {
        fn_000444f0(p, buf, 0x40, (void*)g_006dff52);
        fn_004e4677(buf, (void*)g_006e1a1c, buf);
    }
    return ((__int64)c << 32) | b;
}

// FUNCTION: DAO 0x004248C0
int __thiscall C_248c0::fn_000248c0(void* a, void* b, unsigned int c)
{
    if (!*(void**)((char*)this + 0x30) && *(void**)((char*)this + 0x38)) {
        int r = ((C_20170*)a)->fn_00020170(*(void**)((char*)this + 0xc), *(void**)((char*)this + 0x10), (void*)c);
        if (r < 0) {
            *(int*)((char*)this + 0x20) = -100;
            return r;
        }
        *(int*)((char*)this + 0x14) = r;
        return r;
    }
    unsigned int len = 0;
    while (((char*)a)[len])
        ++len;
    unsigned int ebp = len + c + 0x20;
    void* saved = ((C_244d0*)this)->fn_000244d0(a, (void*)ebp);
    int r = ((C_20170*)a)->fn_00020170(*(void**)((char*)this + 0xc), *(void**)((char*)this + 0x10), (void*)c);
    if (r < 0) {
        ebp = (unsigned int)((C_1f9c0*)this)->fn_0001f9c0(saved, (void*)ebp);
        for (;;) {
            ((C_1fa20*)this)->fn_0001fa20((void*)ebp);
            r = ((C_20170*)a)->fn_00020170(*(void**)((char*)this + 0xc), *(void**)((char*)this + 0x10), (void*)c);
            if (r >= 0)
                break;
            ((C_1fb30*)this)->fn_0001fb30();
            void* obj = g_0081da08;
            typedef void* (__thiscall *F14)(void*);
            F14 f14 = *(F14*)((char*)*(void**)obj + 0x14);
            void* o2 = f14(obj);
            typedef int (__thiscall *F30)(void*);
            F30 f30 = *(F30*)((char*)*(void**)o2 + 0x30);
            ebp += f30(o2);
        }
    }
    *(int*)((char*)this + 0x14) += r;
    void* p = *(void**)((char*)this + 0x34);
    *(int*)((char*)p + 4) += r;
    return r;
}

// FUNCTION: DAO 0x00424CE0
bool __thiscall C_24ce0::fn_00024ce0(void* a, void* b)
{
    Node24ce0* node = *(Node24ce0**)((char*)b + 0x54);
    void* alloc;
    if (!node) {
        alloc = g_0081d9e0;
        if (!alloc) {
            fn_004e4696((void*)g_006e19f0);
            alloc = g_0081d9e0;
        }
        void* p;
        if (alloc) {
            typedef void* (__thiscall *FAlloc1)(void*, int, int);
            FAlloc1 f = *(FAlloc1*)((char*)*(void**)alloc + 0x1c);
            p = f(alloc, 0, 0xc);
        } else {
            p = fn_004e47aa(0xc);
        }
        node = (Node24ce0*)p;
        if (node) {
            node->cap = 0;
            node->len = 0;
            node->data = 0;
            *(void**)node = (void*)g_006e2668;
        }
        *(Node24ce0**)((char*)b + 0x54) = node;
    }
    alloc = g_0081d9e0;
    if (!alloc) {
        fn_004e4696((void*)g_006e19f0);
        alloc = g_0081d9e0;
    }
    void* obj = *(void**)((char*)this + 0x28);
    typedef unsigned int (__thiscall *FCap)(void*, void*);
    FCap fcap = *(FCap*)((char*)*(void**)obj + 0x24);
    node->cap = fcap(obj, a);
    typedef void* (__thiscall *FAlloc2)(void*, int, unsigned int);
    FAlloc2 fa = *(FAlloc2*)((char*)*(void**)alloc + 0x1c);
    node->data = fa(alloc, 1, node->cap + 4);
    void* tmp = fa(alloc, 0, *(unsigned int*)((char*)a + 0x10));
    void* p2 = fn_0001fc40((void*)g_006e3638);
    if (p2)
        fn_000444f0(p2, tmp, *(unsigned int*)((char*)a + 0x10), (void*)g_006dff52);
    else
        *(char*)tmp = 0;
    unsigned int n = 0;
    while (((char*)tmp)[n])
        ++n;
    fn_00045e80((char*)node->data + node->len, tmp, n);
    node->len += (n >> 2) * 3;
    typedef void (__thiscall *FFree)(void*, int, void*);
    FFree ff = *(FFree*)((char*)*(void**)alloc + 0x20);
    ff(alloc, 0, tmp);
    if (node->len < node->cap)
        return false;
    unsigned char local[0x24];
    *(unsigned int*)(local + 0x00) = *(unsigned int*)((char*)a + 0x18);
    *(unsigned int*)(local + 0x04) = *(unsigned int*)((char*)a + 0x1c) & 0xdfffffff;
    *(unsigned int*)(local + 0x08) = (unsigned int)node->data;
    *(unsigned int*)(local + 0x0c) = node->cap;
    *(unsigned int*)(local + 0x10) = 0;
    *(unsigned int*)(local + 0x14) = (unsigned int)g_006e19d0;
    *(unsigned int*)(local + 0x18) = *(unsigned int*)((char*)a + 4);
    *(unsigned short*)(local + 0x1c) = *(unsigned short*)((char*)a + 8);
    void* obj2 = *(void**)((char*)this + 4);
    typedef void (__thiscall *FCall)(void*, void*);
    FCall fc = *(FCall*)((char*)*(void**)obj2 + 0x10);
    fc((char*)this + 4, local);
    return true;
}
