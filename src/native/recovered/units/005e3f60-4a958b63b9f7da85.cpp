struct Entry8 { unsigned int v0; unsigned int v1; };
struct Entry12 { unsigned int v0; unsigned int v1; unsigned int v2; };
struct Pair24 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; unsigned int v4; unsigned int v5; };
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
    unsigned int f40;
    unsigned int f44;
    unsigned int f48;
    unsigned int f4c;
    unsigned int f50;
    unsigned int f54;
    unsigned int f58;
    unsigned int f5c;
    unsigned int f60;
    unsigned int f64;
    unsigned int f68;
    unsigned int f6c;
    void __thiscall fn_005e16e0();
};
struct C_005e2da0 {
    unsigned int f00;
    unsigned int f04;
    unsigned char pad08[0x0c];
    unsigned int f14;
    unsigned int f18;
    unsigned int f1c;
    unsigned int f20;
    unsigned int f24;
    unsigned int f28;
    unsigned int f2c;
    unsigned int f30;
    unsigned int f34;
    unsigned int f38;
    unsigned int f3c;
    unsigned int f40;
    unsigned int f44;
    unsigned int f48;
    unsigned int f4c;
    unsigned int f50;
    unsigned int f54;
    unsigned int f58;
    unsigned int f5c;
    unsigned int f60;
    unsigned int f64;
    unsigned int f68;
    unsigned int f6c;
    unsigned int f70;
    unsigned int f74;
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
struct C_005e3f60 {
    unsigned char pad00[0x138];
    unsigned int f138;
    unsigned int pad13c;
    Entry12* f140;
    unsigned int f144;
    unsigned int pad148;
    Entry12* f14c;
    int __thiscall fn_005e3f60(unsigned int i, unsigned int j, unsigned int key);
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
struct C_005e4a60 {
    unsigned int f0;
    unsigned char pad04[0x08];
    Entry12** fC;
    Entry12* __thiscall fn_005e4a60();
};
struct C_00609440 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    void __thiscall fn_00609440();
};
// FUNCTION: DAO 0x009E1200
void __cdecl fn_005e1200(unsigned char* out, const unsigned char* p1, const unsigned char* p2, const unsigned char* p3, const unsigned char* p4, unsigned int v, unsigned int w)
{
    unsigned int ebx = (0x100u - w) * (0x100u - v);
    unsigned int edi = (0x100u - w) * v;
    unsigned int esi = (0x100u - v) * w;
    unsigned int ebp = v * w;
    int eax = (int)(p1[0] * ebx + p2[0] * edi + p3[0] * esi + p4[0] * ebp + 0x8000u);
    int ecx = (int)(p1[1] * ebx + p2[1] * edi + p3[1] * esi + p4[1] * ebp + 0x8000u);
    int edx = (int)(p1[2] * ebx + p2[2] * edi + p3[2] * esi + p4[2] * ebp + 0x8000u);
    out[0] = (unsigned char)(eax >> 16);
    out[1] = (unsigned char)(ecx >> 16);
    out[2] = (unsigned char)(edx >> 16);
    out[3] = 0xff;
}
// FUNCTION: DAO 0x009E16E0
void __thiscall C_005e16e0::fn_005e16e0()
{
    unsigned int zero = 0;
    unsigned int max = 0x7fffffffu;
    unsigned int min = 0x80000001u;
    f40 = max;
    f44 = max;
    f50 = max;
    f54 = max;
    f14 = zero;
    f28 = zero;
    f34 = zero;
    f48 = zero;
    f4c = zero;
    f58 = min;
    f5c = min;
    f60 = zero;
    f64 = zero;
    f68 = zero;
    f6c = zero;
}
// FUNCTION: DAO 0x009E2DA0
void __thiscall C_005e2da0::fn_005e2da0()
{
    f00 = 0x400u;
    f04 = 0x400u;
    f14 = 0;
    f18 = 0;
    f1c = 0;
    f20 = 0;
    f24 = 0x100u;
    f28 = 0;
    f2c = 0;
    f30 = 0;
    f34 = 0;
    f38 = 0x100u;
    f3c = 0;
    f40 = 0;
    f44 = 0;
    f48 = 0;
    f4c = 0x10u;
    f50 = 0;
    f54 = 0;
    f58 = 0;
    f5c = 0;
    f60 = 0x100u;
    f64 = 0;
    f68 = 0;
    f6c = 0;
    f70 = 0;
    f74 = 0x40u;
}
// FUNCTION: DAO 0x009E3BF0
void __cdecl fn_005e3bf0(Pair24* a, Pair24* b)
{
    unsigned int a0 = a->v0;
    unsigned int a1 = a->v1;
    unsigned int a2 = a->v2;
    unsigned int a3 = a->v3;
    unsigned int a4 = a->v4;
    unsigned int a5 = a->v5;
    a->v0 = b->v0;
    a->v1 = b->v1;
    a->v2 = b->v2;
    a->v3 = b->v3;
    a->v4 = b->v4;
    a->v5 = b->v5;
    b->v0 = a0;
    b->v1 = a1;
    b->v2 = a2;
    b->v3 = a3;
    b->v4 = a4;
    b->v5 = a5;
}
// FUNCTION: DAO 0x009E3DB0
unsigned int __thiscall C_005e3db0::fn_005e3db0()
{
    unsigned int i = fF4;
    unsigned int min = fF0;
    if (i < min) return 0;
    for (;;) {
        if (fEC[i] != 0) return i;
        --i;
        if (i < min) return 0;
    }
}
// FUNCTION: DAO 0x009E3EB0
unsigned int __thiscall C_005e3eb0::fn_005e3eb0(unsigned int* p)
{
    unsigned int idx = p[1];
    if (idx == 0xffffffffu) return 0xffffffffu;
    Entry8* block = f198[idx >> 10];
    return block[idx & 0x3ffu].v0;
}
// FUNCTION: DAO 0x009E3EE0
void __thiscall C_005e3ee0::fn_005e3ee0(Node4* p)
{
    unsigned int idx = p->f4;
    if (idx == 0xffffffffu) return;
    if (idx == f18c - 1u && f18c != 0) {
        --f18c;
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
// FUNCTION: DAO 0x009E3F60
int __thiscall C_005e3f60::fn_005e3f60(unsigned int i, unsigned int j, unsigned int key)
{
    Entry12* a = 0;
    Entry12* b = 0;
    if (i < f138) a = &f140[i];
    if (j < f144) b = &f14c[j];
    if (a != 0 && b != 0 && a->v2 == b->v2) return 0;
    if (b != 0 && b->v2 == key) return 2;
    if (a != 0 && a->v2 == key) return 3;
    return 0;
}
// FUNCTION: DAO 0x009E3FE0
void __thiscall C_005e3fe0::fn_005e3fe0(unsigned int start, unsigned int end)
{
    if (start >= end) return;
    for (unsigned int i = start; i < end; ++i) {
        Tri* block = fDC[i >> 6];
        unsigned int lo = i & 0x3fu;
        unsigned int a = block[lo].v0;
        unsigned int b = block[lo].v1;
        unsigned int ia = fCC[a];
        unsigned int ib = fCC[b];
        unsigned int tmp = fB4[ia];
        fB4[ia] = fB4[ib];
        fB4[ib] = tmp;
        unsigned int tmp2 = fCC[a];
        fCC[a] = fCC[b];
        fCC[b] = tmp2;
    }
}
// FUNCTION: DAO 0x009E4A60
Entry12* __thiscall C_005e4a60::fn_005e4a60()
{
    unsigned int idx = f0 - 1u;
    Entry12* block = fC[idx >> 10];
    return &block[idx & 0x3ffu];
}
// FUNCTION: DAO 0x00A09440
void __thiscall C_00609440::fn_00609440()
{
    f0 = 0;
    f4 = 0;
    f8 = 0;
}