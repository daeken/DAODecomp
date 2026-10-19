struct C_0064e580 {
    int fn_0064e580();
    char pad_0000[0x30];
    int field_30;
    int field_34;
};
struct C_0064e5b0 {
    int fn_0064e5b0(int);
    char pad_0000[0x30];
    int field_30;
};
struct C_006581f0 {
    int fn_006581f0(unsigned int);
    char pad_0000[0x14];
    unsigned char field_14;
};
struct C_00658310_Node {
    C_00658310_Node* next;
    char pad_0004[0x29];
    unsigned char field_2d;
};
struct C_0065c830 {
    int fn_0065c830() const;
    char pad_0000[0x14];
    int field_14;
};
struct C_0065c9d0 {
    int fn_0065c9d0() const;
    char pad_0000[0x1ac];
    int field_1ac;
};
struct C_0065cab0 {
    int fn_0065cab0(unsigned int) const;
    char pad_0000[0x158];
    unsigned int field_158;
};
struct C_0065cb10 {
    int fn_0065cb10() const;
    char pad_0000[0x15c];
    int field_15c;
};
struct C_0065d640_Sub {
    char pad_0000[0xb4];
    int field_b4;
};
struct C_0065d640 {
    void fn_0065d640(int);
    char pad_0000[0x18];
    C_0065d640_Sub* field_18;
    char pad_001c[0x134];
    int field_150;
};
struct C_006625e0_Sub {
    char pad_0000[0x88];
    int field_88;
};
struct C_006625e0 {
    int fn_006625e0() const;
    void fn_006625f0(int);
    char pad_0000[0x14];
    C_006625e0_Sub* field_14;
};
struct C_00662810 {
    void fn_00662810(unsigned char, unsigned int);
    void fn_00662820(unsigned char, unsigned int);
    char pad_0000[0x9c];
    unsigned char field_9c;
    unsigned char field_9d;
};
struct C_006630e0_Sub {
    char pad_0000[0x70];
    unsigned char field_70;
};
struct C_006630e0 {
    unsigned char fn_006630e0() const;
    char pad_0000[0x70];
    C_006630e0_Sub* field_70;
    unsigned char field_74;
    unsigned char field_75;
    unsigned char field_76;
};

// FUNCTION: DAO 0x00a4e580
int __thiscall C_0064e580::fn_0064e580() {
    int a = field_34 - 1;
    int b = field_30;
    return (a / 2) * ((b + 1) / 2) + ((b - 1) / 2) + 1;
}

// FUNCTION: DAO 0x00a4e5b0
int __thiscall C_0064e5b0::fn_0064e5b0(int value) {
    int n = field_30;
    int q = value / n;
    int r = value % n;
    return ((n + 1) / 2) * (q / 2) + (r / 2);
}

// FUNCTION: DAO 0x00a4ec70
void __cdecl fn_0064ec70(unsigned int* dst, unsigned int* end, const unsigned int* src) {
    while (dst != end) {
        dst[0] = src[0];
        dst[1] = src[1];
        dst[2] = src[2];
        dst[3] = src[3];
        dst += 4;
    }
}

// FUNCTION: DAO 0x00a53ba0
void __cdecl fn_00653ba0(unsigned int* begin, unsigned int* end1, unsigned int* end2) {
    if (begin == end1) {
        return;
    }
    do {
        unsigned int v1 = end1[-3];
        unsigned int v2 = end2[-3];
        end1 -= 4;
        end2 -= 4;
        end2[1] = v1;
        end1[1] = v2;
        unsigned int v3 = end1[2];
        unsigned int v4 = end2[2];
        end2[2] = v3;
        end1[2] = v4;
        unsigned int v5 = end1[3];
        unsigned int v6 = end2[3];
        end2[3] = v5;
        end1[3] = v6;
    } while (end1 != begin);
}

// FUNCTION: DAO 0x00a581f0
int __thiscall C_006581f0::fn_006581f0(unsigned int value) {
    unsigned int shift = (unsigned int)field_14 - 1u;
    return ((1u << shift) & value) != 0;
}

// FUNCTION: DAO 0x00a58310
void __cdecl fn_00658310(C_00658310_Node** p) {
    C_00658310_Node* node = *p;
    while (node->field_2d == 0) {
        node = node->next;
    }
}

// FUNCTION: DAO 0x00a5c830
int __thiscall C_0065c830::fn_0065c830() const {
    return field_14 != 0;
}

// FUNCTION: DAO 0x00a5c9d0
int __thiscall C_0065c9d0::fn_0065c9d0() const {
    return field_1ac != 0;
}

// FUNCTION: DAO 0x00a5cab0
int __thiscall C_0065cab0::fn_0065cab0(unsigned int bit) const {
    unsigned int mask = 1u << bit;
    return (field_158 & mask) != 0;
}

// FUNCTION: DAO 0x00a5cb10
int __thiscall C_0065cb10::fn_0065cb10() const {
    return field_15c | 2;
}

// FUNCTION: DAO 0x00a5d640
void __thiscall C_0065d640::fn_0065d640(int value) {
    field_150 = value;
    C_0065d640_Sub* p = field_18;
    if (p != 0) {
        p->field_b4 = value;
    }
}

// FUNCTION: DAO 0x00a625e0
int __thiscall C_006625e0::fn_006625e0() const {
    C_006625e0_Sub* p = field_14;
    if (p != 0) {
        return p->field_88;
    }
    return 0;
}

// FUNCTION: DAO 0x00a625f0
void __thiscall C_006625e0::fn_006625f0(int value) {
    C_006625e0_Sub* p = field_14;
    if (p != 0) {
        p->field_88 = value;
    }
}

// FUNCTION: DAO 0x00a62810
void __thiscall C_00662810::fn_00662810(unsigned char value, unsigned int) {
    field_9d = value;
}

// FUNCTION: DAO 0x00a62820
void __thiscall C_00662810::fn_00662820(unsigned char value, unsigned int) {
    field_9c = value;
}

// FUNCTION: DAO 0x00a630e0
unsigned char __thiscall C_006630e0::fn_006630e0() const {
    if (field_75 == 0) {
        return 0;
    }
    unsigned char result = field_76;
    C_006630e0_Sub* p = field_70;
    if (p != 0 && field_74 != 0) {
        result |= p->field_70;
    }
    return result;
}
