struct Obj3720 {
    unsigned char pad0[8];
    volatile int v8;
    volatile int vc;
    volatile int* volatile p10;
    volatile int* volatile p14;
    volatile int v18;
    volatile int v1c;
    volatile int* volatile p20;
    volatile int* volatile p24;
    volatile int v28;
    volatile int v2c;
    volatile int* volatile p30;
    volatile int* volatile p34;
    void fn_00003720();
};

// FUNCTION: DAO 0x403720
void Obj3720::fn_00003720() {
    p20 = &v18;
    p24 = &v1c;
    p10 = &v8;
    p30 = &v28;
    p14 = &vc;
    p34 = &v2c;
    vc = 0;
    *p24 = 0;
    *p34 = 0;
    *p10 = 0;
    *p20 = 0;
    *p30 = 0;
}

struct Obj3dd0 {
    unsigned char pad0[4];
    unsigned short* ptr;
    unsigned char pad8[0x0C];
    unsigned int length;
    unsigned int capacity;
    unsigned short fn_00003dd0(unsigned int idx);
};

// FUNCTION: DAO 0x403DD0
unsigned short Obj3dd0::fn_00003dd0(unsigned int idx) {
    if (idx <= length) {
        if (capacity >= 8) {
            return ptr[idx];
        }
        return *(unsigned short*)((unsigned char*)this + 4 + idx * 2);
    }
    return 0;
}

struct Obj3e00 {
    unsigned char pad0[4];
    unsigned short* ptr;
    unsigned char pad8[0x0C];
    unsigned int length;
    unsigned int capacity;
    unsigned short* fn_00003e00(unsigned int idx);
};

// FUNCTION: DAO 0x403E00
unsigned short* Obj3e00::fn_00003e00(unsigned int idx) {
    if (idx > length) {
        idx = length;
    }
    if (capacity >= 8) {
        return ptr + idx;
    }
    return (unsigned short*)((unsigned char*)this + 4 + idx * 2);
}

// FUNCTION: DAO 0x408580
void fn_00008580(int, char* out, const char* type, unsigned int flags) {
    out[0] = '%';
    char* p = out + 1;
    if (flags & 0x20) {
        *p++ = '+';
    }
    if (flags & 0x08) {
        *p++ = '#';
    }
    char t = *type;
    if (t == 'L') {
        *p++ = 'I';
        *p++ = '6';
        *p = '4';
    } else {
        *p = t;
    }
    ++p;
    unsigned int mode = flags & 0xE00;
    if (mode == 0x400) {
        char c = 'o';
        *p = c;
        p[1] = 0;
        return;
    }
    if (mode == 0x800) {
        unsigned char c = (unsigned char)flags;
        c += c;
        c += c;
        c += c;
        c = (unsigned char)~c;
        c &= 0x20;
        c |= 0x58;
        *p = c;
        p[1] = 0;
        return;
    }
    char c = type[1];
    *p = c;
    p[1] = 0;
}

struct Obj16ac0 {
    unsigned char pad0[4];
    void* ptr;
    unsigned char pad8[0x10];
    unsigned int capacity;
    void* fn_00016ac0();
};

// FUNCTION: DAO 0x416AC0
void* Obj16ac0::fn_00016ac0() {
    if (capacity >= 0x10) {
        return ptr;
    }
    return (void*)((unsigned char*)this + 4);
}

struct ObjD51e0 {
    unsigned char pad0[8];
    void* p8;
    void* fn_000d51e0();
};

// FUNCTION: DAO 0x4D51E0
void* ObjD51e0::fn_000d51e0() {
    void* p = p8;
    if (p != 0) {
        return *(void**)((unsigned char*)p + 4);
    }
    return 0;
}

struct ObjD51f0 {
    unsigned char pad0[8];
    void* p8;
    void* fn_000d51f0();
};

// FUNCTION: DAO 0x4D51F0
void* ObjD51f0::fn_000d51f0() {
    void* p = p8;
    if (p != 0) {
        return *(void**)((unsigned char*)p + 0xC);
    }
    return 0;
}

struct Elem12 {
    unsigned int a;
    unsigned int b;
    unsigned int c;
};

// FUNCTION: DAO 0x53F320
void fn_0013f320(Elem12* first, Elem12* last, Elem12* dest) {
    int count = (int)(last - first);
    dest -= count;
    while (first != last) {
        --last;
        --dest;
        dest->a = last->a;
        dest->b = last->b;
        dest->c = last->c;
    }
}

struct Node {
    Node* f0;
    Node* f4;
    Node* f8;
    unsigned char pad[0x2D];
    unsigned char color;
};

// FUNCTION: DAO 0x6EACA0
Node* fn_002eaca0(Node* node) {
    Node* result = node;
    Node* x = result->f8;
    if (x->color != 0) {
        return result;
    }
    do {
        result = x;
        x = result->f8;
    } while (x->color == 0);
    return result;
}

// FUNCTION: DAO 0x6EACC0
Node* fn_002eacc0(Node* node) {
    Node* result = node;
    Node* x = result->f0;
    if (x->color != 0) {
        return result;
    }
    do {
        result = x;
        x = result->f0;
    } while (x->color == 0);
    return result;
}
