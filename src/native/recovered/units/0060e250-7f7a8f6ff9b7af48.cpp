typedef unsigned int u32;

struct C0060E1C0 { int fn_0060e1c0(); };
struct C0060E220 { int fn_0060e220(unsigned int key); };
struct C0060E250 { unsigned int fn_0060e250(unsigned int index); };
struct C00615690 { int fn_00615690(unsigned int key); };
struct C00619B20 { int fn_00619b20(); };
struct C006285C0 { unsigned char *fn_006285c0(); };
struct C00629F30 { unsigned char *fn_00629f30(); };

// FUNCTION: DAO 0xA07750
void fn_00607750(unsigned int *p)
{
    int r;
    for (r = 7; r >= 0; --r) {
        unsigned int *a = p + 2 + r * 8;
        unsigned int x0 = a[-2];
        unsigned int x1 = a[-1];
        unsigned int x2 = a[0];
        unsigned int x3 = a[1];
        unsigned int x4 = a[2];
        unsigned int x5 = a[3];
        unsigned int x6 = a[4];
        unsigned int x7 = a[5];

        unsigned int e0 = x0 + x7;
        unsigned int e1 = x1 + x6;
        unsigned int e2 = x2 + x5;
        unsigned int e3 = x3 + x4;
        unsigned int s0 = e0 + e3;
        unsigned int s1 = e1 + e2;
        unsigned int d0 = e0 - e3;
        unsigned int d1 = e1 - e2;

        unsigned int out0 = (s0 + s1) * 4u;
        unsigned int out4 = (s0 - s1) * 4u;

        unsigned int t = d0 + d1;
        unsigned int out2 = (unsigned int)(((int)(t * 4433u + d0 * 6270u + 0x400u)) >> 11);
        unsigned int out6 = (unsigned int)(((int)(t * 4433u - d1 * 15137u + 0x400u)) >> 11);

        unsigned int o0 = x0 - x7;
        unsigned int o1 = x1 - x6;
        unsigned int o2 = x2 - x5;
        unsigned int o3 = x3 - x4;

        unsigned int A = o2 + o0;
        unsigned int B = o3 + o1;
        unsigned int sumOdd = A + B;
        unsigned int C1 = B * 16069u;
        unsigned int C2 = sumOdd * 9633u;
        unsigned int D = (o3 + o0) * 0xffffe333u;
        unsigned int E = (o2 + o1) * 0xffffadfdu;
        unsigned int F = o2 * 16819u;
        unsigned int G = o3 * 2446u;
        unsigned int H = A * 3196u;
        unsigned int T = C2 - C1;
        unsigned int U = C2 - H;

        unsigned int out7 = (unsigned int)(((int)(G + T + D + 0x400u)) >> 11);
        unsigned int out5 = (unsigned int)(((int)(F + U + E + 0x400u)) >> 11);
        unsigned int out1 = (unsigned int)(((int)(o1 * 25172u + T + E + 0x400u)) >> 11);
        unsigned int out3 = (unsigned int)(((int)(o0 * 12299u + U + D + 0x400u)) >> 11);

        a[-2] = out0;
        a[-1] = out3;
        a[0] = out2;
        a[1] = out1;
        a[2] = out4;
        a[3] = out5;
        a[4] = out6;
        a[5] = out7;
    }

    int c;
    for (c = 7; c >= 0; --c) {
        unsigned int *a = p + 16 + c;
        unsigned int y0 = a[-16];
        unsigned int y1 = a[-8];
        unsigned int y2 = a[0];
        unsigned int y3 = a[8];
        unsigned int y4 = a[16];
        unsigned int y5 = a[24];
        unsigned int y6 = a[32];
        unsigned int y7 = a[40];

        unsigned int e0 = y0 + y7;
        unsigned int e1 = y1 + y6;
        unsigned int e2 = y2 + y5;
        unsigned int e3 = y3 + y4;
        unsigned int s0 = e0 + e3;
        unsigned int s1 = e1 + e2;
        unsigned int d0 = e0 - e3;
        unsigned int d1 = e1 - e2;

        unsigned int out0 = (unsigned int)(((int)(s0 + s1 + 2u)) >> 2);
        unsigned int out4 = (unsigned int)(((int)(s0 - s1 + 2u)) >> 2);

        unsigned int t = d0 + d1;
        unsigned int out2 = (unsigned int)(((int)(t * 4433u + d0 * 6270u + 0x4000u)) >> 15);
        unsigned int out6 = (unsigned int)(((int)(t * 4433u - d1 * 15137u + 0x4000u)) >> 15);

        unsigned int o0 = y0 - y7;
        unsigned int o1 = y1 - y6;
        unsigned int o2 = y2 - y5;
        unsigned int o3 = y3 - y4;

        unsigned int A = o2 + o0;
        unsigned int B = o3 + o1;
        unsigned int sumOdd = A + B;
        unsigned int C1 = B * 16069u;
        unsigned int C2 = sumOdd * 9633u;
        unsigned int D = (o3 + o0) * 0xffffe333u;
        unsigned int E = (o2 + o1) * 0xffffadfdu;
        unsigned int F = o2 * 16819u;
        unsigned int G = o3 * 2446u;
        unsigned int H = A * 3196u;
        unsigned int T = C2 - C1;
        unsigned int U = C2 - H;

        unsigned int out7 = (unsigned int)(((int)(G + T + D + 0x4000u)) >> 15);
        unsigned int out5 = (unsigned int)(((int)(F + U + E + 0x4000u)) >> 15);
        unsigned int out1 = (unsigned int)(((int)(o1 * 25172u + T + E + 0x4000u)) >> 15);
        unsigned int out3 = (unsigned int)(((int)(o0 * 12299u + U + D + 0x4000u)) >> 15);

        a[-16] = out0;
        a[-8] = out3;
        a[0] = out2;
        a[8] = out1;
        a[16] = out4;
        a[24] = out5;
        a[32] = out6;
        a[40] = out7;
    }
}

