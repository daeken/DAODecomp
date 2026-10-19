// FUNCTION: DAO 0x4481D0
int __cdecl fn_000481d0(const char* wild, const char* str)
{
    if (*wild == 0) return 0;
    const char* wend = wild;
    while (*wend != 0) ++wend;
    --wend;
    if (*wild == '*') {
        const char* send = str;
        while (*send != 0) ++send;
        --send;
        while (send != str && wend != wild && *send == *wend) {
            --send;
            --wend;
        }
        if (*wend == '*') {
            ++send;
            ++wend;
        }
        while (*wend == *send) {
            if (*wend == 0) return 1;
            ++wend;
            ++send;
        }
        return 0;
    } else if (*wend == '*') {
        const char* w = wild;
        while (*w != 0) {
            if (*str == 0) break;
            if (*w != *str) break;
            ++w;
            ++str;
        }
        return (*w == '*') ? 1 : 0;
    } else {
        while (*wild == *str) {
            if (*wild == 0) return 1;
            ++wild;
            ++str;
        }
        return 0;
    }
}

// FUNCTION: DAO 0x44B900
int __cdecl fn_0004b900(const char* a, const char* b)
{
    for (;;) {
        unsigned char ca = (unsigned char)*a++;
        if ((unsigned char)(ca - 'A') <= 0x19) ca ^= 0x20;
        unsigned char cb = (unsigned char)*b++;
        if ((unsigned char)(cb - 'A') <= 0x19) cb ^= 0x20;
        int diff = (int)(signed char)ca - (int)(signed char)cb;
        if (ca == 0 || diff != 0) return diff;
    }
}

// FUNCTION: DAO 0x44B95B
int __cdecl fn_0004b95b(const char* a, const char* b, unsigned int n)
{
    unsigned int i = 0;
    for (;;) {
        unsigned char ca = (unsigned char)*a++;
        if ((unsigned char)(ca - 'A') <= 0x19) ca ^= 0x20;
        unsigned char cb = (unsigned char)*b++;
        if ((unsigned char)(cb - 'A') <= 0x19) cb ^= 0x20;
        int diff = (int)(signed char)ca - (int)(signed char)cb;
        ++i;
        if (ca == 0 || diff != 0) return diff;
        if (i >= n) return 0;
    }
}

// FUNCTION: DAO 0x44B9E0
int __cdecl fn_0004b9e0(char* dest, int destSize, const char* src, int count)
{
    int i = 0;
    int limit = destSize - 1;
    if (limit < 0) return 0;
    if (count > 0) {
        while (i < limit) {
            char c = src[i];
            if (c == 0) break;
            dest[i] = c;
            ++i;
            if (i >= count) break;
        }
    }
    dest[i] = 0;
    return i;
}

// FUNCTION: DAO 0x44BA30
int __cdecl fn_0004ba30(char* dest, const char* src, int n)
{
    int i = 0;
    int limit = n - 1;
    if (limit < 0) return 0;
    if (limit > 0) {
        while (dest[i] != 0) {
            ++i;
            if (i >= limit) break;
        }
    }
    if (i < limit) {
        while (*src != 0) {
            dest[i] = *src;
            ++i;
            ++src;
            if (i >= limit) break;
        }
    }
    dest[i] = 0;
    return i;
}

struct Fn44CB80_Inner
{
    unsigned char pad_00[0x18];
    int size_18;
    unsigned int offset_1c;
    unsigned char pad_20[0x4958 - 0x20];
    unsigned char data_4958[4];
    unsigned char data_495c[1];
};

class CObj_44CB80
{
public:
    unsigned char* __thiscall fn_0004cb80(unsigned char type);
private:
    unsigned char pad_000[0x124];
    Fn44CB80_Inner* inner_124;
};

// FUNCTION: DAO 0x44CB80
unsigned char* __thiscall CObj_44CB80::fn_0004cb80(unsigned char type)
{
    Fn44CB80_Inner* p = inner_124;
    unsigned int oldOffset = p->offset_1c;
    unsigned char* base = (unsigned char*)p;
    if (base[oldOffset + 0x4958] != type) return 0;
    unsigned int value = ((unsigned int)base[oldOffset + 0x4959] << 16) |
                         ((unsigned int)base[oldOffset + 0x495a] << 8) |
                         (unsigned int)base[oldOffset + 0x495b];
    unsigned int newOffset = oldOffset + value + 4;
    if ((int)newOffset > p->size_18) return 0;
    p->offset_1c = newOffset;
    return base + oldOffset + 0x495c;
}

// FUNCTION: DAO 0x44CC40
unsigned char* __cdecl fn_0004cc40(unsigned char* data, unsigned char* end, unsigned int* out1, unsigned int* out2)
{
    if (out1 != 0) *out1 = 0;
    if (out2 != 0) *out2 = 0;
    if (data == 0) return 0;
    if (data == end) return 0;
    if (out2 != 0) *out2 = (unsigned int)*data;
    ++data;
    if (data == end) return 0;
    unsigned int c = (unsigned int)*data++;
    if (c <= 0x7f) {
        if (out1 != 0) *out1 = c;
        return data;
    }
    unsigned int count = c & 0x7f;
    unsigned int value = 0;
    while (count > 0) {
        if (data == end) return 0;
        value = (value << 8) | (unsigned int)*data++;
        --count;
    }
    if (out1 != 0) *out1 = value;
    return data;
}
