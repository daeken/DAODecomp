typedef unsigned int uint32;
typedef unsigned short uint16;
struct S12 { uint32 a,b,c; };
typedef void (__thiscall *Fn_virt_4)(void*, int, void*, void*, S12, S12, void*);
extern "C" void __cdecl fn_00407b00(int,int);
extern "C" void __cdecl fn_00453f70(void*,void*);
extern "C" void* __cdecl fn_0040a8e0(void*);
extern "C" bool __cdecl fn_00457150(void*);
extern "C" void* __cdecl fn_00458e80(void*);
extern "C" unsigned short __cdecl fn_004d29c0();
extern "C" void __cdecl fn_0046bdf0(void*, int, void*, void*, void*, void*);
extern "C" void* __cdecl fn_0046bd80(void*, void*, void*);
extern "C" void __cdecl fn_004136c0(void*);
extern "C" void __cdecl fn_008e11f2();
extern "C" double __cdecl fn_008e1943(const wchar_t*, int);
extern "C" int __cdecl fn_008e642d();
extern "C" int* __cdecl fn_008e37b6();
extern "C" void __cdecl fn_008e11ce(int,int,int,int,int);
extern "C" int __cdecl fn_008e676c(const wchar_t*, const wchar_t*, int);
extern "C" int __cdecl fn_008e687b(const wchar_t*, const wchar_t*);
extern "C" int g_00c3eee0;
extern "C" wchar_t g_00adec4c[];
extern "C" wchar_t g_00adec3c[];
extern "C" wchar_t g_00ae78e8[];
extern "C" wchar_t g_00ae78cc[];
extern "C" wchar_t g_00ae78b0[];
extern "C" wchar_t g_00ae7894[];
extern "C" wchar_t g_00ae7884[];
extern "C" wchar_t g_00ae7874[];
extern "C" wchar_t g_00ae7864[];
extern "C" wchar_t g_00ae7858[];
extern "C" wchar_t g_00ae7848[];
extern "C" wchar_t g_00ae7840[];
struct C_0040b030 { void fn_0040b030(void*, int); };
struct C_00403610 { void* fn_00003610(void*); };
struct C_004035c0 { void fn_000035c0(); };
struct C_0045da20 { int fn_0005da20(const wchar_t*, void*); };
struct C_004c2480 { void fn_004c2480(void*); };
struct C_004621c0 { void* fn_004621c0(); };
struct C_0053cc40 { void* fn_0053cc40(); };
struct C_004c0db0 { void fn_004c0db0(); };
struct C_00507CE0 { void fn_00507ce0(void*, void*, void*, void*); };
struct C_0046c2f0 { void fn_0046c2f0(int); };
struct C_004c4bc0 { void fn_004c4bc0(void*); };
struct C_008e03fb { void fn_008e03fb(); };
struct C_00454300 { void* fn_00054300(int); };
struct C_00454F20 { void* fn_00054f20(int); };
struct C_0045DBF0 { int fn_0005dbf0(const wchar_t*, const wchar_t*); };
struct C_0045EC30 { bool fn_0005ec30(int); };
struct C_004D29D0 { bool fn_000d29d0(); };
struct C_004D4DD0 { void* fn_000d4dd0(float,float,float,float); };
struct C_00507D70 { void fn_00107d70(void*); };
struct C_00507F00 { void fn_00107f00(bool); };
struct C_0050F440 { void* fn_0010f440(int,int,int,int,int,int,int); };
// FUNCTION: DAO 0x00454300
void* C_00454300::fn_00054300(int arg) {
    unsigned char local_24[0x40];
    unsigned char local_1c[0x10];
    void* local_18 = 0;
    unsigned char local_34 = 0;
    void* local_3c = 0;
    ((C_0040b030*)local_24)->fn_0040b030(this, 0);
    if (local_24[4] != 0) {
        void* sub = (unsigned char*)this + *(int*)(*(int*)this + 4);
        void* r = ((C_00403610*)sub)->fn_00003610(local_1c);
        ((C_004035c0*)local_1c)->fn_000035c0();
        void* edi = fn_0040a8e0(r);
        int field40 = *(int*)((char*)sub + 0x28);
        local_34 = (field40 == 0) ? 1 : 0;
        S12 s1; s1.a = 0; s1.b = 0; s1.c = 1;
        S12 s2; s2.a = 0; s2.b = (uint32)field40; s2.c = (uint32)local_34;
        void** vtbl = *(void***)edi;
        Fn_virt_4 f = (Fn_virt_4)vtbl[4];
        f(edi, arg, &local_18, sub, s1, s2, &local_3c);
        if (local_18 != 0) {
            uint32 flags = *(uint32*)((char*)sub + 8) | (uint32)reinterpret_cast<unsigned int>(local_18);
            if (*(int*)((char*)sub + 0x28) == 0) flags |= 4;
            fn_00407b00(0, (int)flags);
        }
    }
    void* p = *(void**)local_24;
    if (p != 0) {
        int off = *(int*)(*(int*)p + 4);
        int* obj = *(int**)((char*)p + off + 0x28);
        if (obj != 0) ((C_008e03fb*)((char*)obj + 4))->fn_008e03fb();
    }
    return this;
}
// FUNCTION: DAO 0x00454F20
void* C_00454F20::fn_00054f20(int arg) {
    void* sub = (unsigned char*)this + *(int*)(*(int*)this + 4);
    int field = *(int*)((char*)sub + 0x28);
    int size = (field == 0) ? 4 : 0;
    fn_00407b00(0, size);
    fn_00453f70((void*)arg, (char*)this + 8);
    return this;
}
// FUNCTION: DAO 0x0045DBF0
int C_0045DBF0::fn_0005dbf0(const wchar_t* name, const wchar_t* arg2) {
    if (fn_008e687b(name, g_00adec4c) == 0) {
        int r = ((C_0045da20*)this)->fn_0005da20(arg2, (char*)this + 0x34);
        *(int*)((char*)this + 0x2c) = r;
        return r;
    }
    if (fn_008e687b(name, g_00adec3c) == 0) {
        int r = ((C_0045da20*)this)->fn_0005da20(arg2, (char*)this + 0x38);
        *(int*)((char*)this + 0x30) = r;
        return r;
    }
    if (fn_008e687b(name, g_00ae78e8) == 0) { *(int*)((char*)this+0x3c) = 3; return 0; }
    if (fn_008e687b(name, g_00ae78cc) == 0) { *(int*)((char*)this+0x3c) = 11; return 0; }
    if (fn_008e687b(name, g_00ae78b0) == 0) { *(int*)((char*)this+0x3c) = 0x21; return 0; }
    if (fn_008e687b(name, g_00ae7894) == 0) { *(int*)((char*)this+0x3c) = 0x24; return 0; }
    if (fn_008e687b(name, g_00ae7884) == 0) { *(int*)((char*)this+0x3c) = 9; return 0; }
    if (fn_008e687b(name, g_00ae7874) == 0) { *(int*)((char*)this+0x3c) = 0x20; return 0; }
    if (fn_008e687b(name, g_00ae7864) == 0) { *(int*)((char*)this+0x3c) = 0x23; return 0; }
    if (fn_008e687b(name, g_00ae7858) == 0) { *(int*)((char*)this+0x3c) = 0x22; return 0; }
    if (fn_008e687b(name, g_00ae7848) == 0) { *(int*)((char*)this+0x3c) = 2; return 0; }
    if (fn_008e687b(name, g_00ae7840) == 0) { *(int*)((char*)this+0x3c) = 0xc; return 0; }
    return 0;
}
// FUNCTION: DAO 0x0045EC30
bool C_0045EC30::fn_0005ec30(int arg) {
    unsigned char local[0x40];
    ((C_004c2480*)local)->fn_004c2480((void*)arg);
    bool ok = fn_00457150(local);
    if (ok) {
        void* p = fn_00458e80(local);
        p = ((C_004621c0*)p)->fn_004621c0();
        p = ((C_0053cc40*)p)->fn_0053cc40();
        void** vtbl = *(void***)p;
        int v10 = ((int (__thiscall*)(void*))vtbl[4])(p);
        *(int*)((char*)this + 0x2c) = v10;
        int v14 = ((int (__thiscall*)(void*))vtbl[5])(p);
        *(int*)((char*)this + 0x30) = v14;
        int v2c = ((int (__thiscall*)(void*))vtbl[11])(p);
        void** thisvt = *(void***)this;
        ((void (__thiscall*)(void*, int))thisvt[5])(this, v2c);
        *((unsigned char*)this + 0x28) = 1;
        ((C_004c0db0*)local)->fn_004c0db0();
        return true;
    }
    ((C_004c0db0*)local)->fn_004c0db0();
    return false;
}
// FUNCTION: DAO 0x004D29D0
bool C_004D29D0::fn_000d29d0() {
    int* v = *(int**)this;
    unsigned char* p = (unsigned char*)this + v[1] + 8;
    if ((*p & 1) != 0) return true;
    return fn_004d29c0() == 0xffff;
}
// FUNCTION: DAO 0x004D4DD0
void* C_004D4DD0::fn_000d4dd0(float a,float b,float c,float d) {
    *(float*)((char*)this + 0) = a;
    *(float*)((char*)this + 4) = b;
    *(float*)((char*)this + 8) = c;
    *(float*)((char*)this + 0xc) = d;
    return this;
}
// FUNCTION: DAO 0x00507D70
void C_00507D70::fn_00107d70(void* value) {
    unsigned char* begin = *(unsigned char**)((char*)this + 4);
    unsigned char* end = *(unsigned char**)((char*)this + 8);
    unsigned int count = begin ? (unsigned int)((end - begin) / 16) : 0;
    unsigned char* capEnd = *(unsigned char**)((char*)this + 0xc);
    unsigned int cap = begin ? (unsigned int)((capEnd - begin) / 16) : 0;
    if (begin != 0 && count < cap) {
        unsigned char* dest = *(unsigned char**)((char*)this + 8);
        fn_0046bdf0(dest, 1, value, begin, begin, 0);
        *(void**)((char*)this + 8) = dest + 16;
    } else {
        unsigned char* end2 = *(unsigned char**)((char*)this + 8);
        if (begin > end2) fn_008e11f2();
        ((C_00507CE0*)this)->fn_00507ce0(value, end2, this, (void*)((char*)this + 0x10));
    }
}
// FUNCTION: DAO 0x00507F00
void C_00507F00::fn_00107f00(bool flag) {
    if (flag) {
        unsigned char* begin = *(unsigned char**)((char*)this + 4);
        unsigned char* end = *(unsigned char**)((char*)this + 8);
        if (begin > end) fn_008e11f2();
        unsigned char* mid = *(unsigned char**)((char*)this + 8);
        if (begin > mid) fn_008e11f2();
        if (mid != end) {
            void* r = fn_0046bd80(begin, end, mid);
            *(void**)((char*)this + 8) = r;
        }
        void* old = *(void**)((char*)this + 4);
        *(void**)((char*)this + 4) = 0;
        *(void**)((char*)this + 8) = 0;
        *(void**)((char*)this + 0xc) = 0;
        if (old) fn_004136c0(old);
    } else {
        unsigned char* begin = *(unsigned char**)((char*)this + 4);
        if (begin) {
            unsigned char* end = *(unsigned char**)((char*)this + 8);
            if (((end - begin) >> 4) != 0) {
                ((C_0046c2f0*)this)->fn_0046c2f0(0);
            }
        }
    }
}
// FUNCTION: DAO 0x0050F440
void* C_0050F440::fn_0010f440(int a1,int a2,int a3,int a4,int a5,int a6,int a7) {
    (void)a1; (void)a2; (void)a3; (void)a4; (void)a5; (void)a6; (void)a7;
    void* sub = (unsigned char*)this + *(int*)(*(int*)this + 4);
    int field = *(int*)((char*)sub + 0x28);
    int size = (field == 0) ? 4 : 0;
    fn_00407b00(0, size);
    unsigned char local[0x40];
    ((C_004c4bc0*)local)->fn_004c4bc0((char*)this + 8);
    ((C_004c0db0*)local)->fn_004c0db0();
    return this;
}
// FUNCTION: DAO 0x008E19CD
double __cdecl fn_004e19cd(const wchar_t* str) {
    return fn_008e1943(str, 0);
}
// FUNCTION: DAO 0x008E643E
int __cdecl fn_004e643e() {
    return fn_008e642d();
}
// FUNCTION: DAO 0x008E687B
int __cdecl fn_004e687b(const wchar_t* s1, const wchar_t* s2) {
    if (g_00c3eee0 != 0) return fn_008e676c(s1, s2, 0);
    if (s1 == 0 || s2 == 0) {
        *fn_008e37b6() = 0x16;
        fn_008e11ce(0,0,0,0,0);
        return 0x7fffffff;
    }
    const unsigned short* p1 = (const unsigned short*)s1;
    const unsigned short* p2 = (const unsigned short*)s2;
    for (;;) {
        unsigned int c1 = *p1;
        unsigned int c2 = *p2;
        if (c1 >= 'A' && c1 <= 'Z') c1 += 0x20;
        if (c2 >= 'A' && c2 <= 'Z') c2 += 0x20;
        if (c1 == 0) return (int)c1 - (int)c2;
        if (c1 != c2) return (int)c1 - (int)c2;
        ++p1; ++p2;
    }
}
