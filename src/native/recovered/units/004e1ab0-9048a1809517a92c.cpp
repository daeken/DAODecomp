typedef unsigned int uint32;

// free unresolved callees
void __cdecl fn_004e11f2(void);
void __cdecl fn_000bf3d0(void);
int  __cdecl fn_00014170(unsigned int, unsigned int, void*, unsigned int);
int  __cdecl fn_004e7720(void*, unsigned int, const wchar_t*, ...);
void* __cdecl fn_004e47aa(unsigned int);
void* __cdecl fn_004e7e82(void*, void*, void*, void*);
void __cdecl fn_004e1a5a(void*);
void __cdecl fn_00058e90(unsigned int);
void __cdecl fn_004f0940(unsigned int);
int  __cdecl fn_004e8012(void*, void*, void*, int, void*);
void __cdecl fn_004e1613(void);

// unresolved data / import slots
extern wchar_t g_00af01d4[];
extern unsigned char g_00c1eb50;
extern int (__cdecl *g_00ada0dc)(void*, void*, void*, unsigned int);

// unresolved thiscall callees represented as minimal classes
struct C_fn_000c2510 { void fn_000c2510(void*); };
struct C_fn_00009980 { void fn_00009980(void*, void*, unsigned int, void*); };
struct C_fn_0029c280 { void fn_0029c280(void*, void*, void*, void*, void*); };
struct C_fn_000c0db0 { void fn_000c0db0(void); };
struct C_fn_000bf0b0 { void fn_000bf0b0(void*, int); };
struct C_fn_000c2480 { void fn_000c2480(void*); };
struct C_fn_000c9300 { void fn_000c9300(void*, void*); };
struct C_fn_000c8af0 { void fn_000c8af0(void*, int, unsigned int); };
struct C_fn_000c8bb0 { void fn_000c8bb0(void); };
struct C_fn_0013cc40 { int fn_0013cc40(void); };
struct C_fn_00003c70 { void* fn_00003c70(void); };
struct C_fn_00438210 { char fn_00438210(void); };
struct C_fn_00002910 { void fn_00002910(void); };
struct C_fn_000c1270 { void fn_000c1270(void*, void*, void*); };

// requested thiscall functions as out-of-line methods
struct C_0000a320 { void fn_0000a320(unsigned int, void*, void*, void*, void*, void*, void*, void*); };
struct C_0000a450 { void* fn_0000a450(void*, void*, void*, void*); };
struct C_0000bf790 { void fn_0000bf790(void*, int, void*, void*, void*); };
struct C_0000c04c0 { int fn_0000c04c0(unsigned int, unsigned int, const wchar_t*); };
struct C_0000c1240 { unsigned char fn_0000c1240(void*); };
struct C_0000c2670 { void* fn_0000c2670(void*, void*, unsigned int); };
struct C_0000c89f0 { int fn_0000c89f0(void*, void*, unsigned char); };
struct C_001dee10 { void fn_001dee10(void); };

// =====================================================================
// FUNCTION: DAO 0x00406180
void __cdecl fn_00006180(char* first, unsigned int count, void* alloc)
{
    while (count != 0) {
        if (first != 0) {
            ((C_fn_000c2510*)first)->fn_000c2510(alloc);
        }
        --count;
        first += 0x1c;
    }
}

// =====================================================================
// FUNCTION: DAO 0x0040a320
void C_0000a320::fn_0000a320(unsigned int idx, void* p2, void* p3, void* p4, void* p5, void* p6, void* p7, void* p8)
{
    char* b = (char*)this;
    char* first = *(char**)(b + 4);
    char* last = *(char**)(b + 8);
    unsigned int count = 0;
    if (first != 0) {
        count = (unsigned int)((last - first) / 0x1c);
    }
    if (count >= idx) {
        void* tmp = 0;
        ((C_fn_0029c280*)this)->fn_0029c280(&tmp, this, p6, p7, p8);
        ((C_fn_000c0db0*)&tmp)->fn_000c0db0();
    } else {
        char* end = *(char**)(b + 8);
        if (first > end) {
            fn_004e11f2();
        }
        unsigned int delta = idx - count;
        void* tmp = 0;
        ((C_fn_00009980*)this)->fn_00009980(this, end, delta, &tmp);
    }
}

// =====================================================================
// FUNCTION: DAO 0x0040a450
void* C_0000a450::fn_0000a450(void* out, void* a2, void* a3, void* a4)
{
    char* b = (char*)this;
    char* first = *(char**)(b + 4);
    unsigned int cur = 0;
    if (first != 0) {
        char* last = *(char**)(b + 8);
        cur = (unsigned int)((last - first) / 0x1c);
    }
    (void)cur;
    ((C_fn_00009980*)this)->fn_00009980(a2, a3, 1u, a4);
    if (out != 0) {
        *(void**)out = this;
        *(void**)((char*)out + 4) = first;
    }
    return out;
}

