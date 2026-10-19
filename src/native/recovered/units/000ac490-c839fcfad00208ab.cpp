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
struct C_ac490 { void* fn_000ac490(void*); };
struct C_16a470 { void fn_0016a470(void*); };
struct C_28a1f0 { void fn_0028a1f0(void*); };
struct C_2afe40 { void* fn_002afe40(u32, void*); };
struct C_40e170 { void fn_0040e170(void*); };
struct C_447a30 { void fn_00447a30(void*); };

// FUNCTION: DAO 0x4A6540
void* C_a6540::fn_000a6540(void* arg) {
    char* s = reinterpret_cast<char*>(this);
    char* a = reinterpret_cast<char*>(arg);
    if (s == a) return s;
    u32 argCount = 0;
    if (*(reinterpret_cast<void**>(a + 4)) != 0) {
        argCount = (*(reinterpret_cast<u32*>(a + 8)) - *(reinterpret_cast<u32*>(a + 4))) / 28u;
    }
    if (argCount == 0) {
        reinterpret_cast<H_29c340*>(s)->fn_0029c340();
        return s;
    }
    u32 selfCount = 0;
    if (*(reinterpret_cast<void**>(s + 4)) != 0) {
        selfCount = (*(reinterpret_cast<u32*>(s + 8)) - *(reinterpret_cast<u32*>(s + 4))) / 28u;
    }
    if (argCount <= selfCount) {
        void* r = fn_0066b250(*(reinterpret_cast<void**>(a + 4)), *(reinterpret_cast<void**>(a + 8)), s + 4, 0, 0, 0);
        fn_000ceee0(r, *(reinterpret_cast<void**>(s + 8)));
        if (*(reinterpret_cast<void**>(a + 4)) != 0) {
            u32 c = (*(reinterpret_cast<u32*>(a + 8)) - *(reinterpret_cast<u32*>(a + 4))) / 28u;
            *(reinterpret_cast<void**>(s + 8)) = reinterpret_cast<char*>(*(reinterpret_cast<void**>(s + 4))) + c * 28u;
        } else {
            *(reinterpret_cast<void**>(s + 8)) = *(reinterpret_cast<void**>(s + 4));
        }
        return s;
    }
    u32 cap = 0;
    if (*(reinterpret_cast<void**>(s + 4)) != 0) {
        cap = (*(reinterpret_cast<u32*>(s + 0xc)) - *(reinterpret_cast<u32*>(s + 4))) / 28u;
    }
    if (argCount > cap) {
        if (*(reinterpret_cast<void**>(s + 4)) != 0) {
            fn_000ceee0(*(reinterpret_cast<void**>(s + 4)), *(reinterpret_cast<void**>(s + 8)));
        }
        fn_000136c0(*(reinterpret_cast<void**>(s + 4)));
        u32 cnt = reinterpret_cast<H_4714c0*>(a)->fn_004714c0();
        if (reinterpret_cast<H_8390*>(s)->fn_00008390(reinterpret_cast<void*>(cnt))) {
            void* e = fn_00006ce0(*(reinterpret_cast<void**>(a + 4)), *(reinterpret_cast<void**>(a + 8)), *(reinterpret_cast<void**>(s + 4)));
            *(reinterpret_cast<void**>(s + 8)) = e;
        }
        return s;
    }
    u32 cnt = reinterpret_cast<H_4714c0*>(s)->fn_004714c0();
    char* dst = reinterpret_cast<char*>(*(reinterpret_cast<void**>(a + 4))) + cnt * 28u;
    fn_0066bbe0(*(reinterpret_cast<void**>(a + 4)), dst, *(reinterpret_cast<void**>(s + 4)));
    void* e = fn_00006ce0(dst, *(reinterpret_cast<void**>(a + 8)), *(reinterpret_cast<void**>(s + 8)));
    *(reinterpret_cast<void**>(s + 8)) = e;
    return s;
}

// FUNCTION: DAO 0x4AC490
void* C_ac490::fn_000ac490(void* arg) {
    reinterpret_cast<C_a6540*>(this)->fn_000a6540(arg);
    return this;
}

// FUNCTION: DAO 0x4C5510
void* __cdecl fn_000c5510(void) {
    void* p = fn_00013660(0x28);
    if (p != 0) {
        *(reinterpret_cast<void**>(p)) = p;
        void** q = reinterpret_cast<void**>(reinterpret_cast<char*>(p) + 4);
        if (q != 0) *q = p;
    }
    return p;
}

