typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned short u16;

struct C0063D580 {
    u8 pad0[0x3c];
    int* f3c;
    int* f40;
    u8 pad44[0x0c];
    int f50;
    int* f54;
    int* f58;
    int* f5c;
    int fn_0063d580(int a1, int a2, int a3);
};

struct C00641120 {
    u8 pad0[0x30];
    u32 f30;
    u8* f34;
    u8 pad38[0x08];
    u32* f40;
    int fn_00641120(u32 idx, int val);
};

struct C00641A40 {
    u8 pad0[0x84];
    u32 f84[16];
    u32 fC4[16];
    u8 pad2[0x828];
    u32 f92c;
    int fn_00641a40(u32 idx, u32 v);
};

struct C00641E60 {
    u8 pad0[0x2c];
    u32 f2c;
    u8 pad30[0x10];
    u32 f40;
    u8 pad44[0x0c];
    u32 f50;
    u32 f54;
    u8 pad58[0x114];
    u32 f16c;
    u8 pad170[0x7b8];
    u32 f928;
    u32 f92c;
    u8 pad930[0x0c];
    u32 f93c;
    int fn_00641e60(u32 arg);
};

struct C00642F60 {
    u8 pad0[0x104];
    u32 f104[64];
    u32 fn_00642f90(u8 idx);
};

struct C00649010 {
    u8 pad0[0x28];
    int f28;
    int f2c;
    u8 pad30[0x18];
    u8* f48;
    u16* f4c;
    int f50;
    int fn_00649010(int x, int y);
};

struct C00649070 {
    u8 pad0[0x20];
    int f20;
    int f24;
    u8 pad28[0x14];
    u8* f3c;
    u8 fn_00649070(int x, int y);
};

struct Node00648550 {
    u8 pad0[8];
    Node00648550* f8;
    u8 padC[9];
    u8 f15;
};

// FUNCTION: DAO 0x00a3d580
int C0063D580::fn_0063d580(int a1, int a2, int a3)
{
    int count = f50;
    int bestIdx = -1;
    int bestVal = 0x7fffffff;
    for (int i = 0; i < count; ++i) {
        int lo = f54[i];
        int hi = f58[i];
        int include;
        if (hi != -1) {
            include = !(a2 < lo || a2 > hi);
        } else {
            int v = f3c[a1];
            int w = f40[a1];
            include = !(lo < v || lo >= w);
        }
        if (include) {
            int val = f5c[i];
            if (val > a3 && val < bestVal) {
                bestVal = val;
                bestIdx = i;
            }
        }
    }
    return bestIdx;
}

// FUNCTION: DAO 0x00a41120
int C00641120::fn_00641120(u32 idx, int val)
{
    if (idx >= f30) return 0;
    if (f34[idx] != 0) {
        if (val == 1) {
            f40[idx] = (u32)val;
            return val;
        }
    }
    if (val != 0) return 0;
    f40[idx] = 0;
    return 1;
}

// FUNCTION: DAO 0x00a41a40
int C00641A40::fn_00641a40(u32 idx, u32 v)
{
    if (idx >= f92c) return 0;
    if (f84[idx] != 1) return 0;
    if (v > fC4[idx]) return 1;
    return 0;
}

// FUNCTION: DAO 0x00a41e60
int C00641E60::fn_00641e60(u32 arg)
{
    if (f16c == 0 && f2c < f92c && f93c == 0) return 1;
    u32 edx = f50;
    u32 edi = f928;
    if (edi > 0x96) {
        u32 f40v = f40;
        u32 half = f40v >> 1;
        if (edx >= half) edx -= half;
        if (edi > 0x12c) {
            u32 quarter = f40v >> 2;
            if (edx >= quarter) edx -= quarter;
        }
    }
    if (f54 == 1 && arg > edx) return 1;
    return 0;
}

// FUNCTION: DAO 0x00a42f90
u32 C00642F60::fn_00642f90(u8 idx)
{
    if (idx < 0x40)
        return f104[idx];
    return 0;
}

// FUNCTION: DAO 0x00a48550
Node00648550* fn_00648550(Node00648550* p)
{
    Node00648550* eax = p;
    Node00648550* ecx = eax->f8;
    if (ecx->f15 != 0) return eax;
    do {
        eax = ecx;
        ecx = eax->f8;
    } while (ecx->f15 == 0);
    return eax;
}

// FUNCTION: DAO 0x00a48fb0
unsigned char __stdcall fn_00648fb0(u32 target, u32 x, u32 y, u32* out)
{
    if (x == 0xffffffffu) return 0;
    if (y == 0xffffffffu) return 0;
    u32 prod = x * y;
    u32 shift = 0;
    if (prod == target) {
        *out = shift;
        return 1;
    }
    for (;;) {
        if (prod == 0) return 0;
        ++shift;
        prod = (x >> shift) * (y >> shift);
        if (prod == target) {
            *out = shift;
            return 1;
        }
    }
}

// FUNCTION: DAO 0x00a49010
int C00649010::fn_00649010(int x, int y)
{
    int sh = f50;
    x >>= sh;
    y >>= sh;
    if (x >= f2c) return -1;
    if (y >= f28) return -1;
    if (x < 0) return -1;
    if (y < 0) return -1;
    int idx = f28 * x + y;
    if (f48 != 0) {
        u8 c = f48[idx];
        if (c == 0xff) return -1;
        return (int)c;
    }
    if (f4c != 0) {
        u16 c = f4c[idx];
        if (c == 0x00ff) return -1;
        return (int)c;
    }
    return -1;
}

// FUNCTION: DAO 0x00a49070
u8 C00649070::fn_00649070(int x, int y)
{
    if (f3c == 0) return 9;
    if (y >= f24) return 9;
    if (x >= f20) return 9;
    if (y < 0) return 9;
    if (x < 0) return 9;
    int idx = f20 * y + x;
    return (u8)(f3c[idx] & 0x0f);
}
