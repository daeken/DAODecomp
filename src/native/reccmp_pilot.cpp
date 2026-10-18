// FUNCTION: DAO 0x00620910
unsigned int __stdcall fn_00220910(unsigned int value)
{
    if (value == 2u)
        return 5u;
    if (value == 1u)
        return 6u;
    return (value != 0u) ? 0u : 7u;
}

// FUNCTION: DAO 0x0075BCA0
unsigned int __stdcall fn_0035bca0(unsigned int value)
{
    return value == 14u ? 1u : 0u;
}

// FUNCTION: DAO 0x0087A080
unsigned int __stdcall fn_0047a080(unsigned int a, unsigned int b, unsigned int c, unsigned int d)
{
    if (b <= 4u)
        return a * c;
    return d >> 4;
}

// FUNCTION: DAO 0x00880630
unsigned int __cdecl fn_00480630(unsigned int value)
{
    if (value == 0x0cu || value == 0x0du || value == 0x0eu || value == 0x0fu ||
        value == 0x10u || value == 0x11u || value == 0x12u || value == 0x13u)
        return 1u;
    return 0u;
}
