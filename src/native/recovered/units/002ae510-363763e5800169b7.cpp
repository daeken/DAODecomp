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

struct C_002cd5b0;

struct Node_002cd5b0 {
    Node_002cd5b0* left;
    Node_002cd5b0* parent;
    Node_002cd5b0* right;
    unsigned int key;
    char pad10;
    unsigned char isnil;
};

struct Pair_002cd5b0 {
    C_002cd5b0* first;
    Node_002cd5b0* second;
};

struct C_002cd5b0 {
    char pad0[4];
    Node_002cd5b0* header;
    Pair_002cd5b0* fn_002cd5b0(Pair_002cd5b0* out, const unsigned int* key);
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

struct C_003023d0_base {
    char pad0[4];
    void operator=(const C_003023d0_base&) {}
};

struct C_003023d0 : C_003023d0_base {
    unsigned int a4, a8, ac, a10, a14, a18, a1c, a20, a24, a28, a2c, a30, a34, a38, a3c, a40, a44, a48, a4c;
    unsigned char a50;
    char pad51[7];
    unsigned int a58, a5c, a60, a64, a68, a6c, a70, a74, a78;
    void fn_003023d0(const C_003023d0* src);
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

// FUNCTION: DAO 0x006AE510
void fn_002ae510(Node16_002ad870* dst, Node16_002ad870* end, const unsigned char* src) {
    while (dst != end) {
        unsigned short* sp = src ? (unsigned short*)(src + 0xc) : 0;
        dst->fc = *sp;
        unsigned int* ip = src ? (unsigned int*)(src + 4) : 0;
        dst->f8 = *(unsigned int*)((unsigned char*)ip + 4);
        dst += 1;
    }
}

// FUNCTION: DAO 0x006C9F80
int C_002c9f80::fn_002c9f80() {
    unsigned char one = 1;
    fa = 0;
    fd = 0;
    fe = 0;
    fdc = 0;
    f130 = 0;
    f16d = 0;
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
Pair_002cd5b0* C_002cd5b0::fn_002cd5b0(Pair_002cd5b0* out, const unsigned int* key) {
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
    if (y == header || *key < y->key) result.second = header;
    else result.second = y;
    *out = result;
    return out;
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
        unsigned int qlen = q->str.size;
        do {
            const unsigned short* qdata = (q->str.res >= 8) ? q->str.bx.ptr : q->str.bx.buf;
            unsigned int nlen = x->key.size;
            const unsigned short* ndata = (x->key.res >= 8) ? x->key.bx.ptr : x->key.bx.buf;
            unsigned int n = nlen < qlen ? nlen : qlen;
            int cmp = 0;
            const unsigned short* p = ndata;
            const unsigned short* qp = qdata;
            unsigned int cnt = n;
            while (cnt != 0) {
                unsigned short a = *p;
                unsigned short b = *qp;
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                ++p;
                ++qp;
                --cnt;
            }
            if (cmp == 0) {
                if (nlen < qlen) cmp = -1;
                else if (nlen > qlen) cmp = 1;
            }
            if (cmp < 0) x = x->right;
            else { y = x; x = x->left; }
        } while (!x->isnil);
    }
    return y;
}

// FUNCTION: DAO 0x007023D0
void C_003023d0::fn_003023d0(const C_003023d0* src) {
    *this = *src;
}

// FUNCTION: DAO 0x0070AB20
int __stdcall fn_0030ab20(int a, unsigned char b) {
    switch (a) {
    case 1:
        return 0x7541 + ((b != 0) ? 2 : 0);
    case 2:
        return 0x7542;
    default:
        return 0x7541;
    }
}
