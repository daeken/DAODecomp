struct DAObj {
    unsigned int field_0;
    unsigned int field_4;
    unsigned int pad_8[3];
    int* field_14;
    int* field_18;
    unsigned int pad_1c[3];
    unsigned int field_28;
    unsigned int field_2c;
    unsigned int pad_30[1];
    unsigned int field_34;
    unsigned int pad_38[2];
    unsigned int field_40;
    unsigned int field_44;
    unsigned char pad_48[0xa0 - 0x48];
    unsigned int field_a0;
    unsigned int pad_a4[2];
    unsigned int field_ac;
    unsigned char pad_b0[0x134 - 0xb0];
    unsigned char pad_134[0x16c - 0x134];
    unsigned int field_16c;
    unsigned int pad_170[1];
    unsigned int field_174;
    unsigned char pad_178[0x2c0 - 0x178];
    unsigned int field_2c0;
    unsigned char pad_2c4[0x848 - 0x2c4];
    unsigned int field_848;

    void* fn_00154430();
    unsigned int fn_001552b0(unsigned int value);
    unsigned int fn_0015a360();
    unsigned int fn_0015cbd0();
    unsigned int fn_0015cbe0();
    unsigned int fn_0015dcf0();
    int fn_0015e140();
    void* fn_00160060();
    unsigned int fn_00160070();
    unsigned int fn_00162560();
    unsigned int fn_00162680();
    unsigned int fn_00162690();
    unsigned int fn_00444f90();
    unsigned int fn_00444fa0();
};

// FUNCTION: DAO 0x554430
void* DAObj::fn_00154430() {
    unsigned int* p = reinterpret_cast<unsigned int*>(this);
    p[0] = 0;
    p[1] = 0;
    return p;
}

// FUNCTION: DAO 0x5552B0
unsigned int DAObj::fn_001552b0(unsigned int value) {
    field_2c = value;
    return value;
}

// FUNCTION: DAO 0x556220
unsigned short* __cdecl fn_00156220(unsigned short* dst, unsigned int count, const unsigned short* src) {
    unsigned short* p = dst;
    unsigned int n = count;
    if (n != 0) {
        do {
            *p = *src;
            ++p;
            --n;
        } while (n != 0);
    }
    return dst + count;
}

// FUNCTION: DAO 0x55A360
unsigned int DAObj::fn_0015a360() {
    return field_174 + 0x130;
}

// FUNCTION: DAO 0x55CBD0
unsigned int DAObj::fn_0015cbd0() { return field_28; }

// FUNCTION: DAO 0x55CBE0
unsigned int DAObj::fn_0015cbe0() { return field_848; }

// FUNCTION: DAO 0x55DCF0
unsigned int DAObj::fn_0015dcf0() {
    unsigned int v = field_16c;
    if (v != 0) return v;
    return *reinterpret_cast<unsigned int*>(field_174 + 0x120);
}

// FUNCTION: DAO 0x55E140
int DAObj::fn_0015e140() {
    if (field_14 == 0) return 0;
    return field_18 - field_14;
}

// FUNCTION: DAO 0x560060
void* DAObj::fn_00160060() {
    return reinterpret_cast<void*>(reinterpret_cast<char*>(this) + 0x134);
}

// FUNCTION: DAO 0x560070
unsigned int DAObj::fn_00160070() { return field_2c0; }

// FUNCTION: DAO 0x562560
unsigned int DAObj::fn_00162560() {
    field_44 = 0;
    field_34 = 0;
    return 0;
}

// FUNCTION: DAO 0x562680
unsigned int DAObj::fn_00162680() { return field_44 * field_34; }

// FUNCTION: DAO 0x562690
unsigned int DAObj::fn_00162690() { return field_40 * field_34; }

// FUNCTION: DAO 0x844F90
unsigned int DAObj::fn_00444f90() { return field_ac; }

// FUNCTION: DAO 0x844FA0
unsigned int DAObj::fn_00444fa0() { return field_a0; }

// FUNCTION: DAO 0xA1FAD0
void __cdecl fn_0061fad0(int* widthPtr, int* heightPtr, unsigned char* data) {
    int w = *widthPtr;
    int h = *heightPtr;
    int nw = w >> 1;
    int nh = h >> 1;
    if (nw < 1) nw = 1;
    if (nh < 1) nh = 1;
    if (nw * 2 == w && nh * 2 == h) {
        unsigned char* outRow = data;
        for (int y = 0; y < nh; ++y) {
            unsigned char* row = data + (y * 2) * w;
            for (int x = 0; x < nw; ++x) {
                int sum = row[x * 2] + row[x * 2 + 1] + row[x * 2 + w] + row[x * 2 + w + 1];
                outRow[x] = static_cast<unsigned char>(sum >> 2);
            }
            outRow += nw;
        }
    }
    *widthPtr = nw;
    *heightPtr = nh;
}
