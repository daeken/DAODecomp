extern "C" {

// FUNCTION: DAO 0x44A3E0
unsigned short __cdecl fn_0004a3e0(unsigned short value)
{
    return (unsigned short)((value >> 8) | (value << 8));
}

// FUNCTION: DAO 0x44A410
unsigned short __cdecl fn_0004a410(unsigned short value)
{
    return (unsigned short)((value >> 8) | (value << 8));
}

// FUNCTION: DAO 0x44A430
unsigned int __cdecl fn_0004a430(unsigned int value)
{
    return (value >> 24) | ((value >> 8) & 0x0000FF00u) | ((value << 8) & 0x00FF0000u) | (value << 24);
}

// FUNCTION: DAO 0x48D0A0
void __stdcall fn_0008d0a0(unsigned int a, unsigned int b, unsigned int c)
{
    (void)a;
    (void)b;
    (void)c;
}

// FUNCTION: DAO 0x8E53D0
__int64 __stdcall fn_004e53d0(__int64 a, __int64 b)
{
    unsigned int alo = (unsigned int)a;
    unsigned int ahi = (unsigned int)((unsigned __int64)a >> 32);
    unsigned int blo = (unsigned int)b;
    unsigned int bhi = (unsigned int)((unsigned __int64)b >> 32);

    if (a < 0) {
        unsigned int old = alo;
        alo = ~alo + 1u;
        ahi = ~ahi + (old == 0u ? 1u : 0u);
    }
    if (b < 0) {
        unsigned int old = blo;
        blo = ~blo + 1u;
        bhi = ~bhi + (old == 0u ? 1u : 0u);
    }

    unsigned int qlo = 0u;
    unsigned int qhi = 0u;
    unsigned int rlo = 0u;
    unsigned int rhi = 0u;
    int i;
    for (i = 63; i >= 0; --i) {
        rhi = (rhi << 1) | (rlo >> 31);
        rlo = rlo << 1;
        if (i >= 32) {
            rlo |= (ahi >> (i - 32)) & 1u;
        } else {
            rlo |= (alo >> i) & 1u;
        }
        if (rhi > bhi || (rhi == bhi && rlo >= blo)) {
            unsigned int old = rlo;
            rlo = rlo - blo;
            rhi = rhi - bhi - (old < blo ? 1u : 0u);
            if (i >= 32) {
                qhi |= 1u << (i - 32);
            } else {
                qlo |= 1u << i;
            }
        }
    }

    if ((a < 0) != (b < 0)) {
        unsigned int old = qlo;
        qlo = ~qlo + 1u;
        qhi = ~qhi + (old == 0u ? 1u : 0u);
    }

    return (__int64)(((unsigned __int64)qhi << 32) | (unsigned __int64)qlo);
}

// FUNCTION: DAO 0x8F6360
__int64 __stdcall fn_004f6360(__int64 a, __int64 b)
{
    unsigned int nlo = (unsigned int)a;
    unsigned int nhi = (unsigned int)((unsigned __int64)a >> 32);
    unsigned int dlo = (unsigned int)b;
    unsigned int dhi = (unsigned int)((unsigned __int64)b >> 32);
    int neg = (a < 0);

    if (a < 0) {
        unsigned int old = nlo;
        nlo = ~nlo + 1u;
        nhi = ~nhi + (old == 0u ? 1u : 0u);
    }
    if (b < 0) {
        unsigned int old = dlo;
        dlo = ~dlo + 1u;
        dhi = ~dhi + (old == 0u ? 1u : 0u);
    }

    unsigned int rlo = 0u;
    unsigned int rhi = 0u;
    int i;
    for (i = 63; i >= 0; --i) {
        rhi = (rhi << 1) | (rlo >> 31);
        rlo = rlo << 1;
        if (i >= 32) {
            rlo |= (nhi >> (i - 32)) & 1u;
        } else {
            rlo |= (nlo >> i) & 1u;
        }
        if (rhi > dhi || (rhi == dhi && rlo >= dlo)) {
            unsigned int old = rlo;
            rlo = rlo - dlo;
            rhi = rhi - dhi - (old < dlo ? 1u : 0u);
        }
    }

    if (neg) {
        unsigned int old = rlo;
        rlo = ~rlo + 1u;
        rhi = ~rhi + (old == 0u ? 1u : 0u);
    }

    return (__int64)(((unsigned __int64)rhi << 32) | (unsigned __int64)rlo);
}

}
