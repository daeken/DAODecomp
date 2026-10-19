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

// FUNCTION: DAO 0xA3BA80
unsigned int __thiscall GridLookupA::fn_0063ba80(unsigned short a, unsigned short b) {
    if (b == 0xffffu) {
        b = a;
    }
    int n = field20;
    int i = (int)a;
    if (i >= n) {
        return 0;
    }
    int j = (int)b;
    if (j >= n) {
        return 0;
    }
    return field24[i * 5][j];
}

// FUNCTION: DAO 0xA3BAC0
unsigned int __thiscall GridLookupB::fn_0063bac0(int index) {
    if (index < field20) {
        if (index >= 0) {
            return field24[index * 5 + 4];
        }
    }
    return 0;
}

// FUNCTION: DAO 0xA3D270
int __thiscall ChunkParserObj::fn_0063d270(unsigned char** pptr, unsigned int* out) {
    unsigned char* p = *pptr;
    unsigned int off = field8;
    int result = 0;
    if (p[off] == 0x69u) {
        unsigned int v = (unsigned int)p[off + 2];
        v += ((unsigned int)(int)(signed char)p[off + 1]) << 8;
        v <<= 8;
        v += (unsigned int)p[off + 3];
        v <<= 8;
        v += (unsigned int)p[off + 4];
        *out = v;
        *pptr += 5;
        result = 1;
    }
    return result;
}

// FUNCTION: DAO 0xA3D4C0
int __thiscall SortedArrayObj::fn_0063d4c0(int value, int exact) {
    int count = field68;
    int step = count >> 1;
    int index = 0;
    while (index < count) {
        int lower = (field74[index] <= value);
        int upper;
        if (index < count - 1) {
            upper = (field74[index + 1] > value);
        } else {
            upper = 1;
        }
        if (lower == 1 && upper == 1) {
            if (exact == 1) {
                if (field74[index] != value) {
                    return -1;
                }
            }
            return index;
        }
        if (upper == 0) {
            index += step;
        } else if (lower == 0) {
            index -= step;
        }
        step >>= 1;
        if (step < 1) {
            step = 1;
        }
        if (index < 0) {
            return 0;
        }
    }
    if (index < 0) {
        return 0;
    }
    return count - 1;
}
