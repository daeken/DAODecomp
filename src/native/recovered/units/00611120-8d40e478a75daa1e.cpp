typedef unsigned int u32;
typedef unsigned __int64 u64;
typedef __int64 i64;

union U64Parts {
    u64 u;
    i64 i;
    struct {
        u32 lo;
        u32 hi;
    } p;
};

// FUNCTION: DAO 0x903680
i64 __stdcall fn_00503680(u32 dlo, u32 dhi, u32 vlo, u32 vhi)
{
    int negq = 0;
    if ((int)dhi < 0) {
        negq ^= 1;
        u32 old = dlo;
        dlo = 0u - dlo;
        dhi = 0u - dhi - (old != 0u ? 1u : 0u);
    }
    if ((int)vhi < 0) {
        negq ^= 1;
        u32 old = vlo;
        vlo = 0u - vlo;
        vhi = 0u - vhi - (old != 0u ? 1u : 0u);
    }

    u32 qlo = 0u;
    u32 qhi = 0u;
    u32 rlo = 0u;
    u32 rhi = 0u;
    int i;
    for (i = 63; i >= 0; --i) {
        u32 next_hi = (rhi << 1) | (rlo >> 31);
        u32 next_lo = rlo << 1;
        if (i >= 32) {
            next_lo |= (dhi >> (i - 32)) & 1u;
        } else {
            next_lo |= (dlo >> i) & 1u;
        }
        rhi = next_hi;
        rlo = next_lo;

        if (rhi > vhi || (rhi == vhi && rlo >= vlo)) {
            u32 old_rlo = rlo;
            rlo = rlo - vlo;
            rhi = rhi - vhi - (old_rlo < vlo ? 1u : 0u);
            if (i >= 32) {
                qhi |= 1u << (i - 32);
            } else {
                qlo |= 1u << i;
            }
        }
    }

    if (negq) {
        u32 old_qlo = qlo;
        qlo = 0u - qlo;
        qhi = 0u - qhi - (old_qlo != 0u ? 1u : 0u);
    }

    U64Parts out;
    out.p.lo = qlo;
    out.p.hi = qhi;
    return out.i;
}

// FUNCTION: DAO 0x907AC5
u32 __cdecl fn_00507ac5(u32 ebx)
{
    u32 eax = 0u;
    if (ebx & 0x10u) ++eax;
    if (ebx & 0x08u) eax |= 0x04u;
    if (ebx & 0x04u) eax |= 0x08u;
    if (ebx & 0x02u) eax |= 0x10u;
    if (ebx & 0x01u) eax |= 0x20u;
    if (ebx & 0x80000u) eax |= 0x02u;
    u32 ecx = ebx & 0x300u;
    if (ecx != 0u) {
        if (ecx == 0x100u) eax |= 0x400u;
        else if (ecx == 0x200u) eax |= 0x800u;
        else if (ecx == 0x300u) eax |= 0xC00u;
    }
    ecx = ebx & 0x30000u;
    if (ecx == 0u) eax |= 0x300u;
    else if (ecx == 0x10000u) eax |= 0x200u;
    if (ebx & 0x40000u) eax |= 0x1000u;
    return eax;
}

// FUNCTION: DAO 0xA026D0
int __cdecl fn_006026d0(int ecx, int esi)
{
    u32 acc = (u32)ecx * 0xffu;
    int t = esi + (esi < 0 ? 1 : 0);
    acc += (u32)(t >> 1);
    return ((int)acc) / esi;
}

// FUNCTION: DAO 0xA11120
u32 __cdecl fn_00611120(void)
{
    return 4u;
}

// FUNCTION: DAO 0xA21F90
int __stdcall fn_00621f90(int, int)
{
    return 0;
}

// FUNCTION: DAO 0xA38B60
u32 __cdecl fn_00638b60(u32 p)
{
    return p + 0x14u;
}

// FUNCTION: DAO 0xA38B70
u32 __cdecl fn_00638b70(u32 p)
{
    return p + 0x10u;
}
