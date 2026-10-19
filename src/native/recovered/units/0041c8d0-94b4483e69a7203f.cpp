struct C_0041c8d0 {
    unsigned int field0;
    void fn_0041c8d0();
};

struct C_0041cce0 {
    unsigned char pad30[0x30];
    unsigned int field30;
    unsigned int fn_0041cce0();
};

struct C_0041cdd0 {
    unsigned char pad1c[0x1c];
    unsigned int field1c;
    void fn_0041cdd0(unsigned int value);
};

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

struct C_00430cf0 {
    unsigned char padFC[0xfc];
    unsigned int fieldFC;
    unsigned int fn_00430cf0();
};

struct C_00430d00 {
    unsigned char pad1c0[0x1c0];
    unsigned int field1c0;
    unsigned int fn_00430d00();
};

struct C_00430d20 {
    unsigned char padD8[0xd8];
    unsigned int fieldD8;
    unsigned int fn_00430d20();
};

struct C_00430d30 {
    unsigned char padB4[0xb4];
    unsigned int fieldB4;
    unsigned int fn_00430d30();
};

struct C_00430d40 {
    unsigned char padCC[0xcc];
    unsigned int fieldCC;
    unsigned int fn_00430d40();
};

// FUNCTION: DAO 0x0081C8D0
void C_0041c8d0::fn_0041c8d0() {
    field0 = 0;
}

// FUNCTION: DAO 0x0081CCE0
unsigned int C_0041cce0::fn_0041cce0() {
    return field30 & 1u;
}

// FUNCTION: DAO 0x0081CDD0
void C_0041cdd0::fn_0041cdd0(unsigned int value) {
    field1c = value;
}

// FUNCTION: DAO 0x00821520
bool __stdcall fn_00421520(const unsigned int* a, const unsigned int* b) {
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2] && a[3] == b[3];
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
    Node_004215a0* parent = x->field4;
    if (x == field4->field4) {
        field4->field4 = p;
        p->field8 = x;
        x->field4 = p;
        return;
    }
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
    while (src != end) {
        if (dst) {
            dst[0] = src[0];
            dst[1] = src[1];
            dst[2] = src[2];
            dst[3] = src[3];
        }
        src += 4;
        dst += 4;
    }
}

// FUNCTION: DAO 0x00830CF0
unsigned int C_00430cf0::fn_00430cf0() {
    return fieldFC & 0x1fu;
}

// FUNCTION: DAO 0x00830D00
unsigned int C_00430d00::fn_00430d00() {
    unsigned int v = field1c0;
    if (v == 1) {
        return 1;
    }
    unsigned int r = (v != 2) ? 1u : 0u;
    r -= 1u;
    r &= 2u;
    return r;
}

// FUNCTION: DAO 0x00830D20
unsigned int C_00430d20::fn_00430d20() {
    return fieldD8 & 7u;
}

// FUNCTION: DAO 0x00830D30
unsigned int C_00430d30::fn_00430d30() {
    return fieldB4 & 7u;
}

// FUNCTION: DAO 0x00830D40
unsigned int C_00430d40::fn_00430d40() {
    return fieldCC & 3u;
}

// FUNCTION: DAO 0x00837640
unsigned int __cdecl fn_00437640(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) {
        return 0;
    }
    if (v == 1) {
        return 1;
    }
    unsigned int r = (v != 2) ? 1u : 0u;
    r -= 1u;
    r &= 2u;
    return r;
}

// FUNCTION: DAO 0x00837670
unsigned int __cdecl fn_00437670(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) {
        return 0;
    }
    if (v == 1) {
        return 1;
    }
    return 2;
}

// FUNCTION: DAO 0x00837690
unsigned int __cdecl fn_00437690(const unsigned int* p) {
    return *p;
}

// FUNCTION: DAO 0x008376A0
unsigned int __cdecl fn_004376a0(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 1) {
        return 0;
    }
    if (v == 2) {
        return 1;
    }
    if (v == 3) {
        return 2;
    }
    return 0xffu;
}

// FUNCTION: DAO 0x008376D0
unsigned int __cdecl fn_004376d0(const unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) {
        return 2;
    }
    if (v == 1) {
        return 1;
    }
    if (v == 2) {
        return 2;
    }
    return 0xffu;
}