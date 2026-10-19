class C00626520 { public: void* __thiscall fn_00626520(); };
class C00626590 { public: unsigned int __thiscall fn_00626590(); };
class C006265b0 { public: void __thiscall fn_006265b0(unsigned int a, unsigned int b, unsigned int c); };
class C00626600 { public: void __thiscall fn_00626600(unsigned int a, unsigned int b); };
class C00629e50 { public: void* __thiscall fn_00629e50(); };
class C00629f60 { public: unsigned int __thiscall fn_00629f60(); };
class C00629f70 { public: unsigned char __thiscall fn_00629f70(); };
class C00629fe0 { public: unsigned int __thiscall fn_00629fe0(const void* other); };
class C0062a3f0 { public: void* __thiscall fn_0062a3f0(void* a, void* b, void* c); };
class C0062a5e0 { public: void __thiscall fn_0062a5e0(void** out, void* value); };
class C0062cff0 { public: void* __thiscall fn_0062cff0(); };
class C0062d110 { public: unsigned int* __thiscall fn_0062d110(int index, unsigned int value); };
class C0062d140 { public: unsigned int __thiscall fn_0062d140(unsigned int* out); };
class C0062d180 { public: unsigned int __thiscall fn_0062d180(unsigned int value); };
// FUNCTION: DAO 0x00A1DF70
unsigned int __cdecl fn_0061df70(void* p)
{
    unsigned int v = *reinterpret_cast<unsigned int*>(reinterpret_cast<unsigned char*>(p) + 0x62ee0);
    return (v == 0) ? 0xFFFFFFFFu : 0u;
}
// FUNCTION: DAO 0x00A26520
void* __thiscall C00626520::fn_00626520()
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p + 0x98) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x9c) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xa0) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xa4) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xa8) = 0;
    *reinterpret_cast<unsigned int*>(p + 8) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xc) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x10) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x18) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x1c) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x80) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x84) = 0;
    *reinterpret_cast<unsigned char*>(p + 0x88) = 0;
    *reinterpret_cast<unsigned char*>(p + 0x89) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x8c) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x90) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x24) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x28) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x2c) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x30) = 0;
    *reinterpret_cast<unsigned int*>(p) = 0;
    *reinterpret_cast<unsigned int*>(p + 4) = 0;
    return this;
}
// FUNCTION: DAO 0x00A26590
unsigned int __thiscall C00626590::fn_00626590()
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p + 0x78) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x7c) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xac) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xb0) = 0;
    return 0;
}
// FUNCTION: DAO 0x00A265B0
void __thiscall C006265b0::fn_006265b0(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p + 8) = a;
    *reinterpret_cast<unsigned int*>(p + 0x18) = b;
    *reinterpret_cast<unsigned int*>(p + 0x10) = c;
    *reinterpret_cast<unsigned char*>(p + 0x88) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x14) = 4;
    if (c == 0) {
        *reinterpret_cast<unsigned int*>(p + 0x14) = 0;
    } else if (c == 3) {
        *reinterpret_cast<unsigned int*>(p + 0x14) = 8;
    } else if (c == 4) {
        *reinterpret_cast<unsigned int*>(p + 0x14) = 0xc;
    }
}
// FUNCTION: DAO 0x00A26600
void __thiscall C00626600::fn_00626600(unsigned int a, unsigned int b)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p + 0xc) = a;
    *reinterpret_cast<unsigned int*>(p + 0x1c) = b;
    *reinterpret_cast<unsigned char*>(p + 0x89) = 0;
}
// FUNCTION: DAO 0x00A28600
unsigned char __cdecl fn_00628600(unsigned int, unsigned int, unsigned int* out1, unsigned int* out2)
{
    *out1 = 0xFFFFFFFFu;
    *out2 = 0xFFFFFFFFu;
    return 1;
}
// FUNCTION: DAO 0x00A29E50
void* __thiscall C00629e50::fn_00629e50()
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p + 0x21) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x25) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x29) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x2d) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x31) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x35) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x39) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x3d) = 0;
    return this;
}
// FUNCTION: DAO 0x00A29F60
unsigned int __thiscall C00629f60::fn_00629f60()
{
    return (*reinterpret_cast<unsigned char*>(reinterpret_cast<unsigned char*>(this) + 0x21) != 0) ? 1u : 0u;
}
// FUNCTION: DAO 0x00A29F70
unsigned char __thiscall C00629f70::fn_00629f70()
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this) + 0x21;
    unsigned char i = 0;
    while (i < 0x20 && p[i] != 0) {
        ++i;
    }
    return i;
}
// FUNCTION: DAO 0x00A29FE0
unsigned int __thiscall C00629fe0::fn_00629fe0(const void* other)
{
    const unsigned char* a = reinterpret_cast<const unsigned char*>(this) + 0x21;
    const unsigned char* b = reinterpret_cast<const unsigned char*>(other) + 0x21;
    for (unsigned int i = 0; i < 0x20; ++i) {
        if (a[i] != b[i]) {
            return 0;
        }
    }
    return 1;
}
// FUNCTION: DAO 0x00A2A3F0
void* __thiscall C0062a3f0::fn_0062a3f0(void* a, void* b, void* c)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<void**>(p) = a;
    *reinterpret_cast<void**>(p + 4) = b;
    *reinterpret_cast<void**>(p + 8) = c;
    return this;
}
// FUNCTION: DAO 0x00A2A5E0
void __thiscall C0062a5e0::fn_0062a5e0(void** out, void* value)
{
    out[0] = this;
    out[1] = value;
}
// FUNCTION: DAO 0x00A2CFF0
void* __thiscall C0062cff0::fn_0062cff0()
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(p) = 0;
    *reinterpret_cast<unsigned int*>(p + 4) = 0;
    *reinterpret_cast<unsigned int*>(p + 8) = 0;
    *reinterpret_cast<unsigned int*>(p + 0xc) = 0;
    *reinterpret_cast<unsigned int*>(p + 0x10) = 0;
    return this;
}
// FUNCTION: DAO 0x00A2D110
unsigned int* __thiscall C0062d110::fn_0062d110(int index, unsigned int value)
{
    unsigned int* result = reinterpret_cast<unsigned int*>(index);
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    if (index >= 0 && *reinterpret_cast<unsigned int*>(p + 0x14) != 0) {
        unsigned int* types = *reinterpret_cast<unsigned int**>(p + 0xc);
        if (types[index] == 3) {
            unsigned int* values = *reinterpret_cast<unsigned int**>(p + 0x10);
            values[index] += value;
            result = values + index;
        }
    }
    return result;
}
// FUNCTION: DAO 0x00A2D140
unsigned int __thiscall C0062d140::fn_0062d140(unsigned int* out)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    int count = *reinterpret_cast<int*>(p + 0x1750) - 1;
    *reinterpret_cast<int*>(p + 0x1750) = count;
    if (count < 0) {
        *reinterpret_cast<int*>(p + 0x1750) = 0;
        return 0;
    }
    *out = *reinterpret_cast<unsigned int*>(p + 0x175c + count * 4);
    return 1;
}
// FUNCTION: DAO 0x00A2D180
unsigned int __thiscall C0062d180::fn_0062d180(unsigned int value)
{
    unsigned char* p = reinterpret_cast<unsigned char*>(this);
    int count = *reinterpret_cast<int*>(p + 0x1750);
    *reinterpret_cast<unsigned int*>(p + 0x175c + count * 4) = value;
    count = count + 1;
    *reinterpret_cast<int*>(p + 0x1750) = count;
    return (count < 0x80) ? 1u : 0u;
}