// FUNCTION: DAO 0xA0E1C0
int C0060E1C0::fn_0060e1c0()
{
    unsigned int *p = (unsigned int *)((unsigned char *)this + 0x24);
    unsigned int count = 0;
    for (int i = 0; i < 0x20; ++i) {
        if (p[-3] != 0) ++count;
        if (p[0] != 0) ++count;
        if (p[3] != 0) ++count;
        if (p[6] != 0) ++count;
        p += 12;
    }
    return (int)count;
}

// FUNCTION: DAO 0xA0E220
int C0060E220::fn_0060e220(unsigned int key)
{
    unsigned int *desc = *(unsigned int **)((unsigned char *)this + 0x28);
    unsigned int count = desc[2];
    unsigned int *arr = (unsigned int *)desc[0];
    unsigned int i;
    for (i = 0; i < count; ++i) {
        if (arr[i] == key) return (int)i;
    }
    return -1;
}

// FUNCTION: DAO 0xA0E250
unsigned int C0060E250::fn_0060e250(unsigned int index)
{
    unsigned int *desc = *(unsigned int **)((unsigned char *)this + 0x28);
    unsigned int *arr = *(unsigned int **)((unsigned char *)desc + 0x18);
    return *(unsigned int *)((unsigned char *)arr + (index << 4) + 0xc);
}

// FUNCTION: DAO 0xA15690
int C00615690::fn_00615690(unsigned int key)
{
    if (key == 0) return -1;
    unsigned int count = *(unsigned int *)((unsigned char *)this + 0x1c);
    unsigned int *p = *(unsigned int **)((unsigned char *)this + 0x14);
    for (unsigned int i = 0; i < count; ++i) {
        if (p[0] == key) return (int)i;
        p += 4;
    }
    return -1;
}

// FUNCTION: DAO 0xA19B20
int C00619B20::fn_00619b20()
{
    unsigned int *p = (unsigned int *)((unsigned char *)this + 0x24);
    unsigned int count = 0;
    for (int i = 0; i < 0x200; ++i) {
        if (p[-3] != 0) ++count;
        if (p[0] != 0) ++count;
        if (p[3] != 0) ++count;
        if (p[6] != 0) ++count;
        p += 12;
    }
    return (int)count;
}

// FUNCTION: DAO 0xA1C8F0
void *fn_0061c8f0(void *base, unsigned int key, unsigned int *outIndex)
{
    unsigned char *b = (unsigned char *)base;
    int count = *(int *)(b + 0x22c);
    if (count <= 0) return 0;
    unsigned char *p = b + 0x3cc;
    for (int i = 0; i < count; ++i) {
        if (*(unsigned int *)p == key) {
            if (outIndex != 0) *outIndex = (unsigned int)i;
            return b + 0x23c + i * 0x194;
        }
        p += 0x194;
    }
    return 0;
}

// FUNCTION: DAO 0xA1D9B0
void *fn_0061d9b0(void *p)
{
    if (*(int *)((unsigned char *)p + 0x230) > 0)
        return (unsigned char *)p + 0x1cc;
    return 0;
}

// FUNCTION: DAO 0xA285C0
unsigned char *C006285C0::fn_006285c0()
{
    return (unsigned char *)this + 0x2a8;
}

// FUNCTION: DAO 0xA29F30
unsigned char *C00629F30::fn_00629f30()
{
    return (unsigned char *)this + 0x21;
}
