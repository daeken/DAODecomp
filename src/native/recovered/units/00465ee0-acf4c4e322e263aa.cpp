struct Triple {
    unsigned int a;
    unsigned int b;
    unsigned int c;
};

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

struct PairHolder {
    unsigned int a;
    unsigned int b;
    PairHolder* __thiscall fn_00480550(PairHolder* out);
    PairHolder* __thiscall fn_00480570(const PairHolder* x, const PairHolder* y);
};

struct IntNode {
    IntNode* left;
    IntNode* parent;
    IntNode* right;
    int key;
    char pad[0x39 - 0x10];
    unsigned char isnil;
};

struct IntTree;

struct IntPair {
    IntTree* first;
    IntNode* second;
    IntPair(IntTree* f, IntNode* s) : first(f), second(s) {}
};

struct IntTree {
    char pad0[4];
    IntNode* header;
    IntPair __thiscall fn_00480f10(const int* key);
};

// FUNCTION: DAO 0x401180
void __cdecl fn_00001180(Triple* dst, unsigned int count, const Triple* src) {
    if (count <= 0U) {
        return;
    }
    do {
        if (dst != 0) {
            dst->a = src->a;
            dst->b = src->b;
            dst->c = src->c;
        }
        ++dst;
    } while (--count > 0);
}

// FUNCTION: DAO 0x4151A0
StringNode* __thiscall StringTree::fn_000151a0(const StringKey* key) {
    StringNode* header = this->header;
    StringNode* result = header;
    StringNode* node = header->parent;
    if (node->isnil == 0) {
        unsigned int keycap = key->cap;
        unsigned int keylen = key->size;
        const char* keybuf = key->buf;
        do {
            const unsigned short* kptr;
            if (keycap >= 8) {
                kptr = *reinterpret_cast<const unsigned short* const*>(keybuf);
            } else {
                kptr = reinterpret_cast<const unsigned short*>(keybuf);
            }
            unsigned int nlen = node->keylen;
            const unsigned short* nptr;
            if (node->keycap >= 8) {
                nptr = *reinterpret_cast<const unsigned short* const*>(node->keybytes);
            } else {
                nptr = reinterpret_cast<const unsigned short*>(node->keybytes);
            }
            unsigned int n = (nlen < keylen) ? nlen : keylen;
            int cmp = 0;
            unsigned int i = n;
            while (i != 0) {
                unsigned short a = *nptr;
                unsigned short b = *kptr;
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                ++nptr;
                ++kptr;
                --i;
            }
            if (i == 0) {
                if (nlen < keylen) {
                    cmp = -1;
                } else if (nlen > keylen) {
                    cmp = 1;
                } else {
                    cmp = 0;
                }
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

// FUNCTION: DAO 0x67BC10
Triple* __cdecl fn_0027bc10(Triple* first, Triple* last, Triple* dest) {
    Triple* result = dest + (last - first);
    if (first != last) {
        do {
            *dest = *first;
            ++first;
            ++dest;
        } while (first != last);
    }
    return result;
}

// FUNCTION: DAO 0x865EE0
Triple* __cdecl fn_00465ee0(const Triple* first, const Triple* last, Triple* dest) {
    if (first == last) {
        return dest;
    }
    do {
        if (dest != 0) {
            dest->a = first->a;
            dest->b = first->b;
            dest->c = first->c;
        }
        ++first;
        ++dest;
    } while (first != last);
    return dest;
}

// FUNCTION: DAO 0x880550
PairHolder* __thiscall PairHolder::fn_00480550(PairHolder* out) {
    *out = *this;
    return out;
}

// FUNCTION: DAO 0x880570
PairHolder* __thiscall PairHolder::fn_00480570(const PairHolder* x, const PairHolder* y) {
    this->a = x->a | y->a | 0x10000000u;
    return this;
}

// FUNCTION: DAO 0x880F10
IntPair __thiscall IntTree::fn_00480f10(const int* key) {
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
    return (candidate == header || *key < candidate->key) ? IntPair(this, header) : IntPair(this, candidate);
}
