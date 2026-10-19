typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int i32;
typedef float f32;

extern unsigned char g_00C31650[];
extern unsigned char g_00C35A30;
extern unsigned char g_00C32938[];
extern unsigned char g_00C15234[];
extern unsigned char g_00C1D090[];
extern unsigned char g_00C3B9D8[];
extern unsigned char g_00C063EC[];
extern unsigned char g_00C06424[];
extern unsigned char g_00C3BAC0[];

extern float __fastcall fn_00078290(void*, void*);
extern unsigned char __fastcall fn_00438210(void*, void*);
extern void* __cdecl fn_001b9020(void*);
extern void __fastcall fn_001bc2f0(void*, void*);
extern void __fastcall fn_002c3d60(void*, void*);
extern void __fastcall fn_00294210(void*, void*, int, int);
extern int __cdecl fn_000c3420(const char*);
extern void __fastcall fn_00493d70(void*, void*);
extern void __cdecl fn_002e9510();
extern void* __cdecl fn_000df580(u32);
extern void* __fastcall fn_00003c70(void*, void*);
extern void __fastcall fn_000c1150(void*, void*);
extern void __fastcall fn_000c2480(void*, void*, const char*);
extern void __fastcall fn_000c0db0(void*, void*);
extern void __fastcall fn_000c0d90(void*, void*);
extern void* __fastcall fn_000c30f0(void*, void*, int, void*);
extern bool __fastcall fn_000c0e10(void*, void*, const char*);
extern void* __fastcall fn_000c31a0(void*, void*, int, void*);
extern void* __fastcall fn_004823c0(void*, void*, void*);
extern void __fastcall fn_00494cc0(void*, void*, void*, void*);
extern void __fastcall fn_004e1613(void*, void*);
extern void __cdecl fn_002e2fd0();
extern void* __cdecl fn_000c7990(void*);
extern unsigned char __fastcall fn_000c6270(void*, void*);
extern void __fastcall fn_00313920(void*, void*, int, int);
extern void* __cdecl fn_00055bf0();
extern void* __fastcall fn_000ca9a0(void*, void*, void*, int);
extern void __fastcall fn_001c6650(void*, void*, void*, void*);
extern void* __fastcall fn_0008a970(void*, void*);
extern void __fastcall fn_004927f0(void*, void*, void*);
extern void __fastcall fn_000e1bf0(void*, void*, void*, void*, void*);
extern void __fastcall fn_00493ba0(void*, void*, void*, void*);
extern void __fastcall fn_00493a40(void*, void*, void*);
extern void __fastcall fn_000e2900(void*, void*);
extern void __fastcall fn_0008a900(void*, void*);
extern void* __cdecl fn_00013660(u32);
extern void __fastcall fn_00495330(void*, void*);
extern void __cdecl fn_004f0940(int);

extern void __fastcall fn_001dda30(void*, void*);
extern void __fastcall fn_002c4410(void*, void*);
extern void __cdecl fn_002ea8f0();
extern void __cdecl fn_002ea9f0();
extern void __cdecl fn_00306360();
extern void __fastcall fn_0036d3c0(void*, void*, int, int);
extern void __fastcall fn_0036e0a0(void*, void*, int, int);
extern void __fastcall fn_0036e920(void*, void*, int, int);
extern void __fastcall fn_00467f40(void*, void*, int);
extern void __fastcall fn_00495580(void*, void*, int);
extern void* __cdecl fn_00495dc0();
extern void __cdecl fn_004e6bac();

// FUNCTION: DAO 0x5DDA30
void __fastcall fn_001dda30(void* self, void* edx) {
    u8* base = reinterpret_cast<u8*>(self);
    f32 f0 = fn_00078290(base + 0x390, 0);
    u8 bl = fn_00438210(base + 0x3a0, 0);
    f32 f1 = fn_00078290(base + 0x3b0, 0);
    u8 al1 = fn_00438210(base + 0x3c0, 0);
    f32 f2 = fn_00078290(base + 0x3e0, 0);
    u8 al2 = fn_00438210(base + 0x3f0, 0);
    bool take = (bl != 0) || (f0 > 0.0f);
    u8 flag = take ? 1 : 0;
    void* p = *reinterpret_cast<void**>(g_00C31650);
    if (p != 0) {
        void** vt = *reinterpret_cast<void***>(p);
        typedef void* (__fastcall *GetFn)(void*, void*);
        GetFn get = reinterpret_cast<GetFn>(vt[0xC0/4]);
        void* r = get(p, 0);
        if (r != 0) {
            void** vt2 = *reinterpret_cast<void***>(r);
            typedef void (__fastcall *SetFn)(void*, void*, unsigned char);
            SetFn set = reinterpret_cast<SetFn>(vt2[0x10/4]);
            set(r, 0, flag);
        }
    }
    u8 local = 0;
    void* arg = fn_001b9020(&local);
    fn_001bc2f0(arg, 0);
    (void)f1; (void)f2; (void)al1; (void)al2;
}

// FUNCTION: DAO 0x6C4410
void __fastcall fn_002c4410(void* self, void* edx) {
    u8* base = reinterpret_cast<u8*>(self);
    fn_002c3d60(self, 0);
    f32 z = 0.0f;
    *reinterpret_cast<f32*>(base + 0x48) = z;
    *reinterpret_cast<f32*>(base + 0x44) = z;
    *reinterpret_cast<f32*>(base + 0x24) = z;
    *reinterpret_cast<f32*>(base + 0x28) = z;
}

