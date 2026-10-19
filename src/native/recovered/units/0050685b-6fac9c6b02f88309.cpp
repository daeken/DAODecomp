// FUNCTION: DAO 0x8e9a80
unsigned __int64 __cdecl fn_004e9a80(unsigned __int64 dividend, unsigned __int64 divisor) {
    unsigned int a0 = (unsigned int)dividend;
    unsigned int a1 = (unsigned int)(dividend >> 32);
    unsigned int b0 = (unsigned int)divisor;
    unsigned int b1 = (unsigned int)(divisor >> 32);
    unsigned int r0 = 0;
    unsigned int r1 = 0;
    for (int i = 63; i >= 0; --i) {
        unsigned int bit = (i >= 32) ? (a1 >> (i - 32)) : (a0 >> i);
        r1 = (r1 << 1) | (r0 >> 31);
        r0 = (r0 << 1) | (bit & 1u);
        if (r1 > b1 || (r1 == b1 && r0 >= b0)) {
            unsigned int old_r0 = r0;
            r0 -= b0;
            r1 -= b1 + ((old_r0 < b0) ? 1u : 0u);
        }
    }
    return ((unsigned __int64)r1 << 32) | (unsigned __int64)r0;
}

// FUNCTION: DAO 0x8e9af5
int __cdecl fn_004e9af5(unsigned int lo, unsigned int hi) {
    unsigned int hw = (hi >> 16) & 0x7ff8u;
    if (hw == 0x7ff0u) {
        if ((hi & 0x7ffffu) != 0u || lo != 0u) {
            return 1;
        }
    }
    if (hw == 0x7ff8u) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x8ef765
int __cdecl fn_004ef765(unsigned int code) {
    if (code == 0x3a4u) return 0x411;
    if (code == 0x3a8u) return 0x804;
    if (code == 0x3b5u) return 0x412;
    if (code == 0x3b6u) return 0x404;
    return 0;
}

// FUNCTION: DAO 0x8ff692
int __cdecl fn_004ff692(unsigned int lo, unsigned int hi) {
    if (hi == 0x7ff00000u && lo == 0u) return 1;
    if (hi == 0xfff00000u && lo == 0u) return 2;
    unsigned int hw = (hi >> 16) & 0x7ff8u;
    if (hw == 0x7ff8u) return 3;
    if (hw == 0x7ff0u) {
        if ((hi & 0x7ffffu) != 0u || lo != 0u) return 4;
    }
    return 0;
}

// FUNCTION: DAO 0x8ffca0
int __cdecl fn_004ffca0(unsigned char code) {
    if ((code & 0x20u) != 0u) return 5;
    if ((code & 0x08u) != 0u) return 1;
    if ((code & 0x04u) != 0u) return 2;
    if ((code & 0x01u) != 0u) return 3;
    return ((code & 0x02u) != 0u) ? 4 : 0;
}

// FUNCTION: DAO 0x9030cf
int __cdecl fn_005030cf(void* p, unsigned int size) {
    (void)size;
    return (p != 0) ? 1 : 0;
}

// FUNCTION: DAO 0x90685b
int __cdecl fn_0050685b(void) {
    return 0;
}

// FUNCTION: DAO 0x90ee90
unsigned int __cdecl fn_0050ee90(unsigned int value) {
    return value + value;
}

// FUNCTION: DAO 0x91fc50
char __stdcall fn_0051fc50(void* p) {
    (void)p;
    return 0;
}

// FUNCTION: DAO 0x9ff150
int __cdecl fn_005ff150(void* a, void* b, int c) {
    (void)a;
    (void)b;
    return c;
}

// FUNCTION: DAO 0xa09f70
int __cdecl fn_00609f70(void) {
    return 0x6ae;
}

// FUNCTION: DAO 0xa09f80
int __cdecl fn_00609f80(void) {
    return 0x3e8;
}

// FUNCTION: DAO 0xa0dc30
bool __fastcall fn_0060dc30(void* self, int unused_edx, void* other) {
    (void)unused_edx;
    return self == other;
}
