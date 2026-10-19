extern "C" unsigned char _bittestandset(long*, long);
extern "C" unsigned char _bittest(long const*, long);
#pragma intrinsic(_bittestandset)
#pragma intrinsic(_bittest)

struct C00666b40 {
    unsigned char pad0[0x224];
    unsigned int* arr[5];
    unsigned int __thiscall fn_00666b40(unsigned int index);
};

struct C00667ab0 {
    void* field_0;
    unsigned int __thiscall fn_00667ab0();
};

struct C00668ff0 {
    const wchar_t* field_0;
    const wchar_t* field_4;
    bool __thiscall fn_00668ff0(C00668ff0* other);
};

struct C00669140_Node {
    C00669140_Node* left;
    C00669140_Node* parent;
    C00669140_Node* right;
    unsigned char pad[0x19 - 12];
    unsigned char flag19;
};

struct C00669140 {
    unsigned char pad0[4];
    C00669140_Node* header;
    void __thiscall fn_00669140(C00669140_Node* x);
};

// FUNCTION: DAO 0x00A66B40
unsigned int __thiscall C00666b40::fn_00666b40(unsigned int index) {
    unsigned int idx = index;
    if (idx - 3 > 1) {
        return 0;
    }
    unsigned int* p = arr[idx];
    if (p == 0) {
        return 0;
    }
    return p[1];
}

// FUNCTION: DAO 0x00A67AB0
unsigned int __thiscall C00667ab0::fn_00667ab0() {
    unsigned int v = *(unsigned int*)((unsigned char*)field_0 + 0x150);
    unsigned int result = v;
    if (v == 0xFFFFFFFFu) {
        result = 3;
    }
    return result;
}

// FUNCTION: DAO 0x00A68FF0
bool __thiscall C00668ff0::fn_00668ff0(C00668ff0* other) {
    const wchar_t* a = field_0;
    const wchar_t* b = other->field_0;
    int cmp;
    for (;;) {
        wchar_t c = *a;
        if (c != *b) {
            cmp = (c < *b) ? -1 : 1;
            break;
        }
        if (c == 0) {
            cmp = 0;
            break;
        }
        c = a[1];
        if (c != b[1]) {
            cmp = (c < b[1]) ? -1 : 1;
            break;
        }
        a += 2;
        b += 2;
        if (c == 0) {
            cmp = 0;
            break;
        }
    }
    if (cmp < 0) {
        return true;
    }
    if (cmp > 0) {
        return false;
    }
    a = field_4;
    b = other->field_4;
    for (;;) {
        wchar_t c = *a;
        if (c != *b) {
            cmp = (c < *b) ? -1 : 1;
            break;
        }
        if (c == 0) {
            cmp = 0;
            break;
        }
        c = a[1];
        if (c != b[1]) {
            cmp = (c < b[1]) ? -1 : 1;
            break;
        }
        a += 2;
        b += 2;
        if (c == 0) {
            cmp = 0;
            break;
        }
    }
    return cmp < 0;
}

// FUNCTION: DAO 0x00A690E0
void* __cdecl fn_006690e0(void** arg) {
    void* node = *arg;
    if (((unsigned char*)node)[0x19] != 0) {
        return arg;
    }
    void* prev;
    do {
        prev = node;
        node = *(void**)prev;
    } while (((unsigned char*)node)[0x19] == 0);
    return prev;
}

// FUNCTION: DAO 0x00A69140
void __thiscall C00669140::fn_00669140(C00669140_Node* x) {
    C00669140_Node* node = x;
    C00669140_Node* y = node->left;
    node->left = y->right;
    if (y->right->flag19 == 0) {
        y->right->parent = node;
    }
    y->parent = node->parent;
    C00669140_Node* h = header;
    if (node == h->parent) {
        h->parent = y;
        y->right = node;
        node->parent = y;
    } else {
        C00669140_Node* p = node->parent;
        if (node == p->right) {
            p->right = y;
            y->right = node;
            node->parent = y;
        } else {
            p->left = y;
            y->right = node;
            node->parent = y;
        }
    }
}

// FUNCTION: DAO 0x00A6BC10
unsigned int* __cdecl fn_0066bc10(unsigned int* first, unsigned int* last, unsigned int* dest) {
    unsigned int* result = dest + (last - first);
    while (first != last) {
        *dest++ = *first++;
    }
    return result;
}

// FUNCTION: DAO 0x00A6E4E0
unsigned int __cdecl fn_0066e4e0(const char* str, const char* control) {
    unsigned long bits[8] = {0};
    const unsigned char* c = (const unsigned char*)control;
    while (*c) {
        _bittestandset((long*)bits, (long)*c);
        ++c;
    }
    const unsigned char* p = (const unsigned char*)str;
    unsigned int n = 0;
    while (*p) {
        if (!_bittest((long const*)bits, (long)*p)) {
            break;
        }
        ++p;
        ++n;
    }
    return n;
}
