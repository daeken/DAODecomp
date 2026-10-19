class C_1b6cb0 {
public:
    unsigned char pad0[0x90];
    unsigned char b90;
    unsigned char b91;
    bool fn_001b6cb0(unsigned char v);
};

class C5fa0 { public: int pad0; int begin; int end; int fn_001c5fa0(); };

class C8580 { public: char pad0[8]; C8580* f8; char pad1[0x45 - 0x0C]; unsigned char flag45; };
C8580* fn_001c8580(C8580* arg);

class C85a0 { public: C85a0* f0; C85a0* f4; C85a0* f8; char pad[0x45 - 0x0C]; unsigned char flag45; void fn_001c85a0(C85a0* x); };

class C_cbc70 { public: char pad0[0x300]; unsigned int counters[1]; void fn_001cbc70(unsigned int i); };

class C_cf910 { public: char pad0[0x84]; unsigned int field84; unsigned int fn_001cf910(); };

class C_fcf0 { public: int pad0; int begin; int end; int fn_001cfcf0(); };

class C_fdf0 { public: C_fdf0* f0; C_fdf0* f4; C_fdf0* f8; int key; char pad[0x45 - 0x10]; unsigned char flag45; void fn_001cfdf0(C_fdf0** out, int* keyptr); };

class C_1fa0 { public: char pad0[0x324]; unsigned int* arr324; void fn_001d1fa0(unsigned int i, unsigned int v); };

class C_2120 { public: unsigned int f0; unsigned int f4; unsigned int fn_001d2120(); };

class C_d5000 { public: char pad0[0x58]; C_d5000* f58; char pad1[0x74 - 0x5C]; C_d5000* f74; char pad2[0x114 - 0x78]; C_d5000* f114; C_d5000* fn_001d5000(); };

class C_d57c0 { public: char pad0[0x58]; C_d57c0* f58; char pad1[0xD0 - 0x5C]; C_d57c0* pD0; C_d57c0* fn_001d57c0(); };

class C_d5ca0 { public: char pad0[0x5C]; unsigned int f5c; char pad1[0xD0 - 0x60]; C_d5ca0* pD0; unsigned int fn_001d5ca0(); };

class C_d5ea0 { public: char pad0[0x24]; C_d5ea0* p24; char pad1[0x58 - 0x28]; C_d5ea0* p58; char pad2[0x114 - 0x5C]; C_d5ea0* p114; char pad3[0x130 - 0x118]; C_d5ea0* p130; C_d5ea0* fn_001d5ea0(); };

class C_edb10 { public: char pad0[0x2F5]; unsigned char b2f5; bool fn_001edb10(); };

class C_edb60 { public: int pad0; int begin; int end; int fn_001edb60(); };

// FUNCTION: DAO 0x5B6CB0
bool C_1b6cb0::fn_001b6cb0(unsigned char v) {
    b91 = v;
    return b90 = 1;
}

// FUNCTION: DAO 0x5C5FA0
int C5fa0::fn_001c5fa0() {
    if (begin == 0) return 0;
    return (end - begin) / 140;
}

// FUNCTION: DAO 0x5C8580
C8580* fn_001c8580(C8580* arg) {
    C8580* e = arg->f8;
    if (e->flag45 != 0) return arg;
    do {
        arg = e;
        e = arg->f8;
    } while (e->flag45 == 0);
    return arg;
}

// FUNCTION: DAO 0x5C85A0
void C85a0::fn_001c85a0(C85a0* x) {
    C85a0* y = x->f0;
    C85a0* t = y->f8;
    x->f0 = t;
    if (t->flag45 == 0) t->f4 = x;
    y->f4 = x->f4;
    C85a0* r = this->f4;
    if (x == r->f4) {
        r->f4 = y;
        y->f8 = x;
        x->f4 = y;
    } else {
        C85a0* p = x->f4;
        if (x == p->f8) {
            p->f8 = y;
            y->f8 = x;
            x->f4 = y;
        } else {
            p->f0 = y;
            y->f8 = x;
            x->f4 = y;
        }
    }
}

// FUNCTION: DAO 0x5CBC70
void C_cbc70::fn_001cbc70(unsigned int i) {
    if (i != 1) counters[i] += 1;
}

// FUNCTION: DAO 0x5CF910
unsigned int C_cf910::fn_001cf910() {
    return field84;
}

// FUNCTION: DAO 0x5CFCF0
int C_fcf0::fn_001cfcf0() {
    if (begin == 0) return 0;
    return (end - begin) >> 6;
}

// FUNCTION: DAO 0x5CFDF0
void C_fdf0::fn_001cfdf0(C_fdf0** out, int* keyptr) {
    C_fdf0* edx = f4;
    C_fdf0* eax = edx->f4;
    if (eax->flag45 == 0) {
        do {
            int k = *keyptr;
            if (eax->key >= k) {
                edx = eax;
                eax = eax->f0;
            } else {
                eax = eax->f8;
            }
        } while (eax->flag45 == 0);
    }
    C_fdf0* root = f4;
    if (edx == root || *keyptr < edx->key) {
        out[0] = this;
        out[1] = root;
    } else {
        out[0] = this;
        out[1] = edx;
    }
}

// FUNCTION: DAO 0x5D1FA0
void C_1fa0::fn_001d1fa0(unsigned int i, unsigned int v) {
    arr324[i] = v;
}

// FUNCTION: DAO 0x5D2120
unsigned int C_2120::fn_001d2120() {
    if (f4 == 0) return 0;
    return f0;
}

// FUNCTION: DAO 0x5D5000
C_d5000* C_d5000::fn_001d5000() {
    C_d5000* a = f114;
    if (!a) return 0;
    C_d5000* b = a->f74;
    if (!b) return 0;
    return b->f58;
}

// FUNCTION: DAO 0x5D57C0
C_d57c0* C_d57c0::fn_001d57c0() {
    C_d57c0* a = pD0;
    if (!a) return 0;
    return a->f58;
}

// FUNCTION: DAO 0x5D5CA0
unsigned int C_d5ca0::fn_001d5ca0() {
    C_d5ca0* a = pD0;
    if (!a) return 0xffffffff;
    return a->f5c;
}

// FUNCTION: DAO 0x5D5EA0
C_d5ea0* C_d5ea0::fn_001d5ea0() {
    C_d5ea0* a = p114;
    C_d5ea0* b = a->p58;
    C_d5ea0* c = b->p24;
    if (!c) return 0;
    return c->p130;
}

// FUNCTION: DAO 0x5EDB10
bool C_edb10::fn_001edb10() {
    return b2f5 = 1;
}

// FUNCTION: DAO 0x5EDB60
int C_edb60::fn_001edb60() {
    if (begin == 0) return 0;
    return (end - begin) / 708;
}
