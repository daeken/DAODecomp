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

// FUNCTION: DAO 0x67A8F0
NodeA* fn_0027a8f0(NodeA* p) {
    while (p->next->field_25 == 0)
        p = p->next;
    return p;
}

// FUNCTION: DAO 0x67B4D0
bool C_67b4d0::fn_0027b4d0() {
    bool result = false;
    if (field_658 != 0)
        result = (field_658->field_7c == 1);
    return result;
}

// FUNCTION: DAO 0x67BA00
NodeB* C_67ba00::fn_0027ba00(const KeyB* key) {
    NodeB* res = field_4;
    NodeB* cur = res->field_4;
    if (cur->field_25 != 0)
        return res;
    unsigned int keyHigh = key->high;
    do {
        unsigned int high = cur->field_10;
        if (high >= keyHigh) {
            if (high != keyHigh) {
                res = cur;
                cur = cur->field_0;
            } else {
                unsigned int low = cur->field_c;
                if (low < key->low) {
                    cur = cur->field_8;
                } else {
                    res = cur;
                    cur = cur->field_0;
                }
            }
        } else {
            cur = cur->field_8;
        }
    } while (cur->field_25 == 0);
    return res;
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
    unsigned char* begin = field_1a8;
    if (begin == 0)
        return false;
    unsigned char* end = field_1ac;
    int count = (int)(end - begin) >> 2;
    if ((unsigned int)count > index) {
        field_254 = index;
        return true;
    }
    return false;
}
