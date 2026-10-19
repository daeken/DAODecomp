extern "C" {
extern void* g_0081d9e4;
extern void* g_0081da20;
extern void* g_0081d9e8;
extern const char g_006e1a24[];
extern const char g_006e1c60[];
extern const char g_006e1bc4[];
extern const char g_006e1c64[];
extern const char g_006e1c6c[];
extern const char g_006e1c78[];
extern const char g_006e1c80[];
extern const char g_006e1dac[];
extern const char g_006e1db4[];
extern const char g_006e1dbc[];
extern const char g_006e1dc8[];
extern const char g_006e1dd0[];
extern const char g_006e1ddc[];
extern const char g_006e1df8[];
extern const char g_006e1e14[];
extern const char g_006e1e30[];
extern const char g_006e1e50[];
extern const char g_006e1e6c[];
extern const char g_006e1e8c[];
extern const char g_006e1ea8[];
extern const char g_006e1ec8[];
extern const char g_006e1edc[];
extern const char g_006e1eec[];
extern const char g_006e1f04[];
extern const char g_00adff52[];
extern int fn_004e1e2e(char*, const char*, ...);
extern void* fn_004e19e0(void*, int, unsigned int);
extern void fn_00045cc0(void*);
extern void fn_00044aa0(void*);
extern void fn_00044b30(void*);
extern int (__stdcall *g_006da0a0)(void*);
extern int (__stdcall *g_006da468)(int);
}

struct CUnknown33310 {
    void __thiscall fn_00033310(void*);
};

struct CUnknown31850 {
    void* __thiscall fn_00031850();
};

struct CDaoObject {
    void __thiscall fn_0001e4a0();
    void __thiscall fn_0001e4b0();
    int __thiscall fn_0001e5b0(void*, unsigned int, int);
    int __thiscall fn_0001e610(void*, unsigned int, float);
    void __thiscall fn_0001e6a0();
    void __thiscall fn_0001e810();
    void __thiscall fn_0001e840();
    void __thiscall fn_0001e980();
};

typedef void (__thiscall *PFN_Log1)(void*, const char*);
typedef void (__thiscall *PFN_Log4)(void*, void*, int, const char*, void*);
typedef void (__thiscall *PFN_Log5)(void*, void*, int, const char*, unsigned int, unsigned int);

// FUNCTION: DAO 0x41E4A0
void __thiscall CDaoObject::fn_0001e4a0() {
    *(unsigned int*)this = 0xAE1944u;
}

// FUNCTION: DAO 0x41E4B0
void __thiscall CDaoObject::fn_0001e4b0() {
    unsigned char* base = (unsigned char*)this;
    *(unsigned int*)(base + 0) = 0xAE1C50u;
    *(unsigned int*)(base + 4) = 0xAE1C48u;
    *(unsigned int*)(base + 8) = 0xAE1C14u;
    unsigned int* table = (unsigned int*)g_0081d9e4;
    for (unsigned int i = 0; i < 16; ++i) {
        if (table[2 + i] == (unsigned int)(base + 4)) {
            table[2 + i] = 0;
            break;
        }
    }
    ((CUnknown33310*)g_0081da20)->fn_00033310((void*)(base + 8));
    fn_00045cc0(*(void**)(base + 0xC));
    *(unsigned int*)(base + 8) = 0xAE199Cu;
    *(unsigned int*)(base + 4) = 0xAE1A8Cu;
    *(unsigned int*)(base + 0) = 0xAE1944u;
}

// FUNCTION: DAO 0x41E5B0
int __thiscall CDaoObject::fn_0001e5b0(void* a1, unsigned int a2, int a3) {
    char buf[16];
    for (int i = 0; i < 16; ++i) buf[i] = 0;
    fn_004e1e2e(buf, g_006e1c60, a3);
    void** vtbl = *(void***)this;
    typedef int (__thiscall *PFN)(void*, void*, unsigned int, void*);
    PFN fn = (PFN)vtbl[1];
    return fn(this, a1, a2, buf);
}

// FUNCTION: DAO 0x41E610
int __thiscall CDaoObject::fn_0001e610(void* a1, unsigned int a2, float a3) {
    char buf[16];
    for (int i = 0; i < 16; ++i) buf[i] = 0;
    fn_004e1e2e(buf, g_006e1a24, (double)a3);
    void** vtbl = *(void***)this;
    typedef int (__thiscall *PFN)(void*, void*, unsigned int, void*);
    PFN fn = (PFN)vtbl[1];
    return fn(this, a1, a2, buf);
}

