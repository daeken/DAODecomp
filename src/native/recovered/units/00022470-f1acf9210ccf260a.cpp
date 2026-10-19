typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned long ulong;

extern unsigned char g_006dff52[];
extern unsigned char g_006e2da8[];
extern unsigned char g_006e2dc0[];
extern unsigned char g_006e19f0[];
extern unsigned char g_0081d9e0[];
extern unsigned char g_006e1a84[];
extern unsigned char g_006e1a1c[];
extern unsigned char g_006e3818[];
extern unsigned char g_006e3830[];
extern unsigned char g_006e3848[];
extern unsigned char g_006e3860[];
extern unsigned char g_006e5504[];

extern int __cdecl fn_004e1e2e(char*, const char*, ...);
extern int __cdecl fn_004e486d(char*, unsigned, const char*, ...);
extern int __cdecl fn_004e4677(const char*, const char*, ...);
extern void __cdecl fn_004e4696(const char*, ...);
extern void __cdecl fn_004e1a5a(void*);
extern int __fastcall fn_0001fc40(void*, void*, char*);
extern int __cdecl fn_0004444f0(void*, const void*, unsigned, const char*);
extern int __cdecl fn_000444430(const char*, int, int = 0);
extern void __cdecl fn_0001cec0(void*, void*, void*);
extern void __cdecl fn_0001ce70(void*, const char*);
extern void __cdecl fn_000421070(void*, void*, int, int, int);
extern int __fastcall fn_000438140(void*, void*, void*);
extern void __cdecl fn_00043aba0(void*, void*, void*, void*, int);

typedef void (__thiscall *FnThis2)(void*, void*, int);
typedef void (__cdecl *Fn3)(void*, void*, void*);

struct C223b0 { int fn_000223b0(char*, char*, int*); };
struct C22500 { char fn_00022500(char*, char*, char*, int); };
struct C225a0 { char fn_000225a0(char*, char*, char*); };
struct C226b0 { void* fn_000226b0(void*); };
struct C263a0 { char fn_000263a0(void*); };
struct C37650 { int fn_00037650(int); };
struct C380e0 { void fn_000380e0(void*, void*, void*, void*); };
struct C38600 { void fn_00038600(void*); };
struct C39420 { C39420* fn_00039420(); };
struct Node3bf50 { Node3bf50* left; Node3bf50* right; int pad[2]; int key; char data[1]; };
struct C3bf50 { void* fn_0003bf50(void*); };

// FUNCTION: DAO 0x004223B0
int C223b0::fn_000223b0(char* a1, char* a2, int* a3) {
    char buf[64];
    void* self = this;
    fn_004e1e2e(buf, (const char*)g_006e2dc0, *(void**)((char*)self + 4));
    void* found = (void*)fn_0001fc40(*(void**)self, 0, buf);
    if (!found) {
        if (a1) *a1 = 0;
        *(u32*)((char*)self + 4) = 0;
        return 0;
    }
    fn_0004444f0(found, a1, (unsigned)(ulong)a2, (const char*)g_006dff52);
    fn_004e1e2e(buf, (const char*)g_006e2da8, *(void**)((char*)self + 4));
    found = (void*)fn_0001fc40(*(void**)self, 0, buf);
    if (!found) {
        *a3 = -1;
        ++*(u32*)((char*)self + 4);
        return 1;
    }
    *a3 = fn_000444430((const char*)found, -1, -1);
    ++*(u32*)((char*)self + 4);
    return 1;
}

// FUNCTION: DAO 0x00422470
int __cdecl fn_00022470(void) {
    void* p = *reinterpret_cast<void**>(g_0081d9e0);
    if (!p) {
        fn_004e4696((const char*)g_006e19f0);
        p = *reinterpret_cast<void**>(g_0081d9e0);
    }
    return (int)p;
}

