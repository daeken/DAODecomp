// FUNCTION: DAO 0x4481D0
int __cdecl fn_000481d0(const char* wild, const char* str)
{
    if (*wild == 0) return 0;
    const char* star = 0;
    const char* ss = 0;
    while (*str != 0) {
        if (*wild == '*') {
            star = wild++;
            ss = str;
        } else if (*wild == *str) {
            wild++;
            str++;
        } else if (star != 0) {
            wild = star + 1;
            str = ++ss;
        } else {
            return 0;
        }
    }
    while (*wild == '*') wild++;
    return (*wild == 0) ? 1 : 0;
}

// FUNCTION: DAO 0x44B900
int __cdecl fn_0004b900(const char* a, const char* b)
{
    for (;;) {
        unsigned char ca = (unsigned char)*a;
        unsigned char cb = (unsigned char)*b;
        if (ca >= 'A' && ca <= 'Z') ca ^= 0x20;
        if (cb >= 'A' && cb <= 'Z') cb ^= 0x20;
        int diff = (int)(signed char)ca - (int)(signed char)cb;
        if (ca == 0 || diff != 0) return diff;
        a++;
        b++;
    }
}

// FUNCTION: DAO 0x44B95B
int __cdecl fn_0004b95b(const char* a, const char* b, unsigned int n)
{
    unsigned int i = 0;
    for (;;) {
        unsigned char ca = (unsigned char)*a++;
        unsigned char cb = (unsigned char)*b++;
        if (ca >= 'A' && ca <= 'Z') ca ^= 0x20;
        if (cb >= 'A' && cb <= 'Z') cb ^= 0x20;
        int diff = (int)(signed char)ca - (int)(signed char)cb;
        i++;
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
    if (count <= 0) {
        dest[0] = 0;
        return 0;
    }
    while (i < limit && i < count && src[i] != 0) {
        dest[i] = src[i];
        i++;
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
        while (i < limit && dest[i] != 0) i++;
    }
    if (i >= limit) {
        dest[i] = 0;
        return i;
    }
    int j = 0;
    while (i < limit && src[j] != 0) {
        dest[i] = src[j];
        i++;
        j++;
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

struct Fn44CB80_Obj
{
    unsigned char pad_00[0x124];
    Fn44CB80_Inner* inner_124;
};

// FUNCTION: DAO 0x44CB80
unsigned char* __cdecl fn_0004cb80(Fn44CB80_Obj* obj, unsigned char type)
{
    Fn44CB80_Inner* p = obj->inner_124;
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
    if (out1) *out1 = 0;
    if (out2) *out2 = 0;
    if (data == 0) return 0;
    if (data == end) return 0;
    if (out2) *out2 = (unsigned int)*data;
    data++;
    if (data == end) return 0;
    for (;;) {
        unsigned int c = (unsigned int)*data++;
        if (c <= 0x7f) {
            if (out1) *out1 = c;
            return data;
        }
        unsigned int count = c & 0x7f;
        unsigned int value = 0;
        while (count > 0) {
            if (data == end) return 0;
            value = (value << 8) | (unsigned int)*data++;
            count--;
        }
        if (out1) *out1 = value;
        return data;
    }
}

// FUNCTION: DAO 0x44EF70
int __cdecl fn_0004ef70(int* flag, int value)
{
    if (*flag == 0) return value;
    return value + 8;
}

class CObj_4517F0
{
public:
    void __thiscall fn_000517f0();
private:
    unsigned char pad_000[0x678];
    unsigned char field_678;
};

// FUNCTION: DAO 0x4517F0
void __thiscall CObj_4517F0::fn_000517f0()
{
    field_678 = 0;
}

class CObj_45F1C0
{
public:
    char __thiscall fn_0005f1c0();
private:
    unsigned char pad_000[0x28];
    char field_28;
};

// FUNCTION: DAO 0x45F1C0
char __thiscall CObj_45F1C0::fn_0005f1c0()
{
    return field_28;
}
