struct Entry535be0 {
    int next;
    unsigned int key;
    int pad0;
    int pad1;
};
struct Table535be0 {
    int field0;
    unsigned int mask;
    Entry535be0 entries[1];
};
struct Obj535be0 {
    Table535be0* table;
    int fn_00535be0(unsigned int* pKey, unsigned int index);
};

struct Obj544420 {
    char c;
    bool fn_00544420() const;
};

struct Obj544860 {
    int f0;
    int f4;
    unsigned short f8;
    unsigned short fA;
    Obj544860* fn_00544860(unsigned short v);
};

struct Block54920 {
    int f0;
    unsigned int size;
};
struct Obj54920 {
    int f0;
    Block54920* block;
    unsigned short f8;
    unsigned char fn_00544920(unsigned int a1, unsigned int a2, unsigned int a3);
};

struct Obj54980 {
    int f0;
    int f4;
    unsigned short f8;
    unsigned short fA;
    void fn_00544980(unsigned short v);
};

struct Obj549a0 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int f1c;
    unsigned int f20;
    unsigned int f24;
    unsigned int f28;
    unsigned int f2c;
    unsigned int f30;
    unsigned char f34;
    unsigned char f35;
    void fn_005449a0();
};

struct Obj545ce0 {
    int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    int f14;
    unsigned int f18;
    const unsigned short* f1c;
    const unsigned int* f20;
    int fn_00545ce0(int* out);
};

struct Obj545e70 {
    int f0;
    unsigned char* f4;
    unsigned char* f8;
    unsigned int fc;
    unsigned int f10;
    unsigned short f14;
    void fn_00545e70();
};

struct Obj54d2a0 {
    unsigned char pad[0x8c];
    unsigned short f8c;
    void fn_0054d2a0(bool flag);
};

struct Node54d510 {
    Node54d510* next;
};
struct Obj54d510 {
    unsigned char pad[0xb14];
    Node54d510* head;
    void fn_0054d510(Node54d510* p);
};

struct Obj54d5e0 {
    unsigned char pad0[0x5c];
    unsigned int f5c;
    unsigned int f60;
    unsigned int f64;
    void fn_0054d5e0(unsigned int* out);
};

struct Obj54d600 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    Obj54d600* fn_0054d600(unsigned int arg);
};

struct Obj564e90 {
    unsigned char pad[0x9c];
    unsigned char* f9c;
    void fn_00564e90();
};

// FUNCTION: DAO 0x00935be0
int Obj535be0::fn_00535be0(unsigned int* pKey, unsigned int index) {
    Table535be0* t = table;
    unsigned int i = index;
    Entry535be0* e = (Entry535be0*)((unsigned char*)t + 8 + (i << 4));
    int result = (int)i;
    if (e->next == -2) return -1;
    unsigned int mask = t->mask;
    if ((e->key & mask) != i) return -1;
    for (;;) {
        if ((e->key & mask) == i) {
            if (e->key == *pKey) return result;
        }
        int next = e->next;
        if (next == -1) return -1;
        result = next;
        e = (Entry535be0*)((unsigned char*)t + 8 + ((unsigned int)next << 4));
    }
}

// FUNCTION: DAO 0x00944420
bool Obj544420::fn_00544420() const {
    char al = c;
    if (al == 'A') return true;
    if (al == 'C') return true;
    return false;
}

// FUNCTION: DAO 0x00944840
unsigned int __fastcall fn_00544840(unsigned int count, const unsigned char* data) {
    unsigned int seed;
    while (count) {
        seed = (seed * 33) ^ (unsigned int)data[count - 1];
        --count;
    }
    return seed;
}

// FUNCTION: DAO 0x00944860
Obj544860* Obj544860::fn_00544860(unsigned short v) {
    f0 = 0;
    f4 = 0;
    f8 = 0;
    fA = v;
    return this;
}

// FUNCTION: DAO 0x00944920
unsigned char Obj54920::fn_00544920(unsigned int a1, unsigned int a2, unsigned int a3) {
    if (a3 >= a2) return 0;
    Block54920* b = block;
    if (!b) return 0;
    int ebx = (int)a1 - (int)b - 8;
    if (ebx >= (int)b->size) return 0;
    unsigned int eax = a1 - (unsigned int)b - 8;
    unsigned int edx = b->size;
    edx -= eax;
    unsigned int tmp = edx - a2;
    if (tmp != (unsigned int)f8) return 0;
    edx -= a3;
    if (edx < 0x10000) f8 = (unsigned short)edx;
    return 0;
}

