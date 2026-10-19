struct S_00520a40 {
    unsigned char pad0[0xcc];
    unsigned int* p;
    unsigned int __thiscall fn_00520a40();
};

struct S_00522930 {
    unsigned char pad0[0x14];
    unsigned char* base;
    unsigned int count;
    void* __thiscall fn_00522930(void* p);
};

struct S_00522d90 {
    unsigned char pad0[8];
    unsigned int a;
    unsigned int b;
    unsigned int c;
    unsigned int __thiscall fn_00522d90(void* p);
};

struct S_00522fa0 {
    unsigned char pad0[8];
    unsigned int a;
    unsigned int b;
    unsigned char pad1[0xc];
    unsigned int d;
    int __thiscall fn_00522fa0();
};

struct S_00522fc0 {
    unsigned char pad0[4];
    unsigned int value;
    unsigned char pad1[4];
    unsigned char flags;
    void __thiscall fn_00522fc0(unsigned int* out);
};

struct S_00523000 {
    unsigned char pad0[8];
    unsigned int value;
    unsigned char flags;
    void __thiscall fn_00523000(unsigned int* out);
};

struct S_0052a9b0 {
    void* __thiscall fn_0052a9b0(unsigned int idx);
};

struct S_0052ddb0 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int f1c;
    S_0052ddb0* __thiscall fn_0052ddb0(void** param);
};

struct S_0052f920 {
    unsigned char* s;
    bool __thiscall fn_0052f920(void* p);
};

struct S_0052f970 {
    unsigned char* s;
    bool __thiscall fn_0052f970(void* p);
};

struct S_0052f9f0 {
    unsigned char c;
    bool __thiscall fn_0052f9f0(void* p);
};

struct S_0052fa20 {
    unsigned char c;
    bool __thiscall fn_0052fa20();
};

struct S_00590b50 {
    unsigned char pad0[0x14d];
    unsigned char flags1;
    unsigned char flags2;
    void __thiscall fn_00590b50();
};

struct S_00590b70 {
    unsigned char pad0[0x14d];
    unsigned char flags1;
    unsigned char flags2;
    void __thiscall fn_00590b70();
};

struct S_00590b90 {
    unsigned char pad0[0x14d];
    unsigned char flags1;
    unsigned char flags2;
    void __thiscall fn_00590b90();
};

struct S_00598770 {
    unsigned char pad0[0x64];
    unsigned short w;
    void __thiscall fn_00598770(unsigned int, unsigned int, unsigned int flags);
};

// FUNCTION: DAO 0x920A40
unsigned int __thiscall S_00520a40::fn_00520a40() {
    unsigned int* q = p;
    if (q != 0 && *q != 0) return 1;
    return 0;
}

// FUNCTION: DAO 0x922930
void* __thiscall S_00522930::fn_00522930(void* p) {
    int idx = (int)((unsigned int)p - (unsigned int)base) >> 4;
    unsigned int next = (unsigned int)idx + 1;
    if (next >= count) return 0;
    unsigned int off = (unsigned int)idx << 4;
    if (*(unsigned int*)(base + off + 0x14) != *(unsigned int*)((unsigned char*)p + 4)) return 0;
    return base + off + 0x10;
}

// FUNCTION: DAO 0x922D90
unsigned int __thiscall S_00522d90::fn_00522d90(void* p) {
    unsigned int* q = (unsigned int*)p;
    if (a == q[0] && b == q[1] && c == q[2]) return 1;
    return 0;
}

// FUNCTION: DAO 0x922FA0
int __thiscall S_00522fa0::fn_00522fa0() {
    int diff = (int)a - (int)b;
    diff >>= 4;
    unsigned int x = (d - 1) << 5;
    return diff + (int)x;
}

// FUNCTION: DAO 0x922FC0
void __thiscall S_00522fc0::fn_00522fc0(unsigned int* out) {
    if (flags & 0x10) {
        *out = value;
    } else {
        *out = 0;
    }
}

// FUNCTION: DAO 0x923000
void __thiscall S_00523000::fn_00523000(unsigned int* out) {
    if (flags & 0x20) {
        *out = value;
    } else {
        *out = 0;
    }
}

// FUNCTION: DAO 0x92A9B0
void* __thiscall S_0052a9b0::fn_0052a9b0(unsigned int idx) {
    if (idx >= 4) return 0;
    return (unsigned char*)this + idx * 0x30 + 0x8f8;
}

// FUNCTION: DAO 0x92DDB0
S_0052ddb0* __thiscall S_0052ddb0::fn_0052ddb0(void** param) {
    unsigned char* p = (unsigned char*)*param;
    unsigned int* q = *(unsigned int**)(p + 0x10);
    f4 = (unsigned int)q;
    ++*(unsigned int*)((unsigned char*)q + 0xc);
    f8 = 0;
    fc = 0;
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f1c = 0;
    f0 = 0xff000000;
    return this;
}

// FUNCTION: DAO 0x92F920
bool __thiscall S_0052f920::fn_0052f920(void* p) {
    const unsigned char* a = s;
    const unsigned char* b = *(const unsigned char**)p;
    while (*a == *b) {
        if (*a == 0) return false;
        ++a;
        ++b;
    }
    return *a < *b;
}

// FUNCTION: DAO 0x92F970
bool __thiscall S_0052f970::fn_0052f970(void* p) {
    const unsigned char* a = s;
    const unsigned char* b = *(const unsigned char**)p;
    while (*a == *b) {
        if (*a == 0) return false;
        ++a;
        ++b;
    }
    return *a > *b;
}

// FUNCTION: DAO 0x92F9F0
bool __thiscall S_0052f9f0::fn_0052f9f0(void* p) {
    unsigned char a = c;
    unsigned char b = *(unsigned char*)p;
    if (a == b) return true;
    if ((a == 3 || a == 4) && (b == 3 || b == 4)) return true;
    return false;
}

// FUNCTION: DAO 0x92FA20
bool __thiscall S_0052fa20::fn_0052fa20() {
    return c == 8 || c == 0xb;
}

// FUNCTION: DAO 0x990B50
void __thiscall S_00590b50::fn_00590b50() {
    if ((flags1 & 2) == 0) {
        unsigned char v = flags1 | 2;
        flags2 |= 2;
        flags1 = v;
    }
}

// FUNCTION: DAO 0x990B70
void __thiscall S_00590b70::fn_00590b70() {
    if ((flags1 & 8) == 0) {
        unsigned char v = flags1 | 8;
        flags2 |= 2;
        flags1 = v;
    }
}

// FUNCTION: DAO 0x990B90
void __thiscall S_00590b90::fn_00590b90() {
    if (flags1 & 8) {
        unsigned char v = flags1 & 0xf7;
        flags2 |= 2;
        flags1 = v;
    }
}

// FUNCTION: DAO 0x998770
void __thiscall S_00598770::fn_00598770(unsigned int, unsigned int, unsigned int flags) {
    if (flags & 1) return;
    unsigned short v = w;
    if ((v & 2) == 0) return;
    if ((v & 0x20) == 0) return;
    w = v & 0xffdf;
}