// FUNCTION: DAO 0x00422500
char C22500::fn_00022500(char* a1, char* a2, char* a3, int flag) {
    char buf[128];
    if (!flag) {
        fn_004e486d(buf, 128, (const char*)g_006e1a84, (char*)this + 0x28, a1, (char*)this + 8);
    } else {
        fn_004e486d(buf, 128, (const char*)g_006e1a84, (char*)this + 0x28, a1, (char*)this + 8);
    }
    void* found = (void*)fn_0001fc40(*(void**)((char*)this + 0x48), 0, buf);
    if (found) {
        fn_0004444f0(found, a1, (unsigned)(ulong)a2, (const char*)g_006dff52);
        return 1;
    }
    if (a1) *a1 = 0;
    if (a3) *a3 = 0;
    return 0;
}

// FUNCTION: DAO 0x004225A0
char C225a0::fn_000225a0(char* a1, char* a2, char* a3) {
    char buf[128];
    fn_004e486d(buf, 128, (const char*)g_006e1a84, (char*)this + 0x28, a1, (char*)this + 8);
    void* found = (void*)fn_0001fc40(*(void**)((char*)this + 0x48), 0, buf);
    int flag = (a2 != 0);
    if (found) {
        int r = fn_000444430((const char*)found, flag, 0);
        return (r != 0);
    }
    return (flag != 0);
}

// FUNCTION: DAO 0x004226B0
void* C226b0::fn_000226b0(void* a1) {
    void* obj = *reinterpret_cast<void**>(g_0081d9e0);
    if (!obj) {
        fn_004e4696((const char*)g_006e19f0);
        obj = *reinterpret_cast<void**>(g_0081d9e0);
    }
    void* vtbl = *reinterpret_cast<void**>(obj);
    void* m = *reinterpret_cast<void**>((char*)vtbl + 0x20);
    ((FnThis2)m)(obj, *(void**)((char*)this + 8), 1);
    *(u32*)((char*)this + 4) = 0;
    *(u32*)((char*)this) = 0;
    *(u32*)((char*)this + 8) = 0;
    if (((u32)a1 & 1) != 0) {
        void* obj2 = *reinterpret_cast<void**>(g_0081d9e0);
        if (!obj2) {
            fn_004e4696((const char*)g_006e19f0);
            obj2 = *reinterpret_cast<void**>(g_0081d9e0);
        }
        if (obj2) {
            void* vtbl2 = *reinterpret_cast<void**>(obj2);
            void* m2 = *reinterpret_cast<void**>((char*)vtbl2 + 0x20);
            ((FnThis2)m2)(obj2, this, 0);
        }
    }
    return this;
}

// FUNCTION: DAO 0x004263A0
char C263a0::fn_000263a0(void* a1) {
    char buf[64];
    char parsed[64];
    char str[32];
    int v0 = -1;
    int v1 = -1;
    char* p = (char*)a1;
    fn_004e1e2e(buf, (const char*)g_006e3860, *(void**)((char*)this + 4));
    void* found = (void*)fn_0001fc40(*(void**)this, 0, buf);
    if (!found) return 0;
    fn_0004444f0(found, parsed, 0x40, (const char*)g_006dff52);
    fn_004e4677(parsed, (const char*)g_006e1a1c, &v0, &v1);
    if ((v0 & v1) != -1) {
        *(int*)(p + 0x24) = v1;
        *(int*)(p + 0x20) = v0;
        *(int*)(p + 0x28) = 1;
    }
    fn_004e1e2e(buf, (const char*)g_006e3848, *(void**)((char*)this + 4));
    found = (void*)fn_0001fc40(*(void**)this, 0, buf);
    int r = 0;
    if (found) r = fn_000444430((const char*)found, 0, 0);
    *(int*)(p + 0x30) = r;
    fn_004e1e2e(buf, (const char*)g_006e3830, *(void**)((char*)this + 4));
    found = (void*)fn_0001fc40(*(void**)this, 0, buf);
    if (found) fn_0004444f0(found, p, 0x20, (const char*)g_006dff52);
    else *p = 0;
    fn_004e1e2e(buf, (const char*)g_006e3818, *(void**)((char*)this + 4));
    found = (void*)fn_0001fc40(*(void**)this, 0, buf);
    if (found) fn_0004444f0(found, str, 0x20, (const char*)g_006dff52);
    else str[0] = 0;
    void* vt = *(void**)(p + 0x34);
    void* m = *(void**)((char*)vt + 4);
    ((void (__thiscall *)(void*, char*))m)(p + 0x34, str);
    ++*(u32*)((char*)this + 4);
    return 1;
}

