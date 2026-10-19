// FUNCTION: DAO 0x0041D4A0
bool __fastcall fn_0001d4a0(int year) {
    return ((year % 4) == 0 && (year % 100) != 0) || ((year % 400) == 0);
}

// FUNCTION: DAO 0x00448410
int __fastcall fn_00048410(int code, int status) {
    if (status >= 0) {
        return status;
    }
    switch (code) {
    case 0x2733: return 0;
    case 0x03e5: return 0;
    case 0x2743: return -5;
    case 0x2751: return -5;
    case 0x2749: return -2;
    case 0x274d: return -6;
    case 0x2726: return -11;
    case 0x2746: return -13;
    default: return -7;
    }
}

// FUNCTION: DAO 0x00474710
unsigned int __stdcall fn_00074710(unsigned int tag) {
    switch (tag) {
    case 0x47414d45: return 0x474d4f52;
    case 0x43484152: return 0x434d4f52;
    case 0x45555453: return 0x454d4f52;
    case 0x48445752: return 0x484d4f52;
    case 0x4f4e474d: return 0x4f4d4f52;
    default: return 0x554d4f52;
    }
}

// FUNCTION: DAO 0x004E2060
unsigned char __stdcall fn_000e2060(unsigned char value) {
    return value;
}

// FUNCTION: DAO 0x0053AD20
bool __cdecl fn_0013ad20(unsigned int a, unsigned int b, unsigned int c) {
    return (a & b) != (a & c);
}

// FUNCTION: DAO 0x005D4540
int __stdcall fn_001d4540(int, int, int, int) {
    return 1;
}

// FUNCTION: DAO 0x006D27D0
int __stdcall fn_002d27d0(int, int, int, int) {
    return 0;
}

// FUNCTION: DAO 0x008F2410
unsigned __int64 __stdcall fn_004f2410(unsigned __int64 dividend, unsigned __int64 divisor) {
    unsigned int dlo = (unsigned int)dividend;
    unsigned int dhi = (unsigned int)(dividend >> 32);
    unsigned int vlo = (unsigned int)divisor;
    unsigned int vhi = (unsigned int)(divisor >> 32);
    unsigned int qlo = 0;
    unsigned int qhi = 0;
    unsigned int rlo = 0;
    unsigned int rhi = 0;
    int i;
    for (i = 63; i >= 0; --i) {
        unsigned int bit;
        unsigned int old_rlo;
        rhi = (rhi << 1) | (rlo >> 31);
        if (i >= 32) {
            bit = (dhi >> (i - 32)) & 1u;
        } else {
            bit = (dlo >> i) & 1u;
        }
        rlo = (rlo << 1) | bit;
        if ((rhi > vhi) || (rhi == vhi && rlo >= vlo)) {
            old_rlo = rlo;
            rlo -= vlo;
            rhi = rhi - vhi - (old_rlo < vlo ? 1u : 0u);
            if (i >= 32) {
                qhi |= 1u << (i - 32);
            } else {
                qlo |= 1u << i;
            }
        }
    }
    return ((unsigned __int64)qhi << 32) | (unsigned __int64)qlo;
}
