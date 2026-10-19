typedef unsigned int u32;
typedef unsigned char u8;

extern "C" {
void* __cdecl fn_00413660(u32);
void __cdecl fn_008e11f2(void);
__int64 __cdecl fn_008e6ea1(u32, u32);
void* __cdecl fn_005fe920(void);
void __cdecl fn_008e76ac(u32, void*, int, void*);
}

// Minimal __thiscall-able declarations for unresolved callees.
// VC8 rejects __thiscall on free functions (C3865); member functions
// are the only legal way to express thiscall in C++98.
struct TCal {
    void c_004c0db0();
    void c_004c0d90();
    void c_004c2ab0(void*);
    void c_005d27a0(int);
    void c_004f3670(u32);
    void c_0047c9f0(void*, void*, void*);
    void c_00481a80(int);
    void c_00849ea0(void*, void*);
};

// Virtual interface whose 5th slot (offset 0x10) is the disposer invoked
// by fn_00074fd0 as *(*[self+0x20])[4](1).
struct IVObj {
    virtual void v0() = 0;
    virtual void v1() = 0;
    virtual void v2() = 0;
    virtual void v3() = 0;
    virtual void v4(int) = 0;
};

struct DAOFn {
    void  fn_00074fd0();
    void  fn_000857a0(void*, void*);
    void* fn_00088930(int, int, int, int, int, int, int);
    void  fn_000d2160(void*, void*);
    void* fn_000e9710();
    void* fn_000e98c0();
    void* fn_0044a7d0(int);
};

void* __cdecl fn_0011f0d0(void);
void* __cdecl fn_00422a40(void);
void  __cdecl fn_004e7701(void*, void*);

// FUNCTION: DAO 0x474FD0
void DAOFn::fn_00074fd0()
{
    u8* self = reinterpret_cast<u8*>(this);
    void* p = *reinterpret_cast<void**>(self + 0x20);
    if (p) {
        reinterpret_cast<IVObj*>(p)->v4(1);
    }
    reinterpret_cast<TCal*>(self + 4)->c_004c0db0();
}

// FUNCTION: DAO 0x4857A0
void DAOFn::fn_000857a0(void* out_, void* key_)
{
    u8* self = reinterpret_cast<u8*>(this);
    u8* out  = reinterpret_cast<u8*>(out_);
    u8* key  = reinterpret_cast<u8*>(key_);
    u32 limit = *reinterpret_cast<u32*>(self + 0xc) >> 2;
    u32 count = *reinterpret_cast<u32*>(self + 0x24);
    u32 adjust = *reinterpret_cast<u32*>(self + 0x20) + 2;
    if (count <= limit) {
        reinterpret_cast<TCal*>(self + 0x10)->c_004f3670(adjust);
    } else {
        reinterpret_cast<TCal*>(self + 0x10)->c_004f3670(adjust);
    }
    u32 h = static_cast<u32>(fn_008e6ea1(*reinterpret_cast<u32*>(key), 0x1f31d));
    u32 idx = h & *reinterpret_cast<u32*>(self + 0x20);
    u8* node = 0;
    u8* begin = *reinterpret_cast<u8**>(self + 0x14);
    if (begin) {
        u8* end = *reinterpret_cast<u8**>(self + 0x18);
        u32 cnt = static_cast<u32>((end - begin) >> 3);
        if (idx < cnt) {
            node = *reinterpret_cast<u8**>(begin + idx * 8 + 4);
        }
    }
    if (node) {
        reinterpret_cast<TCal*>(node)->c_00481a80(0);
        reinterpret_cast<TCal*>(self)->c_0047c9f0(node, key, self);
    } else {
        fn_008e11f2();
    }
    *reinterpret_cast<u8**>(out) = self;
    *reinterpret_cast<u8**>(out + 4) = key;
    out[8] = 1;
}