// FUNCTION: DAO 0x00437650
int C37650::fn_00037650(int code) {
    *(int*)((char*)this + 0x38) = code;
    switch (code) {
    case 0x63: return code;
    case 0x00: return 0;
    case 0x01: return (int)0xffffff9a;
    case 0x02: return (int)0xfffffd42;
    case 0x03: return (int)0xfffffd43;
    case 0x04: return (int)0xfffffd2e;
    case 0x05: return (int)0xfffffd3b;
    case 0x06: return (int)0xfffffd2f;
    case 0x07: return (int)0xfffffd33;
    }
    return 0;
}

// FUNCTION: DAO 0x004380E0
void C380e0::fn_000380e0(void* a1, void* a2, void* a3, void* fn) {
    typedef void (__cdecl *LocalFn3)(void*, void*, void*);
    ++*(u32*)((char*)this + 0x3c);
    void** begin = *(void***)((char*)this + 4);
    void** end = *(void***)((char*)this + 8);
    for (void** it = begin; it != end; ++it) {
        if (*it) ((LocalFn3)fn)(a1, a2, a3);
    }
    void* p = *(void**)((char*)this + 0x38);
    if (p) ((LocalFn3)fn)(a1, a2, a3);
    --*(u32*)((char*)this + 0x3c);
}

// FUNCTION: DAO 0x00438600
void C38600::fn_00038600(void* p) {
    while (p) {
        void* next = *(void**)((char*)p + 4);
        this->fn_00038600(*(void**)p);
        if ((char*)p >= (char*)this + 0x20 && (char*)p < (char*)this + 0x24) {
            *(void**)((char*)p) = *(void**)((char*)this + 0x18);
            *(void**)((char*)this + 0x18) = p;
        } else {
            fn_0001cec0((char*)this + 0x1c, p, *(void**)((char*)this + 0x28));
        }
        p = next;
    }
}

// FUNCTION: DAO 0x00439420
C39420* C39420::fn_00039420() {
    char local[4];
    local[0] = 0; local[1] = 0; local[2] = 0; local[3] = 0;
    fn_0001ce70(local, (const char*)g_006e5504);
    fn_000421070((char*)this + 0x2c, 0, 4, 0x18, 0x4b0);
    void* p = (char*)this + 0x2c;
    fn_000438140(this, 0, &p);
    return this;
}

// FUNCTION: DAO 0x0043BF50
void* C3bf50::fn_0003bf50(void* keyPtr) {
    Node3bf50* sentinel = (Node3bf50*)((char*)this + 4);
    Node3bf50* e = *(Node3bf50**)((char*)this + 0xc);
    Node3bf50* parent = sentinel;
    int key = *(int*)keyPtr;
    while (e) {
        if (e->key < key) {
            e = e->left;
        } else {
            parent = e;
            e = e->right;
        }
    }
    if (parent == sentinel || key < parent->key) {
        Node3bf50* n = 0;
        fn_00043aba0((char*)this + 4, n, &key, 0, 0);
    }
    return (char*)parent + 0x14;
}

// FUNCTION: DAO 0x00444430
int __cdecl fn_00044430(const char* s, int base, int def) {
    if (!s) return def;
    int sign = 1;
    int b = 10;
    char c = *s;
    if (c == 0x2d) { sign = -1; ++s; }
    else if (c == 0x24) { b = 0x10; ++s; }
    else if (c == 0x2b) { ++s; }
    int v = 0;
    for (;;) {
        u8 ch = (u8)*s;
        int d;
        if (ch >= 0x30 && ch <= 0x39) d = ch - 0x30;
        else if (ch >= 0x41 && ch <= 0x46) d = ch - 0x41 + 10;
        else if (ch >= 0x61 && ch <= 0x66) d = ch - 0x61 + 10;
        else break;
        if ((unsigned)d >= (unsigned)b) break;
        v = v * b + d;
        ++s;
    }
    return v * sign;
}
