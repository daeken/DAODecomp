struct NodeA {
    NodeA* next;
    unsigned char pad0[0x21];
    unsigned char field_25;
};

struct C_67b4d0_Sub {
    unsigned char pad0[0x7c];
    unsigned int field_7c;
};

struct C_67b4d0 {
    unsigned char pad0[0x658];
    C_67b4d0_Sub* field_658;
    bool fn_0027b4d0();
};

struct NodeB {
    NodeB* field_0;
    NodeB* field_4;
    NodeB* field_8;
    unsigned int field_c;
    unsigned int field_10;
    unsigned char pad14[0x11];
    unsigned char field_25;
};

struct KeyB {
    unsigned int low;
    unsigned int high;
};

struct C_67ba00 {
    unsigned char pad0[4];
    NodeB* field_4;
    NodeB* fn_0027ba00(const KeyB* key);
};

struct Elem20 {
    unsigned int f0;
    unsigned int f1;
    unsigned int f2;
    unsigned int f3;
    unsigned int f4;
};

struct C_68d020 {
    unsigned char pad0[0x1a8];
    unsigned char* field_1a8;
    unsigned char* field_1ac;
    unsigned char pad1[0xa4];
    unsigned int field_254;
    bool fn_0028d020(unsigned int index);
};

struct C_694e10 {
    unsigned char pad0[0x42d];
    unsigned char field_42d;
    void fn_00294e10(unsigned char value);
};

struct C_6951c0 {
    unsigned char pad0[0x23c];
    unsigned char field_23c;
    unsigned char fn_002951c0() const;
};

struct S_6956b0 {
    unsigned char pad0[0x13c];
    void* field_13c;
};

struct C_6956b0 {
    unsigned char pad0[0x154];
    S_6956b0* field_154;
    void* fn_002956b0();
};

struct S_695700 {
    unsigned char pad0[0x140];
    void* field_140;
};

struct C_695700 {
    unsigned char pad0[0x154];
    S_695700* field_154;
    void* fn_00295700();
};

struct C_695970 {
    unsigned char pad0[0x250];
    unsigned char field_250;
    void fn_00295970();
};

struct C_695c00 {
    unsigned char pad0[0x18d];
    unsigned char field_18d;
    unsigned char pad1[0x3a];
    unsigned int field_1c8;
    void fn_00295c00(unsigned char value);
};

struct C_699fe0 {
    unsigned char pad0[0x2c0];
    unsigned int field_2c0;
    void fn_00299fe0(unsigned int value);
};

struct S_69e300 {
    unsigned char pad0[0x1c];
    unsigned char field_1c;
};

struct C_69e300 {
    S_69e300* field_0;
    void fn_0029e300(unsigned char value);
};

struct C_69e310 {
    S_69e300* field_0;
    unsigned char fn_0029e310();
};

struct C_69e480 {
    unsigned char pad0[0x7d4];
    unsigned char field_7d4;
    void fn_0029e480(unsigned char value);
};

struct C_69ee60 {
    unsigned char pad0[0xb40];
    unsigned char field_b40;
    unsigned char field_b41;
    void fn_0029ee60(unsigned char value);
};

// FUNCTION: DAO 0x67A8F0
NodeA* fn_0027a8f0(NodeA* p) {
    NodeA* cur = p->next;
    if (cur->field_25 != 0)
        return p;
    do {
        p = cur;
        cur = p->next;
    } while (cur->field_25 == 0);
    return p;
}

// FUNCTION: DAO 0x67B4D0
bool C_67b4d0::fn_0027b4d0() {
    if (field_658 == 0)
        return false;
    return field_658->field_7c == 1;
}

// FUNCTION: DAO 0x67BA00
NodeB* C_67ba00::fn_0027ba00(const KeyB* key) {
    NodeB* eax = field_4;
    NodeB* ecx = eax->field_4;
    if (ecx->field_25 != 0)
        return eax;
    unsigned int keyHigh = key->high;
    do {
        unsigned int edx = ecx->field_10;
        if (edx < keyHigh) {
            ecx = ecx->field_8;
        } else if (edx != keyHigh) {
            eax = ecx;
            ecx = ecx->field_0;
        } else {
            edx = ecx->field_c;
            if (edx >= key->low) {
                eax = ecx;
                ecx = ecx->field_0;
            } else {
                ecx = ecx->field_8;
            }
        }
    } while (ecx->field_25 == 0);
    return eax;
}

// FUNCTION: DAO 0x689A40
void fn_00289a40(const Elem20* first, const Elem20* last, Elem20* dest) {
    while (first != last) {
        dest->f0 = first->f0;
        dest->f1 = first->f1;
        dest->f2 = first->f2;
        dest->f3 = first->f3;
        dest->f4 = first->f4;
        ++first;
        ++dest;
    }
}

// FUNCTION: DAO 0x68D020
bool C_68d020::fn_0028d020(unsigned int index) {
    if (field_1a8 == 0)
        return false;
    int count = (int)(field_1ac - field_1a8) >> 2;
    if ((unsigned int)count > index) {
        field_254 = index;
        return true;
    }
    return false;
}

// FUNCTION: DAO 0x694E10
void C_694e10::fn_00294e10(unsigned char value) {
    field_42d = value;
}

// FUNCTION: DAO 0x6951C0
unsigned char C_6951c0::fn_002951c0() const {
    return field_23c;
}

// FUNCTION: DAO 0x6956B0
void* C_6956b0::fn_002956b0() {
    S_6956b0* p = field_154;
    if (p == 0)
        return 0;
    return p->field_13c;
}

// FUNCTION: DAO 0x695700
void* C_695700::fn_00295700() {
    S_695700* p = field_154;
    if (p == 0)
        return 0;
    return p->field_140;
}

// FUNCTION: DAO 0x695970
void C_695970::fn_00295970() {
    field_250 = 0;
}

// FUNCTION: DAO 0x695C00
void C_695c00::fn_00295c00(unsigned char value) {
    if (this == 0 || field_1c8 != 1)
        field_18d = value;
}

// FUNCTION: DAO 0x699FE0
void C_699fe0::fn_00299fe0(unsigned int value) {
    field_2c0 = value;
}

// FUNCTION: DAO 0x69E300
void C_69e300::fn_0029e300(unsigned char value) {
    S_69e300* p = field_0;
    if (p != 0)
        p->field_1c = value;
}

// FUNCTION: DAO 0x69E310
unsigned char C_69e310::fn_0029e310() {
    S_69e300* p = field_0;
    if (p == 0)
        return 0;
    return p->field_1c;
}

// FUNCTION: DAO 0x69E480
void C_69e480::fn_0029e480(unsigned char value) {
    field_7d4 = value;
}

// FUNCTION: DAO 0x69EE60
void C_69ee60::fn_0029ee60(unsigned char value) {
    field_b40 = 1;
    field_b41 = value;
}
