// FUNCTION: DAO 0x702610
void __cdecl fn_00302610(unsigned int* first, unsigned int* last, unsigned int* destEnd)
{
    while (last != first)
    {
        last -= 5;
        destEnd -= 5;
        destEnd[0] = last[0];
        destEnd[1] = last[1];
        destEnd[2] = last[2];
        destEnd[3] = last[3];
        destEnd[4] = last[4];
    }
}

// FUNCTION: DAO 0x706470
unsigned int* __cdecl fn_00306470(unsigned int* first, unsigned int* last, const unsigned int* value)
{
    while (first != last)
    {
        if (first[0] == value[0] && first[1] == value[1] && first[2] == value[2])
            return first;
        first += 3;
    }
    return first;
}

struct Point0030A9B0 { int x; int y; };
struct Rect0030A9B0 { int x; int y; int w; int h; bool fn_0030a9b0(Point0030A9B0*, int, int); };

// FUNCTION: DAO 0x70A9B0
bool __thiscall Rect0030A9B0::fn_0030a9b0(Point0030A9B0* p, int mx, int my)
{
    int px = p->x;
    if (px < x + mx) return false;
    if (px >= x + w - mx) return false;
    int py = p->y;
    if (py < y + my) return false;
    if (py >= y + h - my) return false;
    return true;
}

class C003199D0 { public: void* fn_003199d0(unsigned int); };

// FUNCTION: DAO 0x7199D0
void* __thiscall C003199D0::fn_003199d0(unsigned int index)
{
    if (index - 1u < 4u)
        return reinterpret_cast<char*>(this) + 0x140u + index * 16u;
    return reinterpret_cast<char*>(this) + 0x150u;
}

class C00319AE0 { public: void fn_00319ae0(int); };

// FUNCTION: DAO 0x719AE0
void __thiscall C00319AE0::fn_00319ae0(int value)
{
    char* self = reinterpret_cast<char*>(this);
    unsigned int* obj = *reinterpret_cast<unsigned int**>(self + 0x1b4);
    if (!obj) return;
    if (value == *reinterpret_cast<int*>(reinterpret_cast<char*>(obj) + 0x1b0)) return;
    if (value >= 5) return;
    *reinterpret_cast<int*>(reinterpret_cast<char*>(obj) + 0x1b0) = value;
    unsigned int* obj2 = *reinterpret_cast<unsigned int**>(self + 0x1b4);
    *reinterpret_cast<unsigned char*>(reinterpret_cast<char*>(obj2) + 0x2c) = 1;
}

// FUNCTION: DAO 0x71F8B0
int __stdcall fn_0031f8b0(const unsigned char* s)
{
    unsigned int cap = *reinterpret_cast<const unsigned int*>(s + 0x18);
    const unsigned short* buf;
    if (cap < 8u)
        buf = reinterpret_cast<const unsigned short*>(s + 4);
    else
        buf = *reinterpret_cast<const unsigned short* const*>(s + 4);
    unsigned int len = *reinterpret_cast<const unsigned int*>(s + 0x14);
    int count = 0;
    unsigned int limit = len - 1u;
    if (limit != 0u)
    {
        for (unsigned int i = 0; i < limit; ++i)
        {
            if (buf[i] == 0x0du && buf[i + 1] == 0x0au)
                ++count;
        }
    }
    return count;
}

class C0033C5E0 { public: unsigned int fn_0033c5e0() const; };

// FUNCTION: DAO 0x73C5E0
unsigned int __thiscall C0033C5E0::fn_0033c5e0() const
{
    return *reinterpret_cast<const unsigned int*>(reinterpret_cast<const char*>(this) + 0x2c8);
}

class C0033C600 { public: unsigned int fn_0033c600() const; };

// FUNCTION: DAO 0x73C600
unsigned int __thiscall C0033C600::fn_0033c600() const
{
    unsigned int* p = *reinterpret_cast<unsigned int* const*>(reinterpret_cast<const char*>(this) + 0x2dc);
    unsigned int q = *p;
    if (q == 0u) return 0u;
    return *reinterpret_cast<unsigned char*>(reinterpret_cast<unsigned char*>(q) + 2u);
}

