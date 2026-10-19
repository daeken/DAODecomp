struct Triple { unsigned int a; unsigned int b; unsigned int c; };

struct StringNode {
    StringNode* left;
    StringNode* parent;
    StringNode* right;
    char pad0[4];
    char keybytes[16];
    unsigned int keylen;
    unsigned int keycap;
    char pad1[5];
    unsigned char isnil;
};

struct StringKey {
    char pad0[4];
    char buf[16];
    unsigned int size;
    unsigned int cap;
};

struct StringTree {
    char pad0[4];
    StringNode* header;
    StringNode* __thiscall fn_000151a0(const StringKey* key);
};

struct BlockHeader {
    char pad[0x18];
    unsigned int capacity;
};

struct RangeOwner {
    BlockHeader* base;
    unsigned int size;
    void* __thiscall fn_000d5360(void** out);
};

struct TreeNode {
    TreeNode* left;
    TreeNode* parent;
    TreeNode* right;
    char pad[0x2d - 12];
    unsigned char isnil;
};

struct TreeBase {
    char pad0[4];
    TreeNode* header;
    void __thiscall fn_001fe540(TreeNode* node);
    void __thiscall fn_00669080(TreeNode* node);
};

struct IntNode {
    IntNode* left;
    IntNode* parent;
    IntNode* right;
    int key;
    char pad[0x39 - 0x10];
    unsigned char isnil;
};

struct IntTree {
    char pad0[4];
    IntNode* header;
    void** __thiscall fn_00480f10(void** out, const int* key);
};

struct PairHolder {
    unsigned int a;
    unsigned int b;
    PairHolder* __thiscall fn_00480550(PairHolder* out);
    PairHolder* __thiscall fn_00480570(PairHolder* x, PairHolder* y);
    PairHolder* __thiscall fn_00480590(PairHolder* x, PairHolder* y);
    PairHolder* __thiscall fn_004805b0(PairHolder* x);
    PairHolder* __thiscall fn_004805d0(PairHolder* x);
};

struct SmallInit {
    unsigned int a;
    unsigned int b;
    unsigned char c;
    unsigned char d;
    SmallInit* __thiscall fn_00491090();
};

// FUNCTION: DAO 0x401180
void __cdecl fn_00001180(Triple* dst, unsigned int count, const Triple* src) {
    Triple* d = dst;
    while (count != 0) {
        if (d != 0) {
            *d = *src;
        }
        d += 1;
        count -= 1;
    }
}

// FUNCTION: DAO 0x4151A0
StringNode* __thiscall StringTree::fn_000151a0(const StringKey* key) {
    StringNode* header = this->header;
    StringNode* result = header;
    StringNode* node = header->parent;
    if (node->isnil == 0) {
        unsigned int kcap = key->cap;
        unsigned int klen = key->size;
        const unsigned short* kptr = (kcap >= 8) ? *reinterpret_cast<const unsigned short* const*>(key->buf) : reinterpret_cast<const unsigned short*>(key->buf);
        do {
            unsigned int ncap = node->keycap;
            unsigned int nlen = node->keylen;
            const unsigned short* nptr = (ncap >= 8) ? *reinterpret_cast<const unsigned short* const*>(node->keybytes) : reinterpret_cast<const unsigned short*>(node->keybytes);
            unsigned int min = (nlen < klen) ? nlen : klen;
            int cmp = 0;
            unsigned int i = 0;
            while (i < min) {
                unsigned short a = nptr[i];
                unsigned short b = kptr[i];
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                i += 1;
            }
            if (i == min) {
                if (nlen < klen) cmp = -1;
                else if (nlen > klen) cmp = 1;
                else cmp = 0;
            }
            if (cmp >= 0) {
                result = node;
                node = node->left;
            } else {
                node = node->right;
            }
        } while (node->isnil == 0);
    }
    return result;
}

// FUNCTION: DAO 0x4D5360
void* __thiscall RangeOwner::fn_000d5360(void** out) {
    BlockHeader* base = this->base;
    unsigned int size = this->size;
    unsigned int* o = reinterpret_cast<unsigned int*>(out);
    unsigned int baseAddr = reinterpret_cast<unsigned int>(base);
    unsigned int end = baseAddr + base->capacity;
    o[1] = size;
    o[0] = baseAddr;
    o[2] = 0;
    o[3] = end;
    if (end > baseAddr + size || end <= baseAddr) {
        o[0] = 0;
        o[1] = 0;
        o[3] = 0;
    }
    return out;
}

