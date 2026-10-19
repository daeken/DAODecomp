typedef unsigned int u32;
typedef unsigned char u8;

extern void* __cdecl fn_00013660(u32);
extern void __cdecl fn_004e11f2(void);
extern void __cdecl fn_000136c0(void*);
extern void* __cdecl fn_0066b250(void*,void*,void*,void*,void*,void*);
extern void __cdecl fn_0066bbe0(void*,void*,void*);
extern void* __stdcall fn_00006ce0(void*,void*,void*);
extern void __stdcall fn_000ceee0(void*,void*);
extern void* __cdecl fn_0046bce0(void*,u32);
extern void __cdecl fn_00369830(void);
extern void __cdecl fn_000ccd70(void*,u32,void*,void*,void*,void*);
extern void* __cdecl fn_004740b0(void);

struct H_29c340 { void fn_0029c340(); };
struct H_4714c0 { u32 fn_004714c0(); };
struct H_8390 { u8 fn_00008390(void*); };
struct H_f3670 { void fn_000f3670(u32); };
struct H_6880 { void fn_00006880(); };
struct H_16a180 { void fn_0016a180(void*,void*,void*,void*,void*,void*,void*); };
struct H_e7d30 { void fn_000e7d30(u32); };
struct H_289d60 { void fn_00289d60(void*,void*,void*,void*,void*,void*,void*); };
struct H_ac430 { void fn_000ac430(void*); };
struct H_c2510 { void fn_000c2510(void*); };
struct H_c2ab0 { void fn_000c2ab0(void*); };
struct H_495090 { void fn_00495090(); };
struct H_4948f0 { void fn_004948f0(); };
struct H_494970 { void fn_00494970(); };

struct C_a6540 { void* fn_000a6540(void*); };
struct C_16a470 { void fn_0016a470(void*); };
struct C_28a1f0 { void fn_0028a1f0(void*); };
struct C_2afe40 { void* fn_002afe40(u32, void*); };
struct C_40e170 { void fn_0040e170(void*); };
struct C_447a30 { void fn_00447a30(void*); };

// FUNCTION: DAO 0x4A6540
void* C_a6540::fn_000a6540(void* arg) {
    char* s = (char*)this;
    char* a = (char*)arg;
    if (s == a) return s;
    u32 argCount = 0;
    if (*(void**)(a + 4) != 0) argCount = (u32)((*(u32*)(a + 8) - *(u32*)(a + 4)) / 28u);
    if (argCount == 0) {
        ((H_29c340*)s)->fn_0029c340();
        return s;
    }
    u32 selfCount = 0;
    if (*(void**)(s + 4) != 0) selfCount = (u32)((*(u32*)(s + 8) - *(u32*)(s + 4)) / 28u);
    if (argCount <= selfCount) {
        void* r = fn_0066b250(*(void**)(a + 4), *(void**)(a + 8), *(void**)(s + 4), 0, 0, 0);
        fn_000ceee0(r, *(void**)(s + 8));
        if (*(void**)(a + 4) != 0) {
            u32 c = (u32)((*(u32*)(a + 8) - *(u32*)(a + 4)) / 28u);
            *(void**)(s + 8) = (char*)(*(void**)(s + 4)) + c * 28u;
        } else {
            *(void**)(s + 8) = *(void**)(s + 4);
        }
        return s;
    }
    u32 cap = 0;
    if (*(void**)(s + 4) != 0) cap = (u32)((*(u32*)(s + 0xc) - *(u32*)(s + 4)) / 28u);
    if (argCount > cap) {
        if (*(void**)(s + 4) != 0) fn_000ceee0(*(void**)(s + 4), *(void**)(s + 8));
        fn_000136c0(*(void**)(s + 4));
        u32 cnt = ((H_4714c0*)a)->fn_004714c0();
        if (((H_8390*)s)->fn_00008390((void*)cnt)) {
            void* e = fn_00006ce0(*(void**)(a + 4), *(void**)(a + 8), *(void**)(s + 4));
            *(void**)(s + 8) = e;
        }
        return s;
    }
    u32 cnt = ((H_4714c0*)s)->fn_004714c0();
    char* dst = (char*)(*(void**)(a + 4)) + cnt * 28u;
    fn_0066bbe0(*(void**)(a + 4), dst, *(void**)(s + 4));
    void* e = fn_00006ce0(dst, *(void**)(a + 8), *(void**)(s + 8));
    *(void**)(s + 8) = e;
    return s;
}

// FUNCTION: DAO 0x4C5510
void* __cdecl fn_000c5510(void) {
    void* p = fn_00013660(0x28);
    if (p != 0) {
        *(void**)p = p;
    }
    void** q = (void**)((char*)p + 4);
    if (q != 0) {
        *q = p;
    }
    return p;
}

