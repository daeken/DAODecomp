struct Node {
    Node* f0;
    Node* f4;
    Node* f8;
    unsigned char pad[0x2D];
    unsigned char color;
};

struct Tree {
    unsigned char pad0[4];
    Node* f4;
    void fn_00002920(Node*);
    void fn_002eaf90(Node*);
};

struct Obj36c0 {
    unsigned char pad0[0x10];
    int* p10;
    unsigned char pad14[0x0C];
    int* p20;
    unsigned char pad24[0x0C];
    int* p30;
    void fn_000036c0(int a, int b, int c);
};

struct Obj36f0 {
    unsigned char pad0[0x14];
    int* p14;
    unsigned char pad18[0x0C];
    int* p24;
    unsigned char pad28[0x0C];
    int* p34;
    void fn_000036f0(int a, int b, int c);
};

struct Obj3720 {
    unsigned char pad0[8];
    int v8;
    int vc;
    void* p10;
    void* p14;
    int v18;
    int v1c;
    void* p20;
    void* p24;
    int v28;
    int v2c;
    void* p30;
    void* p34;
    void fn_00003720();
};

struct Obj3dd0 {
    unsigned char pad0[4];
    union { unsigned short* ptr; unsigned short buf[2]; } u;
    unsigned char pad8[0x0C];
    unsigned int length;
    unsigned int capacity;
    unsigned short fn_00003dd0(unsigned int idx);
};

struct Obj3e00 {
    unsigned char pad0[4];
    union { unsigned short* ptr; unsigned short buf[2]; } u;
    unsigned char pad8[0x0C];
    unsigned int length;
    unsigned int capacity;
    unsigned short* fn_00003e00(unsigned int idx);
};

struct Obj13840 {
    unsigned char pad0[0x2A];
    unsigned char b2a;
    unsigned char pad2b;
    int v2c;
    int v30;
    int v34;
    int v38;
    void fn_00013840(int a, int b, int c, int d);
};

struct Obj16ac0 {
    unsigned char pad0[4];
    union { void* ptr; unsigned char buf[4]; } u;
    unsigned char pad8[0x10];
    unsigned int capacity;
    void* fn_00016ac0();
};

struct ObjD5070 {
    unsigned int a;
    unsigned int b;
    unsigned int c;
    unsigned int d;
    ObjD5070* fn_000d5070(unsigned int x, unsigned int y, unsigned int z, unsigned int w);
};

struct ObjD51e0 {
    unsigned char pad0[8];
    void* p8;
    void* fn_000d51e0();
};

struct ObjD51f0 {
    unsigned char pad0[8];
    void* p8;
    void* fn_000d51f0();
};

struct Elem12 {
    unsigned int a;
    unsigned int b;
    unsigned int c;
};

// FUNCTION: DAO 0x402920
void Tree::fn_00002920(Node* node) {
    Node* eax = node->f0;
    Node* esi = eax->f8;
    node->f0 = esi;
    esi = eax->f8;
    if (esi->color == 0) {
        esi->f4 = node;
    }
    esi = node->f4;
    eax->f4 = esi;
    Node* ecx = this->f4;
    if (node == ecx->f4) {
        ecx->f4 = eax;
        eax->f8 = node;
        node->f4 = eax;
        return;
    }
    ecx = node->f4;
    if (node == ecx->f8) {
        ecx->f8 = eax;
        eax->f8 = node;
        node->f4 = eax;
        return;
    }
    ecx->f0 = eax;
    eax->f8 = node;
    node->f4 = eax;
}

// FUNCTION: DAO 0x4036C0
void Obj36c0::fn_000036c0(int a, int b, int c) {
    *p10 = a;
    *p20 = b;
    int diff = c - b;
    *p30 = diff >> 1;
}

// FUNCTION: DAO 0x4036F0
void Obj36f0::fn_000036f0(int a, int b, int c) {
    *p14 = a;
    *p24 = b;
    int diff = c - b;
    *p34 = diff >> 1;
}

// FUNCTION: DAO 0x403720
void Obj3720::fn_00003720() {
    p20 = &v18;
    p24 = &v1c;
    p10 = &v8;
    p30 = &v28;
    p14 = &vc;
    p34 = &v2c;
    vc = 0;
    *(int*)p24 = 0;
    *(int*)p34 = 0;
    *(int*)p10 = 0;
    *(int*)p20 = 0;
    *(int*)p30 = 0;
}

// FUNCTION: DAO 0x403DD0
unsigned short Obj3dd0::fn_00003dd0(unsigned int idx) {
    unsigned char* base = (unsigned char*)this;
    unsigned int len = *(unsigned int*)(base + 0x14);
    if (idx > len) {
        return 0;
    }
    if (*(unsigned int*)(base + 0x18) < 8) {
        return *(unsigned short*)(base + 4 + idx * 2);
    }
    unsigned short* p = *(unsigned short**)(base + 4);
    return p[idx];
}

