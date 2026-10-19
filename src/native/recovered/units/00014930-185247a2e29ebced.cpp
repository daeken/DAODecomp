typedef unsigned int u32;
typedef unsigned char u8;

extern "C" {
extern void fn_00014170();
extern void fn_000c2510();
extern void fn_00481510();
extern void fn_0072bb00();
extern void fn_008e11f2();
extern void fn_00769830();
extern void fn_008e18c1();
extern void fn_008e37b6();
extern void fn_008e11ce();
extern void fn_008ee7d0();
extern void fn_008e6c0d();
extern void fn_008e19e0();
extern void fn_008eab50();
extern void fn_008e47aa();
extern void fn_008edf18();
extern void fn_008e10d2();
extern void fn_008e8ea0();
extern void fn_008e1613();
extern void fn_008eac58();
extern void fn_008eb4e1();
extern void fn_008e1a5a();
extern void fn_0048d0b0();
extern void* g_00ada1cc;
extern void* g_00ada148;
extern void* g_00ada220;
extern void* g_00ada0d8;
extern void* g_00ada264;
extern void* g_00c16a7c;
}

typedef int (__thiscall *Th4)(void*, void*, void*, void*, void*);
typedef void (__thiscall *Th1v)(void*, void*);
typedef void* (__thiscall *Th4p)(void*, void*, void*, void*, void*);
typedef void (__cdecl *InvalidFn)();
typedef void (__cdecl *Invalid5Fn)(u32,u32,u32,u32,u32);
typedef u32 (__cdecl *StrlenFn)(const char*);
typedef void* (__cdecl *MallocFn)(u32);
typedef int (__cdecl *StrcpySFn)(char*, u32, const char*);
typedef u32 (__cdecl *FreeSizeFn)(void*);
typedef void* (__cdecl *ReallocFn)(void*, u32);
typedef void* (__cdecl *MemsetFn)(void*, int, u32);
typedef int (__stdcall *WCTMBFn)(u32, u32, const wchar_t*, int, char*, int, const char*, int*);
typedef int (__stdcall *MultiByteToWideChar2)(u32,u32,const char*,int,wchar_t*,int,const char*,int*);
typedef u32 (__stdcall *GetErrFn)();
typedef void* (__cdecl *CreateFn)(const char*, u32, u32, void*, u32, u32, void*);
typedef void* (__cdecl *AllocFn)(u32, void*);

struct C_e6e50 { void* p0; void* p1; void __thiscall fn_000e6e50(); };
struct C_301640 { void* p0; void* p1; void* p2; void* p3; bool __thiscall fn_00301640(u32 n); };
struct C_32bc30 { void* p0; void* p1; void* p2; void* p3; void* __thiscall fn_0032bc30(void* a); };
struct C_480550 { u32 a; u32 b; void __thiscall fn_00480550(void* out); };
struct C_481d20 { void* p0; void* p1; void* p2; void* p3; void* __thiscall fn_00481d20(void* a, void* b, void* c, void* d); };

// FUNCTION: DAO 0x00414930
extern "C" bool __stdcall fn_00014930(void* self, void* str)
{
    u8* eax = (u8*)str;
    u32 ecx = *(u32*)(eax + 0x14);
    u8* p;
    if (*(u32*)(eax + 0x18) >= 8) p = *(u8**)(eax + 4);
    else p = eax + 4;
    u8* s = (u8*)self;
    int r = ((Th4)&fn_00014170)(self, (void*)0, (void*)*(u32*)(s + 0x14), (void*)p, (void*)ecx);
    return r < 0;
}

// FUNCTION: DAO 0x00475860
extern "C" void __cdecl fn_00075860(void* a, void* b)
{
    __try {
        if (a) ((Th1v)&fn_000c2510)(a, b);
    } __except(1) {
    }
}

// FUNCTION: DAO 0x004E6E50
void __thiscall C_e6e50::fn_000e6e50()
{
    if (p0 == 0) ((InvalidFn)&fn_008e11f2)();
    u8* node = (u8*)p1;
    if (node == 0) { ((InvalidFn)&fn_008e11f2)(); return; }
    if (node[0x2d] == 0) {
        u8* left = *(u8**)node;
        if (left[0x2d] != 0) {
            u8* parent = *(u8**)(node + 4);
            if (parent[0x2d] == 0) {
                for (;;) {
                    u8* cur = (u8*)p1;
                    if (cur != *(u8**)parent) break;
                    p1 = parent;
                    u8* next = *(u8**)(parent + 4);
                    if (next[0x2d] != 0) break;
                    parent = next;
                }
            }
            {
                u8* cur = (u8*)p1;
                if (cur[0x2d] == 0) p1 = parent;
                else ((InvalidFn)&fn_008e11f2)();
            }
        } else {
            u8* n = *(u8**)(left + 8);
            if (n[0x2d] == 0) {
                do {
                    left = n;
                    n = *(u8**)(left + 8);
                } while (n[0x2d] == 0);
                p1 = left;
            } else {
                p1 = left;
            }
        }
    } else {
        u8* right = *(u8**)(node + 8);
        p1 = right;
        if (right[0x2d] == 0) return;
        ((InvalidFn)&fn_008e11f2)();
    }
}

// FUNCTION: DAO 0x00701640
bool __thiscall C_301640::fn_00301640(u32 n)
{
    p1 = 0; p2 = 0; p3 = 0;
    if (n == 0) return false;
    if (n > 0x3fffffffu) { ((InvalidFn)&fn_00769830)(); }
    void* mem = ((AllocFn)&fn_0048d0b0)(n, (void*)0);
    p1 = mem; p2 = mem; p3 = (u8*)mem + n * 4;
    return true;
}

