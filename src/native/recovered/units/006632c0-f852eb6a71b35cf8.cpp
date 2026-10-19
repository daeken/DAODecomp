struct C006632c0 {
    unsigned char pad0[0x10];
    unsigned int field_10;
    unsigned int field_14;
    void __thiscall fn_006632c0();
};

// FUNCTION: DAO 0x00A632C0
void __thiscall C006632c0::fn_006632c0() {
    field_10 = field_14;
}

struct C00665250 {
    unsigned char pad0[0x40];
    unsigned int field_40;
    void __thiscall fn_00665250(unsigned int value);
};

// FUNCTION: DAO 0x00A65250
void __thiscall C00665250::fn_00665250(unsigned int value) {
    field_40 = value;
}

struct C00666b40 {
    unsigned char pad0[0x224];
    unsigned int* arr[5];
    unsigned int __thiscall fn_00666b40(unsigned int index);
};

// FUNCTION: DAO 0x00A66B40
unsigned int __thiscall C00666b40::fn_00666b40(unsigned int index) {
    if (index - 3 > 1) {
        return 0;
    }
    unsigned int* p = arr[index];
    return p ? p[1] : 0;
}

struct C00667a90 {
    unsigned char pad0[0xB8];
    unsigned int fields[4];
    bool __thiscall fn_00667a90();
};

// FUNCTION: DAO 0x00A67A90
bool __thiscall C00667a90::fn_00667a90() {
    for (unsigned int i = 0; i < 4; ++i) {
        if (fields[i] != 0) {
            return true;
        }
    }
    return false;
}

struct C00667ab0 {
    void* field_0;
    unsigned int __thiscall fn_00667ab0();
};

// FUNCTION: DAO 0x00A67AB0
unsigned int __thiscall C00667ab0::fn_00667ab0() {
    unsigned int v = *(unsigned int*)((unsigned char*)field_0 + 0x150);
    return v == 0xFFFFFFFFu ? 3u : v;
}

struct C00668ff0 {
    const unsigned short* field_0;
    const unsigned short* field_4;
    bool __thiscall fn_00668ff0(C00668ff0* other);
};

// FUNCTION: DAO 0x00A68FF0
bool __thiscall C00668ff0::fn_00668ff0(C00668ff0* other) {
    const unsigned short* a = field_0;
    const unsigned short* b = other->field_0;
    int cmp = 0;
    for (;;) {
        unsigned short ca = *a;
        unsigned short cb = *b;
        if (ca != cb) {
            cmp = (ca < cb) ? -1 : 1;
            break;
        }
        if (ca == 0) {
            cmp = 0;
            break;
        }
        unsigned short ca2 = a[1];
        unsigned short cb2 = b[1];
        if (ca2 != cb2) {
            cmp = (ca2 < cb2) ? -1 : 1;
            break;
        }
        a += 2;
        b += 2;
        if (ca2 == 0) {
            cmp = 0;
            break;
        }
    }
    if (cmp < 0) {
        return true;
    }
    if (cmp != 0) {
        return false;
    }

    a = field_4;
    b = other->field_4;
    cmp = 0;
    for (;;) {
        unsigned short ca = *a;
        unsigned short cb = *b;
        if (ca != cb) {
            cmp = (ca < cb) ? -1 : 1;
            break;
        }
        if (ca == 0) {
            cmp = 0;
            break;
        }
        unsigned short ca2 = a[1];
        unsigned short cb2 = b[1];
        if (ca2 != cb2) {
            cmp = (ca2 < cb2) ? -1 : 1;
            break;
        }
        a += 2;
        b += 2;
        if (ca2 == 0) {
            cmp = 0;
            break;
        }
    }
    return cmp < 0;
}

// FUNCTION: DAO 0x00A690E0
void* __cdecl fn_006690e0(void** arg) {
    void* prev = arg;
    void* node = *arg;
    if (((unsigned char*)node)[0x19] != 0) {
        return prev;
    }
    do {
        prev = node;
        node = *(void**)prev;
    } while (((unsigned char*)node)[0x19] == 0);
    return prev;
}

struct C00669140_Node {
    C00669140_Node* left;
    C00669140_Node* parent;
    C00669140_Node* right;
    unsigned char pad[0x19 - 0xC];
    unsigned char flag19;
};

struct C00669140 {
    unsigned char pad0[4];
    C00669140_Node* header;
    void __thiscall fn_00669140(C00669140_Node* x);
};

// FUNCTION: DAO 0x00A69140
void __thiscall C00669140::fn_00669140(C00669140_Node* x) {
    C00669140_Node* y = x->left;
    C00669140_Node* tmp = y->right;
    x->left = tmp;
    if (tmp->flag19 == 0) {
        tmp->parent = x;
    }
    tmp = x->parent;
    y->parent = tmp;
    C00669140_Node* h = header;
    if (x == h->parent) {
        h->parent = y;
        y->right = x;
        x->parent = y;
    } else {
        C00669140_Node* p = x->parent;
        if (x == p->right) {
            p->right = y;
            y->right = x;
            x->parent = y;
        } else {
            p->left = y;
            y->right = x;
            x->parent = y;
        }
    }
}

struct C00669c90 {
    unsigned char pad0[0x70];
    unsigned char flag70;
    unsigned char pad1[0xDC - 0x71];
    unsigned int field_dc;
    unsigned char pad2[0x13C - 0xE0];
    unsigned int field_13c;
    void __thiscall fn_00669c90(unsigned int value);
};

// FUNCTION: DAO 0x00A69C90
void __thiscall C00669c90::fn_00669c90(unsigned int value) {
    unsigned int old = field_13c;
    field_dc = old;
    field_13c = value;
    if (value != 0) {
        flag70 = 1;
    }
}

// FUNCTION: DAO 0x00A6BC10
unsigned int* __cdecl fn_0066bc10(unsigned int* first, unsigned int* last, unsigned int* dest) {
    while (first != last) {
        *dest = *first;
        ++dest;
        ++first;
    }
    return dest;
}

// FUNCTION: DAO 0x00A6E4E0
unsigned int __cdecl fn_0066e4e0(const char* str, const char* control) {
    unsigned int bits[8] = { 0 };
    const unsigned char* c = (const unsigned char*)control;
    while (*c) {
        unsigned int v = *c;
        bits[v >> 5] |= 1u << (v & 31);
        ++c;
    }
    const unsigned char* s = (const unsigned char*)str;
    const unsigned char* p = s;
    while (*p) {
        unsigned int v = *p;
        if ((bits[v >> 5] & (1u << (v & 31))) == 0) {
            break;
        }
        ++p;
    }
    return (unsigned int)(p - s);
}