// FUNCTION: DAO 0x00944980
void Obj54980::fn_00544980(unsigned short v) {
    if (f0 == 0) fA = v;
}

// FUNCTION: DAO 0x009449a0
void Obj549a0::fn_005449a0() {
    f8 = 0;
    f4 = 0;
    f0 = 0;
    f18 = 0;
    f14 = 0;
    f10 = 0;
    fc = 0;
    f28 = 0;
    f2c = 0;
    f30 = 0;
    f34 = 0;
    f35 = 0;
}

// FUNCTION: DAO 0x009449d0
void __fastcall fn_005449d0(unsigned int count, unsigned int value) {
    unsigned char* dest;
    unsigned int shift = 0;
    while (count) {
        *dest = (unsigned char)(value >> shift);
        ++dest;
        shift += 8;
        --count;
    }
}

// FUNCTION: DAO 0x00945ce0
int Obj545ce0::fn_00545ce0(int* out) {
    if (f4 >= f8) return (int)f4;
    if (f1c) {
        if (f18 > 0x8000) {
            f14 = (int)*(const short*)f1c;
            f1c++;
            f18 = 1;
        }
        const unsigned short* p = f1c;
        out[0] = (int)*(const short*)p;
        if ((f18 & (unsigned int)f14) != 0) {
            p++; out[1] = (int)*(const short*)p;
            p++; out[2] = (int)*(const short*)p;
            p++; out[3] = (int)*(const short*)p;
            p++;
            f1c = p;
            f4++;
            f18 <<= 1;
            out[4] = 4;
            return 4;
        } else {
            p++; out[1] = (int)*(const short*)p;
            p++;
            f1c = p;
            f4++;
            f18 <<= 1;
            out[4] = 2;
            return 2;
        }
    } else {
        if (f18 == 0) {
            const unsigned int* p = f20;
            f14 = (int)*p;
            p++;
            f20 = p;
            f18 = 1;
        }
        const unsigned int* p = f20;
        out[0] = (int)*p;
        if ((f18 & (unsigned int)f14) != 0) {
            p++; out[1] = (int)*p;
            p++; out[2] = (int)*p;
            p++; out[3] = (int)*p;
            p++;
            f20 = p;
            f4++;
            f18 <<= 1;
            out[4] = 4;
            return 4;
        } else {
            p++; out[1] = (int)*p;
            p++;
            f20 = p;
            f4++;
            f18 <<= 1;
            out[4] = 2;
            return 2;
        }
    }
}

// FUNCTION: DAO 0x00945e70
void Obj545e70::fn_00545e70() {
    unsigned int off = f14;
    unsigned char* base = (unsigned char*)((unsigned int)f8 - off);
    int edx = (int)f4 - (int)base - 8;
    if (edx < *(int*)(base + 4)) return;
    unsigned char* next = *(unsigned char**)base;
    if (next) {
        f4 = next + 8;
        f8 = next + 8;
        f14 = (unsigned short)((unsigned int)(next + 8) - (unsigned int)next);
    } else {
        f4 = 0;
    }
}

// FUNCTION: DAO 0x0094d2a0
void Obj54d2a0::fn_0054d2a0(bool flag) {
    if (flag) f8c |= 4;
    else f8c &= 0xfffb;
}

// FUNCTION: DAO 0x0094d510
void Obj54d510::fn_0054d510(Node54d510* p) {
    Node54d510* cur = head;
    if (!cur) {
        head = p;
        return;
    }
    while (cur->next) cur = cur->next;
    cur->next = p;
}

// FUNCTION: DAO 0x0094d5e0
void Obj54d5e0::fn_0054d5e0(unsigned int* out) {
    if (out) *out = f5c;
    f64++;
    f5c = f64;
}

// FUNCTION: DAO 0x0094d600
Obj54d600* Obj54d600::fn_0054d600(unsigned int arg) {
    f4 = arg;
    f0 = 0;
    fc = 0;
    f8 = 0;
    return this;
}

// FUNCTION: DAO 0x00964e90
void Obj564e90::fn_00564e90() {
    f9c[0x9ca] = 1;
}
