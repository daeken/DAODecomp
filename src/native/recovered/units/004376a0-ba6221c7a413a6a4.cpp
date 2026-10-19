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
    Node_004215a0* r = p->field8;
    x->field0 = r;
    if (r->field11 == 0) {
        r->field4 = x;
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
void __cdecl fn_00422ad0(const unsigned int* src, const unsigned int* end, unsigned int* dst) {
    const unsigned int* s = src;
    const unsigned int* e = end;
    unsigned int* d = dst;
    while (s != e) {
        if (d != 0) {
            d[0] = s[0];
            d[1] = s[1];
            d[2] = s[2];
            d[3] = s[3];
        }
        s += 4;
        d += 4;
    }
}

// FUNCTION: DAO 0x00837670
unsigned int __cdecl fn_00437670(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) {
        return 0;
    }
    unsigned int r = 1;
    if (v != 1) {
        r = 2;
    }
    return r;
}

// FUNCTION: DAO 0x008376A0
unsigned int __cdecl fn_004376a0(const unsigned int* p) {
    unsigned int v = *p;
    switch (v) {
    case 1:
        return 0;
    case 2:
        return 1;
    case 3:
        return 2;
    default:
        return 0xffu;
    }
}

// FUNCTION: DAO 0x008376D0
unsigned int __cdecl fn_004376d0(const unsigned int* p) {
    unsigned int v = *p;
    switch (v) {
    case 1:
        return 1;
    case 0:
    case 2:
        return 2;
    default:
        return 0xffu;
    }
}
