class C006265b0 {
public:
    void __thiscall fn_006265b0(unsigned int a, unsigned int b, unsigned int c);
};

class C00629fe0 {
public:
    unsigned int __thiscall fn_00629fe0(const void* other);
};

class C0062d110 {
public:
    unsigned int* __thiscall fn_0062d110(int index, unsigned int value);
};

class C0062d140 {
public:
    unsigned int __thiscall fn_0062d140(unsigned int* out);
};

class C0062d180 {
public:
    unsigned int __thiscall fn_0062d180(unsigned int value);
};

extern "C" int __cdecl memcmp(const void*, const void*, unsigned int);
#pragma intrinsic(memcmp)

// FUNCTION: DAO 0x00A265B0
void __thiscall C006265b0::fn_006265b0(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p + 8) = a;
    *reinterpret_cast<unsigned int*>(p + 0x18) = b;
    *reinterpret_cast<unsigned int*>(p + 0x10) = c;
    *reinterpret_cast<unsigned char*>(p + 0x88) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x14) = 4;
    switch (c) {
    case 0:
        *reinterpret_cast<unsigned int*>(p + 0x14) = 0;
        return;
    case 3:
        *reinterpret_cast<unsigned int*>(p + 0x14) = 8;
        return;
    case 4:
        *reinterpret_cast<unsigned int*>(p + 0x14) = 0xc;
        return;
    }
}

// FUNCTION: DAO 0x00A29FE0
unsigned int __thiscall C00629fe0::fn_00629fe0(const void* other)
{
    return memcmp(reinterpret_cast<const unsigned char*>(this) + 0x21,
                  reinterpret_cast<const unsigned char*>(other) + 0x21,
                  0x20) == 0;
}

// FUNCTION: DAO 0x00A2D110
unsigned int* __thiscall C0062d110::fn_0062d110(int index, unsigned int value)
{
    if (index < 0)
        return reinterpret_cast<unsigned int*>(index);
    if (*reinterpret_cast<unsigned int*>(reinterpret_cast<unsigned char*>(this) + 0x14) == 0)
        return reinterpret_cast<unsigned int*>(index);
    unsigned int* types = *reinterpret_cast<unsigned int**>(reinterpret_cast<unsigned char*>(this) + 0xc);
    if (types[index] != 3)
        return reinterpret_cast<unsigned int*>(index);
    unsigned int* values = *reinterpret_cast<unsigned int**>(reinterpret_cast<unsigned char*>(this) + 0x10);
    values[index] += value;
    return &values[index];
}

// FUNCTION: DAO 0x00A2D140
unsigned int __thiscall C0062d140::fn_0062d140(unsigned int* out)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    int* count = reinterpret_cast<int*>(p + 0x1750);
    (*count)--;
    int c = *count;
    if (c < 0) {
        *count = 0;
        return 0;
    }
    *out = *reinterpret_cast<unsigned int*>(p + 0x175c + c * 4);
    return 1;
}

// FUNCTION: DAO 0x00A2D180
unsigned int __thiscall C0062d180::fn_0062d180(unsigned int value)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    int* count = reinterpret_cast<int*>(p + 0x1750);
    int c = *count;
    *reinterpret_cast<unsigned int*>(p + 0x175c + c * 4) = value;
    (*count)++;
    int nc = *count;
    return (nc < 0x80) ? 1u : 0u;
}
