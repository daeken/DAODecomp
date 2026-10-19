class C00629fe0 {
public:
    unsigned int __thiscall fn_00629fe0(const void* other);
};

class C0062d110 {
public:
    unsigned int* __thiscall fn_0062d110(int index, unsigned int value);
};

extern "C" int __cdecl memcmp(const void*, const void*, unsigned int);
#pragma intrinsic(memcmp)

// FUNCTION: DAO 0x00A29FE0
unsigned int __thiscall C00629fe0::fn_00629fe0(const void* other)
{
    return memcmp(reinterpret_cast<const unsigned char*>(other) + 0x21,
                  reinterpret_cast<const unsigned char*>(this) + 0x21,
                  0x20) == 0;
}

// FUNCTION: DAO 0x00A2D110
unsigned int* __thiscall C0062d110::fn_0062d110(int index, unsigned int value)
{
    if (index < 0)
        return reinterpret_cast<unsigned int*>(index);

    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    if (*reinterpret_cast<unsigned int*>(p + 0x14) == 0)
        return reinterpret_cast<unsigned int*>(index);

    unsigned int* types = *reinterpret_cast<unsigned int**>(p + 0xc);
    if (types[index] != 3)
        return reinterpret_cast<unsigned int*>(index);

    unsigned int* values = *reinterpret_cast<unsigned int**>(p + 0x10);
    return &(values[index] += value);
}
