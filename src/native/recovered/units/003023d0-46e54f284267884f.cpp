struct Node16_002ad870 {
    unsigned char pad0[8];
    unsigned int f8;
    unsigned short fc;
    unsigned char pad_e[2];
};

struct C_002c9f80 {
    char pad0[8];
    unsigned char f8, f9, fa, fb, fc, fd, fe;
    char pad_f[0xdc - 0xf];
    unsigned int fdc;
    char pad_e0[0x130 - 0xe0];
    unsigned char f130;
    char pad_131[0x144 - 0x131];
    unsigned char f144;
    char pad_145[0x148 - 0x145];
    unsigned int f148, f14c, f150, f154, f158;
    char pad_15c[0x16c - 0x15c];
    unsigned char f16c, f16d;
    int fn_002c9f80();
};

struct Node_002cd5b0 {
    Node_002cd5b0* left;
    Node_002cd5b0* parent;
    Node_002cd5b0* right;
    unsigned int key;
    char pad10;
    unsigned char isnil;
};

struct C_002cd5b0;

struct Pair_002cd5b0 {
    C_002cd5b0* first;
    Node_002cd5b0* second;
};

struct C_002cd5b0 {
    char pad0[4];
    Node_002cd5b0* header;
    Pair_002cd5b0 fn_002cd5b0(const unsigned int* key);
};

struct C_002eace0 {
    char pad0[8];
    unsigned int index;
    int fn_002eace0(void* dst, const unsigned short* src);
};

struct String_002ee3e0 {
    union Bx_002ee3e0 {
        unsigned short buf[8];
        unsigned short* ptr;
    } bx;
    unsigned int size;
    unsigned int res;
};

struct Node_002ee3e0 {
    Node_002ee3e0* left;
    Node_002ee3e0* parent;
    Node_002ee3e0* right;
    unsigned int pad0;
    String_002ee3e0 key;
    char pad_28[0x39 - 0x28];
    unsigned char isnil;
};

struct Query_002ee3e0 {
    char pad0[4];
    String_002ee3e0 str;
};

struct C_002ee3e0 {
    char pad0[4];
    Node_002ee3e0* header;
    Node_002ee3e0* fn_002ee3e0(const Query_002ee3e0* q);
};

struct C_003023d0 {
    char pad0[4];
    unsigned int a4, a8, ac, a10, a14, a18, a1c, a20, a24, a28, a2c, a30, a34, a38, a3c, a40, a44, a48, a4c;
    unsigned char a50;
    char pad51[7];
    unsigned int a58, a5c, a60, a64, a68, a6c, a70, a74, a78;
    C_003023d0* fn_003023d0(const C_003023d0* src);
};

// FUNCTION: DAO 0x006AD870
void fn_002ad870(unsigned char* src, unsigned char* end, Node16_002ad870* dst) {
    while (src != end) {
        unsigned short* sp = src ? (unsigned short*)(src + 0xc) : 0;
        dst->fc = *sp;
        unsigned int* ip = src ? (unsigned int*)(src + 4) : 0;
        dst->f8 = *(unsigned int*)((unsigned char*)ip + 4);
        src += 16;
        dst += 1;
    }
}

// FUNCTION: DAO 0x006AD8B0
void fn_002ad8b0(unsigned char* begin, unsigned char* end, Node16_002ad870* dst_end) {
    while (begin != end) {
        end -= 16;
        dst_end -= 1;
        unsigned short* sp = end ? (unsigned short*)(end + 0xc) : 0;
        dst_end->fc = *sp;
        unsigned int* ip = end ? (unsigned int*)(end + 4) : 0;
        dst_end->f8 = *(unsigned int*)((unsigned char*)ip + 4);
    }
}

