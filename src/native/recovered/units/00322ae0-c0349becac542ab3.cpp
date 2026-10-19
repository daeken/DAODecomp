// FUNCTION: DAO 0x00722AE0
bool __stdcall fn_00322ae0(unsigned int)
{
    return true;
}

// FUNCTION: DAO 0x00738C90
void __stdcall fn_00338c90(unsigned int, unsigned int)
{
}

// FUNCTION: DAO 0x007A2240
bool __stdcall fn_003a2240(unsigned int a, unsigned int b)
{
    if (a == 0)
        return false;
    return b != 0;
}

// FUNCTION: DAO 0x007A2260
bool __stdcall fn_003a2260(unsigned int a, unsigned int)
{
    return a != 0;
}

// FUNCTION: DAO 0x00821560
bool __stdcall fn_00421560(unsigned int, unsigned int)
{
    return true;
}

// FUNCTION: DAO 0x0083F740
unsigned int __fastcall fn_0043f740(unsigned int value, int count)
{
    unsigned int result = 0;
    do
    {
        result |= value & 1u;
        --count;
        value >>= 1;
        result += result;
    } while (count > 0);
    return result >> 1;
}

// FUNCTION: DAO 0x0084AEF0
bool __cdecl fn_0044aef0(unsigned int code)
{
    return code == 0 || code == 1 || code == 2 || code == 9;
}

// FUNCTION: DAO 0x0084B1B0
unsigned int __cdecl fn_0044b1b0(unsigned int value)
{
    unsigned int base = 2;
    unsigned int result = 1;
    if (value <= base)
        return result;
    do
    {
        base += base;
        result += result;
    } while (base < value);
    return result;
}

// FUNCTION: DAO 0x00862E70
unsigned int __cdecl fn_00462e70(void)
{
    return 0x778u;
}

// FUNCTION: DAO 0x00880670
bool __cdecl fn_00480670(unsigned int code)
{
    return code == 0 || code == 1 || code == 2 || code == 3 ||
           code == 4 || code == 5 || code == 6 || code == 7 ||
           code == 8 || code == 9 || code == 10 || code == 11 ||
           code == 12 || code == 13 || code == 14 || code == 15 ||
           code == 16 || code == 17 || code == 18 || code == 19 ||
           code == 20 || code == 21 || code == 22 || code == 23 ||
           code == 24 || code == 25 || code == 26 || code == 27 ||
           code == 28 || code == 29 || code == 30 || code == 31;
}

// FUNCTION: DAO 0x008B6520
char __fastcall fn_004b6520(char value)
{
    return value < 10 ? (char)(value + 0x30) : (char)(value + 0x37);
}

// FUNCTION: DAO 0x008B65E0
char __fastcall fn_004b65e0(char value)
{
    unsigned char digit = (unsigned char)(value - 0x30);
    unsigned char result = 0;
    if (digit <= 9)
        return (char)(value - 0x30);
    digit = (unsigned char)(value - 0x61);
    if (digit <= 5)
        return (char)(value - 0x57);
    digit = (unsigned char)(value - 0x41);
    if (digit <= 5)
        return (char)(value - 0x37);
    return (char)result;
}

// FUNCTION: DAO 0x008BC140
unsigned short __stdcall fn_004bc140(unsigned short value)
{
    return value;
}

// FUNCTION: DAO 0x008F404E
void __cdecl fn_004f404e(void)
{
}

// FUNCTION: DAO 0x008F5078
unsigned int __cdecl fn_004f5078(unsigned int, unsigned int high)
{
    unsigned int exponent = high & 0x7ff00000u;
    if (exponent == 0x7ff00000u)
        return high;
    return exponent;
}
