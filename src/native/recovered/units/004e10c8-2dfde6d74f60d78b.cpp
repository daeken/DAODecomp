typedef unsigned int u32;
typedef unsigned char u8;

struct TryBlockMapEntry04e { int tryLow; int tryHigh; int catchHigh; int nCatches; void* pHandlerArray; };
struct FuncInfo04e { u8 pad0[0xc]; int nTryBlocks; TryBlockMapEntry04e* pTryBlockMap; };

extern "C" u32 g_0083ee98;
extern "C" u32 g_0083f594;
extern "C" u32 g_0083f900;
extern "C" u32 g_0083f95c;
extern "C" void* g_0083ef4c;
extern "C" u32 g_00815554;
extern "C" u32 g_00815550;
extern "C" char g_0073abe4[];
extern "C" char g_0073abd4[];
extern "C" u8 g_004e13e4[];
extern "C" void* (__stdcall *g_006da234)(u32);
extern "C" void* (__stdcall *g_006da22c)(const char*);
extern "C" void* (__stdcall *g_006da110)(void*, const char*);

extern "C" void* __cdecl fn_004ee2b8(void);
extern "C" void __cdecl fn_004ee62a(void);
extern "C" int __cdecl fn_004edf85(void);
extern "C" void* __cdecl fn_004ee068(void*);
extern "C" void __cdecl fn_004ed38a(void*, void*, void*, void*);
extern "C" void __cdecl fn_004e1283(void*, void*);
extern "C" void __cdecl fn_004ecdfb(void*, void*, void*, void*);
extern "C" void* __cdecl fn_004ed06f(void*, void*, void*, void*, void*, void*, void*);
extern "C" void __cdecl fn_004e124c(void*, void*);
extern "C" void __cdecl fn_004f0940(u32);
extern "C" void __cdecl fn_004ee874(void);

// FUNCTION: DAO 0x008E10C8
extern "C" void __cdecl fn_004e10c8(u32 value) { g_0083ee98 = value; }

// FUNCTION: DAO 0x008E133B
extern "C" int __cdecl fn_004e133b(void* param_1, void** param_2, void* param_3, void* param_4, void* param_5, int param_6, void* param_7) {
    if (param_1 == (void*)0x123) {
        *param_2 = (void*)g_004e13e4;
        return 1;
    }
    struct { void* p1; void* p3; void* translator; } args;
    args.p1 = param_1;
    args.p3 = param_3;
    void* ptd = fn_004ee2b8();
    void* tr = *(void**)((u8*)ptd + 0x80);
    args.translator = tr;
    typedef void (__cdecl *TrFn)(void*, void*);
    ((TrFn)tr)(*(void**)param_1, &args);
    return 0;
}

// FUNCTION: DAO 0x008E14AD
extern "C" TryBlockMapEntry04e* __cdecl fn_004e14ad(FuncInfo04e* fi, int limit, int value, u32* outStart, u32* outEnd) {
    TryBlockMapEntry04e* map = fi->pTryBlockMap;
    int esi = fi->nTryBlocks;
    int ebx = esi;
    int prev = esi;
    for (;;) {
        if (limit < 0) break;
        if (esi == -1) fn_004ee62a();
        esi--;
        TryBlockMapEntry04e* e = (TryBlockMapEntry04e*)((u8*)map + esi * 0x14);
        int take = 0;
        if (e->tryLow >= value) {
            take = 0;
        } else if (value <= e->tryHigh) {
            take = 1;
        } else {
            take = 0;
        }
        if (take) {
            limit--;
            ebx = prev;
            prev = esi;
        } else {
            if (esi == -1) {
                limit--;
                ebx = prev;
                prev = esi;
            }
        }
    }
    *outStart = (u32)(esi + 1);
    *outEnd = (u32)ebx;
    if ((u32)ebx > (u32)fi->nTryBlocks) fn_004ee62a();
    if ((u32)(esi + 1) > (u32)ebx) fn_004ee62a();
    return (TryBlockMapEntry04e*)((u8*)map + esi * 0x14);
}

// FUNCTION: DAO 0x008ED41B
extern "C" void __cdecl fn_004ed41b(void* p8, void* p0c, void* p10, void* p14, void* p18, void* p1c, void* p20) {
    void* ebx = p8;
    void* esi = p0c;
    void* edi = p10;
    if (p18) fn_004ed38a(p8, ebx, esi, p18);
    if (p20) fn_004e1283(p8, p20); else fn_004e1283(p8, esi);
    fn_004ecdfb(esi, p10, p14, *(void**)edi);
    *(u32*)((u8*)esi + 8) = *(u32*)((u8*)edi + 4) + 1;
    void* thisptr = *(void**)((u8*)ebx + 0xc);
    void* r = fn_004ed06f(thisptr, p8, esi, p0c, p14, p1c, (void*)0x100);
    if (r) fn_004e124c(r, esi);
}

// FUNCTION: DAO 0x008EDB6A
extern "C" void __cdecl fn_004edb6a(void** begin, void** end) {
    for (void** p = begin; p < end; ++p) {
        void (__cdecl *f)(void) = (void (__cdecl *)(void))*p;
        if (f) f();
    }
}

// FUNCTION: DAO 0x008EDD74
extern "C" void __cdecl fn_004edd74(void* a, void* b, int c) {
    if (c) fn_004f0940(8);
}

// FUNCTION: DAO 0x008EDFF1
extern "C" void* __cdecl fn_004edff1(void* arg) {
    void* p = g_006da234(g_00815554);
    if (p) {
        u32 idx = g_00815550;
        if (idx != 0xFFFFFFFFu) {
            void* q = g_006da234(idx);
            if (q) {
                typedef void* (__cdecl *F0)(void);
                void* r = ((F0)q)();
                if (r) return *(void**)((u8*)r + 0x1f8);
            }
        }
    }
    void* h = g_006da22c(g_0073abe4);
    if (h && fn_004edf85()) {
        void* enc = g_006da110(h, g_0073abd4);
        if (enc) {
            typedef void* (__cdecl *F1)(void*);
            arg = ((F1)enc)(arg);
        }
    }
    return arg;
}

// FUNCTION: DAO 0x008EE05F
extern "C" void* __cdecl fn_004ee05f(void) { return fn_004edff1(0); }

// FUNCTION: DAO 0x008EE62A
extern "C" void __cdecl fn_004ee62a(void) {
    void* p = fn_004ee068(g_0083ef4c);
    if (p) ((void (__cdecl *)(void))p)();
}

// FUNCTION: DAO 0x008EF75B
extern "C" void __cdecl fn_004ef75b(u32 value) { g_0083f594 = value; }

// FUNCTION: DAO 0x008F71FB
extern "C" void __cdecl fn_004f71fb(u32 value) { g_0083f900 = value; }

// FUNCTION: DAO 0x009030E6
extern "C" void __cdecl fn_005030e6(u32 value) { g_0083f95c = value; }
