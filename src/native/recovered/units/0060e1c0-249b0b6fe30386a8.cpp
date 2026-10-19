typedef unsigned int u32;

struct C0060E1C0 { int fn_0060e1c0(); };
struct C0060E220 { int fn_0060e220(unsigned int key); };
struct C00615690 { int fn_00615690(unsigned int key); };
struct C00619B20 { int fn_00619b20(); };

// FUNCTION: DAO 0xA07750
void fn_00607750(unsigned int *p)
{
    unsigned int *a;
    int n;

    for (a = p + 2, n = 7; n >= 0; --n, a += 8) {
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

        a[-2] = (s0 + s1) * 4u;
        a[2] = (s0 - s1) * 4u;

        unsigned int t = d0 + d1;
        a[0] = (unsigned int)(((int)(t * 4433u + d0 * 6270u + 0x400u)) >> 11);
        a[4] = (unsigned int)(((int)(t * 4433u - d1 * 15137u + 0x400u)) >> 11);

        unsigned int o0 = x0 - x7;
        unsigned int o1 = x1 - x6;
        unsigned int o2 = x2 - x5;
        unsigned int o3 = x3 - x4;

        unsigned int A = o2 + o0;
        unsigned int B = o3 + o1;
        unsigned int C2 = (A + B) * 9633u;
        unsigned int C1 = B * 16069u;
        unsigned int D = (o3 + o0) * 0xffffe333u;
        unsigned int E = (o2 + o1) * 0xffffadfdu;
        unsigned int F = o2 * 16819u;
        unsigned int G = o3 * 2446u;
        unsigned int H = A * 3196u;
        unsigned int T = C2 - C1;
        unsigned int U = C2 - H;

        a[5] = (unsigned int)(((int)(G + T + D + 0x400u)) >> 11);
        a[3] = (unsigned int)(((int)(F + U + E + 0x400u)) >> 11);
        a[1] = (unsigned int)(((int)(o1 * 25172u + T + E + 0x400u)) >> 11);
        a[-1] = (unsigned int)(((int)(o0 * 12299u + U + D + 0x400u)) >> 11);
    }

    for (a = p + 16, n = 7; n >= 0; --n, a += 1) {
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

        a[-16] = (unsigned int)(((int)(s0 + s1 + 2u)) >> 2);
        a[16] = (unsigned int)(((int)(s0 - s1 + 2u)) >> 2);

        unsigned int t = d0 + d1;
        a[0] = (unsigned int)(((int)(t * 4433u + d0 * 6270u + 0x4000u)) >> 15);
        a[32] = (unsigned int)(((int)(t * 4433u - d1 * 15137u + 0x4000u)) >> 15);

        unsigned int o0 = y0 - y7;
        unsigned int o1 = y1 - y6;
        unsigned int o2 = y2 - y5;
        unsigned int o3 = y3 - y4;

        unsigned int A = o2 + o0;
        unsigned int B = o3 + o1;
        unsigned int C2 = (A + B) * 9633u;
        unsigned int C1 = B * 16069u;
        unsigned int D = (o3 + o0) * 0xffffe333u;
        unsigned int E = (o2 + o1) * 0xffffadfdu;
        unsigned int F = o2 * 16819u;
        unsigned int G = o3 * 2446u;
        unsigned int H = A * 3196u;
        unsigned int T = C2 - C1;
        unsigned int U = C2 - H;

        a[40] = (unsigned int)(((int)(G + T + D + 0x4000u)) >> 15);
        a[24] = (unsigned int)(((int)(F + U + E + 0x4000u)) >> 15);
        a[8] = (unsigned int)(((int)(o1 * 25172u + T + E + 0x4000u)) >> 15);
        a[-8] = (unsigned int)(((int)(o0 * 12299u + U + D + 0x4000u)) >> 15);
    }
}

// FUNCTION: DAO 0xA0E1C0
int C0060E1C0::fn_0060e1c0()
{
    unsigned int count = 0;
    unsigned int *p = (unsigned int *)((unsigned char *)this + 0x24);
    int n = 0x20;
    do {
        if (p[-3] != 0) ++count;
        if (p[0] != 0) ++count;
        if (p[3] != 0) ++count;
        if (p[6] != 0) ++count;
        p += 12;
    } while (--n != 0);
    return (int)count;
}

// FUNCTION: DAO 0xA0E220
int C0060E220::fn_0060e220(unsigned int key)
{
    unsigned int *desc = *(unsigned int **)((unsigned char *)this + 0x28);
    unsigned int count = desc[2];
    unsigned int i = 0;
    if (count <= 0u) return -1;
    unsigned int *arr = (unsigned int *)desc[0];
    do {
        if (key == *arr) return (int)i;
        ++i;
        ++arr;
    } while (i < count);
    return -1;
}

// FUNCTION: DAO 0xA15690
int C00615690::fn_00615690(unsigned int key)
{
    if (key == 0) return -1;
    unsigned int count = *(unsigned int *)((unsigned char *)this + 0x1c);
    unsigned int i = 0;
    if (count <= 0u) return -1;
    unsigned int *p = *(unsigned int **)((unsigned char *)this + 0x14);
    do {
        if (*p == key) return (int)i;
        ++i;
        p += 4;
    } while (i < count);
    return -1;
}

// FUNCTION: DAO 0xA19B20
int C00619B20::fn_00619b20()
{
    unsigned int count = 0;
    unsigned int *p = (unsigned int *)((unsigned char *)this + 0x24);
    int n = 0x200;
    do {
        if (p[-3] != 0) ++count;
        if (p[0] != 0) ++count;
        if (p[3] != 0) ++count;
        if (p[6] != 0) ++count;
        p += 12;
    } while (--n != 0);
    return (int)count;
}

// FUNCTION: DAO 0xA1C8F0
void *fn_0061c8f0(void *base, unsigned int key, unsigned int *outIndex)
{
    unsigned char *b = (unsigned char *)base;
    int count = *(int *)(b + 0x22c);
    if (count <= 0) return 0;
    unsigned int i = 0;
    unsigned char *p = b + 0x3cc;
    do {
        if (*(unsigned int *)p == key) {
            if (outIndex != 0) *outIndex = i;
            return b + 0x23c + i * 0x194;
        }
        ++i;
        p += 0x194;
    } while ((int)i < count);
    return 0;
}
