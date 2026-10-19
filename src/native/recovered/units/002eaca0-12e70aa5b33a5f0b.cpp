struct Obj3720 {
    unsigned char pad0[8];
    int v8;
    int vc;
    int* p10;
    int* p14;
    int v18;
    int v1c;
    int* p20;
    int* p24;
    int v28;
    int v2c;
    int* p30;
    int* p34;
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
    if (idx > length) {
        return 0;
    }
    if (capacity >= 8) {
        return ptr[idx];
    }
    unsigned short* base = (unsigned short*)((unsigned char*)this + 4);
    return base[idx];
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
        idx = *(volatile unsigned int*)((unsigned char*)this + 0x14);
    }
    if (capacity >= 8) {
        return ptr + idx;
    }
    unsigned short* base = (unsigned short*)((unsigned char*)this + 4);
    return base + idx;
}

// FUNCTION: DAO 0x408580
void fn_00008580(int, char* out, const char* type, unsigned int flags) {
    unsigned int f = flags;
    const char* ti = type;
    char* p = out;
    *p++ = '%';
    if (f & 0x20) {
        *p++ = '+';
    }
    if (f & 0x08) {
        *p++ = '#';
    }
    char bl = ti[0];
    if (bl == 'L') {
        *p++ = 'I';
        *p++ = '6';
        *p = '4';
    } else {
        *p = bl;
    }
    ++p;
    unsigned int mode = f & 0xE00;
    if (mode == 0x400) {
        *p = 'o';
        p[1] = 0;
        return;
    }
    if (mode == 0x800) {
        unsigned char c = (unsigned char)f;
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
    *p = ti[1];
    p[1] = 0;
}

struct Elem12 {
    unsigned int a;
    unsigned int b;
    unsigned int c;
};

// FUNCTION: DAO 0x53F320
void fn_0013f320(Elem12* first, Elem12* last, Elem12* destEnd) {
    int count = (int)((char*)last - (char*)first) / 12;
    Elem12* dest = destEnd - count;
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
    Node* x = node;
    while (x->f8->color == 0) {
        x = x->f8;
    }
    return x;
}

// FUNCTION: DAO 0x6EACC0
Node* fn_002eacc0(Node* node) {
    Node* x = node;
    while (x->f0->color == 0) {
        x = x->f0;
    }
    return x;
}
