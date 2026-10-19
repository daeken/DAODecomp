typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int i32;

extern void fn_008dfd0c(...);
extern int fn_004e0e10(...);
extern void fn_000136c0(...);
extern int fn_00413800(...);
extern void fn_008dfd4b(...);
extern int fn_008e2da2(...);
extern void* fn_00013660(...);
extern int fn_004c2510(...);
extern int fn_004c0d90(...);
extern int fn_00406970(...);
extern int fn_004c36a0(...);
extern int fn_004c2ad0(...);
extern int fn_004c2ab0(...);
extern int fn_008e8100(...);
extern int fn_004c93e0(...);
extern int fn_004c9550(...);
extern int fn_004c0db0(...);
extern int fn_0040ade0(...);
extern int fn_005c5c20(...);
extern int fn_00573ed0(...);
extern int fn_0040d610(...);
extern int fn_005c5ca0(...);
extern int fn_0049d170(...);
extern int fn_008f160e(...);
extern int fn_008f1548(...);
extern int* fn_008e37c9(...);
extern int* fn_008e37b6(...);
extern int fn_008e11ce(...);
extern int fn_008e6bce(...);
extern int fn_008e37dc(...);
extern int fn_008f0940(...);
extern int fn_008f0955(...);
extern int fn_008edaf9(...);

extern int (*g_00ada210)(...);
extern int (*g_00ada160)(...);
extern int (*g_00ada148)(...);
extern void (*g_00ada180)(...);
extern int (*g_00ada190)(...);
extern void (*g_00ada0b4)(...);
extern u8 g_00c15c60[];

struct C06530 {
    u8 pad0[4];
    u16* data;
    u8 pad8[0xC];
    u32 len;
    u32 cap;
    int __thiscall reserve(u32, u32);
    int __thiscall fn_00006530(u32, u8);
};

struct C14170 {
    u8 pad0[4];
    u16* data;
    u8 pad8[0xC];
    u32 len;
    u32 cap;
    int __thiscall fn_00014170(u32, u32, const u16*, u32);
};

struct Sub8A900 {
    void __thiscall fn_00483980();
};

struct C8A900 {
    void* vtable;
    void* ptr;
    u8 pad8[4];
    Sub8A900 sub;
    void __thiscall fn_00489550();
    void __thiscall fn_0008a900();
};

struct CBF300 {
    u8 pad0[4];
    void* ptr;
    u8 pad8[0xC];
    u32 len;
    u32 cap;
};

struct C1C7470 {
    void* vtable;
    u8 field4[0x3C];
    u8 field40[0x10];
    u8 field50[0x10];
    void __thiscall fn_001c7470();
};

// FUNCTION: DAO 0x00406530
int __thiscall C06530::fn_00006530(u32 n, u8 flag)
{
    if (n > 0x7ffffffeU) fn_008dfd0c();
    if (cap < n) reserve(n, len);
    if (flag && n < 8U) {
        u32 newlen = len < n ? len : n;
        if (cap >= 8U) {
            u16* p = data;
            if (newlen != 0) fn_004e0e10((u8*)this + 4, 0x10U, p, newlen * 2U);
            fn_000136c0(p);
        }
        len = newlen;
        cap = 7U;
        ((u16*)((u8*)this + 4))[newlen] = 0;
        return n != 0U;
    }
    if (n == 0U) {
        if (cap >= 8U) data[0] = 0; else ((u16*)((u8*)this + 4))[0] = 0;
        return 0;
    }
    ((u16*)this)[0] = 0;
    return 1;
}

// FUNCTION: DAO 0x00414170
int __thiscall C14170::fn_00014170(u32 pos, u32 n, const u16* s, u32 count)
{
    if (len < pos) fn_008dfd4b();
    u32 avail = len - pos;
    u32 m = n < avail ? n : avail;
    u32 k = m < count ? m : count;
    const u16* base = cap >= 8U ? data : (const u16*)((const u8*)this + 4);
    int r = fn_00413800(base + pos, s, k);
    if (r != 0) return m != count;
    if (m < count) return -1;
    return m != count;
}

// FUNCTION: DAO 0x0048a900
void __thiscall C8A900::fn_0008a900()
{
    sub.fn_00483980();
    fn_00489550();
    fn_000136c0(ptr);
    ptr = 0;
}

// FUNCTION: DAO 0x004bf300
int __stdcall fn_000bf300(CBF300* p)
{
    u32 n = p->len;
    if (n > 0x104U) n = 0x104U;
    void* src = (p->cap >= 8U) ? p->ptr : (void*)((u8*)p + 4);
    return fn_008e2da2((const char*)0x00c2b9b8, src, n);
}

