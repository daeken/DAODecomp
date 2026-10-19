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
    int n = f50;
    int bestIdx = -1;
    int bestVal = 0x7fffffff;
    for (int i = 0; i < n; ++i) {
        int hi = f58[i];
        int lo = f54[i];
        if (hi != -1) {
            if (a2 < lo || a2 > hi)
                continue;
        } else {
            int v = f3c[a1];
            if (lo < v)
                continue;
            int w = f40[a1];
            if (lo >= w)
                continue;
        }
        int val = f5c[i];
        if (val > a3 && val < bestVal) {
            bestVal = val;
            bestIdx = i;
        }
    }
    return bestIdx;
}

// FUNCTION: DAO 0x00a41120
int C00641120::fn_00641120(u32 idx, int val)
{
    if (idx < f30) {
        if (f34[idx] != 0 && val == 1) {
            f40[idx] = (u32)val;
            return val;
        }
        if (val == 0) {
            f40[idx] = 0;
            return 1;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x00a41a40
int C00641A40::fn_00641a40(u32 idx, u32 v)
{
    if (idx < f92c) {
        if (f84[idx] == 1) {
            if (v > fC4[idx]) {
                return 1;
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x00a41e60
int C00641E60::fn_00641e60(u32 arg)
{
    if (f16c == 0 && f2c < f92c && f93c == 0)
        return 1;
    u32 value = f50;
    if (f928 > 0x96) {
        u32 width = f40;
        u32 half = width >> 1;
        if (value >= half)
            value -= half;
        if (f928 > 0x12c) {
            u32 quarter = width >> 2;
            if (value >= quarter)
                value -= quarter;
        }
    }
    if (f54 == 1 && arg > value)
        return 1;
    return 0;
}

// FUNCTION: DAO 0x00a48550
Node00648550* fn_00648550(Node00648550* p)
{
    Node00648550* eax = p;
    Node00648550* ecx = eax->f8;
    if (ecx->f15 != 0)
        return eax;
    do {
        eax = ecx;
        ecx = eax->f8;
    } while (ecx->f15 == 0);
    return eax;
}

// FUNCTION: DAO 0x00a48fb0
unsigned char __stdcall fn_00648fb0(u32 target, u32 x, u32 y, u32* out)
{
    if (x == 0xffffffffu || y == 0xffffffffu)
        goto fail;
    {
        u32 prod = x * y;
        u32 shift = 0;
        if (prod == target)
            goto success;
        while (prod != 0) {
            ++shift;
            prod = (x >> shift) * (y >> shift);
            if (prod == target)
                goto success;
        }
        goto fail;
success:
        *out = shift;
        return 1;
    }
fail:
    return 0;
}

// FUNCTION: DAO 0x00a49010
int C00649010::fn_00649010(int x, int y)
{
    int xx = x;
    int sh = f50;
    xx >>= sh;
    int result = -1;
    int yy = y;
    yy >>= sh;
    if (xx < f2c) {
        int width = f28;
        if (yy < width) {
            if (xx >= 0) {
                if (yy >= 0) {
                    int idx = width * xx + yy;
                    if (f48 != 0) {
                        u8 c = f48[idx];
                        if (c != 0xff)
                            result = (int)c;
                    } else if (f4c != 0) {
                        u16 c = f4c[idx];
                        if (c != 0xff)
                            result = (int)c;
                    }
                }
            }
        }
    }
    return result;
}

// FUNCTION: DAO 0x00a49070
u8 C00649070::fn_00649070(int x, int y)
{
    u8 result = 9;
    if (f3c != 0) {
        int xv = x;
        if (xv < f24) {
            int width = f20;
            int yv = y;
            if (yv < width) {
                if (xv >= 0) {
                    if (yv >= 0) {
                        int idx = width * xv + yv;
                        result = (u8)(f3c[idx] & 0x0f);
                    }
                }
            }
        }
    }
    return result;
}
