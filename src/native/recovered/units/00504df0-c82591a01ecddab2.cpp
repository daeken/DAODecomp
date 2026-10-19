typedef unsigned char u8;
typedef unsigned int u32;
typedef int s32;

extern void fn_004e11f2();
extern void* fn_000151a0(void*, void*);
extern int fn_00014170(void*, int, void*, void*);
extern void* fn_0011fb90(void*, void*, void*, void*);
extern void fn_000c2510(void*, void*);
extern void fn_000c0db0(void*);
extern void* fn_00138a00(void*, void*, void*, void*);
extern void fn_003d4f60(void*, int);
extern void fn_0047c840(void*, int);
extern void fn_000c5c60(void*, int);
extern void fn_0047cfb0(void*, void*);
extern void fn_00482680();
extern void* fn_0047b840(void*);
extern int fn_00480be0(void*, void*);
extern void fn_003d7b80(void*, void*);
extern void fn_001744e0(void*);
extern void* fn_0047d090(void*, void*, void*, void*, void*);
extern void fn_00480790(void*, void*, void*);
extern int fn_00480780(void*);
extern int fn_00480610(void*);
extern int fn_00480630(int);
extern void fn_00480760(void*, void*);
extern void fn_00480740(void*, void*);
extern void* fn_001fe920();
extern void fn_000c0d90(void*);
extern void fn_000c2ab0(void*, void*);
extern int fn_004f0940(int);

struct C00112A10 { void fn_00112a10(void*, void*); };
struct C0011FE10 { void* fn_0011fe10(void*); };
struct C00298C30 { void fn_00298c30(void*); };
struct C0047D280 { void fn_0047d280(); };
struct C0047D3A0 { void* fn_0047d3a0(void*); };
struct C00482160 { void fn_00482160(int,int,int,int,int,int,int); };
struct C00482200 { void fn_00482200(int); };
struct C00482280 { void* fn_00482280(); };
struct C004910A0 { void fn_004910a0(int); };
struct C00612A40 { void* fn_00612a40(const int*); };

// FUNCTION: DAO 0x00512a10
void C00112A10::fn_00112a10(void* arg, void* out)
{
    u8* s = reinterpret_cast<u8*>(this);
    void* node = fn_000151a0(this, arg);
    if (!this) fn_004e11f2();
    if (node == *reinterpret_cast<void**>(s + 4)) {
        node = *reinterpret_cast<void**>(s + 4);
    } else {
        u32 len = *reinterpret_cast<u32*>(reinterpret_cast<u8*>(node) + 0x24);
        void* key = (len < 8) ? reinterpret_cast<void*>(reinterpret_cast<u8*>(node) + 0x10)
                              : *reinterpret_cast<void**>(reinterpret_cast<u8*>(node) + 0x10);
        int c = fn_00014170(arg, 0, *reinterpret_cast<void**>(reinterpret_cast<u8*>(arg) + 0x14), key);
        if (c < 0) {
            node = *reinterpret_cast<void**>(s + 4);
        }
    }
    *reinterpret_cast<void**>(out) = this;
    *reinterpret_cast<void**>(reinterpret_cast<u8*>(out) + 4) = node;
}

// FUNCTION: DAO 0x0051fe10
void* C0011FE10::fn_0011fe10(void* arg)
{
    u8* s = reinterpret_cast<u8*>(this);
    void* node = fn_000151a0(this, arg);
    if (!this) fn_004e11f2();
    if (node != *reinterpret_cast<void**>(s + 4)) {
        u32 len = *reinterpret_cast<u32*>(reinterpret_cast<u8*>(node) + 0x24);
        void* key = (len < 8) ? reinterpret_cast<void*>(reinterpret_cast<u8*>(node) + 0x10)
                              : *reinterpret_cast<void**>(reinterpret_cast<u8*>(node) + 0x10);
        int c = fn_00014170(arg, 0, *reinterpret_cast<void**>(reinterpret_cast<u8*>(arg) + 0x14), key);
        if (c >= 0) {
            return reinterpret_cast<void*>(reinterpret_cast<u8*>(node) + 0x28);
        }
    }
    u8 tmp[0x10];
    fn_000c2510(tmp, arg);
    u8* p = reinterpret_cast<u8*>(fn_0011fb90(this, node, arg, tmp));
    node = *reinterpret_cast<void**>(p + 4);
    fn_000c0db0(tmp);
    return reinterpret_cast<void*>(reinterpret_cast<u8*>(node) + 0x28);
}

// FUNCTION: DAO 0x00698c30
void C00298C30::fn_00298c30(void* arg)
{
    u8* s = reinterpret_cast<u8*>(this);
    void* edi = *reinterpret_cast<void**>(s + 4);
    void* ecxv = *reinterpret_cast<void**>(reinterpret_cast<u8*>(edi) + 4);
    void* ebx = fn_00138a00(this, edi, ecxv, arg);
    fn_003d4f60(this, 1);
    *reinterpret_cast<void**>(reinterpret_cast<u8*>(edi) + 4) = ebx;
    void* edx = *reinterpret_cast<void**>(reinterpret_cast<u8*>(ebx) + 4);
    *reinterpret_cast<void**>(edx) = ebx;
}

// FUNCTION: DAO 0x0087d280
void C0047D280::fn_0047d280()
{
    u8* s = reinterpret_cast<u8*>(this);
    *reinterpret_cast<u32*>(s) = 0;
    fn_0047c840(s + 4, 0);
    u8 tmp1[0x10];
    fn_000c5c60(tmp1, 0);
    fn_0047cfb0(s + 0x14, tmp1);
    u8 tmp2[0x10];
    fn_000c5c60(tmp2, 0);
    fn_0047cfb0(s + 0x38, tmp2);
    s[0x5c] = 0;
    fn_00482680();
}

