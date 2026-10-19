struct CrcTableBuilder {
    unsigned char pad0[0x48];
    unsigned int table[256];
    void __thiscall fn_00639560();
};

struct ShiftObj {
    unsigned char pad0[0x44];
    unsigned int field44;
    unsigned int field48;
    unsigned int field4c;
    unsigned int __thiscall fn_0063a340(unsigned int, unsigned int, unsigned int);
};

struct GridLookupA {
    unsigned char pad0[0x20];
    unsigned int field20;
    unsigned int** field24;
    unsigned int __thiscall fn_0063ba80(unsigned short, unsigned short);
};

struct GridLookupB {
    unsigned char pad0[0x20];
    unsigned int field20;
    unsigned int* field24;
    unsigned int __thiscall fn_0063bac0(int);
};

struct GridLookupC {
    unsigned char pad0[0x20];
    unsigned int field20;
    unsigned char* field24;
    unsigned int __thiscall fn_0063bae0(int, unsigned int);
};

struct DoublePtrObj {
    unsigned int* field0;
    unsigned int __thiscall fn_0063bb80();
};

struct ChunkParserObj {
    unsigned char pad0[8];
    unsigned int field8;
    int __thiscall fn_0063d270(unsigned char**, unsigned int*);
};

struct IntervalObj {
    unsigned char pad0[0x34];
    int field34;
    unsigned char pad_38[4];
    int* field3c;
    int* field40;
    int __thiscall fn_0063d490(int);
};

struct SortedArrayObj {
    unsigned char pad0[0x68];
    int field68;
    unsigned char pad_6c[8];
    int* field74;
    int __thiscall fn_0063d4c0(int, int);
};

struct FlagObj1 {
    unsigned char pad0[8];
    int field8;
    int __thiscall fn_006408e0(int);
};

struct FlagObj2 {
    unsigned char pad0[8];
    int field8;
    unsigned char pad_0c[0x18];
    int field24;
    int __thiscall fn_00640900(int);
};

struct RecordArrayObj {
    unsigned char pad0[0x30];
    unsigned int field30;
    unsigned char pad_34[8];
    unsigned char* field3c;
    int __thiscall fn_00640f10(unsigned int);
};

// FUNCTION: DAO 0xA39560
void __thiscall CrcTableBuilder::fn_00639560() {
    unsigned int edx = 0;
    while (edx < 0x100u) {
        unsigned int eax = edx;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        if (eax & 1u) eax = (eax >> 1) ^ 0xEDB88320u; else eax >>= 1;
        table[edx] = eax;
        ++edx;
    }
}

// FUNCTION: DAO 0xA3A340
unsigned int __thiscall ShiftObj::fn_0063a340(unsigned int a, unsigned int b, unsigned int c) {
    unsigned int shift = field44 + field4c;
    unsigned int r1 = a << shift;
    unsigned int r2 = b << field44;
    return r1 | r2 | c;
}

// FUNCTION: DAO 0xA3BA80
unsigned int __thiscall GridLookupA::fn_0063ba80(unsigned short a, unsigned short b) {
    if (b == 0xffffu) b = a;
    unsigned int i = a;
    unsigned int n = field20;
    if (i >= n) return 0;
    unsigned int j = b;
    if (j >= n) return 0;
    return field24[i * 5][j];
}

// FUNCTION: DAO 0xA3BAC0
unsigned int __thiscall GridLookupB::fn_0063bac0(int index) {
    if (index >= (int)field20) return 0;
    if (index < 0) return 0;
    return field24[(unsigned int)index * 5 + 4];
}

// FUNCTION: DAO 0xA3BAE0
unsigned int __thiscall GridLookupC::fn_0063bae0(int index, unsigned int sub) {
    if (index < 0) return 0;
    if ((unsigned int)index >= field20) return 0;
    if (sub > 1u) return 0;
    unsigned char* p = field24 + (unsigned int)index * 20u;
    return (unsigned int)*(unsigned short*)(p + sub * 6u + 4u);
}

// FUNCTION: DAO 0xA3BB80
unsigned int __thiscall DoublePtrObj::fn_0063bb80() {
    return *field0;
}

// FUNCTION: DAO 0xA3D270
int __thiscall ChunkParserObj::fn_0063d270(unsigned char** pptr, unsigned int* out) {
    unsigned char* p = *pptr;
    unsigned int off = field8;
    if (p[off] != 0x69u) return 0;
    unsigned int v = (unsigned int)p[off + 2u];
    v += ((unsigned int)(int)(signed char)p[off + 1u]) << 8;
    v <<= 8;
    v += (unsigned int)p[off + 3u];
    v <<= 8;
    v += (unsigned int)p[off + 4u];
    *out = v;
    *pptr += 5;
    return 1;
}

// FUNCTION: DAO 0xA3D420
unsigned char* __stdcall fn_0063d420(unsigned char* base, unsigned int end, unsigned int start, unsigned int* out, int flag) {
    unsigned int i = start;
    unsigned char* p = base + i;
    while (i < end) {
        unsigned char c = *p;
        if (c == 0x0au || c == 0x0du) break;
        ++i;
        ++p;
    }
    if (flag == 1 && i < end) {
        unsigned char c = *p;
        if (c == 0x0au) {
            ++i;
            ++p;
            if (i < end && *p == 0x0du) {
                ++p;
                ++i;
            }
        } else if (c == 0x0du) {
            ++i;
            ++p;
            if (i < end && *p == 0x0au) {
                ++p;
                ++i;
            }
        }
    }
    *out = i;
    return p;
}

// FUNCTION: DAO 0xA3D490
int __thiscall IntervalObj::fn_0063d490(int value) {
    int n = field34;
    for (int i = 0; i < n; ++i) {
        if (value >= field3c[i] && value < field40[i]) return i;
    }
    return -1;
}

// FUNCTION: DAO 0xA3D4C0
int __thiscall SortedArrayObj::fn_0063d4c0(int value, int exact) {
    int n = field68;
    if (n <= 0) return n - 1;
    if (field74[0] > value) return 0;
    int idx = 0;
    while (idx + 1 < n && field74[idx + 1] <= value) ++idx;
    if (exact == 1 && field74[idx] != value) return -1;
    return idx;
}

// FUNCTION: DAO 0xA408E0
int __thiscall FlagObj1::fn_006408e0(int arg) {
    if (arg == 1 && field8 == -1) return 1;
    return 0;
}

// FUNCTION: DAO 0xA40900
int __thiscall FlagObj2::fn_00640900(int arg) {
    if (arg == 1 && field8 != -1) return field24;
    return -1;
}

// FUNCTION: DAO 0xA40F10
int __thiscall RecordArrayObj::fn_00640f10(unsigned int index) {
    if (index >= field30) return -1;
    unsigned char* p = field3c + index * 16u;
    return (int)*(unsigned short*)(p + 2u);
}
