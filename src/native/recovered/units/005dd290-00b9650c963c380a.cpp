struct Node4 {
    Node4* next0;
    Node4* next4;
};

class CList {
public:
    char pad0[0x2c];
    bool fn_005dcf80(Node4* p);
};

// FUNCTION: DAO 0x9dcf80
bool CList::fn_005dcf80(Node4* p) {
    Node4* head = reinterpret_cast<Node4*>(reinterpret_cast<char*>(this) + 0x2c);
    Node4* a = p;
    Node4* b = p;
    if (a == head) return true;
    do {
        if (b == head) return false;
        a = a->next0;
        b = b->next4;
    } while (a != head);
    return true;
}

class CCopy {
public:
    unsigned int v0;
    unsigned int v1;
    unsigned int v2;
    unsigned int v3;
    unsigned int v4;
    CCopy& fn_005dd290(const CCopy& src);
};

// FUNCTION: DAO 0x9dd290
CCopy& CCopy::fn_005dd290(const CCopy& src) {
    v0 = src.v0;
    v1 = src.v1;
    v2 = src.v2;
    v3 = src.v3;
    v4 = src.v4;
    return *this;
}

struct HashEntry {
    int next;
    unsigned int key0;
    unsigned short key4;
    unsigned char key6;
    unsigned char key7;
    unsigned char key8;
    unsigned char key9;
    unsigned char key10;
    unsigned char key11;
};

struct HashKey {
    unsigned int d0;
    unsigned short w4;
    unsigned char b6;
    unsigned char b7;
    unsigned char b8;
    unsigned char b9;
    unsigned char b10;
    unsigned char b11;
};

class CHash {
public:
    unsigned char* base;
    int fn_005dd520(const HashKey* key, unsigned int index);
};

// FUNCTION: DAO 0x9dd520
int CHash::fn_005dd520(const HashKey* key, unsigned int index) {
    unsigned char* base = this->base;
    HashEntry* e = reinterpret_cast<HashEntry*>(base + index * 20u + 8u);
    unsigned int cur = index;
    if (e->next == -2) return -1;
    unsigned int mask = *reinterpret_cast<unsigned int*>(base + 4u);
    unsigned int h = static_cast<unsigned int>(e->key11)
        ^ (static_cast<unsigned int>(e->key9) << 1)
        ^ static_cast<unsigned int>(e->key10)
        ^ static_cast<unsigned int>(e->key8)
        ^ static_cast<unsigned int>(e->key7)
        ^ static_cast<unsigned int>(e->key6)
        ^ static_cast<unsigned int>(e->key4)
        ^ (e->key0 >> 6)
        ^ e->key0;
    if ((h & mask) != index) return -1;
    do {
        h = static_cast<unsigned int>(e->key11)
            ^ (static_cast<unsigned int>(e->key9) << 1)
            ^ static_cast<unsigned int>(e->key10)
            ^ static_cast<unsigned int>(e->key8)
            ^ static_cast<unsigned int>(e->key7)
            ^ static_cast<unsigned int>(e->key6)
            ^ static_cast<unsigned int>(e->key4)
            ^ (e->key0 >> 6)
            ^ e->key0;
        if ((h & mask) == index
            && e->key0 == key->d0
            && e->key4 == key->w4
            && e->key6 == key->b6
            && e->key7 == key->b7
            && e->key8 == key->b8
            && e->key9 == key->b9
            && e->key10 == key->b10
            && e->key11 == key->b11) {
            return static_cast<int>(cur);
        }
        cur = static_cast<unsigned int>(e->next);
        if (cur == 0xffffffffu) return -1;
        e = reinterpret_cast<HashEntry*>(base + cur * 20u + 8u);
    } while (true);
}

class CInit {
public:
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fC;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int f1C;
    unsigned int f20;
    unsigned int f24;
    unsigned int f28;
    void* p2c;
    void* p30;
    unsigned int f34;
    char pad38[0x14];
    void* p4c;
    void* p50;
    char pad54[0x0c];
    unsigned int f60;
    unsigned int f64;
    unsigned int f68;
    unsigned int f6c;
    unsigned int f70;
    unsigned int f74;
    unsigned int f78;
    unsigned int f7c;
    unsigned int f80;
    CInit* fn_005deee0();
};

