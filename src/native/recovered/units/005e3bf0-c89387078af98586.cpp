struct Pair24 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; unsigned int v4; unsigned int v5; };
struct Entry8 { unsigned int v0; unsigned int v1; };
struct Node4 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fC; };
struct Tri { unsigned int v0; unsigned int v1; unsigned int v2; };
struct C_005e16e0 {
    unsigned char pad0[0x14];
    unsigned int f14;
    unsigned char pad18[0x10];
    unsigned int f28;
    unsigned char pad2c[0x08];
    unsigned int f34;
    unsigned char pad38[0x08];
    unsigned int f40, f44, f48, f4c, f50, f54, f58, f5c, f60, f64, f68, f6c;
    void __thiscall fn_005e16e0();
};
struct C_005e2da0 {
    unsigned int f00, f04;
    unsigned char pad08[0x0c];
    unsigned int f14, f18, f1c, f20, f24, f28, f2c, f30, f34, f38, f3c, f40, f44, f48, f4c, f50, f54, f58, f5c, f60, f64, f68, f6c, f70, f74;
    void __thiscall fn_005e2da0();
};
struct C_005e3db0 {
    unsigned char pad00[0xec];
    unsigned int* fEC;
    unsigned int fF0;
    unsigned int fF4;
    unsigned int __thiscall fn_005e3db0();
};
struct C_005e3eb0 {
    unsigned char pad00[0x198];
    Entry8** f198;
    unsigned int __thiscall fn_005e3eb0(unsigned int* p);
};
struct C_005e3ee0 {
    unsigned char pad00[0x18c];
    unsigned int f18c;
    unsigned char pad190[0x08];
    Entry8** f198;
    void __thiscall fn_005e3ee0(Node4* p);
};
struct C_005e3fe0 {
    unsigned char pad00[0xb4];
    unsigned int* fB4;
    unsigned char padB8[0x14];
    unsigned int* fCC;
    unsigned char padD0[0x0c];
    Tri** fDC;
    void __thiscall fn_005e3fe0(unsigned int start, unsigned int end);
};
// FUNCTION: DAO 0x009E1200
void __cdecl fn_005e1200(unsigned char* out, const unsigned char* p1, const unsigned char* p2, const unsigned char* p3, const unsigned char* p4, unsigned int v, unsigned int w)
{
    unsigned int a0 = p1[0];
    unsigned int a1 = p1[1];
    unsigned int a2 = p1[2];
    unsigned int w0 = (0x100u - w) * (0x100u - v);
    unsigned int w1 = (0x100u - w) * v;
    unsigned int w2 = (0x100u - v) * w;
    unsigned int w3 = v * w;
    int r0 = (int)(a0 * w0);
    int r1 = (int)(a1 * w0);
    int r2 = (int)(a2 * w0);
    r0 += 0x8000;
    r0 += (int)(p2[0] * w1);
    r1 += 0x8000;
    r1 += (int)(p2[1] * w1);
    r2 += 0x8000;
    r2 += (int)(p2[2] * w1);
    r0 += (int)(p3[0] * w2);
    r1 += (int)(p3[1] * w2);
    r2 += (int)(p3[2] * w2);
    r0 += (int)(p4[0] * w3);
    r1 += (int)(p4[1] * w3);
    r2 += (int)(p4[2] * w3);
    out[0] = (unsigned char)(r0 >> 16);
    out[1] = (unsigned char)(r1 >> 16);
    out[2] = (unsigned char)(r2 >> 16);
    out[3] = 0xff;
}
// FUNCTION: DAO 0x009E16E0
void __thiscall C_005e16e0::fn_005e16e0()
{
    int zero = 0;
    int max = 0x7fffffff;
    int min = 0x80000001;
    f40 = (unsigned int)max;
    f44 = (unsigned int)max;
    f50 = (unsigned int)max;
    f54 = (unsigned int)max;
    f14 = (unsigned int)zero;
    f28 = (unsigned int)zero;
    f34 = (unsigned int)zero;
    f48 = (unsigned int)zero;
    f4c = (unsigned int)zero;
    f58 = (unsigned int)min;
    f5c = (unsigned int)min;
    f60 = (unsigned int)zero;
    f64 = (unsigned int)zero;
    f68 = (unsigned int)zero;
    f6c = (unsigned int)zero;
}
// FUNCTION: DAO 0x009E2DA0
void __thiscall C_005e2da0::fn_005e2da0()
{
    f00 = 0x400u;
    f04 = 0x400u;
    unsigned int zero = 0;
    f14 = zero;
    f18 = zero;
    f1c = zero;
    f20 = zero;
    unsigned int one = 0x100u;
    f24 = one;
    f28 = zero;
    f2c = zero;
    f30 = zero;
    f34 = zero;
    f38 = one;
    f3c = zero;
    f40 = zero;
    f44 = zero;
    f48 = zero;
    f4c = 0x10u;
    f50 = zero;
    f54 = zero;
    f58 = zero;
    f5c = zero;
    f60 = one;
    f64 = zero;
    f68 = zero;
    f6c = zero;
    f70 = zero;
    f74 = 0x40u;
}
// FUNCTION: DAO 0x009E3BF0
void __cdecl fn_005e3bf0(Pair24* a, Pair24* b)
{
    Pair24 tmp = *a;
    *a = *b;
    *b = tmp;
}
// FUNCTION: DAO 0x009E3DB0
unsigned int __thiscall C_005e3db0::fn_005e3db0()
{
    unsigned int i = fF4;
    unsigned int min = fF0;
    if (i < min) return 0;
    unsigned int* p = &fEC[i];
    for (;;) {
        if (*p != 0) return i;
        --i;
        --p;
        if (i < min) return 0;
    }
}
// FUNCTION: DAO 0x009E3EB0
unsigned int __thiscall C_005e3eb0::fn_005e3eb0(unsigned int* p)
{
    unsigned int idx = p[1];
    if (idx != 0xffffffffu) {
        Entry8* block = f198[idx >> 10];
        return block[idx & 0x3ffu].v0;
    }
    return 0xffffffffu;
}
// FUNCTION: DAO 0x009E3EE0
void __thiscall C_005e3ee0::fn_005e3ee0(Node4* p)
{
    unsigned int idx = p->f4;
    if (idx == 0xffffffffu) return;
    if (idx == f18c - 1u) {
        if (f18c != 0) {
            f18c = f18c - 1u;
        }
    }
    p->f4 = p->f8;
    p->f8 = p->fC;
    unsigned int newIdx = p->f4;
    p->fC = 0xffffffffu;
    if (newIdx == 0xffffffffu) {
        p->f0 = 0;
        return;
    }
    Entry8* block = f198[newIdx >> 10];
    block[newIdx & 0x3ffu].v1 = 0;
}
// FUNCTION: DAO 0x009E3FE0
void __thiscall C_005e3fe0::fn_005e3fe0(unsigned int start, unsigned int end)
{
    if (start >= end) return;
    unsigned int i = start;
    do {
        Tri* block = fDC[i >> 6];
        unsigned int* pb4 = fB4;
        unsigned int lo = i & 0x3fu;
        Tri* e = block + lo;
        unsigned int b = e->v1;
        unsigned int a = e->v0;
        unsigned int* pcc = fCC;
        unsigned int ib = pcc[b];
        unsigned int ia = pcc[a];
        unsigned int* qb = &pb4[ib];
        unsigned int* qa = &pb4[ia];
        unsigned int tmp = *qb;
        unsigned int va = *qa;
        *qa = tmp;
        *qb = va;
        unsigned int* pb = &fCC[b];
        unsigned int* pa = &fCC[a];
        unsigned int tmpb = *pb;
        unsigned int tmpa = *pa;
        *pa = tmpb;
        *pb = tmpa;
        ++i;
    } while (i < end);
}
