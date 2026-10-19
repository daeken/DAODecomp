// FUNCTION: DAO 0x00A4BAA0
int __stdcall fn_0064baa0(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6)
{
    unsigned int d46 = a4 - a6;
    unsigned int d35 = a3 - a5;
    unsigned int d24 = a2 - a4;
    unsigned int d13 = a1 - a3;
    unsigned int d26 = a2 - a6;
    unsigned int d15 = a1 - a5;
    unsigned int lhs = d46 * d46;
    lhs += d35 * d35;
    lhs += d24 * d24;
    lhs += d13 * d13;
    unsigned int rhs = d26 * d26;
    rhs += d15 * d15;
    return ((int)lhs < (int)rhs) ? 1 : 0;
}

// FUNCTION: DAO 0x00A66470
unsigned int __cdecl fn_00666470(unsigned int bit)
{
    if (bit < 0x14u)
        return 1u << bit;
    return 0xFFu;
}

// FUNCTION: DAO 0x00A66490
unsigned int __cdecl fn_00666490(unsigned int mask)
{
    unsigned int i;
    for (i = 0; i < 0x14u; ++i) {
        if (mask & (1u << i))
            return i;
    }
    return 0xFFu;
}

// FUNCTION: DAO 0x00AD5D30
void __cdecl fn_006d5d30(void)
{
}

// FUNCTION: DAO 0x00AD5E70
void __cdecl fn_006d5e70(void)
{
}

// FUNCTION: DAO 0x00AD8AB0
void __cdecl fn_006d8ab0(void)
{
}

// FUNCTION: DAO 0x00AD8AC0
void __cdecl fn_006d8ac0(void)
{
}

// FUNCTION: DAO 0x00AD8BF0
void __cdecl fn_006d8bf0(void)
{
}

// FUNCTION: DAO 0x00AD8C70
void __cdecl fn_006d8c70(void)
{
}

// FUNCTION: DAO 0x00AD9290
void __cdecl fn_006d9290(void)
{
}

// FUNCTION: DAO 0x00AD9300
void __cdecl fn_006d9300(void)
{
}

// FUNCTION: DAO 0x00AD93B0
void __cdecl fn_006d93b0(void)
{
}