// FUNCTION: DAO 0x403E00
unsigned short* Obj3e00::fn_00003e00(unsigned int idx) {
    unsigned char* base = (unsigned char*)this;
    unsigned int len = *(unsigned int*)(base + 0x14);
    if (idx > len) {
        idx = len;
    }
    if (*(unsigned int*)(base + 0x18) < 8) {
        return (unsigned short*)(base + 4 + idx * 2);
    }
    unsigned short* p = *(unsigned short**)(base + 4);
    return p + idx;
}

// FUNCTION: DAO 0x408580
void fn_00008580(void* unused, char* out, const char* type, unsigned int flags) {
    unsigned char dl = (unsigned char)flags;
    char* ecx = out;
    *ecx++ = '%';
    if (dl & 0x20) {
        *ecx++ = '+';
    }
    if (dl & 0x08) {
        *ecx++ = '#';
    }
    char bl = *type;
    if (bl == 'L') {
        *ecx++ = 'I';
        *ecx++ = '6';
        *ecx++ = '4';
    } else {
        *ecx++ = bl;
    }
    unsigned int esi = flags & 0xE00;
    if (esi == 0x400) {
        *ecx++ = 'o';
        *ecx = 0;
        return;
    }
    if (esi == 0x800) {
        unsigned char c = (unsigned char)(~(unsigned char)(dl << 3));
        c = (unsigned char)((c & 0x20) | 0x58);
        *ecx++ = c;
        *ecx = 0;
        return;
    }
    *ecx++ = type[1];
    *ecx = 0;
}

// FUNCTION: DAO 0x413840
void Obj13840::fn_00013840(int a, int b, int c, int d) {
    v2c = a;
    v30 = b;
    v34 = c;
    v38 = d;
    b2a = 1;
}

// FUNCTION: DAO 0x416AC0
void* Obj16ac0::fn_00016ac0() {
    unsigned char* base = (unsigned char*)this;
    if (*(unsigned int*)(base + 0x18) < 0x10) {
        return base + 4;
    }
    return *(void**)(base + 4);
}

// FUNCTION: DAO 0x4D5070
ObjD5070* ObjD5070::fn_000d5070(unsigned int x, unsigned int y, unsigned int z, unsigned int w) {
    a = x;
    b = y;
    c = z;
    d = w;
    bool valid = true;
    if (x == 0 || y == 0 || z == 0 || w == 0) {
        valid = false;
    } else {
        unsigned int end = x + y;
        if (z > end) {
            valid = false;
        } else if (z <= x) {
            valid = false;
        } else if (w > end) {
            valid = false;
        } else if (!(w > x)) {
            valid = false;
        }
    }
    if (!valid) {
        a = 0;
        b = 0;
        c = 0;
        d = 0;
    }
    return this;
}

// FUNCTION: DAO 0x4D51E0
void* ObjD51e0::fn_000d51e0() {
    void* p = *(void**)((unsigned char*)this + 8);
    if (p == 0) {
        return 0;
    }
    return *(void**)((unsigned char*)p + 4);
}

// FUNCTION: DAO 0x4D51F0
void* ObjD51f0::fn_000d51f0() {
    void* p = *(void**)((unsigned char*)this + 8);
    if (p == 0) {
        return 0;
    }
    return *(void**)((unsigned char*)p + 0xC);
}

// FUNCTION: DAO 0x53F320
void fn_0013f320(Elem12* begin, Elem12* end, Elem12* destEnd) {
    Elem12* d = destEnd;
    while (begin != end) {
        --end;
        --d;
        d->a = end->a;
        d->b = end->b;
        d->c = end->c;
    }
}

// FUNCTION: DAO 0x6EACA0
Node* fn_002eaca0(Node* node) {
    Node* x = node->f8;
    if (x->color != 0) {
        return node;
    }
    do {
        node = x;
        x = node->f8;
    } while (x->color == 0);
    return node;
}

// FUNCTION: DAO 0x6EACC0
Node* fn_002eacc0(Node* node) {
    Node* x = node->f0;
    if (x->color != 0) {
        return node;
    }
    do {
        node = x;
        x = node->f0;
    } while (x->color == 0);
    return node;
}

// FUNCTION: DAO 0x6EAF90
void Tree::fn_002eaf90(Node* node) {
    Node* eax = node->f8;
    Node* esi = eax->f0;
    node->f8 = esi;
    esi = eax->f0;
    if (esi->color == 0) {
        esi->f4 = node;
    }
    esi = node->f4;
    eax->f4 = esi;
    Node* ecx = this->f4;
    if (node == ecx->f4) {
        ecx->f4 = eax;
        eax->f0 = node;
        node->f4 = eax;
        return;
    }
    ecx = node->f4;
    if (node == ecx->f0) {
        ecx->f0 = eax;
        eax->f0 = node;
        node->f4 = eax;
        return;
    }
    ecx->f8 = eax;
    eax->f0 = node;
    node->f4 = eax;
}