// FUNCTION: DAO 0x56A470
void C_16a470::fn_0016a470(void* arg) {
    char* s = reinterpret_cast<char*>(this);
    char* a = reinterpret_cast<char*>(arg);
    u32 n = 0;
    if (*(reinterpret_cast<void**>(a + 0x14)) != 0) {
        n = (*(reinterpret_cast<u32*>(a + 0x18)) - *(reinterpret_cast<u32*>(a + 0x14))) / 8u;
    }
    reinterpret_cast<H_f3670*>(s + 0x10)->fn_000f3670(n);
    *(reinterpret_cast<void**>(s + 0x20)) = *(reinterpret_cast<void**>(a + 0x20));
    *(reinterpret_cast<void**>(s + 0x24)) = *(reinterpret_cast<void**>(a + 0x24));
    reinterpret_cast<H_6880*>(s + 4)->fn_00006880();
    reinterpret_cast<H_16a180*>(s + 4)->fn_0016a180(s + 4, a, a + 4, a + 8, s + 8, a + 0x14, s + 0x10);
    for (u32 i = 0; ; ++i) {
        u32 c = 0;
        if (*(reinterpret_cast<void**>(a + 0x14)) != 0) {
            c = (*(reinterpret_cast<u32*>(a + 0x18)) - *(reinterpret_cast<u32*>(a + 0x14))) / 8u;
        }
        if (i >= c) break;
        if (*(reinterpret_cast<void**>(a + 0x14)) == 0) fn_004e11f2();
        if (*(reinterpret_cast<void**>(s + 4)) == *(reinterpret_cast<void**>(a + 0x14))) fn_004e11f2();
    }
    if (*(reinterpret_cast<void**>(s + 4)) == 0) fn_004e11f2();
    if (*(reinterpret_cast<void**>(a + 0x14)) == 0) fn_004e11f2();
}

// FUNCTION: DAO 0x5DF080
void* __cdecl fn_001df080(void* src, void* end, void* dst) {
    char* s = reinterpret_cast<char*>(src);
    char* e = reinterpret_cast<char*>(end);
    char* d = reinterpret_cast<char*>(dst);
    if (s == e) return d;
    do {
        reinterpret_cast<H_c2ab0*>(d + 0xc)->fn_000c2ab0(s + 0xc);
        u32 v = 0;
        if (s != 0) v = *(reinterpret_cast<u32*>(s + 8));
        *(reinterpret_cast<u32*>(d + 8)) = v;
        s += 0x28;
        d += 0x28;
    } while (s != e);
    return d;
}

// FUNCTION: DAO 0x5E3F80
void __cdecl fn_001e3f80(void* first, u32 count, void* arg) {
    char* p = reinterpret_cast<char*>(first);
    u32 n = count;
    while (n != 0) {
        if (p != 0) reinterpret_cast<H_ac430*>(p)->fn_000ac430(arg);
        --n;
        p += 0x10;
    }
}

// FUNCTION: DAO 0x5E5380
void* __stdcall fn_001e5380(void* a, void* b, void* c, void* d, u8 e) {
    void* p = fn_00013660(0x34);
    if (p == 0) return 0;
    char* q = reinterpret_cast<char*>(p);
    *(reinterpret_cast<void**>(q + 4)) = b;
    *(reinterpret_cast<void**>(q)) = a;
    *(reinterpret_cast<void**>(q + 8)) = c;
    char* dst = q + 0xc;
    reinterpret_cast<H_c2510*>(dst)->fn_000c2510(d);
    char* dd = reinterpret_cast<char*>(d);
    *(reinterpret_cast<u32*>(dst + 0x1c)) = *(reinterpret_cast<u32*>(dd + 0x1c));
    *(reinterpret_cast<u32*>(dst + 0x20)) = *(reinterpret_cast<u32*>(dd + 0x20));
    *(reinterpret_cast<u8*>(q + 0x30)) = e;
    *(reinterpret_cast<u8*>(q + 0x31)) = 0;
    return p;
}

// FUNCTION: DAO 0x68A1F0
void C_28a1f0::fn_0028a1f0(void* arg) {
    char* s = reinterpret_cast<char*>(this);
    char* a = reinterpret_cast<char*>(arg);
    u32 n = 0;
    if (*(reinterpret_cast<void**>(a + 0x14)) != 0) {
        n = (*(reinterpret_cast<u32*>(a + 0x18)) - *(reinterpret_cast<u32*>(a + 0x14))) / 8u;
    }
    reinterpret_cast<H_e7d30*>(s + 0x10)->fn_000e7d30(n);
    *(reinterpret_cast<void**>(s + 0x20)) = *(reinterpret_cast<void**>(a + 0x20));
    *(reinterpret_cast<void**>(s + 0x24)) = *(reinterpret_cast<void**>(a + 0x24));
    reinterpret_cast<H_6880*>(s + 4)->fn_00006880();
    reinterpret_cast<H_289d60*>(s + 4)->fn_00289d60(s + 4, a, a + 4, a + 8, s + 8, a + 0x14, s + 0x10);
    for (u32 i = 0; ; ++i) {
        u32 c = 0;
        if (*(reinterpret_cast<void**>(a + 0x14)) != 0) {
            c = (*(reinterpret_cast<u32*>(a + 0x18)) - *(reinterpret_cast<u32*>(a + 0x14))) / 8u;
        }
        if (i >= c) break;
        if (*(reinterpret_cast<void**>(a + 0x14)) == 0) fn_004e11f2();
        if (*(reinterpret_cast<void**>(s + 4)) == *(reinterpret_cast<void**>(a + 0x14))) fn_004e11f2();
    }
    if (*(reinterpret_cast<void**>(s + 4)) == 0) fn_004e11f2();
    if (*(reinterpret_cast<void**>(a + 0x14)) == 0) fn_004e11f2();
}

