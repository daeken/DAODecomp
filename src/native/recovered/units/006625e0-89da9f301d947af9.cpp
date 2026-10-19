struct C_00658310_Node {
    C_00658310_Node* next;
    char pad_0004[0x29];
    unsigned char field_2d;
};

struct C_006625e0_Sub {
    char pad_0000[0x88];
    int field_88;
};

struct C_006625e0 {
    int fn_006625e0() const;
    char pad_0000[0x14];
    C_006625e0_Sub* field_14;
};

// FUNCTION: DAO 0x00a53ba0
void __cdecl fn_00653ba0(unsigned int* begin, unsigned int* end1, unsigned int* end2) {
    while (end1 != begin) {
        end1 -= 4;
        end2 -= 4;
        unsigned int t;
        t = end1[1];
        end1[1] = end2[1];
        end2[1] = t;
        t = end1[2];
        end1[2] = end2[2];
        end2[2] = t;
        t = end1[3];
        end1[3] = end2[3];
        end2[3] = t;
    }
}

// FUNCTION: DAO 0x00a58310
C_00658310_Node* __cdecl fn_00658310(C_00658310_Node** p) {
    C_00658310_Node* node = *p;
    C_00658310_Node* prev;
    while (node->field_2d == 0) {
        prev = node;
        node = node->next;
    }
    return prev;
}

// FUNCTION: DAO 0x00a625e0
int __thiscall C_006625e0::fn_006625e0() const {
    C_006625e0_Sub* p = field_14;
    int r = 0;
    if (p != 0) {
        r = p->field_88;
    }
    return r;
}