// FUNCTION: DAO 0x9deee0
CInit* CInit::fn_005deee0() {
    CInit* p = this;
    unsigned int zero = 0;
    p->f0 = 0x0a;
    p->f4 = zero;
    p->f8 = zero;
    p->fC = zero;
    p->f10 = zero;
    p->f14 = zero;
    p->f18 = zero;
    p->f1C = zero;
    p->f20 = zero;
    p->f24 = 0x7f;
    p->f28 = zero;
    p->p2c = reinterpret_cast<void*>(reinterpret_cast<char*>(p) + 0x2c);
    p->p30 = reinterpret_cast<void*>(reinterpret_cast<char*>(p) + 0x2c);
    p->f34 = zero;
    p->p4c = reinterpret_cast<void*>(reinterpret_cast<char*>(p) + 0x38);
    p->p50 = reinterpret_cast<void*>(reinterpret_cast<char*>(p) + 0x38);
    p->f60 = zero;
    p->f64 = zero;
    p->f68 = 0x7f;
    p->f6c = zero;
    p->f70 = zero;
    p->f74 = zero;
    p->f78 = zero;
    p->f7c = zero;
    p->f80 = zero;
    return p;
}

// FUNCTION: DAO 0x9e1020
void fn_005e1020(unsigned char* out, const unsigned char* p0, const unsigned char* p1, const unsigned char* p2, const unsigned char* p3, unsigned int u, unsigned int v) {
    int b0 = static_cast<int>(p0[0]);
    int b1 = static_cast<int>(p0[1]);
    int b2 = static_cast<int>(p0[2]);
    int b3 = static_cast<int>(p0[3]);
    int vv = 256 - static_cast<int>(v);
    int uu = 256 - static_cast<int>(u);
    int w10 = vv * static_cast<int>(u);
    int w00 = vv * uu;
    int w01 = uu * static_cast<int>(v);
    int a0 = b0 * w00 + 0x8000;
    int a1 = b1 * w00 + 0x8000;
    int a2 = b2 * w00 + 0x8000;
    int a3 = b3 * w00 + 0x8000;
    a0 += static_cast<int>(p1[0]) * w10;
    a1 += static_cast<int>(p1[1]) * w10;
    a2 += static_cast<int>(p1[2]) * w10;
    a3 += static_cast<int>(p1[3]) * w10;
    a0 += static_cast<int>(p2[0]) * w01;
    a1 += static_cast<int>(p2[1]) * w01;
    a2 += static_cast<int>(p2[2]) * w01;
    a3 += static_cast<int>(p2[3]) * w01;
    int w11 = static_cast<int>(u) * static_cast<int>(v);
    a0 += static_cast<int>(p3[0]) * w11;
    a1 += static_cast<int>(p3[1]) * w11;
    a2 += static_cast<int>(p3[2]) * w11;
    a3 += static_cast<int>(p3[3]) * w11;
    out[0] = static_cast<unsigned char>(a0 >> 16);
    out[1] = static_cast<unsigned char>(a1 >> 16);
    out[2] = static_cast<unsigned char>(a2 >> 16);
    out[3] = static_cast<unsigned char>(a3 >> 16);
}

// FUNCTION: DAO 0x9e1130
void fn_005e1130(unsigned char* out, const unsigned char* p0, const unsigned char* p1, const unsigned char* p2, const unsigned char* p3, unsigned int u, unsigned int v) {
    int b0 = static_cast<int>(p0[0]);
    int b1 = static_cast<int>(p0[1]);
    int b2 = static_cast<int>(p0[2]);
    int vv = 256 - static_cast<int>(v);
    int uu = 256 - static_cast<int>(u);
    int w10 = vv * static_cast<int>(u);
    int w11 = static_cast<int>(u) * static_cast<int>(v);
    int w00 = vv * uu;
    int w01 = uu * static_cast<int>(v);
    int a0 = b0 * w00 + 0x8000;
    int a1 = b1 * w00 + 0x8000;
    int a2 = b2 * w00 + 0x8000;
    a0 += static_cast<int>(p1[0]) * w10;
    a1 += static_cast<int>(p1[1]) * w10;
    a2 += static_cast<int>(p1[2]) * w10;
    a0 += static_cast<int>(p2[0]) * w01;
    a1 += static_cast<int>(p2[1]) * w01;
    a2 += static_cast<int>(p2[2]) * w01;
    a0 += static_cast<int>(p3[0]) * w11;
    a1 += static_cast<int>(p3[1]) * w11;
    a2 += static_cast<int>(p3[2]) * w11;
    out[0] = static_cast<unsigned char>(a0 >> 16);
    out[1] = static_cast<unsigned char>(a1 >> 16);
    out[2] = static_cast<unsigned char>(a2 >> 16);
}
