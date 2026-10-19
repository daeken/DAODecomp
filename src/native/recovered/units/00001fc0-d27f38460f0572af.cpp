typedef void (__thiscall *FnThis0)(void*);
typedef void (__thiscall *FnThis1)(void*, void*);
typedef void (__thiscall *FnThis2)(void*, void*, void*);
typedef unsigned char (__thiscall *FnThis0R8)(void*);
typedef unsigned char (__thiscall *FnThis1R8)(void*, int);
typedef unsigned char (__thiscall *FnThis1R8Ptr)(void*, void*);
typedef void* (__thiscall *FnThis2RetPtr)(void*, void*, void*);

extern "C" void* g_00831650;
extern "C" void* g_008327ec;
extern "C" void* g_0082be24;
extern "C" unsigned char g_00831644;

extern "C" void fn_004c3a50();
extern "C" void fn_004cb2b0();
extern "C" void fn_004c5bf0();
extern "C" void* fn_004c3360();
extern "C" void fn_004c2ab0();
extern "C" void fn_004c0d90();
extern "C" void fn_004c0db0();
extern "C" void fn_004cb300();
extern "C" unsigned char fn_004c80f0();
extern "C" void __cdecl fn_008e11f2(void);
extern "C" void __cdecl fn_004cc2f0(void*);
extern "C" void fn_004c2510();
extern "C" void __cdecl fn_004cc230(void*);
extern "C" void* __cdecl fn_00401f30(...);
extern "C" void* __cdecl fn_00402900(void);
extern "C" void fn_0047d4d0();
extern "C" void __cdecl fn_004c3030(void*, const char*, void*);
extern "C" void fn_004c4140();
extern "C" void* __cdecl fn_00419550(void);
extern "C" void* __cdecl fn_0044dcb0(void);
extern "C" void* __cdecl fn_001b9020(void);
extern "C" void fn_001bbf60();
extern "C" void fn_005d7180();
extern "C" void fn_000d6700();
extern "C" void __cdecl fn_000c5360(void);

struct C_00402010 { unsigned char fn_00002010(); };
struct C_00402090 { unsigned char fn_00002090(); };
struct C_004c8330 { unsigned char fn_000c8330(void*); };
struct C_005d5640 { void fn_001d5640(); };

// FUNCTION: DAO 0x00401fc0
extern "C" unsigned char __cdecl fn_00001fc0(void) {
    fn_000c5360();
    return 1;
}

// FUNCTION: DAO 0x00401fe0
extern "C" void __cdecl fn_00001fe0(void) {
    void* p = fn_00419550();
    void** vt = *(void***)p;
    ((FnThis0)vt[0x14 / 4])(p);
}

// FUNCTION: DAO 0x00402000
extern "C" void __cdecl fn_00002000(void) {
    void* p = fn_0044dcb0();
    void** vt = *(void***)p;
    ((FnThis0)vt[0xc / 4])(p);
}

// FUNCTION: DAO 0x00402010
unsigned char C_00402010::fn_00002010() {
    unsigned char* s = (unsigned char*)this;
    void* p = g_00831650;
    void** vt = *(void***)p;
    void* arg = *(void**)(s + 0x4c);
    ((FnThis1)vt[0x38 / 4])(p, arg);
    *(void**)(s + 0x4c) = 0;
    ((FnThis1)vt[0x20 / 4])(p, (void*)0);
    unsigned char bl = ((FnThis0R8)vt[0xc / 4])(p);
    void* p2 = *(void**)(s + 0xc8);
    void** vt2 = *(void***)p2;
    unsigned char al = ((FnThis0R8)vt2[0xc / 4])(p2);
    return (unsigned char)(al & bl);
}

// FUNCTION: DAO 0x00402080
extern "C" unsigned char __cdecl fn_00002080(void) {
    void* p = fn_001b9020();
    ((FnThis0)fn_001bbf60)(p);
    return 1;
}

// FUNCTION: DAO 0x00402090
unsigned char C_00402090::fn_00002090() {
    unsigned char* s = (unsigned char*)this;
    void* g = g_008327ec;
    void* p = *(void**)((unsigned char*)g + 0xc8);
    if (p) {
        void** vt = *(void***)p;
        ((FnThis0)vt[0xc8 / 4])(p);
    }
    ((FnThis0)fn_005d7180)(g);
    p = *(void**)(s + 0xb4);
    if (p) {
        void** vt = *(void***)p;
        ((FnThis1)vt[0])(p, (void*)1);
    }
    *(void**)(s + 0xb4) = 0;
    p = *(void**)(s + 0xb8);
    if (p) {
        void** vt = *(void***)p;
        ((FnThis1)vt[0])(p, (void*)1);
    }
    *(void**)(s + 0xb8) = 0;
    return 1;
}

