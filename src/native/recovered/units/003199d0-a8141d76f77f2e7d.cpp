// FUNCTION: DAO 0x702610
void __cdecl fn_00302610(unsigned int* first, unsigned int* last, unsigned int* destEnd)
{
    while (first != last)
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

class C003199D0 { public: void* fn_003199d0(unsigned int); };

// FUNCTION: DAO 0x7199D0
void* __thiscall C003199D0::fn_003199d0(unsigned int index)
{
    unsigned int i = index - 1u;
    if (i < 4u)
        return reinterpret_cast<char*>(this) + (i + 0x15u) * 16u;
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
    *reinterpret_cast<unsigned char*>(reinterpret_cast<char*>(*reinterpret_cast<unsigned int**>(self + 0x1b4)) + 0x2c) = 1;
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
    unsigned int i = 0;
    if (limit != 0u)
    {
        do
        {
            if (buf[i] == 0x0du && buf[i + 1] == 0x0au)
                ++count;
            ++i;
        } while (i < limit);
    }
    return count;
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

class C0033D6E0 { public: int fn_0033d6e0() const; };

// FUNCTION: DAO 0x73D6E0
int __thiscall C0033D6E0::fn_0033d6e0() const
{
    int result = 0;
    const unsigned char* p = *reinterpret_cast<const unsigned char* const*>(reinterpret_cast<const char*>(this) + 0x14);
    if (p != 0)
    {
        if (*p != 0)
        {
            result = 1;
        }
        else
        {
            const unsigned char* begin = *reinterpret_cast<const unsigned char* const*>(p + 0x18);
            if (begin != 0)
            {
                const unsigned char* end = *reinterpret_cast<const unsigned char* const*>(p + 0x1c);
                if (((end - begin) >> 2) != 0)
                    result = 1;
            }
        }
    }
    return result;
}

class C00340CC0 { public: int fn_00340cc0(unsigned int) const; };

// FUNCTION: DAO 0x740CC0
int __thiscall C00340CC0::fn_00340cc0(unsigned int index) const
{
    int result = -1;
    const char* self = reinterpret_cast<const char*>(this);
    const char* begin = *reinterpret_cast<const char* const*>(self + 4);
    if (begin != 0)
    {
        const char* end = *reinterpret_cast<const char* const*>(self + 8);
        int count = static_cast<int>(end - begin) / 12;
        if (index < static_cast<unsigned int>(count))
        {
            const char* current = *reinterpret_cast<const char* const*>(self + 4);
            result = *reinterpret_cast<const int*>(current + index * 12u);
        }
    }
    return result;
}