// =====================================================================
// FUNCTION: DAO 0x004bf790
void C_0000bf790::fn_0000bf790(void* a1, int a2, void* a3, void* a4, void* a5)
{
    char* b = (char*)this;
    (void)a5;
    if (*(unsigned char*)(b + 0x878) == 0) return;
    if (*(void**)(b + 0x38) == 0) return;
    if (*(char**)(b + 0x3c) > *(char**)(b + 0x40)) {
        fn_000bf3d0();
        return;
    }
    void* local = 0;
    ((C_fn_000bf0b0*)this)->fn_000bf0b0(&local, a2);
    wchar_t buf[0x400];
    void* s = *(void**)(b + 0x38);
    fn_004e7720(buf, 0x3ff, (const wchar_t*)g_00af01d4, a4, a3, a1);
    ((C_fn_000c8af0*)s)->fn_000c8af0(buf, 1, 0xffffffffu);
    if (*(unsigned char*)(b + 0x87c) != 0) {
        ((C_fn_000c8bb0*)s)->fn_000c8bb0();
    }
    fn_004e1613();
}

// =====================================================================
// FUNCTION: DAO 0x004c04c0
int C_0000c04c0::fn_0000c04c0(unsigned int count, unsigned int pos, const wchar_t* needle)
{
    char* b = (char*)this;
    unsigned int len = *(unsigned int*)(b + 0x14);
    unsigned int cap = *(unsigned int*)(b + 0x18);
    wchar_t* buf = (cap >= 8) ? *(wchar_t**)(b + 4) : (wchar_t*)(b + 4);
    ((C_fn_00002910*)this)->fn_00002910();
    if (needle == 0) {
        return (pos >= len) ? -1 : (int)pos;
    }
    if (pos > len) {
        return -1;
    }
    unsigned int n = count;
    if (n > len - pos) {
        n = len - pos;
    }
    for (unsigned int i = pos; i + n <= len; ++i) {
        unsigned int j = 0;
        while (j < n && buf[i + j] == needle[j]) {
            ++j;
        }
        if (j == n) {
            return (int)i;
        }
    }
    return -1;
}

// =====================================================================
// FUNCTION: DAO 0x004c1240
unsigned char C_0000c1240::fn_0000c1240(void* other)
{
    char* b = (char*)this;
    unsigned int cap = *(unsigned int*)(b + 0x18);
    unsigned int lenA = *(unsigned int*)(b + 0x14);
    wchar_t* bufA = (cap >= 8) ? *(wchar_t**)(b + 4) : (wchar_t*)(b + 4);
    unsigned int lenB = *(unsigned int*)((char*)other + 0x14);
    int r = fn_00014170(0u, lenB, bufA, lenA);
    return (unsigned char)(r < 0);
}

// =====================================================================
// FUNCTION: DAO 0x004c2670
void* C_0000c2670::fn_0000c2670(void* dst, void* src, unsigned int len)
{
    char* b = (char*)dst;
    *(unsigned int*)(b + 0x14) = 0;
    *(unsigned int*)(b + 0x18) = 7;
    *(unsigned short*)(b + 4) = 0;
    ((C_fn_000c1270*)dst)->fn_000c1270(this, src, (void*)len);
    return dst;
}

// =====================================================================
// FUNCTION: DAO 0x004c89f0
int C_0000c89f0::fn_0000c89f0(void* a1, void* a2, unsigned char a3)
{
    void* ecx = *(void**)((char*)this + 4);
    if (ecx == (void*)(-1)) {
        return -1;
    }
    void* local = 0;
    (void)a3;
    return g_00ada0dc(ecx, a2, &local, (unsigned int)a1);
}

// =====================================================================
// FUNCTION: DAO 0x005dee10
void C_001dee10::fn_001dee10(void)
{
    char* s = (char*)this;
    int i = ((C_fn_0013cc40*)(s + 0x8c0))->fn_0013cc40();
    if (i >= 0) {
        char* lo = *(char**)(s + 0x898);
        char* hi = *(char**)(s + 0x89c);
        int n = (int)((hi - lo) >> 3);
        if (i < n) {
            fn_00058e90(0);
        }
    }
    {
        void* c = ((C_fn_00003c70*)(s + 0x8f0))->fn_00003c70();
        (void)c;
    }
    ((C_fn_0013cc40*)(s + 0x8e0))->fn_0013cc40();
    {
        int k = ((C_fn_0013cc40*)(s + 0x90c))->fn_0013cc40();
        (void)k;
    }
    ((C_fn_0013cc40*)(s + 0x92c))->fn_0013cc40();
    g_00c1eb50 = (unsigned char)((C_fn_00438210*)(s + 0x450))->fn_00438210();
}

// =====================================================================
// FUNCTION: DAO 0x008e1ab0
void __cdecl fn_004e1ab0(void)
{
    fn_004f0940(4);
}

// =====================================================================
// FUNCTION: DAO 0x008e80e4
int __cdecl fn_004e80e4(void* a1, void* a2, void* a3, void* a4)
{
    return fn_004e8012(a1, a2, a3, 0, a4);
}
