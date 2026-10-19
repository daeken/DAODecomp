struct NodeA {
    NodeA* left;
    NodeA* parent;
    NodeA* right;
    unsigned char pad[0xa5];
    unsigned char sentinel;
};

// FUNCTION: DAO 0x0088E6A0
NodeA* __cdecl fn_0048e6a0(NodeA* p) {
    NodeA* x = p->right;
    if (x->sentinel != 0) return p;
    do {
        p = x;
        x = p->right;
    } while (x->sentinel == 0);
    return p;
}

// FUNCTION: DAO 0x0088E6C0
NodeA* __cdecl fn_0048e6c0(NodeA* p) {
    NodeA* x = p->left;
    if (x->sentinel != 0) return p;
    do {
        p = x;
        x = p->left;
    } while (x->sentinel == 0);
    return p;
}

struct TreeRot {
    void* unused;
    NodeA* header;
    void fn_0048e760(NodeA*);
    void fn_0048e7c0(NodeA*);
};

// FUNCTION: DAO 0x0088E760
void TreeRot::fn_0048e760(NodeA* x) {
    NodeA* y = x->right;
    x->right = y->left;
    if (y->left->sentinel == 0) {
        y->left->parent = x;
    }
    y->parent = x->parent;
    if (x == header->parent) {
        header->parent = y;
        y->left = x;
        x->parent = y;
    } else {
        NodeA* p = x->parent;
        if (x == p->left) {
            p->left = y;
            y->left = x;
            x->parent = y;
        } else {
            p->right = y;
            y->left = x;
            x->parent = y;
        }
    }
}

// FUNCTION: DAO 0x0088E7C0
void TreeRot::fn_0048e7c0(NodeA* x) {
    NodeA* y = x->left;
    x->left = y->right;
    if (y->right->sentinel == 0) {
        y->right->parent = x;
    }
    y->parent = x->parent;
    if (x == header->parent) {
        header->parent = y;
        y->right = x;
        x->parent = y;
    } else {
        NodeA* p = x->parent;
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

struct Obj910 {
    void* field0;
    void* field4;
    unsigned char field8;
    unsigned char field9;
    Obj910* fn_004910c0(void*, void*);
    void fn_004910e0(void**);
    void fn_004910f0(void**);
};

// FUNCTION: DAO 0x008910C0
Obj910* Obj910::fn_004910c0(void* a, void* b) {
    field0 = a;
    field4 = b;
    field8 = 1;
    field9 = 1;
    return this;
}

// FUNCTION: DAO 0x008910E0
void Obj910::fn_004910e0(void** out) {
    *out = field0;
}

// FUNCTION: DAO 0x008910F0
void Obj910::fn_004910f0(void** out) {
    *out = field4;
}

struct NodeB;
struct TreeB;
struct IterPair {
    TreeB* first;
    NodeB* second;
};
struct NodeB {
    NodeB* left;
    NodeB* parent;
    NodeB* right;
    int key;
    unsigned char pad[0x1d];
    unsigned char sentinel;
};
struct TreeB {
    void* unused;
    NodeB* header;
    void fn_00495e40(IterPair*, int*);
};

// FUNCTION: DAO 0x00895E40
void TreeB::fn_00495e40(IterPair* out, int* key) {
    NodeB* header = this->header;
    NodeB* node = header->parent;
    NodeB* found = header;
    int k = *key;
    while (node->sentinel == 0) {
        if (node->key >= k) {
            found = node;
            node = node->left;
        } else {
            node = node->right;
        }
    }
    if (found == header || k < found->key) {
        out->first = this;
        out->second = header;
    } else {
        out->first = this;
        out->second = found;
    }
}

struct Obj973 {
    unsigned int field0;
    unsigned int field4;
    unsigned char pad[0x300];
    unsigned int table[1];
    Obj973* fn_004973e0();
    unsigned char fn_004973f0();
    unsigned int fn_00497400();
    void fn_00497420(unsigned char);
    void fn_00497430(unsigned int);
    unsigned int fn_004974c0(unsigned int);
};

// FUNCTION: DAO 0x008973E0
Obj973* Obj973::fn_004973e0() {
    field4 = 3;
    return this;
}

// FUNCTION: DAO 0x008973F0
unsigned char Obj973::fn_004973f0() {
    if (field4 == 3) return 0;
    return (unsigned char)field0;
}

// FUNCTION: DAO 0x00897400
unsigned int Obj973::fn_00497400() {
    if (field4 == 3) return 0;
    return field0;
}

// FUNCTION: DAO 0x00897420
void Obj973::fn_00497420(unsigned char v) {
    field4 = 0;
    *(unsigned char*)&field0 = v;
}

// FUNCTION: DAO 0x00897430
void Obj973::fn_00497430(unsigned int v) {
    field4 = 1;
    field0 = v;
}

// FUNCTION: DAO 0x008974C0
unsigned int Obj973::fn_004974c0(unsigned int index) {
    return table[index];
}

struct Obj985 {
    unsigned char pad70[0x70];
    unsigned int field70;
    unsigned char pad90[0x1c];
    unsigned int field90;
    void fn_004985b0(unsigned int);
    void fn_004985d0();
};

// FUNCTION: DAO 0x008985B0
void Obj985::fn_004985b0(unsigned int v) {
    if (field90 == 0) {
        field70 = v;
        field90 = 1;
    }
}

// FUNCTION: DAO 0x008985D0
void Obj985::fn_004985d0() {
    field90 = 0;
    field70 = 0;
}
