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

struct IntTree {
    char pad0[4];
    IntNode* header;
    void** __thiscall fn_00480f10(void** out, const int* key);
};

// FUNCTION: DAO 0x401180
void __cdecl fn_00001180(Triple* dst, unsigned int count, const Triple* src) {
    if (count <= 0U) {
        return;
    }
    const Triple* s = src;
    Triple* d = dst;
    do {
        if (d != 0) {
            d->a = s->a;
            d->b = s->b;
            d->c = s->c;
        }
        ++d;
    } while (--count > 0U);
}

// FUNCTION: DAO 0x4151A0
StringNode* __thiscall StringTree::fn_000151a0(const StringKey* key) {
    StringNode* result = this->header;
    StringNode* node = result->parent;
    if (node->isnil != 0) {
        return result;
    }
    unsigned int keycap = key->cap;
    unsigned int keylen = key->size;
    const char* keybuf = key->buf;
    do {
        const unsigned short* kptr;
        if (keycap < 8U) {
            kptr = reinterpret_cast<const unsigned short*>(keybuf);
        } else {
            kptr = *reinterpret_cast<const unsigned short* const*>(keybuf);
        }
        unsigned int nlen = node->keylen;
        unsigned int min = (nlen < keylen) ? nlen : keylen;
        const unsigned short* nptr;
        if (node->keycap < 8U) {
            nptr = reinterpret_cast<const unsigned short*>(node->keybytes);
        } else {
            nptr = *reinterpret_cast<const unsigned short* const*>(node->keybytes);
        }
        int cmp = 0;
        unsigned int i = min;
        while (i != 0U) {
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
        if (i == 0U) {
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
    return result;
}

// FUNCTION: DAO 0x67BC10
Triple* __cdecl fn_0027bc10(Triple* first, Triple* last, Triple* dest) {
    Triple* result = dest + (last - first);
    if (first != last) {
        Triple* p = first;
        do {
            *reinterpret_cast<Triple*>(reinterpret_cast<char*>(dest) + (reinterpret_cast<char*>(p) - reinterpret_cast<char*>(first))) = *p;
            ++p;
        } while (p != last);
    }
    return result;
}

// FUNCTION: DAO 0x880550
PairHolder* __thiscall PairHolder::fn_00480550(PairHolder* out) {
    unsigned int a = this->a;
    PairHolder* p = out;
    unsigned int b = this->b;
    p->a = a;
    p->b = b;
    return p;
}

// FUNCTION: DAO 0x880570
PairHolder* __thiscall PairHolder::fn_00480570(const PairHolder* x, const PairHolder* y) {
    this->a = x->a | y->a | 0x10000000u;
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
    IntNode* result = (candidate == header || *key < candidate->key) ? header : candidate;
    out[0] = this;
    out[1] = result;
    return out;
}