// FUNCTION: DAO 0x41E6A0
void __thiscall CDaoObject::fn_0001e6a0() {
    CUnknown31850* h = (CUnknown31850*)g_0081da20;
    void* r = h->fn_00031850();
    int state = *(int*)r;
    if (state == 0 || state == 1) {
        void** vtbl = *(void***)this;
        typedef void (__thiscall *PFN)(void*, unsigned int, unsigned int, unsigned int);
        PFN fn = (PFN)vtbl[1];
        fn(this, 0x434F4E4Eu, 0x45564E53u, 0u);
    }
    r = h->fn_00031850();
    void* p = (char*)r + 0x44A;
    void** vtbl2 = *(void***)this;
    typedef void (__thiscall *PFN2)(void*, unsigned int, unsigned int, void*);
    PFN2 fn2 = (PFN2)vtbl2[1];
    fn2(this, 0x48445752u, 0x4C4F434Cu, p);
}

// FUNCTION: DAO 0x41E700
extern "C" const char* fn_0001e700(void) {
    unsigned char osvi[0x9C];
    fn_004e19e0(osvi, 0, 0x9C);
    *(unsigned int*)osvi = 0x9C;
    if (!g_006da0a0(osvi)) return g_006e1bc4;
    unsigned int major = *(unsigned int*)(osvi + 4);
    unsigned int minor = *(unsigned int*)(osvi + 8);
    if (major == 5) {
        if (minor == 0) return g_006e1bc4;
        if (*(unsigned int*)(osvi + 0x98) & 0x200u) return g_006e1c80;
        if (*(unsigned char*)(osvi + 0x9A) == 1) return g_006e1c78;
        if (g_006da468(0x57)) return g_006e1c6c;
        return g_006e1bc4;
    }
    if (major == 6) return g_006e1c64;
    return g_006e1bc4;
}

// FUNCTION: DAO 0x41E7B0
extern "C" int fn_0001e7b0(int a1, int a2, int a3) {
    unsigned char* base = (unsigned char*)g_0081d9e4;
    void* obj = *(void**)(base + 0xD4);
    if (!obj) return -1;
    void** vtbl = *(void***)obj;
    typedef int (__thiscall *PFN)(void*, int, int, int);
    PFN fn = (PFN)vtbl[1];
    return fn(obj, a1, a2, a3);
}

// FUNCTION: DAO 0x41E7E0
extern "C" int fn_0001e7e0(void* a1, unsigned int a2, int a3) {
    unsigned char* base = (unsigned char*)g_0081d9e4;
    CDaoObject* obj = (CDaoObject*)*(void**)(base + 0xD4);
    if (!obj) return -1;
    return obj->fn_0001e5b0(a1, a2, a3);
}

// FUNCTION: DAO 0x41E810
void __thiscall CDaoObject::fn_0001e810() {
    fn_00044aa0(*(void**)((char*)this + 4));
}

// FUNCTION: DAO 0x41E840
void __thiscall CDaoObject::fn_0001e840() {
    fn_00044b30(*(void**)((char*)this + 4));
}

// FUNCTION: DAO 0x41E850
extern "C" void* fn_0001e850(void) {
    return (void*)0xBF1DD4;
}

// FUNCTION: DAO 0x41E980
void __thiscall CDaoObject::fn_0001e980() {
    void* logger = g_0081d9e8;
    void** vtbl = *(void***)logger;
    ((PFN_Log1)vtbl[4])(logger, g_006e1f04);
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1eec, (void*)((char*)this + 0x10));
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1edc, (void*)*(unsigned int*)((char*)this + 4));
    unsigned int mode = *(unsigned int*)((char*)this + 0x114);
    const char* selected;
    if (mode == 0) selected = g_006e1dac;
    else if (mode == 2) selected = g_006e1db4;
    else selected = g_00adff52;
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1ec8, (void*)selected);
    unsigned int v118 = *(unsigned int*)((char*)this + 0x118);
    ((PFN_Log5)vtbl[5])(logger, logger, 0, g_006e1ea8, v118, v118);
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1e8c, (void*)((char*)this + 0x50));
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1e6c, (void*)((char*)this + 0x90));
    unsigned int v8 = *(unsigned int*)((char*)this + 8);
    if (v8) ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1e50, (void*)v8);
    else ((PFN_Log1)vtbl[4])(logger, g_006e1e30);
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1e14, (void*)((char*)this + 0xD0));
    unsigned int vc = *(unsigned int*)((char*)this + 0xC);
    if (vc) ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1df8, (void*)vc);
    else ((PFN_Log1)vtbl[4])(logger, g_006e1ddc);
    const char* en = (*(unsigned char*)((char*)this + 0x110)) ? g_006e1dd0 : g_006e1dc8;
    ((PFN_Log4)vtbl[5])(logger, logger, 0, g_006e1dbc, (void*)en);
}