// FUNCTION: DAO 0x56A470
void C_16a470::fn_0016a470(void* arg) {
    char* s = (char*)this;
    char* a = (char*)arg;
    u32 n = 0;
    if (*(void**)(a + 0x14) != 0) n = (u32)((*(u32*)(a + 0x18) - *(u32*)(a + 0x14)) / 8u);
    ((H_f3670*)(s + 0x10))->fn_000f3670(n);
    *(void**)(s + 0x20) = *(void**)(a + 0x20);
    *(void**)(s + 0x24) = *(void**)(a + 0x24);
    ((H_6880*)(s + 4))->fn_00006880();
    void* a8 = *(void**)(a + 8);
    ((H_16a180*)(s + 4))->fn_0016a180((void*)(s + 4), *(void**)(s + 8), (void*)(a + 4), *(void**)a8, (void*)(a + 4), a8, a);
    void* v1 = *(void**)(*(void**)(s + 8));
    void* v2 = *(void**)(*(void**)(a + 8));
    u32 i = 0;
    for (;;) {
        u32 cs = 0;
        if (*(void**)(s + 0x14) != 0) cs = (u32)((*(u32*)(s + 0x18) - *(u32*)(s + 0x14)) / 8u);
        if (i >= cs) break;
        if (*(void**)(a + 0x14) == 0) fn_004e11f2();
        u32 ca = (u32)((*(u32*)(a + 0x18) - *(u32*)(a + 0x14)) / 8u);
        if (i >= ca) fn_004e11f2();
        u32 av = *(u32*)(*(u32*)(a + 0x14) + i * 8u + 4u);
        if (av == (u32)v2) {
            if (*(void**)(s + 0x14) == 0) fn_004e11f2();
            u32 cs2 = (u32)((*(u32*)(s + 0x18) - *(u32*)(s + 0x14)) / 8u);
            if (i >= cs2) fn_004e11f2();
            *(u32*)(*(u32*)(s + 0x14) + i * 8u) = (u32)(s + 4);
            *(u32*)(*(u32*)(s + 0x14) + i * 8u + 4u) = (u32)v1;
            ++i;
            continue;
        }
        if (v1 == *(void**)(s + 8)) fn_004e11f2();
        void* n1 = *(void**)v1;
        if (v2 == *(void**)(a + 8)) fn_004e11f2();
        void* n2 = *(void**)v2;
        v1 = n1;
        v2 = n2;
    }
}

// FUNCTION: DAO 0x5DF080
void* __cdecl fn_001df080(void* src, void* end, void* dst) {
    char* s = (char*)src;
    char* e = (char*)end;
    char* d = (char*)dst;
    if (s == e) return d;
    do {
        ((H_c2ab0*)(d + 0xc))->fn_000c2ab0(s + 0xc);
        *(u32*)(d + 8) = *(u32*)(s ? (s + 8) : (char*)4);
        s += 0x28;
        d += 0x28;
    } while (s != e);
    return d;
}

// FUNCTION: DAO 0x5E3F80
void __cdecl fn_001e3f80(void* first, u32 count, void* arg) {
    char* p = (char*)first;
    u32 n = count;
    while (n != 0) {
        if (p != 0) ((H_ac430*)p)->fn_000ac430(arg);
        --n;
        p += 0x10;
    }
}

// FUNCTION: DAO 0x5E5380
void* __stdcall fn_001e5380(void* a, void* b, void* c, void* d, u8 e) {
    void* p = fn_00013660(0x34);
    if (p == 0) return 0;
    char* q = (char*)p;
    *(void**)(q + 4) = b;
    *(void**)(q) = a;
    *(void**)(q + 8) = c;
    char* dq = q + 0xc;
    ((H_c2510*)dq)->fn_000c2510(d);
    char* dd = (char*)d;
    *(u32*)(dq + 0x1c) = *(u32*)(dd + 0x1c);
    *(u32*)(dq + 0x20) = *(u32*)(dd + 0x20);
    *(u8*)(q + 0x30) = e;
    *(u8*)(q + 0x31) = 0;
    return p;
}

