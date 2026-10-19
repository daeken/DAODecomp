struct C365390 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned char f10;
    unsigned char pad11[3];
    unsigned int f14;
    unsigned int f18;
    unsigned int pad1c;
    unsigned int pad20;
    unsigned int f24;
    unsigned int f28;
    unsigned int f2c;
    unsigned int f30;
    C365390* fn_00365390(unsigned int, unsigned int, unsigned int, unsigned char, unsigned int, unsigned int, unsigned int);
};

struct CHeapObj {
    char pad0[0xbc];
    unsigned short* dataPtr;
    char pad2[0xc];
    unsigned int length;
    unsigned int capacity;
};

struct C39F2A0 {
    char pad0[0x2c];
    int f2c;
    int f30;
    void fn_0039f2a0(int);
};

struct C3B1950Obj {
    char pad0[8];
    C3B1950Obj* child8;
    char padC[0xd];
    unsigned char flag19;
};

struct C3B4470Node {
    C3B4470Node* left;
    C3B4470Node* parent;
    C3B4470Node* right;
    unsigned int key;
    char pad10[9];
    unsigned char flag19;
};

struct C3B4470;

struct C3B4470Pair {
    C3B4470* first;
    C3B4470Node* second;
    C3B4470Pair(C3B4470* a, C3B4470Node* b) : first(a), second(b) {}
};

struct C3B4470 {
    char pad0[4];
    C3B4470Node* header;
    C3B4470Pair fn_003b4470(const unsigned int* key);
};

struct C3C9690 {
    char pad0[0x18];
    int f18;
    int f1c;
    int fn_003c9690(const int* p);
};

// FUNCTION: DAO 0x00765390
C365390* C365390::fn_00365390(unsigned int a1, unsigned int a2, unsigned int a3, unsigned char a4, unsigned int a5, unsigned int a6, unsigned int a7) {
    this->f0 = a1;
    this->f4 = a2;
    this->f8 = a3;
    this->f10 = a4;
    this->fc = a5;
    this->f18 = 1;
    this->f14 = 1;
    this->f24 = 0xffffffffu;
    this->f28 = a6;
    this->f2c = a7;
    this->f30 = 0xffffffffu;
    return this;
}

// FUNCTION: DAO 0x00768950
void __cdecl fn_00368950(CHeapObj** first, int hole, int top, CHeapObj* value) {
    int parent = (hole - 1) / 2;
    while (hole > top) {
        CHeapObj* p = first[parent];
        unsigned int vlen = value->length;
        const unsigned short* vdata = (value->capacity >= 8) ? value->dataPtr : (const unsigned short*)((char*)value + 0xbc);
        unsigned int plen = p->length;
        const unsigned short* pdata = (p->capacity >= 8) ? p->dataPtr : (const unsigned short*)((char*)p + 0xbc);
        unsigned int n = (plen < vlen) ? plen : vlen;
        bool less;
        if (n == 0) {
            less = (plen < vlen);
        } else {
            for (;;) {
                unsigned short pc = *pdata;
                unsigned short vc = *vdata;
                if (pc != vc) {
                    less = (pc < vc);
                    break;
                }
                ++pdata;
                ++vdata;
                --n;
                if (n == 0) {
                    less = (plen < vlen);
                    break;
                }
            }
        }
        if (!less) {
            first[hole] = value;
            return;
        }
        first[hole] = p;
        hole = parent;
        parent = (hole - 1) / 2;
    }
    first[hole] = value;
}

// FUNCTION: DAO 0x0079F2A0
void C39F2A0::fn_0039f2a0(int delta) {
    int v = delta + this->f30;
    if (v > this->f2c) {
        v = this->f2c;
    }
    this->f30 = v;
}

// FUNCTION: DAO 0x007B1950
C3B1950Obj* __cdecl fn_003b1950(C3B1950Obj* p) {
    C3B1950Obj* x = p;
    C3B1950Obj* y = x->child8;
    if (y->flag19 != 0) {
        return x;
    }
    do {
        x = y;
        y = x->child8;
    } while (y->flag19 == 0);
    return x;
}

// FUNCTION: DAO 0x007B4470
C3B4470Pair C3B4470::fn_003b4470(const unsigned int* key) {
    C3B4470Node* header = this->header;
    C3B4470Node* node = header->parent;
    C3B4470Node* lower = header;
    if (node->flag19 == 0) {
        unsigned int k = *key;
        do {
            if (node->key >= k) {
                lower = node;
                node = node->left;
            } else {
                node = node->right;
            }
        } while (node->flag19 == 0);
    }
    C3B4470Pair result(this, lower);
    if (lower == header || *key < lower->key) {
        return C3B4470Pair(this, header);
    }
    return result;
}

// FUNCTION: DAO 0x007C9690
int C3C9690::fn_003c9690(const int* p) {
    int x = p[0];
    if (x < 0) {
        return 0;
    }
    int y = p[1];
    if (y < 0) {
        return 0;
    }
    if (x >= this->f18) {
        return 0;
    }
    if (y >= this->f1c) {
        return 0;
    }
    return 1;
}
