struct C_002a9600 {
    char pad0[0x6f0];
    int begin;
    int end;
    int fn_002a9600();
};

struct C_002c23e0 {
    char pad0[0x114];
    unsigned int f114;
    unsigned int fn_002c23e0();
};

struct C_002c5100 {
    char pad0[0x74];
    unsigned int f74;
    void fn_002c5100(unsigned int v);
};

struct C_002c9e60 {
    char pad0[0xdc];
    unsigned int fdc;
    char pad_e0[0x144 - 0xe0];
    unsigned char f144;
    void fn_002c9e60();
};

struct C_002c9f80 {
    char pad0[8];
    unsigned char f8;
    unsigned char f9;
    unsigned char fa;
    unsigned char fb;
    unsigned char fc;
    unsigned char fd;
    unsigned char fe;
    char pad_f[0xdc - 0xf];
    unsigned int fdc;
    char pad_e0[0x130 - 0xe0];
    unsigned char f130;
    char pad_131[0x144 - 0x131];
    unsigned char f144;
    char pad_145[0x148 - 0x145];
    unsigned int f148;
    unsigned int f14c;
    unsigned int f150;
    unsigned int f154;
    unsigned int f158;
    char pad_15c[0x16c - 0x15c];
    unsigned char f16c;
    unsigned char f16d;
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

struct C_002ef100 {
    unsigned char* fn_002ef100();
};

struct C_002ffb20 {
    char pad0[0x100];
    unsigned char f100;
    unsigned char fn_002ffb20();
};

struct C_003023d0 {
    char pad0[4];
    unsigned int a4, a8, ac, a10, a14, a18, a1c, a20, a24, a28, a2c, a30, a34, a38, a3c, a40, a44, a48, a4c;
    unsigned char a50;
    char pad51[7];
    unsigned int a58, a5c, a60, a64, a68, a6c, a70, a74, a78;
    void fn_003023d0(const C_003023d0* src);
};

struct C_0030abe0 {
    char pad0[0x40];
    unsigned int f40;
    char pad44[0x4c - 0x44];
    unsigned int f4c;
    char pad50[0x54 - 0x50];
    unsigned int f54;
    unsigned int fn_0030abe0();
};

// FUNCTION: DAO 0x006A9600
int C_002a9600::fn_002a9600() {
    if (begin == 0) return 0;
    return (end - begin) >> 2;
}

// FUNCTION: DAO 0x006AD870
void fn_002ad870(unsigned char* src, unsigned char* end, unsigned char* dst) {
    while (src != end) {
        unsigned short* sp = src ? (unsigned short*)(src + 0xc) : 0;
        *(unsigned short*)(dst + 0xc) = *sp;
        unsigned int* ip = src ? (unsigned int*)(src + 4) : 0;
        *(unsigned int*)(dst + 8) = *(unsigned int*)((unsigned char*)ip + 4);
        src += 16;
        dst += 16;
    }
}

// FUNCTION: DAO 0x006AD8B0
void fn_002ad8b0(unsigned char* begin, unsigned char* end, unsigned char* dst_end) {
    while (begin != end) {
        end -= 16;
        dst_end -= 16;
        unsigned short* sp = end ? (unsigned short*)(end + 0xc) : 0;
        *(unsigned short*)(dst_end + 0xc) = *sp;
        unsigned int* ip = end ? (unsigned int*)(end + 4) : 0;
        *(unsigned int*)(dst_end + 8) = *(unsigned int*)((unsigned char*)ip + 4);
    }
}

// FUNCTION: DAO 0x006AE510
void fn_002ae510(unsigned char* dst_begin, unsigned char* dst_end, const unsigned char* src) {
    unsigned char* d = dst_begin;
    while (d != dst_end) {
        unsigned short* sp = src ? (unsigned short*)(src + 0xc) : 0;
        *(unsigned short*)(d + 0xc) = *sp;
        unsigned int* ip = src ? (unsigned int*)(src + 4) : 0;
        *(unsigned int*)(d + 8) = *(unsigned int*)((unsigned char*)ip + 4);
        d += 16;
    }
}

// FUNCTION: DAO 0x006C23E0
unsigned int C_002c23e0::fn_002c23e0() {
    return f114 + 0x20;
}

// FUNCTION: DAO 0x006C5100
void C_002c5100::fn_002c5100(unsigned int v) {
    f74 = v;
}

// FUNCTION: DAO 0x006C9E60
void C_002c9e60::fn_002c9e60() {
    if (fdc != 0) {
        fdc = 2;
        f144 = 1;
    }
}

// FUNCTION: DAO 0x006C9F80
int C_002c9f80::fn_002c9f80() {
    fa = 0;
    fd = 0;
    fe = 0;
    fdc = 0;
    f130 = 0;
    f16d = 0;
    f148 = 0;
    f8 = 1;
    f9 = 1;
    fb = 1;
    fc = 1;
    f16c = 1;
    f144 = 1;
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
    Node_002cd5b0* h = this->header;
    if (y == h || *key < y->key) {
        out->first = this;
        out->second = h;
    } else {
        out->first = this;
        out->second = y;
    }
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
        const unsigned short* qdata = (q->str.res >= 8) ? q->str.bx.ptr : q->str.bx.buf;
        do {
            unsigned int nlen = x->key.size;
            const unsigned short* ndata = (x->key.res >= 8) ? x->key.bx.ptr : x->key.bx.buf;
            unsigned int n = nlen < qlen ? nlen : qlen;
            int cmp = 0;
            unsigned int i = 0;
            while (i < n) {
                unsigned short a = ndata[i];
                unsigned short b = qdata[i];
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                ++i;
            }
            if (cmp == 0) {
                if (nlen < qlen) cmp = -1;
                else if (nlen > qlen) cmp = 1;
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

// FUNCTION: DAO 0x006EF100
unsigned char* C_002ef100::fn_002ef100() {
    return (unsigned char*)this + 4;
}

// FUNCTION: DAO 0x006FFB20
unsigned char C_002ffb20::fn_002ffb20() {
    return f100;
}

// FUNCTION: DAO 0x007023D0
void C_003023d0::fn_003023d0(const C_003023d0* src) {
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
}

// FUNCTION: DAO 0x0070AB20
int __stdcall fn_0030ab20(int a, unsigned char b) {
    if (a == 1) return 0x7541 + ((b != 0) ? 1 : 0);
    if (a == 2) return 0x7542;
    return 0x7541;
}

// FUNCTION: DAO 0x0070ABE0
unsigned int C_0030abe0::fn_0030abe0() {
    if (f40 != 0) return f4c;
    return f54;
}
