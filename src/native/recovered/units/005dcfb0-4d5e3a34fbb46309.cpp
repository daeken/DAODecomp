struct Node4 {
    Node4* next0;
    Node4* next4;
    unsigned int pad8;
    unsigned int padC;
    unsigned int pad10;
    unsigned int pad14;
    unsigned int pad18;
    unsigned int pad1C;
    unsigned short flags20;
};

class CList {
public:
    char pad0[0x2c];
    Node4 head;
    bool fn_005dcf80(Node4* p);
    void fn_005dcfb0();
};

class CCopy {
public:
    unsigned int v0;
    unsigned int v1;
    unsigned int v2;
    unsigned int v3;
    unsigned int v4;
    void fn_005dd290(const unsigned int* src);
};

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
    void fn_005deee0();
};

// FUNCTION: DAO 0x9dcf80
bool CList::fn_005dcf80(Node4* p) {
    Node4* head = reinterpret_cast<Node4*>(reinterpret_cast<char*>(this) + 0x2c);
    Node4* a = p;
    Node4* b = p;
    if (a == head) return true;
    while (b != head) {
        a = a->next0;
        b = b->next4;
        if (a == head) return true;
    }
    return false;
}

// FUNCTION: DAO 0x9dcfb0
void CList::fn_005dcfb0() {
    Node4* head = reinterpret_cast<Node4*>(reinterpret_cast<char*>(this) + 0x2c);
    Node4* n = head->next4;
    while (n != head) {
        n->flags20 = static_cast<unsigned short>(n->flags20 & 0x7fff);
        n = n->next4;
    }
}

// FUNCTION: DAO 0x9dd290
void CCopy::fn_005dd290(const unsigned int* src) {
    v0 = src[0];
    v1 = src[1];
    v2 = src[2];
    v3 = src[3];
    v4 = src[4];
}

// FUNCTION: DAO 0x9dd520
int CHash::fn_005dd520(const HashKey* key, unsigned int index) {
    unsigned char* b = base;
    HashEntry* e = reinterpret_cast<HashEntry*>(b + index * 20u + 8u);
    int cur = static_cast<int>(index);
    if (e->next == -2) return -1;
    unsigned int mask = *reinterpret_cast<unsigned int*>(b + 4u);
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
    for (;;) {
        unsigned int h2 = static_cast<unsigned int>(e->key11)
            ^ (static_cast<unsigned int>(e->key9) << 1)
            ^ static_cast<unsigned int>(e->key10)
            ^ static_cast<unsigned int>(e->key8)
            ^ static_cast<unsigned int>(e->key7)
            ^ static_cast<unsigned int>(e->key6)
            ^ static_cast<unsigned int>(e->key4)
            ^ (e->key0 >> 6)
            ^ e->key0;
        if ((h2 & mask) == index) {
            if (e->key0 == key->d0
                && e->key4 == key->w4
                && e->key6 == key->b6
                && e->key7 == key->b7
                && e->key8 == key->b8
                && e->key9 == key->b9
                && e->key10 == key->b10
                && e->key11 == key->b11) {
                return cur;
            }
        }
        int next = e->next;
        if (next == -1) return -1;
        cur = next;
        e = reinterpret_cast<HashEntry*>(b + static_cast<unsigned int>(cur) * 20u + 8u);
    }
}

// FUNCTION: DAO 0x9deee0
void CInit::fn_005deee0() {
    f0 = 0x0a;
    f4 = 0;
    f8 = 0;
    fC = 0;
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f1C = 0;
    f20 = 0;
    f24 = 0x7f;
    f28 = 0;
    p2c = reinterpret_cast<void*>(reinterpret_cast<char*>(this) + 0x2c);
    p30 = reinterpret_cast<void*>(reinterpret_cast<char*>(this) + 0x2c);
    f34 = 0;
    p4c = reinterpret_cast<void*>(reinterpret_cast<char*>(this) + 0x38);
    p50 = reinterpret_cast<void*>(reinterpret_cast<char*>(this) + 0x38);
    f60 = 0;
    f64 = 0;
    f68 = 0x7f;
    f6c = 0;
    f70 = 0;
    f74 = 0;
    f78 = 0;
    f7c = 0;
    f80 = 0;
}

// FUNCTION: DAO 0x9e1020
void fn_005e1020(unsigned char* out, const unsigned char* p0, const unsigned char* p1, const unsigned char* p2, const unsigned char* p3, unsigned int u, unsigned int v) {
    unsigned int w0 = (256u - v) * (256u - u);
    unsigned int w1 = (256u - v) * u;
    unsigned int w2 = (256u - u) * v;
    unsigned int w3 = u * v;
    for (int i = 0; i < 4; ++i) {
        unsigned int val = static_cast<unsigned int>(p0[i]) * w0
            + static_cast<unsigned int>(p1[i]) * w1
            + static_cast<unsigned int>(p2[i]) * w2
            + static_cast<unsigned int>(p3[i]) * w3
            + 0x8000u;
        out[i] = static_cast<unsigned char>(val >> 16);
    }
}

// FUNCTION: DAO 0x9e1130
void fn_005e1130(unsigned char* out, const unsigned char* p0, const unsigned char* p1, const unsigned char* p2, const unsigned char* p3, unsigned int u, unsigned int v) {
    unsigned int w0 = (256u - v) * (256u - u);
    unsigned int w1 = (256u - v) * u;
    unsigned int w2 = (256u - u) * v;
    unsigned int w3 = u * v;
    for (int i = 0; i < 3; ++i) {
        unsigned int val = static_cast<unsigned int>(p0[i]) * w0
            + static_cast<unsigned int>(p1[i]) * w1
            + static_cast<unsigned int>(p2[i]) * w2
            + static_cast<unsigned int>(p3[i]) * w3
            + 0x8000u;
        out[i] = static_cast<unsigned char>(val >> 16);
    }
}