// FUNCTION: DAO 0x0087d3a0
void* C0047D3A0::fn_0047d3a0(void* arg)
{
    u8* s = reinterpret_cast<u8*>(this);
    void* esi = fn_0047b840(arg);
    if (this) {
        if (esi != *reinterpret_cast<void**>(s + 4)) {
            u8* p = reinterpret_cast<u8*>(esi) + 0xc;
            if (fn_00480be0(arg, p)) {
                u8 tmp[0x20];
                fn_000c5c60(tmp, 0);
                u32 a = *reinterpret_cast<u32*>(arg);
                u32 b = *reinterpret_cast<u32*>(reinterpret_cast<u8*>(arg) + 4);
                *reinterpret_cast<u32*>(tmp + 0x14) = a;
                *reinterpret_cast<u32*>(tmp + 0x18) = b;
                void* out = fn_0047d090(this, tmp, esi, arg, 0);
                fn_001744e0(tmp);
                (void)out;
            }
        }
    }
    return reinterpret_cast<void*>(reinterpret_cast<u8*>(esi) + 0x14);
}

// FUNCTION: DAO 0x008807e0
int __cdecl fn_004807e0(void* a, void* b)
{
    if (!a) return 0;
    u32 v = *reinterpret_cast<u32*>(a);
    if (v == 0) {
        fn_00480790(b, a, 0);
        return (int)b;
    }
    u32 t1 = v & 0xf0000000u;
    u32 t2 = *reinterpret_cast<u32*>(b) & 0xf0000000u;
    if (t1 != t2) return 0;
    if (t1 == 0x10000000u) {
        return (int)b;
    } else if (t1 == 0x20000000u) {
        int x = fn_00480780(b);
        if (x == 0x10000 || x == 0x20000 || x == 0x30000 || x == 0x40000) {
            int c = fn_00480610(a);
            if (c == 0x14 || c == 0x15) {
                fn_00480790(b, a, 0);
                return (int)a;
            }
        }
        if (x == 0x50000) {
            int c = fn_00480610(a);
            if (c == 0x16 || c == 0x17 || fn_00480630(c)) {
                u8 tmp[0x10];
                fn_00480760(tmp, tmp);
                fn_00480790(b, a, tmp);
                return (int)a;
            }
        }
        if (fn_00480630(fn_00480610(a))) {
            return (int)b;
        }
        if (x == 0x20000) {
            int c = fn_00480610(a);
            if (c == 0x16 || c == 0x17) return (int)b;
        }
    } else if (t1 == 0x30000000u) {
        return (int)b;
    } else if (t1 == 0x40000000u) {
        int c = fn_00480610(a);
        if (c >= 0 && c <= 0x1f) return (int)b;
    }
    return 0;
}

// FUNCTION: DAO 0x00882160
void C00482160::fn_00482160(int, int, int, int, int, int, int)
{
    u8* s = reinterpret_cast<u8*>(this);
    u8* p = reinterpret_cast<u8*>(fn_001fe920());
    *reinterpret_cast<void**>(s + 4) = p;
    p[0x2d] = 1;
    *reinterpret_cast<void**>(p + 4) = p;
    *reinterpret_cast<void**>(p) = p;
    *reinterpret_cast<void**>(p + 8) = p;
    *reinterpret_cast<u32*>(s + 8) = 0;
    *reinterpret_cast<u32*>(s + 0xc) = 0;
    fn_000c0d90(s + 0x10);
    int tmp = 0;
    fn_000c2ab0(s + 0x10, &tmp);
    fn_000c0db0(&tmp);
}

// FUNCTION: DAO 0x00882200
void C00482200::fn_00482200(int arg)
{
    u8* s = reinterpret_cast<u8*>(this);
    u8* p = reinterpret_cast<u8*>(fn_001fe920());
    *reinterpret_cast<void**>(s + 4) = p;
    p[0x2d] = 1;
    *reinterpret_cast<void**>(p + 4) = p;
    *reinterpret_cast<void**>(p) = p;
    *reinterpret_cast<void**>(p + 8) = p;
    *reinterpret_cast<u32*>(s + 8) = 0;
    fn_000c0d90(s + 0xc);
    *reinterpret_cast<u32*>(s + 0x28) = 0;
    *reinterpret_cast<u32*>(s + 0x28) = arg;
}

// FUNCTION: DAO 0x00882280
void* C00482280::fn_00482280()
{
    u8* s = reinterpret_cast<u8*>(this);
    int tmp[7] = {0, 0, 0, 0, 0, 0, 0};
    fn_000c0d90(tmp);
    reinterpret_cast<C00482160*>(s)->fn_00482160(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6]);
    reinterpret_cast<C00482200*>(s + 0x2c)->fn_00482200(0);
    return s;
}

// FUNCTION: DAO 0x008910a0
void C004910A0::fn_004910a0(int arg)
{
    u8* s = reinterpret_cast<u8*>(this);
    *reinterpret_cast<int*>(s) = arg;
    *reinterpret_cast<int*>(s + 4) = 0;
    *reinterpret_cast<u8*>(s + 8) = 1;
    *reinterpret_cast<u8*>(s + 9) = 0;
}

// FUNCTION: DAO 0x00904df0
void __cdecl fn_00504df0(void)
{
    (void)fn_004f0940(10);
}

// FUNCTION: DAO 0x00a12a40
void* C00612A40::fn_00612a40(const int* src)
{
    *reinterpret_cast<int*>(this) = *src;
    return this;
}
