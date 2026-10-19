typedef int (__thiscall *VFunc)(void*, int, int, int, int);
typedef void (__thiscall *VFuncV)(void*, int);

extern "C" {
void __fastcall fn_004be090(void*, void*);
void __fastcall fn_004c0db0(void*, void*);
void __fastcall fn_0046c760(void*, void*);
void __fastcall fn_004cb310(void*, void*);
void __fastcall fn_005744e0(void*, void*);
void fn_001d42c0(void);
void fn_0052be10(void);
void __fastcall fn_004c0d90(void*, void*);
void* fn_005fe920(void);
void __fastcall fn_00401210(void*, void*, unsigned int, int);
void __fastcall fn_004c1e20(void*, void*, unsigned int, unsigned int);
void fn_004c1270(void*, unsigned int, unsigned int);
void __fastcall fn_00405eb0(void*, void*, unsigned int, unsigned int);
void fn_008dfd0c(void);
unsigned char fn_004b8da0(void);
unsigned int fn_004b8af0(void);
void* __fastcall fn_004b9100(void*, void*, int);
int* fn_008e37b6(void);
void fn_008e11ce(int, int, int, int, int);
int fn_008f3dea(const char*, void*, int);
void fn_004b9080(void*);
void fn_000136c0(void*);
void* g_00c1d0a0;
void* g_00c1d25c;
void* g_00c2b584;
void* g_00c2b588;
unsigned char g_00bf4628;
}

struct C_00401000 { void* fn_00001000(); };
struct C_004013f0 { void fn_000013f0(); };
struct C_00406e10 { void fn_00006e10(); };
struct C_00413780 { void* fn_00013780(); };
struct C_004c1f20 { void* fn_000c1f20(const void*, unsigned int); };
struct C_004c3ae0 { void* fn_000c3ae0(void*); };
struct C_004f6eb0 { void* fn_000f6eb0(void*); };

// FUNCTION: DAO 0x00401000
void* C_00401000::fn_00001000() {
    fn_004be090(this, 0);
    *reinterpret_cast<unsigned int*>(this) = 0xadd8f0;
    *reinterpret_cast<unsigned char*>(reinterpret_cast<unsigned char*>(this) + 0x68) = 1;
    return this;
}

// FUNCTION: DAO 0x004013f0
void C_004013f0::fn_000013f0() {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    if (*reinterpret_cast<unsigned int*>(self + 0x18) >= 0x10) {
        void* p = *reinterpret_cast<void**>(self + 4);
        fn_000136c0(p);
    }
    *reinterpret_cast<unsigned int*>(self + 0x18) = 0xf;
    *reinterpret_cast<unsigned int*>(self + 0x14) = 0;
    *reinterpret_cast<unsigned char*>(self + 4) = 0;
}

// FUNCTION: DAO 0x00406e10
void C_00406e10::fn_00006e10() {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    fn_001d42c0();
    fn_0052be10();
    fn_005744e0(self + 0x260, 0);
    fn_004c0db0(self + 0x234, 0);
    fn_004c0db0(self + 0x218, 0);
    fn_0046c760(self + 0x1f8, 0);
    fn_004c0db0(self + 0x1c4, 0);
    fn_004c0db0(self + 0x1a0, 0);
    fn_004c0db0(self + 0x17c, 0);
    fn_004c0db0(self + 0x160, 0);
    fn_004c0db0(self + 0x144, 0);
    fn_004c0db0(self + 0x128, 0);
    fn_004c0db0(self + 0x10c, 0);
    fn_004c0db0(self + 0xf0, 0);
    fn_004c0db0(self + 0xd4, 0);
    fn_004cb310(self + 0x90, 0);
    fn_005744e0(self + 0x3c, 0);
    fn_004c0db0(self + 0x20, 0);
    fn_004c0db0(self + 4, 0);
}

// FUNCTION: DAO 0x00407e00
void __cdecl fn_00007e00(void) {
    void* p = g_00c1d0a0;
    if (p != 0) {
        reinterpret_cast<C_00406e10*>(p)->fn_00006e10();
        fn_000136c0(p);
        g_00c1d0a0 = 0;
    }
}

// FUNCTION: DAO 0x004136c0
void __cdecl fn_000136c0(void* p) {
    fn_004b9080(p);
}

// FUNCTION: DAO 0x00413780
void* C_00413780::fn_00013780() {
    *reinterpret_cast<unsigned int*>(this) = 0xae0084;
    g_00c1d25c = this;
    return this;
}

// FUNCTION: DAO 0x004b92c0
int __cdecl fn_000b92c0(int arg0, int arg1) {
    if (g_00c2b584 == 0) {
        if (!fn_004b8da0()) return 0;
    }
    if (arg0 == 0) return 0;
    unsigned int idx = fn_004b8af0() & 0xffffU;
    void* obj = fn_004b9100(g_00c2b584, 0, (int)idx);
    int edi = 0;
    if (obj == 0) return 0;
    void** vtbl = *reinterpret_cast<void***>(obj);
    VFunc f = reinterpret_cast<VFunc>(vtbl[4]);
    edi = f(obj, arg1, 0x7fffffff, 0x7fffffff, arg0);
    if (edi != 0) return edi;
    if (g_00bf4628 == (unsigned char)edi) return edi;
    int flag = *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(obj) + 0xf4);
    if (flag != 1 && flag != 0) return edi;
    void* obj2 = fn_004b9100(g_00c2b584, 0, 0);
    void** vtbl2 = *reinterpret_cast<void***>(obj2);
    VFunc f2 = reinterpret_cast<VFunc>(vtbl2[4]);
    edi = f2(obj2, arg1, 0x7fffffff, 0x7fffffff, arg0);
    return edi;
}

