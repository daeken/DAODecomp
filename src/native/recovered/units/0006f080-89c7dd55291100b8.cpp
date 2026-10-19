class C1 {
public:
    unsigned char pad0[0x3c];
    unsigned int field3c;
    unsigned char pad40[0x14];
    void* field54;
    void fn_0006c740(unsigned int v);
};

class CFlags {
public:
    unsigned char pad0[0x6c];
    unsigned int flags;
    void fn_0006f080(unsigned char b);
    bool fn_0006f0a0();
    void fn_0006f0b0(unsigned char b);
    bool fn_0006f0d0();
};

class CAt {
public:
    void* fn_00074c10();
};

struct List45Node {
    List45Node* next;
    unsigned char pad[0x41];
    unsigned char field45;
};

class CStore {
public:
    unsigned char pad0[8];
    unsigned int offset8;
    void fn_00074e10(void* base, const unsigned int* src);
};

class CRange {
public:
    unsigned char pad0[4];
    int field4;
    int field8;
    int fn_00074f20();
    int fn_00074f30();
    int fn_00074f50();
    int fn_00074f80();
};

struct HeapNode {
    unsigned char pad0[0x3c];
    int key3c;
    unsigned char pad40[0x120 - 0x40];
    int key120;
};

struct TreeNode {
    TreeNode* left;
    TreeNode* parent;
    TreeNode* right;
    unsigned char pad[0x45 - 0xc];
    unsigned char field45;
};

class CTree {
public:
    unsigned char pad0[4];
    TreeNode* head;
    void fn_000780a0(TreeNode* node);
};

class COffset {
public:
    unsigned char pad0[8];
    unsigned int offset8;
};

// FUNCTION: DAO 0x46c740
void C1::fn_0006c740(unsigned int v) {
    field3c = v;
    if (v == 1) {
        field54 = (void*)((unsigned char*)this + 0x44);
    } else {
        field54 = (void*)((unsigned char*)this + 8);
    }
}

// FUNCTION: DAO 0x46f080
void CFlags::fn_0006f080(unsigned char b) {
    if (b) {
        flags |= 8u;
    } else {
        flags &= ~8u;
    }
}

// FUNCTION: DAO 0x46f0a0
bool CFlags::fn_0006f0a0() {
    return ((flags >> 3) & 1u) != 0;
}

// FUNCTION: DAO 0x46f0b0
void CFlags::fn_0006f0b0(unsigned char b) {
    if (b) {
        flags |= 0x20u;
    } else {
        flags &= ~0x20u;
    }
}

// FUNCTION: DAO 0x46f0d0
bool CFlags::fn_0006f0d0() {
    return ((flags >> 4) & 1u) != 0;
}

// FUNCTION: DAO 0x474c10
void* CAt::fn_00074c10() {
    return (void*)((unsigned char*)this + 0x6f00);
}

// FUNCTION: DAO 0x474df0
List45Node* __cdecl fn_00074df0(List45Node* p) {
    List45Node* prev = p;
    List45Node* cur = p->next;
    while (cur->field45 == 0) {
        prev = cur;
        cur = cur->next;
    }
    return prev;
}

// FUNCTION: DAO 0x474e10
void CStore::fn_00074e10(void* base, const unsigned int* src) {
    *(unsigned int*)((unsigned char*)base + offset8) = *src;
}

// FUNCTION: DAO 0x474f20
int CRange::fn_00074f20() {
    if (field4 == 0) {
        return 0;
    }
    return field8 - field4;
}

// FUNCTION: DAO 0x474f30
int CRange::fn_00074f30() {
    if (field4 == 0) {
        return 0;
    }
    return (field8 - field4) / 33;
}

// FUNCTION: DAO 0x474f50
int CRange::fn_00074f50() {
    if (field4 == 0) {
        return 0;
    }
    return (field8 - field4) / 69;
}

// FUNCTION: DAO 0x474f80
int CRange::fn_00074f80() {
    if (field4 == 0) {
        return 0;
    }
    return (field8 - field4) / 137;
}

// FUNCTION: DAO 0x4758c0
void __cdecl fn_000758c0(HeapNode** heap, int index, int stop, HeapNode* item) {
    int child = index;
    int parent = (child - 1) / 2;
    if (stop >= child) {
        heap[child] = item;
        return;
    }
    for (;;) {
        HeapNode* p = heap[parent];
        if (p->key120 < item->key120 ||
            (p->key120 == item->key120 && p->key3c < item->key3c)) {
            heap[child] = p;
            child = parent;
            parent = (child - 1) / 2;
            if (stop >= child) {
                break;
            }
        } else {
            break;
        }
    }
    heap[child] = item;
}

// FUNCTION: DAO 0x4780a0
void CTree::fn_000780a0(TreeNode* node) {
    TreeNode* right = node->right;
    node->right = right->left;
    if (right->left->field45 == 0) {
        right->left->parent = node;
    }
    right->parent = node->parent;
    if (node == head->parent) {
        head->parent = right;
    } else if (node == node->parent->left) {
        node->parent->left = right;
    } else {
        node->parent->right = right;
    }
    right->left = node;
    node->parent = right;
}

// FUNCTION: DAO 0x4785e0
unsigned int __cdecl fn_000785e0(COffset* obj, const unsigned char* data) {
    return *(const unsigned int*)(data + obj->offset8);
}

// FUNCTION: DAO 0x478930
void __cdecl fn_00078930(HeapNode** a, HeapNode** b, HeapNode** c) {
    HeapNode* x = *a;
    HeapNode* y = *b;
    if (y->key120 < x->key120 ||
        (y->key120 == x->key120 && y->key3c < x->key3c)) {
        *b = x;
        *a = y;
    }
    x = *b;
    y = *c;
    if (y->key120 < x->key120 ||
        (y->key120 == x->key120 && y->key3c < x->key3c)) {
        *c = x;
        *b = y;
    }
    x = *a;
    y = *b;
    if (y->key120 < x->key120 ||
        (y->key120 == x->key120 && y->key3c < x->key3c)) {
        *b = x;
        *a = y;
    }
}