// FUNCTION: DAO 0x0072BC30
void* __thiscall C_32bc30::fn_0032bc30(void* a)
{
    ((Th1v)&fn_0072bb00)(this, a);
    return this;
}

// FUNCTION: DAO 0x00880550
void __thiscall C_480550::fn_00480550(void* out)
{
    u32* o = (u32*)out;
    o[0] = a;
    o[1] = b;
}

// FUNCTION: DAO 0x00881D20
void* __thiscall C_481d20::fn_00481d20(void* a, void* b, void* c, void* d)
{
    if (p2 == 0) {
        ((Th4p)&fn_00481510)(this, a, (void*)1, p1, d);
        return a;
    }
    {
        void* root = p1;
        void* first = root ? *(void**)root : 0;
        if (b == 0 || b == this) ((InvalidFn)&fn_008e11f2)();
        if (c == first) {
            if (d && *(u32*)d < *(u32*)((u8*)c + 0xc)) {
                ((Th4p)&fn_00481510)(this, a, (void*)1, c, d);
                return a;
            }
        } else {
            if (c && d && *(u32*)c < *(u32*)((u8*)d + 0xc)) {
                ((Th4p)&fn_00481510)(this, a, (void*)0, c, d);
                return a;
            }
        }
        {
            C_e6e50 tmp;
            tmp.p0 = b;
            tmp.p1 = c;
            tmp.fn_000e6e50();
        }
        ((Th4p)&fn_00481510)(this, a, (void*)0, c, d);
        return a;
    }
}

// FUNCTION: DAO 0x008E6E28
extern "C" void* __cdecl fn_004e6e28(void* p, u32 count, u32 size)
{
    if (count == 0 || (0xffffffe0u / count) >= size) {
        ((void (__cdecl*)())&fn_008e37b6)();
        ((Invalid5Fn)&fn_008e11ce)(0,0,0,0,0);
        return 0;
    }
    {
        u32 total = count * size;
        u32 old = 0;
        if (p) old = ((FreeSizeFn)&fn_008ee7d0)(p);
        void* r = ((ReallocFn)&fn_008e6c0d)(p, total);
        if (!r) return 0;
        if (old < total) ((MemsetFn)&fn_008e19e0)((u8*)r + old, 0, total - old);
        return r;
    }
}

// FUNCTION: DAO 0x008FF09E
extern "C" int __cdecl fn_004ff09e(int* sizeOut, char* mb, u32 sizeBytes, wchar_t wch, void* locale)
{
    if (mb == 0) {
        if (sizeBytes > 0) { if (sizeOut) *sizeOut = 0; return 0; }
    }
    if (sizeOut) *sizeOut = -1;
    if (sizeBytes > 0x7fffffffu) {
        ((void (__cdecl*)())&fn_008e37b6)();
        ((Invalid5Fn)&fn_008e11ce)(0,0,0,0,0);
        return 22;
    }
    {
        u8 locbuf[0x10];
        ((Th1v)&fn_008e18c1)(locbuf, locale);
        (void)locbuf;
    }
    if (wch > 0xff) {
        int r = ((WCTMBFn)g_00ada1cc)(0, 0, &wch, 1, mb, (int)sizeBytes, 0, 0);
        if (r == 0) {
            if (((GetErrFn)g_00ada148)() == 0x7a) {
                if (mb && sizeBytes > 0) ((MemsetFn)&fn_008e19e0)(mb, 0, sizeBytes);
            } else {
                return 42;
            }
        } else {
            if (sizeOut) *sizeOut = r;
            return 0;
        }
    } else {
        if (mb && sizeBytes > 0) { mb[0] = (char)wch; if (sizeOut) *sizeOut = 1; return 0; }
    }
    return 42;
}

// FUNCTION: DAO 0x009002B3
extern "C" int __cdecl fn_005002b3(void* a0, void* a1, void* a2, void* a3, void* a4, void* a5, void* a6)
{
    u32 n1 = (u32)a1;
    u32 n2 = (u32)a2;
    u32 n3 = (u32)a3;
    int result = 0;
    (void)a4; (void)a5; (void)a6;
    if (n1 != 0 && n2 != 0) {
        int r = ((MultiByteToWideChar2)g_00ada220)(0,0,(const char*)a0,(int)n1,0,0,0,0);
        if (r > 0) {
            int r2 = ((MultiByteToWideChar2)g_00ada220)(0,0,(const char*)a0,(int)n1,(wchar_t*)a3,(int)n2,0,0);
            if (r2 > 0) {
                int r3 = ((WCTMBFn)g_00ada0d8)(0,0,(const wchar_t*)a3,r2,(char*)a2,(int)n3,0,0);
                if (r3 > 0) result = r3;
            }
        }
    }
    ((void (__cdecl*)())&fn_008e1613)();
    return result;
}

// FUNCTION: DAO 0x00907EF6
extern "C" void __cdecl fn_00507ef6(void)
{
    g_00c16a7c = ((CreateFn)g_00ada264)((const char*)0x00b479d0, 0x40000000u, 3, 0, 3, 0, 0);
}

// FUNCTION: DAO 0x00908D98
extern "C" char* __cdecl fn_00508d98(char* src)
{
    if (src == 0) return 0;
    {
        u32 len = ((StrlenFn)&fn_008eab50)(src) + 1;
        char* dst = (char*)((MallocFn)&fn_008e47aa)(len);
        if (dst == 0) return 0;
        if (((StrcpySFn)&fn_008edf18)(dst, len, src) != 0) {
            ((Invalid5Fn)&fn_008e10d2)(0,0,0,0,0);
        }
        return dst;
    }
}