// FUNCTION: DAO 0x004bbe10
void __cdecl fn_000bbe10(void) {
    void* p = g_00c2b588;
    if (p != 0) {
        void** vtbl = *reinterpret_cast<void***>(p);
        VFuncV f = reinterpret_cast<VFuncV>(vtbl[0]);
        f(p, 1);
        g_00c2b588 = 0;
    }
}

// FUNCTION: DAO 0x004c1f20
void* C_004c1f20::fn_000c1f20(const void* src, unsigned int count) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    unsigned int cap = *reinterpret_cast<unsigned int*>(self + 0x18);
    unsigned char* buf = (cap >= 8) ? *reinterpret_cast<unsigned char**>(self + 4) : self + 4;
    unsigned int len = *reinterpret_cast<unsigned int*>(self + 0x14);
    const unsigned char* s = reinterpret_cast<const unsigned char*>(src);
    if (s >= buf && s < buf + len * 2) {
        fn_004c1270(this, (unsigned int)((s - buf) / 2), count);
        return this;
    }
    if (count > 0x7ffffffeU) fn_008dfd0c();
    if (cap < count) {
        unsigned int oldlen = *reinterpret_cast<unsigned int*>(self + 0x14);
        fn_00405eb0(this, 0, count, oldlen);
    }
    if (count == 0) {
        *reinterpret_cast<unsigned int*>(self + 0x14) = 0;
        unsigned int cap2 = *reinterpret_cast<unsigned int*>(self + 0x18);
        unsigned short* p2 = (cap2 >= 8) ? *reinterpret_cast<unsigned short**>(self + 4) : reinterpret_cast<unsigned short*>(self + 4);
        *p2 = 0;
        return this;
    }
    unsigned int cap2 = *reinterpret_cast<unsigned int*>(self + 0x18);
    unsigned short* dst = (cap2 >= 8) ? *reinterpret_cast<unsigned short**>(self + 4) : reinterpret_cast<unsigned short*>(self + 4);
    const unsigned short* s2 = reinterpret_cast<const unsigned short*>(src);
    for (unsigned int i = 0; i < count; ++i) dst[i] = s2[i];
    *reinterpret_cast<unsigned int*>(self + 0x14) = count;
    dst[count] = 0;
    return this;
}

// FUNCTION: DAO 0x004c3ae0
void* C_004c3ae0::fn_000c3ae0(void* dest) {
    unsigned char* d = reinterpret_cast<unsigned char*>(dest);
    unsigned char* s = reinterpret_cast<unsigned char*>(this);
    unsigned int srclen = *reinterpret_cast<unsigned int*>(s + 0x14);
    *reinterpret_cast<unsigned int*>(d + 0x18) = 0xf;
    *reinterpret_cast<unsigned int*>(d + 0x14) = 0;
    *reinterpret_cast<unsigned char*>(d + 4) = 0;
    if (srclen > 0xfU) {
        fn_00401210(d, 0, srclen, -1);
    } else {
        fn_004c1e20(d, 0, srclen, 0);
    }
    unsigned char* srcbuf = (*reinterpret_cast<unsigned int*>(s + 0x18) >= 8) ? *reinterpret_cast<unsigned char**>(s + 4) : s + 4;
    unsigned char* dstbuf = (*reinterpret_cast<unsigned int*>(d + 0x18) >= 8) ? *reinterpret_cast<unsigned char**>(d + 4) : d + 4;
    for (unsigned int i = 0; i < srclen; ++i) dstbuf[i] = srcbuf[i * 2];
    *reinterpret_cast<unsigned int*>(d + 0x14) = srclen;
    dstbuf[srclen] = 0;
    return d;
}

// FUNCTION: DAO 0x004f6eb0
void* C_004f6eb0::fn_000f6eb0(void* arg) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    unsigned char* p = reinterpret_cast<unsigned char*>(fn_005fe920());
    *reinterpret_cast<void**>(self + 4) = p;
    p[0x2d] = 1;
    *reinterpret_cast<void**>(p + 4) = p;
    *reinterpret_cast<void**>(p) = p;
    *reinterpret_cast<void**>(p + 8) = p;
    *reinterpret_cast<unsigned int*>(self + 8) = 0;
    fn_004c0d90(self + 0xc, 0);
    *reinterpret_cast<void**>(self + 0x28) = arg;
    return self;
}

// FUNCTION: DAO 0x008e2d59
int __cdecl fn_004e2d59(char* filename, char* arglist, ...) {
    int local = 0;
    if (filename == 0) goto error;
    if (*filename == 0) goto error;
    if (arglist == 0) goto error;
    if (*arglist == 0) goto error;
    return fn_008f3dea(filename, &local, 0);
error:
    {
        int* err = fn_008e37b6();
        *err = 0x16;
        fn_008e11ce(0, 0, 0, 0, 0);
        return -1;
    }
}
