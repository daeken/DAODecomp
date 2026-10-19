struct Entry8 { unsigned int v0; unsigned int v1; };
struct Node4 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fC; };
struct Tri { unsigned int v0; unsigned int v1; unsigned int v2; };

struct C_005e16e0 {
    unsigned char pad00[0x14];
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
    C_005e2da0* __thiscall fn_005e2da0();
};

struct C_005e3db0 {
    unsigned char pad00[0xec];
    unsigned int* fEC;
    unsigned int fF0;
    unsigned int fF4;
    unsigned int __thiscall fn_005e3db0();
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
    unsigned int t1 = (0x100u - w) * v;
    unsigned int t3 = v * w;
    unsigned int t0 = (0x100u - w) * (0x100u - v);
    unsigned int t2 = (0x100u - v) * w;
    unsigned int r0 = a0 * t0;
    unsigned int r1 = a1 * t0;
    unsigned int r2 = a2 * t0;
    r0 += 0x8000u;
    r0 += p2[0] * t1;
    r1 += 0x8000u;
    r1 += p2[1] * t1;
    r2 += 0x8000u;
    r2 += p2[2] * t1;
    r0 += p3[0] * t2;
    r1 += p3[1] * t2;
    r2 += p3[2] * t2;
    r0 += p4[0] * t3;
    r1 += p4[1] * t3;
    r2 += p4[2] * t3;
    out[0] = (unsigned char)((int)r0 >> 16);
    out[1] = (unsigned char)((int)r1 >> 16);
    out[2] = (unsigned char)((int)r2 >> 16);
    out[3] = 0xff;
}

// FUNCTION: DAO 0x009E16E0
void __thiscall C_005e16e0::fn_005e16e0()
{
    unsigned int z = 0;
    unsigned int maxv = 0x7fffffffu;
    f40 = maxv;
    f44 = maxv;
    f50 = maxv;
    f54 = maxv;
    unsigned int minv = 0x80000001u;
    f14 = z;
    f28 = z;
    f34 = z;
    f48 = z;
    f4c = z;
    f58 = minv;
    f5c = minv;
    f60 = z;
    f64 = z;
    f68 = z;
    f6c = z;
}

// FUNCTION: DAO 0x009E2DA0
C_005e2da0* __thiscall C_005e2da0::fn_005e2da0()
{
    C_005e2da0* self = this;
    self->f00 = 0x400u;
    self->f04 = 0x400u;
    unsigned int zero = 0;
    self->f14 = zero;
    self->f18 = zero;
    self->f1c = zero;
    self->f20 = zero;
    self->f24 = 0x100u;
    self->f28 = zero;
    self->f2c = zero;
    self->f30 = zero;
    self->f34 = zero;
    self->f38 = 0x100u;
    self->f3c = zero;
    self->f40 = zero;
    self->f44 = zero;
    self->f48 = zero;
    self->f4c = 0x10u;
    self->f50 = zero;
    self->f54 = zero;
    self->f58 = zero;
    self->f5c = zero;
    self->f60 = 0x100u;
    self->f64 = zero;
    self->f68 = zero;
    self->f6c = zero;
    self->f70 = zero;
    self->f74 = 0x40u;
    return self;
}

// FUNCTION: DAO 0x009E3DB0
unsigned int __thiscall C_005e3db0::fn_005e3db0()
{
    unsigned int i = fF4;
    unsigned int min = fF0;
    if (i < min) return 0;
    unsigned int* p = fEC + i;
    do {
        if (*p != 0) return i;
        --i;
        --p;
    } while (i >= min);
    return 0;
}

// FUNCTION: DAO 0x009E3EE0
void __thiscall C_005e3ee0::fn_005e3ee0(Node4* p)
{
    unsigned int idx = p->f4;
    if (idx == 0xffffffffu) return;
    if (idx == f18c - 1u) {
        if (f18c != 0) {
            f18c -= 1u;
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
        unsigned int b = block[lo].v1;
        unsigned int a = block[lo].v0;
        Tri* e = block + lo;
        unsigned int* pcc = fCC;
        unsigned int ib = pcc[b];
        unsigned int ia = pcc[a];
        unsigned int val_b = pb4[ib];
        unsigned int* pib = pb4 + ib;
        unsigned int* pia = pb4 + ia;
        unsigned int val_a = *pia;
        *pia = val_b;
        *pib = val_a;
        unsigned int b2 = e->v1;
        unsigned int a2 = e->v0;
        unsigned int ib2 = fCC[b2];
        unsigned int* pb2 = fCC + b2;
        unsigned int* pa2 = fCC + a2;
        unsigned int val_a2 = *pa2;
        *pa2 = ib2;
        *pb2 = val_a2;
        ++i;
    } while (i < end);
}
