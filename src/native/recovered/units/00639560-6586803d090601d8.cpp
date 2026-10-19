struct CrcTableBuilder {
    unsigned char pad0[0x48];
    unsigned int table[256];
    void __thiscall fn_00639560();
};

struct GridLookupA {
    unsigned char pad0[0x20];
    int field20;
    unsigned int** field24;
    unsigned int __thiscall fn_0063ba80(unsigned short a, unsigned short b);
};

struct GridLookupB {
    unsigned char pad0[0x20];
    int field20;
    unsigned int* field24;
    unsigned int __thiscall fn_0063bac0(int index);
};

struct GridLookupC {
    unsigned char pad0[0x20];
    int field20;
    unsigned char* field24;
    unsigned int __thiscall fn_0063bae0(int index, unsigned int sub);
};

struct ChunkParserObj {
    unsigned char pad0[8];
    unsigned int field8;
    int __thiscall fn_0063d270(unsigned char** pptr, unsigned int* out);
};

struct SortedArrayObj {
    unsigned char pad0[0x68];
    int field68;
    unsigned char pad_6c[8];
    int* field74;
    int __thiscall fn_0063d4c0(int value, int exact);
};

struct FlagObj1 {
    unsigned char pad0[8];
    int field8;
    int __thiscall fn_006408e0(int arg);
};

struct RecordArrayObj {
    unsigned char pad0[0x30];
    unsigned int field30;
    unsigned char pad_34[8];
    unsigned char* field3c;
    int __thiscall fn_00640f10(unsigned int index);
};

// FUNCTION: DAO 0xA39560
void __thiscall CrcTableBuilder::fn_00639560() {
    int edx = 0;
    while (edx < 0x100) {
        unsigned int eax = (unsigned int)edx;
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

// FUNCTION: DAO 0xA3BA80
unsigned int __thiscall GridLookupA::fn_0063ba80(unsigned short a, unsigned short b) {
    if (b == 0xffffu) b = a;
    int n = field20;
    int i = (int)a;
    if (i >= n) return 0;
    int j = (int)(unsigned short)b;
    if (j >= n) return 0;
    return field24[i * 5][j];
}

// FUNCTION: DAO 0xA3BAC0
unsigned int __thiscall GridLookupB::fn_0063bac0(int index) {
    int n = field20;
    if (index >= n) return 0;
    if (index < 0) return 0;
    return field24[(unsigned int)index * 5u + 4u];
}

// FUNCTION: DAO 0xA3BAE0
unsigned int __thiscall GridLookupC::fn_0063bae0(int index, unsigned int sub) {
    unsigned int result = 0;
    if (index >= 0 && index < field20 && sub <= 1u) {
        unsigned char* p = field24 + (unsigned int)index * 20u;
        result = (unsigned int)*(unsigned short*)(p + sub * 6u + 4u);
    }
    return result;
}

// FUNCTION: DAO 0xA3D270
int __thiscall ChunkParserObj::fn_0063d270(unsigned char** pptr, unsigned int* out) {
    unsigned char* p = *pptr;
    unsigned int off = field8;
    int result = 0;
    if (p[off] == 0x69u) {
        unsigned char* q = p + off;
        unsigned int v = (unsigned int)q[2];
        v += ((unsigned int)(int)(signed char)q[1]) << 8;
        v <<= 8;
        v += (unsigned int)q[3];
        v <<= 8;
        v += (unsigned int)q[4];
        *out = v;
        *pptr += 5;
        result = 1;
    }
    return result;
}

// FUNCTION: DAO 0xA3D4C0
int __thiscall SortedArrayObj::fn_0063d4c0(int value, int exact) {
    int n = field68;
    int step = n >> 1;
    int idx = 0;
    int n_minus_1 = (int)((unsigned int)n - 1u);
    while (idx < n) {
        int* arr = field74;
        int le = (arr[idx] <= value);
        int gt_next;
        if (idx < n_minus_1) {
            gt_next = (arr[idx + 1] > value);
        } else {
            gt_next = 1;
        }
        if (le == 1 && gt_next == 1) {
            if (exact == 1) {
                if (field74[idx] != value) return -1;
            }
            return idx;
        }
        if (gt_next == 0) {
            idx = (int)((unsigned int)idx + (unsigned int)step);
        } else if (le == 0) {
            idx = (int)((unsigned int)idx - (unsigned int)step);
        }
        step >>= 1;
        if (step < 1) step = 1;
        if (idx < 0) return 0;
    }
    return n_minus_1;
}

// FUNCTION: DAO 0xA408E0
int __thiscall FlagObj1::fn_006408e0(int arg) {
    if (arg == 1) {
        if (field8 != -1) return 1;
    }
    return 0;
}

// FUNCTION: DAO 0xA40F10
int __thiscall RecordArrayObj::fn_00640f10(unsigned int index) {
    if (index < field30) {
        unsigned char* p = field3c + index * 16u;
        return (int)*(unsigned short*)(p + 2u);
    }
    return -1;
}
