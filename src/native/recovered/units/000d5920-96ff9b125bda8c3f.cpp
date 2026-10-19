struct Fn000d3710Obj {
    unsigned char pad0[0x24];
    unsigned int* field24;
    unsigned char pad1[0x0C];
    unsigned int* field34;
    unsigned int fn_000d3710();
};

struct Fn000d50e0Obj {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fC;
    Fn000d50e0Obj* fn_000d50e0(unsigned int, unsigned int, unsigned int, unsigned int);
};

struct Fn000d5120Obj {
    unsigned int* f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fC;
    unsigned int* fn_000d5120(unsigned int*, unsigned int);
};

struct Fn000d5150Obj {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fC;
};

struct Fn000d5190Obj {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
};

struct Fn000d51d0Obj {
    unsigned char pad0[8];
    int* field8;
    int fn_000d51d0();
};

struct Fn000d53e0Obj {
    unsigned int field0;
    unsigned int field4;
    unsigned int field8;
    unsigned int fieldC;
    unsigned int* fn_000d53e0(unsigned int*);
};

struct Fn000d5920Obj {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned char fC;
    Fn000d5920Obj* fn_000d5920(unsigned int, unsigned int);
};

struct Fn000d7c20Obj {
    unsigned char pad0[8];
    unsigned int field8;
    unsigned int fieldC;
    unsigned int fn_000d7c20();
};

struct Fn000d9450Obj {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fC;
    unsigned int f10;
    unsigned int f14;
    Fn000d9450Obj* fn_000d9450(unsigned int, unsigned int, unsigned int, unsigned int, unsigned int);
};

struct Fn000d9480Obj {
    unsigned int field0;
    unsigned int fn_000d9480();
};

struct Fn000d9840Out {
    unsigned int f0;
    unsigned int f4;
    unsigned char f8;
};

struct Fn000d9840Obj {
    unsigned int pad0;
    unsigned int* field4;
    unsigned int field8;
    Fn000d9840Out* fn_000d9840(Fn000d9840Out*);
};

struct Fn000df570Obj {
    unsigned int pad0;
    unsigned int field4;
    unsigned int field8;
    void fn_000df570();
};

struct Fn000e1290Obj {
    unsigned char pad0[0x20];
    unsigned int* field20;
    unsigned char pad1[0x0C];
    unsigned int* field30;
    unsigned int fn_000e1290();
};

struct Fn000e7760Node {
    unsigned char pad0[8];
    Fn000e7760Node* field8;
    unsigned char pad1[0x15];
    unsigned char flag21;
};

struct Fn000e7780Node {
    Fn000e7780Node* left;
    Fn000e7780Node* parent;
    Fn000e7780Node* right;
    unsigned char pad[0x15];
    unsigned char flag21;
};

struct Fn000e7780Tree {
    unsigned int pad0;
    Fn000e7780Node* header;
    Fn000e7780Node* fn_000e7780(Fn000e7780Node*);
};

// FUNCTION: DAO 0x4D3710
unsigned int Fn000d3710Obj::fn_000d3710() {
    unsigned int* p = this->field24;
    if (*p == 0) {
        return 0;
    }
    unsigned int* q = this->field34;
    return *q;
}

// FUNCTION: DAO 0x4D50E0
Fn000d50e0Obj* Fn000d50e0Obj::fn_000d50e0(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4) {
    unsigned int s = a2 + a1;
    this->f4 = a2;
    this->f8 = a3;
    this->f0 = a1;
    this->fC = a4;
    if (a4 > s || a4 <= a1) {
        this->f0 = 0;
        this->f4 = 0;
        this->fC = 0;
    }
    return this;
}

// FUNCTION: DAO 0x4D5120
unsigned int* Fn000d5120Obj::fn_000d5120(unsigned int* out, unsigned int idx) {
    out[0] = this->f4;
    out[1] = this->f8;
    out[2] = this->f0[idx + 1];
    out[3] = this->fC;
    return out;
}

// FUNCTION: DAO 0x4D5150
bool fn_000d5150(const Fn000d5150Obj* a, const Fn000d5150Obj* b) {
    bool r = (a->fC == b->fC);
    r = r & (a->f8 == b->f8);
    r = r & (a->f4 == b->f4);
    r = r & (a->f0 == b->f0);
    return r;
}