// FUNCTION: DAO 0x488930
void* DAOFn::fn_00088930(int, int, int, int, int, int, int)
{
    u8* self = reinterpret_cast<u8*>(this);
    void* p = fn_005fe920();
    *reinterpret_cast<void**>(self + 4) = p;
    *reinterpret_cast<u8*>(reinterpret_cast<u8*>(p) + 0x2d) = 1;
    void* q = *reinterpret_cast<void**>(self + 4);
    *reinterpret_cast<void**>(reinterpret_cast<u8*>(q) + 4) = q;
    *reinterpret_cast<void**>(reinterpret_cast<u8*>(q)) = q;
    *reinterpret_cast<void**>(reinterpret_cast<u8*>(q) + 8) = q;
    *reinterpret_cast<void**>(self + 8) = 0;
    u8* r = self + 0x10;
    reinterpret_cast<TCal*>(r)->c_004c0d90();
    u32 tmp = 0;
    reinterpret_cast<TCal*>(r)->c_004c2ab0(&tmp);
    reinterpret_cast<TCal*>(&tmp)->c_004c0db0();
    return self;
}

// FUNCTION: DAO 0x4D2160
void DAOFn::fn_000d2160(void* out_, void* key_)
{
    u8* self = reinterpret_cast<u8*>(this);
    u8* out  = reinterpret_cast<u8*>(out_);
    u8* key  = reinterpret_cast<u8*>(key_);
    u32 h = static_cast<u32>(fn_008e6ea1(*reinterpret_cast<u32*>(key), 0x1f31d));
    u32 idx = h & *reinterpret_cast<u32*>(self + 0x20);
    u8* node = 0;
    u8* begin = *reinterpret_cast<u8**>(self + 0x14);
    if (begin) {
        u8* end = *reinterpret_cast<u8**>(self + 0x18);
        u32 cnt = static_cast<u32>((end - begin) >> 3);
        if (idx < cnt) {
            node = *reinterpret_cast<u8**>(begin + idx * 8 + 4);
        }
    }
    if (!node) {
        fn_008e11f2();
    }
    *reinterpret_cast<u8**>(out) = node;
    *reinterpret_cast<u8**>(out + 4) = key;
}

// FUNCTION: DAO 0x4E9710
void* DAOFn::fn_000e9710()
{
    u8* self = reinterpret_cast<u8*>(this);
    *reinterpret_cast<u32*>(self) = 0xaf03fc;
    reinterpret_cast<TCal*>(self + 4)->c_005d27a0(0);
    return self;
}

// FUNCTION: DAO 0x4E98C0
void* DAOFn::fn_000e98c0()
{
    u8* self = reinterpret_cast<u8*>(this);
    *reinterpret_cast<u32*>(self) = 0xaf13f4;
    self[4] = 1;
    return self;
}

// FUNCTION: DAO 0x51F0D0
void* __cdecl fn_0011f0d0(void)
{
    u8* p = reinterpret_cast<u8*>(fn_00413660(0x18));
    if (p) {
        *reinterpret_cast<u32*>(p + 0) = 0;
        *reinterpret_cast<u32*>(p + 4) = 0;
        *reinterpret_cast<u32*>(p + 8) = 0;
        p[0x14] = 1;
        p[0x15] = 0;
    }
    return p;
}

// FUNCTION: DAO 0x822A40
void* __cdecl fn_00422a40(void)
{
    u8* p = reinterpret_cast<u8*>(fn_00413660(0x10));
    if (p) {
        *reinterpret_cast<u8**>(p) = p;
        u8* q = p + 4;
        if (q) {
            *reinterpret_cast<u8**>(q) = p;
        }
    }
    return p;
}

// FUNCTION: DAO 0x84A7D0
void* DAOFn::fn_0044a7d0(int)
{
    u8* self = reinterpret_cast<u8*>(this);
    void* a = 0;
    void* b = 0;
    reinterpret_cast<TCal*>(self)->c_00849ea0(&a, &b);
    reinterpret_cast<TCal*>(self + 0x28)->c_004c0d90();
    *reinterpret_cast<void**>(self + 0x44) = a;
    return self;
}

// FUNCTION: DAO 0x8E7701
void __cdecl fn_004e7701(void* a, void* b)
{
    fn_008e76ac(0x8faf8b, a, 0, b);
}