// FUNCTION: DAO 0x5FE540
void __thiscall TreeBase::fn_001fe540(TreeNode* node) {
    TreeNode* right = node->right;
    node->right = right->left;
    TreeNode* rl = right->left;
    if (rl->isnil == 0) {
        rl->parent = node;
    }
    right->parent = node->parent;
    TreeNode* header = this->header;
    if (node == header->parent) {
        header->parent = right;
        right->left = node;
        node->parent = right;
    } else {
        TreeNode* parent = node->parent;
        if (node == parent->left) {
            parent->left = right;
            right->left = node;
            node->parent = right;
        } else {
            parent->right = right;
            right->left = node;
            node->parent = right;
        }
    }
}

// FUNCTION: DAO 0x66CA50
void __cdecl fn_0026ca50(Triple* first, Triple* last, const Triple* value) {
    Triple* p = first;
    while (p != last) {
        *p = *value;
        p += 1;
    }
}

// FUNCTION: DAO 0x67BC10
void __cdecl fn_0027bc10(Triple* first, Triple* last, Triple* dest) {
    Triple* s = first;
    Triple* d = dest;
    while (s != last) {
        *d = *s;
        s += 1;
        d += 1;
    }
}

// FUNCTION: DAO 0x865EE0
void* __cdecl fn_00465ee0(const Triple* first, const Triple* last, Triple* dest) {
    Triple* d = dest;
    const Triple* s = first;
    while (s != last) {
        if (d != 0) {
            *d = *s;
        }
        s += 1;
        d += 1;
    }
    return d;
}

// FUNCTION: DAO 0x880550
PairHolder* __thiscall PairHolder::fn_00480550(PairHolder* out) {
    unsigned int va = this->a;
    unsigned int vb = this->b;
    out->a = va;
    out->b = vb;
    return out;
}

// FUNCTION: DAO 0x880570
PairHolder* __thiscall PairHolder::fn_00480570(PairHolder* x, PairHolder* y) {
    this->a = x->a | y->a | 0x10000000u;
    return this;
}

// FUNCTION: DAO 0x880590
PairHolder* __thiscall PairHolder::fn_00480590(PairHolder* x, PairHolder* y) {
    this->a = x->a | y->a | 0x20000000u;
    return this;
}

// FUNCTION: DAO 0x8805B0
PairHolder* __thiscall PairHolder::fn_004805b0(PairHolder* x) {
    this->a = x->a | 0x30000000u;
    return this;
}

// FUNCTION: DAO 0x8805D0
PairHolder* __thiscall PairHolder::fn_004805d0(PairHolder* x) {
    this->a = x->a | 0x40000000u;
    return this;
}

// FUNCTION: DAO 0x880F10
void** __thiscall IntTree::fn_00480f10(void** out, const int* key) {
    IntNode* header = this->header;
    IntNode* candidate = header;
    IntNode* node = header->parent;
    if (node->isnil == 0) {
        do {
            if (node->key >= *key) {
                candidate = node;
                node = node->left;
            } else {
                node = node->right;
            }
        } while (node->isnil == 0);
    }
    if (candidate == header || *key < candidate->key) {
        out[0] = this;
        out[1] = header;
    } else {
        out[0] = this;
        out[1] = candidate;
    }
    return out;
}

// FUNCTION: DAO 0x891090
SmallInit* __thiscall SmallInit::fn_00491090() {
    this->a = 0;
    this->b = 0;
    this->c = 0;
    this->d = 0;
    return this;
}

// FUNCTION: DAO 0xA69080
void __thiscall TreeBase::fn_00669080(TreeNode* node) {
    TreeNode* left = node->left;
    node->left = left->right;
    TreeNode* lr = left->right;
    if (lr->isnil == 0) {
        lr->parent = node;
    }
    left->parent = node->parent;
    TreeNode* header = this->header;
    if (node == header->parent) {
        header->parent = left;
        left->right = node;
        node->parent = left;
    } else {
        TreeNode* parent = node->parent;
        if (node == parent->right) {
            parent->right = left;
            left->right = node;
            node->parent = left;
        } else {
            parent->left = left;
            left->right = node;
            node->parent = left;
        }
    }
}
