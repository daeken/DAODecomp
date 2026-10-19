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

struct Fn000d7c20Obj {
    unsigned char pad0[8];
    unsigned int field8;
    unsigned int fieldC;
    unsigned int fn_000d7c20();
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
    unsigned char pad0[4];
    unsigned int* field4;
    unsigned int field8;
    Fn000d9840Out* fn_000d9840(Fn000d9840Out*);
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

// FUNCTION: DAO 0x4D3710
unsigned int Fn000d3710Obj::fn_000d3710() {
    if (*this->field24 != 0) {
        return *this->field34;
    }
    return 0;
}

// FUNCTION: DAO 0x4D50E0
Fn000d50e0Obj* Fn000d50e0Obj::fn_000d50e0(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4) {
    unsigned int v3 = a3;
    this->f4 = a2;
    this->f8 = v3;
    unsigned int s = a1 + a2;
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
    unsigned int* p = out;
    p[0] = this->f4;
    p[1] = this->f8;
    p[2] = this->f0[idx + 1];
    p[3] = this->fC;
    return p;
}

// FUNCTION: DAO 0x4D5150
bool __cdecl fn_000d5150(const Fn000d5150Obj* a, const Fn000d5150Obj* b) {
    int r = (a->fC == b->fC);
    r = r & (a->f8 == b->f8);
    r = r & (a->f4 == b->f4);
    r = r & (a->f0 == b->f0);
    return r;
}

// FUNCTION: DAO 0x4D5190
bool __cdecl fn_000d5190(const Fn000d5190Obj* a, const Fn000d5190Obj* b) {
    int r = (a->f8 == b->f8);
    r = r & (a->f4 == b->f4);
    r = r & (a->f0 == b->f0);
    return r;
}

// FUNCTION: DAO 0x4D51D0
int Fn000d51d0Obj::fn_000d51d0() {
    if (this->field8 != 0) {
        return *this->field8;
    }
    return -1;
}

// FUNCTION: DAO 0x4D53E0
unsigned int* Fn000d53e0Obj::fn_000d53e0(unsigned int* out) {
    unsigned int edi = this->field8;
    if (edi != 0xFFFFFFFFu) {
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
    out[2] = 0;
    out[3] = 0;
    out[1] = 0;
    out[0] = 0;
    return out;
}

// FUNCTION: DAO 0x4D7C20
unsigned int Fn000d7c20Obj::fn_000d7c20() {
    unsigned int p = this->field8;
    if (p == 0) {
        return 0;
    }
    unsigned int d = this->fieldC - p;
    return (d >> 2) << 2;
}

// FUNCTION: DAO 0x4D9480
unsigned int Fn000d9480Obj::fn_000d9480() {
    unsigned int v = this->field0;
    unsigned char hi = (unsigned char)(v >> 29);
    if ((hi & 1) != 0 && (v & 0xFFFF) == 0xFFFF) {
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
    out->f4 = *this->field4;
    out->f0 = reinterpret_cast<unsigned int>(this);
    out->f8 = 1;
    return out;
}

// FUNCTION: DAO 0x4E1290
unsigned int Fn000e1290Obj::fn_000e1290() {
    if (*this->field20 != 0) {
        return *this->field30;
    }
    return 0;
}

// FUNCTION: DAO 0x4E7760
Fn000e7760Node* __cdecl fn_000e7760(Fn000e7760Node* node) {
    while (node->field8->flag21 == 0) {
        node = node->field8;
    }
    return node;
}