// FUNCTION: DAO 0x6AFE40
void* C_2afe40::fn_002afe40(u32 n, void* src) {
    char* s = reinterpret_cast<char*>(this);
    *(reinterpret_cast<void**>(s + 4)) = 0;
    *(reinterpret_cast<void**>(s + 8)) = 0;
    *(reinterpret_cast<void**>(s + 0xc)) = 0;
    if (n != 0) {
        if (n > 0x1fffffffu) fn_00369830();
        void* p = fn_0046bce0(0, n);
        *(reinterpret_cast<void**>(s + 0xc)) = reinterpret_cast<char*>(p) + n * 8u;
        *(reinterpret_cast<void**>(s + 4)) = p;
        *(reinterpret_cast<void**>(s + 8)) = p;
        fn_000ccd70(p, n, src, s, 0, 0);
        *(reinterpret_cast<void**>(s + 8)) = reinterpret_cast<char*>(p) + n * 8u;
    }
    return s;
}

// FUNCTION: DAO 0x80E170
void C_40e170::fn_0040e170(void* node) {
    char* n = reinterpret_cast<char*>(node);
    char* p = *(reinterpret_cast<char**>(n));
    char* c = *(reinterpret_cast<char**>(p + 8));
    *(reinterpret_cast<char**>(n)) = c;
    char* c2 = *(reinterpret_cast<char**>(p + 8));
    if (*(reinterpret_cast<u8*>(c2 + 0x31)) == 0) {
        *(reinterpret_cast<char**>(c2 + 4)) = n;
    }
    *(reinterpret_cast<char**>(p + 4)) = *(reinterpret_cast<char**>(n + 4));
    char* parent = *(reinterpret_cast<char**>(reinterpret_cast<char*>(this) + 4));
    if (n == *(reinterpret_cast<char**>(parent + 4))) {
        *(reinterpret_cast<char**>(parent + 4)) = p;
        *(reinterpret_cast<char**>(p + 8)) = n;
        *(reinterpret_cast<char**>(n + 4)) = p;
        return;
    }
    if (n == *(reinterpret_cast<char**>(parent + 8))) {
        *(reinterpret_cast<char**>(parent + 8)) = p;
        *(reinterpret_cast<char**>(p + 8)) = n;
        *(reinterpret_cast<char**>(n + 4)) = p;
        return;
    }
    *(reinterpret_cast<char**>(parent)) = p;
    *(reinterpret_cast<char**>(p + 8)) = n;
    *(reinterpret_cast<char**>(n + 4)) = p;
}

// FUNCTION: DAO 0x847A30
void C_447a30::fn_00447a30(void* node) {
    char* n = reinterpret_cast<char*>(node);
    char* p = *(reinterpret_cast<char**>(n + 8));
    char* c = *(reinterpret_cast<char**>(p));
    *(reinterpret_cast<char**>(n + 8)) = c;
    char* c2 = *(reinterpret_cast<char**>(p));
    if (*(reinterpret_cast<u8*>(c2 + 0x31)) == 0) {
        *(reinterpret_cast<char**>(c2 + 4)) = n;
    }
    *(reinterpret_cast<char**>(p + 4)) = *(reinterpret_cast<char**>(n + 4));
    char* parent = *(reinterpret_cast<char**>(reinterpret_cast<char*>(this) + 4));
    if (n == *(reinterpret_cast<char**>(parent + 4))) {
        *(reinterpret_cast<char**>(parent + 4)) = p;
        *(reinterpret_cast<char**>(p)) = n;
        *(reinterpret_cast<char**>(n + 4)) = p;
        return;
    }
    if (n == *(reinterpret_cast<char**>(parent))) {
        *(reinterpret_cast<char**>(parent)) = p;
        *(reinterpret_cast<char**>(p)) = n;
        *(reinterpret_cast<char**>(n + 4)) = p;
        return;
    }
    *(reinterpret_cast<char**>(parent + 8)) = p;
    *(reinterpret_cast<char**>(p)) = n;
    *(reinterpret_cast<char**>(n + 4)) = p;
}

// FUNCTION: DAO 0x895270
void __cdecl fn_00495270(void) {
    void* p = fn_004740b0();
    reinterpret_cast<H_495090*>(p)->fn_00495090();
    p = fn_004740b0();
    reinterpret_cast<H_4948f0*>(p)->fn_004948f0();
    p = fn_004740b0();
    reinterpret_cast<H_494970*>(p)->fn_00494970();
}