class C0033D6E0 { public: bool fn_0033d6e0() const; };

// FUNCTION: DAO 0x73D6E0
bool __thiscall C0033D6E0::fn_0033d6e0() const
{
    const unsigned char* p = *reinterpret_cast<const unsigned char* const*>(reinterpret_cast<const char*>(this) + 0x14);
    if (!p) return false;
    if (*p != 0) return true;
    const unsigned char* begin = *reinterpret_cast<const unsigned char* const*>(p + 0x18);
    if (!begin) return false;
    const unsigned char* end = *reinterpret_cast<const unsigned char* const*>(p + 0x1c);
    int diff = static_cast<int>(end - begin);
    return (diff >> 2) != 0;
}

class C00340CC0 { public: int fn_00340cc0(unsigned int) const; };

// FUNCTION: DAO 0x740CC0
int __thiscall C00340CC0::fn_00340cc0(unsigned int index) const
{
    const char* self = reinterpret_cast<const char*>(this);
    const char* begin = *reinterpret_cast<const char* const*>(self + 4);
    if (!begin) return -1;
    const char* end = *reinterpret_cast<const char* const*>(self + 8);
    int signedCount = static_cast<int>(end - begin) / 12;
    unsigned int count = static_cast<unsigned int>(signedCount);
    if (index >= count) return -1;
    const unsigned int* p = reinterpret_cast<const unsigned int*>(begin + index * 12u);
    return static_cast<int>(*p);
}

class C00342120 { public: void* fn_00342120(); };

// FUNCTION: DAO 0x742120
void* __thiscall C00342120::fn_00342120()
{
    char* p = reinterpret_cast<char*>(this);
    *reinterpret_cast<unsigned int*>(p + 0x00) = 0u;
    *reinterpret_cast<unsigned char*>(p + 0x04) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x08) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x0c) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x10) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x14) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x18) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x1c) = 0u;
    return this;
}

class C00352C70 { public: unsigned int fn_00352c70() const; };
class C00352C80 { public: bool fn_00352c80() const; };
class C00352D60 { public: bool fn_00352d60(unsigned int) const; };

// FUNCTION: DAO 0x752C70
unsigned int __thiscall C00352C70::fn_00352c70() const
{
    return *reinterpret_cast<const unsigned int*>(reinterpret_cast<const char*>(this) + 0x6e0);
}

// FUNCTION: DAO 0x752C80
bool __thiscall C00352C80::fn_00352c80() const
{
    return *reinterpret_cast<const unsigned int*>(reinterpret_cast<const char*>(this) + 0x6e4) != 0u;
}

// FUNCTION: DAO 0x752D60
bool __thiscall C00352D60::fn_00352d60(unsigned int value) const
{
    return value == *reinterpret_cast<const unsigned int*>(reinterpret_cast<const char*>(this) + 0x6d8);
}

// FUNCTION: DAO 0x75BC70
bool __stdcall fn_0035bc70(const unsigned int* bits, unsigned int bit)
{
    unsigned int word = bit >> 5;
    if (word > 3u) return false;
    unsigned int mask = 1u << (bit & 0x1fu);
    return (bits[word] & mask) != 0u;
}

class C00365360 { public: void* fn_00365360(); };

// FUNCTION: DAO 0x765360
void* __thiscall C00365360::fn_00365360()
{
    char* p = reinterpret_cast<char*>(this);
    *reinterpret_cast<unsigned int*>(p + 0x00) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x04) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x08) = 0u;
    *reinterpret_cast<unsigned char*>(p + 0x10) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x18) = 1u;
    *reinterpret_cast<unsigned int*>(p + 0x14) = 1u;
    *reinterpret_cast<unsigned int*>(p + 0x24) = 0xffffffffu;
    *reinterpret_cast<unsigned int*>(p + 0x28) = 1u;
    *reinterpret_cast<unsigned int*>(p + 0x2c) = 0u;
    *reinterpret_cast<unsigned int*>(p + 0x30) = 0xffffffffu;
    return this;
}