// FUNCTION: DAO 0x4D5190
bool fn_000d5190(const Fn000d5190Obj* a, const Fn000d5190Obj* b) {
    bool r = (a->f8 == b->f8);
    r = r & (a->f4 == b->f4);
    r = r & (a->f0 == b->f0);
    return r;
}

// FUNCTION: DAO 0x4D51D0
int Fn000d51d0Obj::fn_000d51d0() {
    if (this->field8 == 0) {
        return -1;
    }
    return *this->field8;
}

// FUNCTION: DAO 0x4D53E0
unsigned int* Fn000d53e0Obj::fn_000d53e0(unsigned int* out) {
    unsigned int edi = this->field8;
    if (edi == 0xFFFFFFFFu) {
        out[2] = 0;
        out[3] = 0;
        out[1] = 0;
        out[0] = 0;
        return out;
    }
    unsigned int edx = this->field0;
    unsigned int esi = this->field4;
    unsigned int ecx = this->fieldC;
    out[2] = ecx;
    ecx = *reinterpret_cast<unsigned int*>(edx + 0x18);
    ecx += edi;
    out[1] = esi;
    ecx += edx;
    esi += edx;
    out[0] = edx;
    out[3] = ecx;
    if (ecx > esi || ecx <= edx) {
        out[3] = 0;
        out[1] = 0;
        out[0] = 0;
    }
    return out;
}

// FUNCTION: DAO 0x4D5920
Fn000d5920Obj* Fn000d5920Obj::fn_000d5920(unsigned int a, unsigned int b) {
    unsigned int c = a;
    if (c == 0) {
        c = 1;
    }
    this->f0 = c;
    this->f4 = b;
    this->f8 = c - 1;
    this->fC = 0;
    return this;
}

// FUNCTION: DAO 0x4D7C20
unsigned int Fn000d7c20Obj::fn_000d7c20() {
    if (this->field8 == 0) {
        return 0;
    }
    int d = (int)this->fieldC - (int)this->field8;
    return (unsigned int)((d >> 2) * 4);
}

// FUNCTION: DAO 0x4D9450
Fn000d9450Obj* Fn000d9450Obj::fn_000d9450(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5) {
    this->f0 = a1;
    this->f4 = a2;
    this->f8 = a3;
    this->fC = a4;
    this->f10 = a5;
    this->f14 = 0;
    return this;
}

// FUNCTION: DAO 0x4D9480
unsigned int Fn000d9480Obj::fn_000d9480() {
    unsigned int v = this->field0;
    if (((v >> 29) & 1) != 0 && (v & 0xFFFF) == 0xFFFF) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x4D9840
Fn000d9840Out* Fn000d9840Obj::fn_000d9840(Fn000d9840Out* out) {
    if (this->field8 == 0) {
        out->f8 = 0;
        return out;
    }
    out->f0 = reinterpret_cast<unsigned int>(this);
    out->f4 = *this->field4;
    out->f8 = 1;
    return out;
}

// FUNCTION: DAO 0x4DF570
void Fn000df570Obj::fn_000df570() {
    this->field4 = 0;
    this->field8 = 0;
}

// FUNCTION: DAO 0x4E1290
unsigned int Fn000e1290Obj::fn_000e1290() {
    unsigned int* p = this->field20;
    if (*p == 0) {
        return 0;
    }
    unsigned int* q = this->field30;
    return *q;
}

// FUNCTION: DAO 0x4E7760
Fn000e7760Node* fn_000e7760(Fn000e7760Node* node) {
    Fn000e7760Node* c = node->field8;
    if (c->flag21 != 0) {
        return node;
    }
    do {
        node = c;
        c = node->field8;
    } while (c->flag21 == 0);
    return node;
}

// FUNCTION: DAO 0x4E7780
Fn000e7780Node* Fn000e7780Tree::fn_000e7780(Fn000e7780Node* z) {
    Fn000e7780Node* x = z->left;
    z->left = x->right;
    if (x->right->flag21 == 0) {
        x->right->parent = z;
    }
    x->parent = z->parent;
    Fn000e7780Node* header = this->header;
    if (z == header->parent) {
        header->parent = x;
    } else if (z == z->parent->right) {
        z->parent->right = x;
    } else {
        z->parent->left = x;
    }
    x->right = z;
    z->parent = x;
    return x;
}