// FUNCTION: DAO 0x6EA8F0
void __cdecl fn_002ea8f0() {
    if (g_00C35A30 != 0) {
        void* base = *reinterpret_cast<void**>(g_00C32938);
        char* p = reinterpret_cast<char*>(base) + 0x550;
        fn_000c3420(p);
        void* obj = fn_00495dc0();
        fn_00495580(obj, 0, 0);
    }
}

// FUNCTION: DAO 0x6EA9F0
void __cdecl fn_002ea9f0() {
    void* obj = fn_00495dc0();
    fn_00493d70(obj, 0);
    fn_002e9510();
    void* g = *reinterpret_cast<void**>(g_00C1D090);
    if (g != 0) {
        void* p = fn_000df580(0x124);
        if (p != 0) {
            void* base = *reinterpret_cast<void**>(g_00C32938);
            void* v = fn_00003c70(reinterpret_cast<u8*>(base) + 0x118, 0);
            fn_000c1150(v, 0);
            fn_000c2480(p, 0, reinterpret_cast<const char*>(0xb0067c));
        }
    }
    fn_002e2fd0();
}

// FUNCTION: DAO 0x706360
void __cdecl fn_00306360() {
    for (u32 i = 0; i < 0x240; i += 0x40) {
        void* p = fn_000c7990(g_00C063EC + i);
        g_00C06424[i] = fn_000c6270(p, 0);
    }
}

// FUNCTION: DAO 0x76D3C0
void __fastcall fn_0036d3c0(void* self, void* edx, int a, int b) {
    u8* base = reinterpret_cast<u8*>(self);
    fn_00294210(self, 0, a, b);
    *reinterpret_cast<void**>(base) = reinterpret_cast<void*>(0xb1d60c);
    *reinterpret_cast<void**>(base + 8) = reinterpret_cast<void*>(0xb1d5f8);
    *reinterpret_cast<void**>(base + 0x1c) = reinterpret_cast<void*>(0xb1d59c);
    *reinterpret_cast<void**>(base + 0x20) = reinterpret_cast<void*>(0xb1d588);
    *reinterpret_cast<u32*>(base + 0x5c) = 6;
}

// FUNCTION: DAO 0x76E0A0
void __fastcall fn_0036e0a0(void* self, void* edx, int a, int b) {
    u8* base = reinterpret_cast<u8*>(self);
    fn_00294210(self, 0, a, b);
    *reinterpret_cast<void**>(base) = reinterpret_cast<void*>(0xb1d734);
    *reinterpret_cast<void**>(base + 8) = reinterpret_cast<void*>(0xb1d720);
    *reinterpret_cast<void**>(base + 0x1c) = reinterpret_cast<void*>(0xb1d6c4);
    *reinterpret_cast<void**>(base + 0x20) = reinterpret_cast<void*>(0xb1d6ac);
    *reinterpret_cast<u32*>(base + 0x5c) = 2;
    base[0x68] = 1;
    base[0x69] = 0;
}

// FUNCTION: DAO 0x76E920
void __fastcall fn_0036e920(void* self, void* edx, int a, int b) {
    u8* base = reinterpret_cast<u8*>(self);
    fn_00313920(self, 0, a, b);
    *reinterpret_cast<void**>(base) = reinterpret_cast<void*>(0xb1d89c);
    *reinterpret_cast<void**>(base + 8) = reinterpret_cast<void*>(0xb1d888);
    *reinterpret_cast<void**>(base + 0x1c) = reinterpret_cast<void*>(0xb1d82c);
    *reinterpret_cast<void**>(base + 0x20) = reinterpret_cast<void*>(0xb1d818);
    fn_000c2480(reinterpret_cast<u8*>(base) + 0x18, 0, reinterpret_cast<const char*>(0xb13528));
    void* ctx = fn_00055bf0();
    if (ctx != 0) fn_001c6650(ctx, 0, self, 0);
    *reinterpret_cast<u32*>(base + 0x5c) = 1;
    base[0x68] = 1;
    base[0x69] = 0;
}

// FUNCTION: DAO 0x867F40
void __fastcall fn_00467f40(void* self, void* edx, int a) {
    *reinterpret_cast<int*>(self) = a;
}

// FUNCTION: DAO 0x895580
void __fastcall fn_00495580(void* self, void* edx, int arg) {
    u8* base = reinterpret_cast<u8*>(self);
    fn_0008a970(base + 0xb4, 0);
    void* begin = *reinterpret_cast<void**>(base + 0xdc);
    void* end = *reinterpret_cast<void**>(base + 0xe0);
    if (begin != 0 && end != 0) {
        u32 n = static_cast<u32>(reinterpret_cast<u8*>(end) - reinterpret_cast<u8*>(begin)) / 4;
        for (u32 i = 0; i < n; ++i) {
            void* item = *reinterpret_cast<void**>(reinterpret_cast<u8*>(begin) + i * 4);
            if (item != 0) fn_000ca9a0(item, 0, 0, 0);
        }
    }
    fn_000e2900(base + 0xb4, 0);
    fn_0008a900(base + 0xd0, 0);
    fn_000c0db0(base + 0xb4, 0);
}

// FUNCTION: DAO 0x895DC0
void* __cdecl fn_00495dc0() {
    void* p = *reinterpret_cast<void**>(g_00C3B9D8);
    if (p == 0) {
        p = fn_00013660(0xe8);
        if (p != 0) {
            fn_00495330(p, 0);
            *reinterpret_cast<void**>(g_00C3B9D8) = p;
        } else {
            *reinterpret_cast<void**>(g_00C3B9D8) = 0;
        }
    }
    return *reinterpret_cast<void**>(g_00C3B9D8);
}

// FUNCTION: DAO 0x8E6BAC
void __cdecl fn_004e6bac() {
    fn_004f0940(4);
}
