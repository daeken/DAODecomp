// FUNCTION: DAO 0x00413770
int __cdecl fn_00013770(void)
{
    return 0x7fffffff;
}

// FUNCTION: DAO 0x004137B0
int __cdecl fn_000137b0(void)
{
    return 0;
}

// FUNCTION: DAO 0x004137C0
bool __cdecl fn_000137c0(void)
{
    return true;
}

// FUNCTION: DAO 0x004137D0
bool __stdcall fn_000137d0(unsigned int, unsigned int, unsigned int)
{
    return false;
}

// FUNCTION: DAO 0x0041CB20
void __stdcall fn_0001cb20(unsigned int, unsigned int, unsigned int, unsigned int, unsigned int)
{
}

// FUNCTION: DAO 0x0041CE70
int __fastcall fn_0001ce70(int a, int b, int c)
{
    (void)b;
    (void)c;
    return a;
}

// FUNCTION: DAO 0x00455850
void __stdcall fn_00055850(unsigned int)
{
}

// FUNCTION: DAO 0x004E13D0
int __cdecl fn_000e13d0(void)
{
    return -1;
}

// FUNCTION: DAO 0x005BDCF0
void __cdecl fn_001bdcf0(void)
{
}

// FUNCTION: DAO 0x005C5E80
bool __cdecl fn_001c5e80(void)
{
    return false;
}

// FUNCTION: DAO 0x0067A170
bool __stdcall fn_0027a170(unsigned int a, unsigned int b, unsigned int c)
{
    if (a == 0 || a == 1) {
        if (b == 1) {
            if (c == 0) {
                return (a == 0 || a == 1);
            } else if (c == 1) {
                return a == 1;
            }
        } else if (b == 0) {
            if (c == 0) {
                return a == 0;
            }
        }
    }
    return false;
}

// FUNCTION: DAO 0x00702510
unsigned char __stdcall fn_00302510(unsigned int code)
{
    if (code == 0x31495653) return 1;
    if (code == 0x31465653) return 2;
    if (code == 0x31535653) return 3;
    if (code == 0x314F5653) return 4;
    return code == 0x31525653 ? 12 : 0;
}

// FUNCTION: DAO 0x0079AF30
int __fastcall fn_0039af30(int a)
{
    return a;
}

// FUNCTION: DAO 0x008E5A20
unsigned __int64 __stdcall fn_004e5a20(unsigned __int64 a, unsigned __int64 b)
{
    unsigned int a_lo = (unsigned int)a;
    unsigned int a_hi = (unsigned int)(a >> 32);
    unsigned int b_lo = (unsigned int)b;
    unsigned int b_hi = (unsigned int)(b >> 32);

    if ((a_hi | b_hi) == 0) {
        return (unsigned __int64)a_lo * b_lo;
    }

    unsigned int low = a_lo * b_lo;
    unsigned int high = a_hi * b_lo;
    high += a_lo * b_hi;
    high += (unsigned int)(((unsigned __int64)a_lo * b_lo) >> 32);
    return ((unsigned __int64)high << 32) | low;
}

// FUNCTION: DAO 0x008E6EA1
int __cdecl fn_004e6ea1(int a, int b)
{
    int q = a / b;
    int r = a % b;
    if (a < 0 && r > 0) {
        ++q;
        r -= b;
    }
    return q;
}

// FUNCTION: DAO 0x008E8100
unsigned __int64 __stdcall fn_004e8100(unsigned __int64 dividend, unsigned __int64 divisor)
{
    unsigned int a_lo = (unsigned int)dividend;
    unsigned int a_hi = (unsigned int)(dividend >> 32);
    unsigned int b_lo = (unsigned int)divisor;
    unsigned int b_hi = (unsigned int)(divisor >> 32);

    if (b_hi == 0) {
        unsigned int q_hi = a_hi / b_lo;
        unsigned int rem = a_hi % b_lo;
        unsigned int q_lo = 0;
        unsigned __int64 r = rem;
        for (int i = 31; i >= 0; --i) {
            r = (r << 1) | ((a_lo >> i) & 1u);
            if (r >= (unsigned __int64)b_lo) {
                r -= (unsigned __int64)b_lo;
                q_lo |= (1u << i);
            }
        }
        return ((unsigned __int64)q_hi << 32) | q_lo;
    }

    unsigned int d_hi = b_hi;
    unsigned int d_lo = b_lo;
    unsigned int n_hi = a_hi;
    unsigned int n_lo = a_lo;
    while (d_hi != 0) {
        unsigned int carry_d = d_hi & 1u;
        d_hi >>= 1;
        d_lo = (d_lo >> 1) | (carry_d << 31);
        unsigned int carry_n = n_hi & 1u;
        n_hi >>= 1;
        n_lo = (n_lo >> 1) | (carry_n << 31);
    }

    unsigned int q = 0;
    unsigned __int64 rem64 = 0;
    for (int i = 63; i >= 0; --i) {
        unsigned int bit;
        if (i >= 32) {
            bit = (n_hi >> (i - 32)) & 1u;
        } else {
            bit = (n_lo >> i) & 1u;
        }
        rem64 = (rem64 << 1) | bit;
        if (rem64 >= (unsigned __int64)d_lo) {
            rem64 -= (unsigned __int64)d_lo;
            if (i < 32) {
                q |= (1u << i);
            }
        }
    }

    unsigned int prod_lo = q * b_lo;
    unsigned int base_hi = (unsigned int)(((unsigned __int64)q * b_lo) >> 32);
    unsigned int prod_hi = base_hi + q * b_hi;
    if (prod_hi < base_hi || prod_hi > a_hi || (prod_hi == a_hi && prod_lo > a_lo)) {
        --q;
    }
    return (unsigned __int64)q;
}
