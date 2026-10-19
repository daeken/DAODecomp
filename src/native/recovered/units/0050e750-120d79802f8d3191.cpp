// FUNCTION: DAO 0x907B53
unsigned int __fastcall fn_00507b53(unsigned int unused, unsigned int value)
{
    unsigned int result = 0;
    if (value & 0x10u) result |= 0x80u;
    if (value & 0x8u) result |= 0x200u;
    if (value & 0x4u) result |= 0x400u;
    if (value & 0x2u) result |= 0x800u;
    if (value & 0x1u) result |= 0x1000u;
    if (value & 0x80000u) result |= 0x100u;
    unsigned int field = value & 0x300u;
    if (field == 0x100u) result |= 0x2000u;
    else if (field == 0x200u) result |= 0x4000u;
    else if (field == 0x300u) result |= 0x6000u;
    unsigned int high = value & 0x3000000u;
    if (high == 0x1000000u) result |= 0x8040u;
    else if (high == 0x2000000u) result |= 0x40u;
    else if (high == 0x3000000u) result |= 0x8000u;
    return result;
}

// FUNCTION: DAO 0x90E750
unsigned int __stdcall fn_0050e750(unsigned int value)
{
    if (value <= 0x7Fu) return 1u;
    if (value <= 0x7FFu) return 2u;
    if (value <= 0xFFFFu) return 3u;
    if (value <= 0x1FFFFFu) return 4u;
    if (value <= 0x3FFFFFFu) return 5u;
    if (value <= 0x7FFFFFFFu) return 6u;
    return 0u;
}

// FUNCTION: DAO 0x97B6A0
unsigned int fn_0057b6a0(unsigned int value)
{
    value = (value & 0x55555555u) + ((value >> 1) & 0x55555555u);
    value = (value & 0x33333333u) + ((value >> 2) & 0x33333333u);
    value = (value & 0x0F0F0F0Fu) + ((value >> 4) & 0x0F0F0F0Fu);
    return value % 255u;
}

// FUNCTION: DAO 0x9F70C0
int fn_005f70c0(int value)
{
    if (value <= 0) return 5000;
    if (value > 100) return 0;
    if (value >= 50) return 2 * (100 - value);
    return 5000 / value;
}

// FUNCTION: DAO 0xA418C0
unsigned int __stdcall fn_006418c0(unsigned int a, unsigned int b, unsigned int c)
{
    if (a <= b) {
        if (b < c) return 1u;
        if (c < a) return 1u;
    }
    if (b >= c) return 0u;
    if (c >= a) return 0u;
    return 1u;
}

// FUNCTION: DAO 0xA53670
unsigned int __stdcall fn_00653670(unsigned int value)
{
    return ((value >> 16) & 0xFu) + ((value & 0xFu) << 4);
}

// FUNCTION: DAO 0xAD5410
void __cdecl fn_006d5410(void)
{
}

// FUNCTION: DAO 0xAD54E0
void __cdecl fn_006d54e0(void)
{
}

// FUNCTION: DAO 0xAD5D10
void __cdecl fn_006d5d10(void)
{
}

// FUNCTION: DAO 0xAD5D20
void __cdecl fn_006d5d20(void)
{
}