// FUNCTION: DAO 0x68A1F0
void C_28a1f0::fn_0028a1f0(void* arg) {
    char* s = (char*)this;
    char* a = (char*)arg;
    u32 n = 0;
    if (*(void**)(a + 0x14) != 0) n = (u32)((*(u32*)(a + 0x18) - *(u32*)(a + 0x14)) / 8u);
    ((H_e7d30*)(s + 0x10))->fn_000e7d30(n);
    *(void**)(s + 0x20) = *(void**)(a + 0x20);
    *(void**)(s + 0x24) = *(void**)(a + 0x24);
    ((H_6880*)(s + 4))->fn_00006880();
    void* a8 = *(void**)(a + 8);
    ((H_289d60*)(s + 4))->fn_00289d60((void*)(s + 4), *(void**)(s + 8), (void*)(a + 4), *(void**)a8, (void*)(a + 4), a8, a);
    void* v1 = *(void**)(*(void**)(s + 8));
    void* v2 = *(void**)(*(void**)(a + 8));
    u32 i = 0;
    for (;;) {
        u32 cs = 0;
        if (*(void**)(s + 0x14) != 0) cs = (u32)((*(u32*)(s + 0x18) - *(u32*)(s + 0x14)) / 8u);
        if (i >= cs) break;
        if (*(void**)(a + 0x14) == 0) fn_004e11f2();
        u32 ca = (u32)((*(u32*)(a + 0x18) - *(u32*)(a + 0x14)) / 8u);
        if (i >= ca) fn_004e11f2();
        u32 av = *(u32*)(*(u32*)(a + 0x14) + i * 8u + 4u);
        if (av == (u32)v2) {
            if (*(void**)(s + 0x14) == 0) fn_004e11f2();
            u32 cs2 = (u32)((*(u32*)(s + 0x18) - *(u32*)(s + 0x14)) / 8u);
            if (i >= cs2) fn_004e11f2();
            *(u32*)(*(u32*)(s + 0x14) + i * 8u) = (u32)(s + 4);
            *(u32*)(*(u32*)(s + 0x14) + i * 8u + 4u) = (u32)v1;
            ++i;
            continue;
        }
        if (v1 == *(void**)(s + 8)) fn_004e11f2();
        void* n1 = *(void**)v1;
        if (v2 == *(void**)(a + 8)) fn_004e11f2();
        void* n2 = *(void**)v2;
        v1 = n1;
        v2 = n2;
    }
}

// FUNCTION: DAO 0x6AFE40
void* C_2afe40::fn_002afe40(u32 n, void* src) {
    char* s = (char*)this;
    *(void**)(s + 4) = 0;
    *(void**)(s + 8) = 0;
    *(void**)(s + 0xc) = 0;
    if (n != 0) {
        if (n > 0x1fffffffu) fn_00369830();
        void* p = fn_0046bce0(0, n);
        *(void**)(s + 0xc) = (char*)p + n * 8u;
        *(void**)(s + 4) = p;
        *(void**)(s + 8) = p;
        fn_000ccd70(p, n, src, s, 0, 0);
        *(void**)(s + 8) = (char*)p + n * 8u;
    }
    return s;
}

// FUNCTION: DAO 0x80E170
void C_40e170::fn_0040e170(void* node) {
    char* n = (char*)node;
    char* p = *(char**)n;
    char* c = *(char**)(p + 8);
    *(char**)n = c;
    c = *(char**)(p + 8);
    if (*(u8*)(c + 0x31) == 0) *(char**)(c + 4) = n;
    *(char**)(p + 4) = *(char**)(n + 4);
    char* tree = *(char**)((char*)this + 4);
    if (n == *(char**)(tree + 4)) {
        *(char**)(tree + 4) = p;
        *(char**)(p + 8) = n;
        *(char**)(n + 4) = p;
        return;
    }
    char* parent = *(char**)(n + 4);
    if (n == *(char**)(parent + 8)) {
        *(char**)(parent + 8) = p;
        *(char**)(p + 8) = n;
        *(char**)(n + 4) = p;
        return;
    }
    *(char**)(parent) = p;
    *(char**)(p + 8) = n;
    *(char**)(n + 4) = p;
}

// FUNCTION: DAO 0x847A30
void C_447a30::fn_00447a30(void* node) {
    char* n = (char*)node;
    char* p = *(char**)(n + 8);
    char* c = *(char**)(p);
    *(char**)(n + 8) = c;
    c = *(char**)(p);
    if (*(u8*)(c + 0x31) == 0) *(char**)(c + 4) = n;
    *(char**)(p + 4) = *(char**)(n + 4);
    char* tree = *(char**)((char*)this + 4);
    if (n == *(char**)(tree + 4)) {
        *(char**)(tree + 4) = p;
        *(char**)(p) = n;
        *(char**)(n + 4) = p;
        return;
    }
    char* parent = *(char**)(n + 4);
    if (n == *(char**)(parent)) {
        *(char**)(parent) = p;
        *(char**)(p) = n;
        *(char**)(n + 4) = p;
        return;
    }
    *(char**)(parent + 8) = p;
    *(char**)(p) = n;
    *(char**)(n + 4) = p;
}

// FUNCTION: DAO 0x895270
void __cdecl fn_00495270(void) {
    void* p = fn_004740b0();
    ((H_495090*)p)->fn_00495090();
    p = fn_004740b0();
    ((H_4948f0*)p)->fn_004948f0();
    p = fn_004740b0();
    ((H_494970*)p)->fn_00494970();
}
