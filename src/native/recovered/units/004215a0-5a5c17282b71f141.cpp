struct Node_004215a0 {
    Node_004215a0* field0;
    Node_004215a0* field4;
    Node_004215a0* field8;
    unsigned int fieldC;
    unsigned char field10;
    unsigned char field11;
};

struct Tree_004215a0 {
    unsigned int pad0;
    Node_004215a0* field4;
    void fn_004215a0(Node_004215a0* x);
};

// FUNCTION: DAO 0x00821520
unsigned char __stdcall fn_00421520(const unsigned int* a, const unsigned int* b) {
    if (a[0] != b[0]) {
        return 0;
    }
    if (a[1] != b[1]) {
        return 0;
    }
    if (a[2] != b[2]) {
        return 0;
    }
    if (a[3] != b[3]) {
        return 0;
    }
    return 1;
}

// FUNCTION: DAO 0x008215A0
void Tree_004215a0::fn_004215a0(Node_004215a0* x) {
    Node_004215a0* p = x->field0;
    x->field0 = p->field8;
    if (p->field8->field11 == 0) {
        p->field8->field4 = x;
    }
    p->field4 = x->field4;
    if (x == field4->field4) {
        field4->field4 = p;
        p->field8 = x;
        x->field4 = p;
        return;
    }
    Node_004215a0* parent = x->field4;
    if (x == parent->field8) {
        parent->field8 = p;
        p->field8 = x;
        x->field4 = p;
        return;
    }
    parent->field0 = p;
    p->field8 = x;
    x->field4 = p;
}

// FUNCTION: DAO 0x00822AD0
void __cdecl fn_00422ad0(unsigned int* src, unsigned int* end, unsigned int* dst) {
    while (src != end) {
        if (dst != 0) {
            dst[0] = src[0];
            dst[1] = src[1];
            dst[2] = src[2];
            dst[3] = src[3];
        }
        src += 4;
        dst += 4;
    }
}

// FUNCTION: DAO 0x00837670
unsigned int __cdecl fn_00437670(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) {
        return 0;
    }
    return (v == 1) ? 1u : 2u;
}