// FUNCTION: DAO 0x004028f0
extern "C" void* __cdecl fn_000028f0(void) {
    return (void*)0x00c32dc0;
}

// FUNCTION: DAO 0x004c5360
extern "C" void __cdecl fn_000c5360(void) {
    void* p = g_0082be24;
    if (p) {
        ((FnThis1)fn_000d6700)(p, (void*)0);
        g_0082be24 = 0;
    }
}

// FUNCTION: DAO 0x004c8330
unsigned char C_004c8330::fn_000c8330(void* arg) {
    unsigned char buf5c[0x20];
    unsigned char buf40[0x20];
    unsigned char buf24[0x20];
    unsigned char result = 0;
    ((FnThis0)fn_004c0d90)(buf5c);
    ((FnThis1)fn_004c3a50)(arg, buf5c);
    ((FnThis0)fn_004c0d90)(buf40);
    unsigned char* ebp = (unsigned char*)this + 0xe8;
    if (((FnThis1R8)fn_004cb2b0)(ebp, -1) == 1) {
        ((FnThis2)fn_004c5bf0)((unsigned char*)this + 0x90, buf5c, buf24);
        if (buf24[0] == 1) {
            fn_008e11f2();
            fn_008e11f2();
            void* tmp = (void*)0;
            void* ret3360 = ((FnThis2RetPtr)fn_004c3360)(tmp, arg, buf24);
            ((FnThis1)fn_004c2ab0)(buf40, ret3360);
            ((FnThis0)fn_004c0db0)(buf24);
            ((FnThis0)fn_004cb300)(ebp);
            if (*(void**)(buf40 + 0x14) != 0) {
                result = ((FnThis1R8Ptr)fn_004c80f0)(this, buf40);
            }
        }
    } else {
        fn_004cc2f0(arg);
        ((FnThis1)fn_004c2510)(buf24, arg);
        fn_004cc230(buf24);
        if (*(void**)(buf24 + 0x14) != 0) {
            ((FnThis0)fn_004cb300)(ebp);
            result = fn_000c8330(buf24);
        }
        ((FnThis0)fn_004c0db0)(buf24);
    }
    ((FnThis0)fn_004c0db0)(buf40);
    ((FnThis0)fn_004c0db0)(buf5c);
    return result;
}

// FUNCTION: DAO 0x00527900
extern "C" void __cdecl fn_00127900(unsigned char flag) {
    g_00831644 = flag;
    void* p = g_00831650;
    if (flag) {
        *(void**)((unsigned char*)p + 0xc0) = *(void**)((unsigned char*)p + 0xb8);
    } else {
        *(void**)((unsigned char*)p + 0xc0) = *(void**)((unsigned char*)p + 0xb4);
    }
}

// FUNCTION: DAO 0x005d5640
void C_005d5640::fn_001d5640() {
    unsigned char* s = (unsigned char*)this;
    if (!fn_00401f30()) return;
    void* p = *(void**)(s + 0x158);
    if (p) {
        void** vt = *(void***)p;
        void* esi = ((void* (__thiscall *)(void*, int))vt[0x60 / 4])(p, 0x17);
        if (esi) {
            unsigned char buf28[0x20];
            ((FnThis0)fn_004c0d90)(buf28);
            void* value = *(void**)((unsigned char*)esi + 0xc0);
            fn_004c3030(buf28, (const char*)0x00aea900, value);
            void* eax1 = fn_00401f30((void*)0x47414d45, (void*)0x43544143, buf28, (void*)0);
            void* eax2 = fn_00402900();
            ((FnThis0)fn_0047d4d0)(eax2);
            ((FnThis0)fn_004c0db0)(buf28);
        }
    }
    unsigned char buf0c[0x20];
    ((FnThis0)fn_004c0d90)(buf0c);
    void* value2 = *(void**)(s + 0xfc);
    fn_004c3030(buf0c, (const char*)0x00aeab64, value2);
    void* eax3 = fn_00401f30((void*)0x47414d45, (void*)0x43504155, buf0c, (void*)0);
    void* eax4 = fn_00402900();
    ((FnThis0)fn_0047d4d0)(eax4);
    unsigned char buf44[0x20];
    ((FnThis1)fn_004c4140)(buf44, (void*)0x00adff52);
    void* eax5 = fn_00401f30((void*)0x47414d45, (void*)0x53485444, buf44, (void*)0);
    void* eax6 = fn_00402900();
    ((FnThis0)fn_0047d4d0)(eax6);
    ((FnThis0)fn_004c0db0)(buf44);
    ((FnThis0)fn_004c0db0)(buf0c);
}