// FUNCTION: DAO 0x004c5530
void* __cdecl fn_000c5530()
{
    void* p = fn_00013660(0x38U);
    if (p) *(void**)p = p;
    void** q = (void**)((u8*)p + 4);
    if (q) *q = p;
    return p;
}

// FUNCTION: DAO 0x004c97c0
bool __cdecl fn_000c97c0(const char* a, const char* b, void* c, u8 d)
{
    u8 buf[0x2c4];
    fn_004c2510(buf + 0x20, a);
    fn_004c0d90(buf + 0x38);
    fn_00406970(buf + 0x20, 0x5c, 1);
    fn_004c36a0(buf + 0x20, b);
    int h = g_00ada210((const char*)(buf + 0x20), buf + 0x84);
    bool ok = false;
    if (h != -1) {
        fn_004c0d90(buf + 0x68);
        g_00ada160(buf + 0xb0, (void*)0x00aeb520, 0, buf + 0x84);
        g_00ada160(buf + 0xb0, (void*)0x00af0478, 0, buf + 0x84);
        fn_004c2ad0(buf + 0x6c, buf + 0xb0);
        fn_004c2ab0(buf + 0x3c, buf + 0x68);
        fn_008e8100(0, 0, 0x00989680, 0);
        fn_004c93e0(c, buf + 0x38);
        int r = g_00ada160(h, buf + 0x84);
        if (r == 0) {
            if (g_00ada148() != 0x12) d = 0;
        }
        fn_004c0db0(buf + 0x68);
        if (d) fn_004c9550(c);
        g_00ada180(h);
        fn_004c0db0(buf + 0x38);
        fn_004c0db0(buf + 0x1c);
        ok = true;
    }
    return ok;
}

// FUNCTION: DAO 0x005c7470
void __thiscall C1C7470::fn_001c7470()
{
    vtable = (void*)0x00affd44;
    fn_0040ade0(field4, field4 + 0x10);
    fn_005c5c20(field4, field4);
    fn_00573ed0(field4);
    fn_0040d610(field40, 0);
    fn_005c5ca0(field50);
    fn_0049d170(field40, field4);
}

// FUNCTION: DAO 0x008e1ca6
u16* __cdecl fn_004e1ca6(int drive, u16* buf, int size)
{
    if (drive == 0) {
        *fn_008e37c9() = 0xf;
        *fn_008e37b6() = 0xd;
        fn_008e11ce(0,0,0,0,0);
        return 0;
    }
    if (fn_008f160e(drive) == 0) {
        *fn_008e37c9() = 0xf;
        *fn_008e37b6() = 0xd;
        fn_008e11ce(0,0,0,0,0);
        return 0;
    }
    int cur = fn_008f1548();
    if (buf == 0 || size <= 0) {
        *fn_008e37b6() = 0x16;
        return 0;
    }
    *buf = 0;
    u16 tmp[4];
    if (cur != 0) {
        tmp[0] = (u16)(cur + 0x40);
        tmp[1] = 0x3a;
        tmp[2] = 0x2e;
        tmp[3] = 0;
    } else {
        tmp[0] = 0x2e;
        tmp[1] = 0;
    }
    int r = g_00ada190(tmp, buf, size, 0);
    if (r == 0) {
        *fn_008e37b6() = 0x22;
        *buf = 0;
        return 0;
    }
    if (r > size) {
        *fn_008e37b6() = 0xc;
        *fn_008e37c9() = 8;
        return 0;
    }
    u16* p = (u16*)fn_008e6bce(size, 2);
    if (p == 0) {
        *fn_008e37b6() = 0xc;
        *fn_008e37c9() = 8;
        return 0;
    }
    g_00ada190(tmp, p, size, 0);
    return p;
}

// FUNCTION: DAO 0x008e1e25
void __cdecl fn_004e1e25()
{
    fn_008f0940(7);
}

// FUNCTION: DAO 0x008ee874
void __cdecl fn_004ee874()
{
}

// FUNCTION: DAO 0x008ee8b9
void __cdecl fn_004ee8b9()
{
}

// FUNCTION: DAO 0x008f0a18
void __cdecl fn_004f0a18(int file)
{
    void** p = (void**)(g_00c15c60 + file * 8);
    if (*p == 0) {
        if (fn_008f0955(file) == 0) fn_008edaf9(0x11);
    }
    g_00ada0b4(*p);
}
