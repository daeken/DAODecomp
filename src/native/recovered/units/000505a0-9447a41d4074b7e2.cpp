struct CObj56230 {
    void* field0;
    void* fn_00056230();
};

struct CObj56240 {
    unsigned int pad[24];
    unsigned int f60;
    unsigned int f64;
    unsigned int f68;
    unsigned int f6c;
    void fn_00056240(unsigned int* out);
};

// FUNCTION: DAO 0x44A180
char* fn_0004a180(const unsigned char* src, char* dest, int len)
{
    if (len <= 0)
        return 0;
    if (len < 16) {
        dest[0] = 0;
        return 0;
    }

    char* out = dest;
    for (unsigned int i = 4; i < 8; ++i) {
        unsigned int value = src[i];
        if (value > 99) {
            unsigned int q = value / 100;
            *out++ = (char)(q + '0');
            value -= q * 100;
            q = value / 10;
            *out++ = (char)(q + '0');
            value -= q * 10;
        } else if (value > 9) {
            unsigned int q = value / 10;
            *out++ = (char)(q + '0');
            value -= q * 10;
        }
        *out++ = (char)(value + '0');
        *out++ = '.';
    }
    *out = 0;
    return dest;
}

// FUNCTION: DAO 0x44F010
void fn_0004f010(unsigned char* state, const unsigned char* key, int keylen, int rounds)
{
    if (rounds < 1)
        rounds = 1;
    state[0x100] = 0;
    state[0x101] = 0;
    for (unsigned int i = 0; i < 256; ++i)
        state[i] = (unsigned char)i;

    if (keylen <= 0)
        return;

    unsigned char j = 0;
    do {
        for (unsigned int i = 0; i < 256; ++i) {
            unsigned char si = state[i];
            unsigned char k = key[i % (unsigned int)keylen];
            j = (unsigned char)(j + si + k);
            unsigned char sj = state[j];
            state[i] = sj;
            state[j] = si;
        }
        --rounds;
    } while (rounds > 0);
}

// FUNCTION: DAO 0x4505A0
void fn_000505a0(void* ctx)
{
    unsigned int* p = (unsigned int*)ctx;
    p[0] = 0;
    p[1] = 0;
    p[2] = 0x67452301u;
    p[3] = 0xefcdab89u;
    p[4] = 0x98badcfeu;
    p[5] = 0x10325476u;
    p[6] = 0xc3d2e1f0u;
}

// FUNCTION: DAO 0x450E40
void fn_00050e40(void* ctx)
{
    unsigned int* p = (unsigned int*)ctx;
    p[0x48 / 4] = 0;
    p[0x4c / 4] = 0x67452301u;
    p[0x50 / 4] = 0xefcdab89u;
    p[0x54 / 4] = 0x98badcfeu;
    p[0x58 / 4] = 0x10325476u;
}

// FUNCTION: DAO 0x456230
void* CObj56230::fn_00056230()
{
    void* p = field0;
    if (p != 0)
        return *(void**)p;
    return 0;
}

// FUNCTION: DAO 0x456240
void CObj56240::fn_00056240(unsigned int* out)
{
    out[0] = f60;
    out[1] = f64;
    out[2] = f68;
    out[3] = f6c;
}