// FUNCTION: DAO 0x006C9F80
int C_002c9f80::fn_002c9f80() {
    unsigned char zero = 0;
    unsigned char one = 1;
    fa = zero;
    fd = zero;
    fe = zero;
    fdc = 0;
    f130 = zero;
    f16d = zero;
    f148 = 0;
    f8 = one;
    f9 = one;
    fb = one;
    fc = one;
    f16c = one;
    f144 = one;
    f14c = 0xffffffffu;
    f150 = 0xffffffffu;
    f154 = 0xffffffffu;
    f158 = 0xffffffffu;
    return -1;
}

// FUNCTION: DAO 0x006CD5B0
Pair_002cd5b0 C_002cd5b0::fn_002cd5b0(const unsigned int* key) {
    Node_002cd5b0* header = this->header;
    Node_002cd5b0* x = header->parent;
    Node_002cd5b0* y = header;
    while (!x->isnil) {
        if (x->key < *key) {
            x = x->right;
        } else {
            y = x;
            x = x->left;
        }
    }
    Pair_002cd5b0 result;
    result.first = this;
    if (y == header || *key < y->key) {
        result.second = header;
    } else {
        result.second = y;
    }
    return result;
}

// FUNCTION: DAO 0x006EACE0
int C_002eace0::fn_002eace0(void* dst, const unsigned short* src) {
    unsigned int i = index;
    unsigned short v = *src;
    *(unsigned short*)((unsigned char*)dst + i) = v;
    return (int)i;
}

// FUNCTION: DAO 0x006EE3E0
Node_002ee3e0* C_002ee3e0::fn_002ee3e0(const Query_002ee3e0* q) {
    Node_002ee3e0* header = this->header;
    Node_002ee3e0* x = header->parent;
    Node_002ee3e0* y = header;
    if (!x->isnil) {
        unsigned int qsize = q->str.size;
        unsigned int qres = q->str.res;
        const unsigned short* qdata = (qres >= 8) ? q->str.bx.ptr : q->str.bx.buf;
        do {
            unsigned int nsize = x->key.size;
            unsigned int nres = x->key.res;
            const unsigned short* ndata = (nres >= 8) ? x->key.bx.ptr : x->key.bx.buf;
            unsigned int min = (nsize < qsize) ? nsize : qsize;
            int cmp = 0;
            const unsigned short* p1 = ndata;
            const unsigned short* p2 = qdata;
            unsigned int count = min;
            while (count != 0) {
                unsigned short a = *p1;
                unsigned short b = *p2;
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                ++p1;
                ++p2;
                --count;
            }
            if (cmp == 0) {
                if (nsize < qsize) cmp = -1;
                else if (nsize > qsize) cmp = 1;
            }
            if (cmp < 0) {
                x = x->right;
            } else {
                y = x;
                x = x->left;
            }
        } while (!x->isnil);
    }
    return y;
}

// FUNCTION: DAO 0x007023D0
C_003023d0* C_003023d0::fn_003023d0(const C_003023d0* src) {
    a4 = src->a4;
    a8 = src->a8;
    ac = src->ac;
    a10 = src->a10;
    a14 = src->a14;
    a18 = src->a18;
    a1c = src->a1c;
    a20 = src->a20;
    a24 = src->a24;
    a28 = src->a28;
    a2c = src->a2c;
    a30 = src->a30;
    a34 = src->a34;
    a38 = src->a38;
    a3c = src->a3c;
    a40 = src->a40;
    a44 = src->a44;
    a48 = src->a48;
    a4c = src->a4c;
    a50 = src->a50;
    a58 = src->a58;
    a5c = src->a5c;
    a60 = src->a60;
    a64 = src->a64;
    a68 = src->a68;
    a6c = src->a6c;
    a70 = src->a70;
    a74 = src->a74;
    a78 = src->a78;
    return this;
}

// FUNCTION: DAO 0x0070AB20
int __stdcall fn_0030ab20(int a, unsigned char b) {
    if (a == 1) {
        unsigned int temp = (b != 0) ? 1 : 0;
        return 0x7541 + temp * 2;
    } else if (a == 2) {
        return 0x7542;
    } else {
        return 0x7541;
    }
}
