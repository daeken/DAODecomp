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
    unsigned int* field_1a8;
    unsigned int* field_1ac;
    unsigned char pad1[0xa4];
    unsigned int field_254;
    bool fn_0028d020(unsigned int index);
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

struct S_69e300 {
    unsigned char pad0[0x1c];
    unsigned char field_1c;
};

struct C_69e310 {
    S_69e300* field_0;
    unsigned char fn_0029e310();
};

// FUNCTION: DAO 0x67A8F0
NodeA* fn_0027a8f0(NodeA* p) {
    NodeA* cur = p->next;
    if (cur->field_25 != 0)
        return p;
    do {
        cur = (p = cur)->next;
    } while (cur->field_25 == 0);
    return p;
}

// FUNCTION: DAO 0x67B4D0
bool C_67b4d0::fn_0027b4d0() {
    return field_658 && field_658->field_7c == 1;
}

// FUNCTION: DAO 0x67BA00
NodeB* C_67ba00::fn_0027ba00(const KeyB* key) {
    NodeB* eax = field_4;
    NodeB* ecx = eax->field_4;
    if (ecx->field_25 != 0)
        return eax;
    unsigned int keyHigh = key->high;
loop:
    unsigned int edx = ecx->field_10;
    if (edx < keyHigh)
        goto L_left;
    if (edx != keyHigh)
        goto L_right;
    edx = ecx->field_c;
    if (edx >= key->low)
        goto L_right;
L_left:
    ecx = ecx->field_8;
    goto L_test;
L_right:
    eax = ecx;
    ecx = ecx->field_0;
L_test:
    if (ecx->field_25 == 0)
        goto loop;
    return eax;
}

// FUNCTION: DAO 0x689A40
void fn_00289a40(const Elem20* first, const Elem20* last, Elem20* dest) {
    while (first != last) {
        *dest = *first;
        ++first;
        ++dest;
    }
}

// FUNCTION: DAO 0x68D020
bool C_68d020::fn_0028d020(unsigned int index) {
    unsigned int* begin = field_1a8;
    if (begin == 0)
        return false;
    unsigned int* end = field_1ac;
    int count = (int)(end - begin) >> 2;
    if ((unsigned int)count > index) {
        field_254 = index;
        return true;
    }
    return false;
}

// FUNCTION: DAO 0x6956B0
void* C_6956b0::fn_002956b0() {
    S_6956b0* p = field_154;
    return p ? p->field_13c : 0;
}

// FUNCTION: DAO 0x695700
void* C_695700::fn_00295700() {
    S_695700* p = field_154;
    return p ? p->field_140 : 0;
}

// FUNCTION: DAO 0x69E310
unsigned char C_69e310::fn_0029e310() {
    S_69e300* p = field_0;
    return p ? p->field_1c : 0;
}
