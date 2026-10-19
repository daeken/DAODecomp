// FUNCTION: DAO 0x00821520
unsigned char __stdcall fn_00421520(const unsigned int* a, const unsigned int* b) {
    if (a[0] != b[0] || a[1] != b[1] || a[2] != b[2] || a[3] != b[3]) {
        return 0;
    }
    return 1;
}

// FUNCTION: DAO 0x00822AD0
void __cdecl fn_00422ad0(unsigned int* src, unsigned int* end, unsigned int* dst) {
    while (src != end) {
        if (dst != 0) {
            dst[0] = src[0];
            dst[1] = src[1];
            dst[2] = src[2];
            dst[3] = src[3];
        }
        src += 4;
        dst += 4;
    }
}

// FUNCTION: DAO 0x00837670
unsigned int __cdecl fn_00437670(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) {
        return 0;
    }
    return (v == 1) ? 1u : 2u;
}
