class C8580 {
public:
    char pad0[8];
    C8580* f8;
    char pad1[0x45 - 0x0c];
    unsigned char flag45;
};
C8580* fn_001c8580(C8580* p);

class C85a0 {
public:
    C85a0* f0;
    C85a0* f4;
    C85a0* f8;
    char pad0[0x45 - 0x0c];
    unsigned char flag45;
    void fn_001c85a0(C85a0* x);
};

class C_fdf0;
struct Pair_fdf0 {
    C_fdf0* first;
    C_fdf0* second;
    Pair_fdf0(C_fdf0* a, C_fdf0* b) : first(a), second(b) {}
};

class C_fdf0 {
public:
    C_fdf0* f0;
    C_fdf0* f4;
    C_fdf0* f8;
    int key;
    char pad0[0x45 - 0x10];
    unsigned char flag45;
    void fn_001cfdf0(Pair_fdf0* out, int* keyptr);
};

class C_d5000 {
public:
    char pad0[0x58];
    C_d5000* f58;
    char pad1[0x74 - 0x5c];
    C_d5000* f74;
    char pad2[0x114 - 0x78];
    C_d5000* f114;
    C_d5000* fn_001d5000();
};

class C_d57c0 {
public:
    char pad0[0x58];
    C_d57c0* f58;
    char pad1[0xd0 - 0x5c];
    C_d57c0* pD0;
    C_d57c0* fn_001d57c0();
};

class C_d5ca0 {
public:
    char pad0[0x5c];
    unsigned int f5c;
    char pad1[0xd0 - 0x60];
    C_d5ca0* pD0;
    unsigned int fn_001d5ca0();
};

class C_d5ea0 {
public:
    char pad0[0x24];
    C_d5ea0* p24;
    char pad1[0x58 - 0x28];
    C_d5ea0* p58;
    char pad2[0x114 - 0x5c];
    C_d5ea0* p114;
    char pad3[0x130 - 0x118];
    C_d5ea0* p130;
    C_d5ea0* fn_001d5ea0();
};

// FUNCTION: DAO 0x5C8580
C8580* fn_001c8580(C8580* p) {
    C8580* q = p->f8;
    while (q->flag45 == 0) {
        p = q;
        q = p->f8;
    }
    return p;
}

// FUNCTION: DAO 0x5C85A0
void C85a0::fn_001c85a0(C85a0* x) {
    C85a0* y = x->f0;
    x->f0 = y->f8;
    if (y->f8->flag45 == 0)
        y->f8->f4 = x;
    y->f4 = x->f4;
    if (x == f4->f4)
        f4->f4 = y;
    else if (x == x->f4->f8)
        x->f4->f8 = y;
    else
        x->f4->f0 = y;
    y->f8 = x;
    x->f4 = y;
}

// FUNCTION: DAO 0x5CFDF0
void C_fdf0::fn_001cfdf0(Pair_fdf0* out, int* keyptr) {
    C_fdf0* p = f4;
    C_fdf0* n = p->f4;
    if (n->flag45 == 0) {
        do {
            int k = *keyptr;
            if (n->key >= k) {
                p = n;
                n = n->f0;
            } else {
                n = n->f8;
            }
        } while (n->flag45 == 0);
    }
    *out = (p == f4 || *keyptr < p->key) ? Pair_fdf0(this, f4) : Pair_fdf0(this, p);
}

// FUNCTION: DAO 0x5D5000
C_d5000* C_d5000::fn_001d5000() {
    C_d5000* a = f114;
    if (a) {
        C_d5000* b = a->f74;
        if (b)
            return b->f58;
    }
    return 0;
}

// FUNCTION: DAO 0x5D57C0
C_d57c0* C_d57c0::fn_001d57c0() {
    C_d57c0* a = pD0;
    if (a)
        return a->f58;
    return 0;
}

// FUNCTION: DAO 0x5D5CA0
unsigned int C_d5ca0::fn_001d5ca0() {
    C_d5ca0* a = pD0;
    if (a)
        return a->f5c;
    return 0xffffffff;
}

// FUNCTION: DAO 0x5D5EA0
C_d5ea0* C_d5ea0::fn_001d5ea0() {
    C_d5ea0* a = p114;
    C_d5ea0* b = a->p58;
    C_d5ea0* c = b->p24;
    if (c)
        return c->p130;
    return 0;
}
