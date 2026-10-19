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
    char* out;
    int value;
    int q;

    if (len <= 0)
        return 0;
    if (len < 16) {
        dest[0] = 0;
        return 0;
    }

    out = dest;

    value = src[4];
    if (value > 99) {
        q = value / 100;
        *out++ = (char)(q + '0');
        value -= q * 100;
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    if (value > 9) {
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    *out++ = (char)(value + '0');
    *out++ = '.';

    value = src[5];
    if (value > 99) {
        q = value / 100;
        *out++ = (char)(q + '0');
        value -= q * 100;
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    if (value > 9) {
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    *out++ = (char)(value + '0');
    *out++ = '.';

    value = src[6];
    if (value > 99) {
        q = value / 100;
        *out++ = (char)(q + '0');
        value -= q * 100;
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    if (value > 9) {
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    *out++ = (char)(value + '0');
    *out++ = '.';

    value = src[7];
    if (value > 99) {
        q = value / 100;
        *out++ = (char)(q + '0');
        value -= q * 100;
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    if (value > 9) {
        q = value / 10;
        *out++ = (char)(q + '0');
        value -= q * 10;
    }
    *out++ = (char)(value + '0');
    *out = 0;
    return dest;
}

// FUNCTION: DAO 0x44F010
void fn_0004f010(unsigned char* state, const unsigned char* key, int keylen, int rounds)
{
    unsigned int i;
    unsigned char j;

    if (rounds < 1)
        rounds = 1;

    state[0x100] = 0;
    state[0x101] = 0;
    for (i = 0; i < 256; ++i)
        state[i] = (unsigned char)i;

    if (keylen <= 0)
        return;

    j = 0;
    while (rounds > 0) {
        for (i = 0; i < 256; ++i) {
            unsigned char s = state[i];
            j = (unsigned char)(j + s + key[i % (unsigned int)keylen]);
            state[i] = state[j];
            state[j] = s;
        }
        --rounds;
    }
}

// FUNCTION: DAO 0x456240
void CObj56240::fn_00056240(unsigned int* out)
{
    unsigned int* p = out;
    p[0] = f60;
    p[1] = f64;
    p[2] = f68;
    p[3] = f6c;
}
