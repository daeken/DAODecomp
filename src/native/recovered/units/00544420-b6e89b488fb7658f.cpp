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
    int fn_00535be0(unsigned int* key, unsigned int index);
};

struct Obj544420 {
    char c;
    int fn_00544420() const;
};

struct Block54920 {
    int f0;
    int size;
};
struct Obj54920 {
    int f0;
    Block54920* block;
    unsigned short f8;
    unsigned char fn_00544920(unsigned int a1, unsigned int a2, unsigned int a3);
};

struct Obj545ce0 {
    int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    int f14;
    unsigned int f18;
    const short* f1c;
    const int* f20;
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

// FUNCTION: DAO 0x00935be0
int Obj535be0::fn_00535be0(unsigned int* key, unsigned int index) {
    unsigned int i = index;
    Table535be0* t = table;
    Entry535be0* e = (Entry535be0*)((unsigned char*)t + 8 + (i << 4));
    int result = (int)i;
    if (e->next == -2) return -1;
    unsigned int mask = t->mask;
    if ((e->key & mask) != i) return -1;
    for (;;) {
        unsigned int k = e->key;
        if ((k & mask) == i) {
            if (k == *key) return result;
        }
        int next = e->next;
        if (next == -1) return -1;
        result = next;
        e = (Entry535be0*)((unsigned char*)t + 8 + ((unsigned int)next << 4));
    }
}

// FUNCTION: DAO 0x00944420
int Obj544420::fn_00544420() const {
    return c == 'A' || c == 'C';
}

// FUNCTION: DAO 0x00944840
unsigned int __fastcall fn_00544840(unsigned int count, const unsigned char* data) {
    register unsigned int seed;
    while (count) {
        seed = ((seed << 5) + seed) ^ (unsigned int)data[count - 1];
        --count;
    }
    return seed;
}

// FUNCTION: DAO 0x00944920
unsigned char Obj54920::fn_00544920(unsigned int a1, unsigned int a2, unsigned int a3) {
    if (a3 >= a2) return 0;
    Block54920* b = block;
    if (b == 0) return 0;
    int off = (int)a1 - (int)b - 8;
    if (off >= b->size) return 0;
    unsigned int tmp = (unsigned int)b->size - (unsigned int)off;
    if (tmp - a2 != (unsigned int)f8) return 0;
    tmp -= a3;
    if (tmp < 0x10000) f8 = (unsigned short)tmp;
    return 0;
}

// FUNCTION: DAO 0x009449d0
unsigned char* __fastcall fn_005449d0(unsigned int count, unsigned int, unsigned int value) {
    register unsigned char* dest;
    unsigned int shift = 0;
    while (count > 0) {
        *dest = (unsigned char)(value >> shift);
        ++dest;
        shift += 8;
        --count;
    }
    return dest;
}

// FUNCTION: DAO 0x00945ce0
int Obj545ce0::fn_00545ce0(int* out) {
    if (f4 >= f8) return (int)f4;
    if (f1c != 0) {
        if (f18 > 0x8000) {
            f14 = (int)*f1c;
            f1c = (const short*)((const char*)f1c + 2);
            f18 = 1;
        }
        out[0] = (int)*f1c;
        if ((f18 & (unsigned int)f14) != 0) {
            f1c = (const short*)((const char*)f1c + 2);
            out[1] = (int)*f1c;
            f1c = (const short*)((const char*)f1c + 2);
            out[2] = (int)*f1c;
            f1c = (const short*)((const char*)f1c + 2);
            out[3] = (int)*f1c;
            f1c = (const short*)((const char*)f1c + 2);
            ++f4;
            f18 <<= 1;
            out[4] = 4;
            return 4;
        } else {
            f1c = (const short*)((const char*)f1c + 2);
            out[1] = (int)*f1c;
            f1c = (const short*)((const char*)f1c + 2);
            ++f4;
            f18 <<= 1;
            out[4] = 2;
            return 2;
        }
    } else {
        if (f18 == 0) {
            f14 = (int)*f20;
            ++f20;
            f18 = 1;
        }
        out[0] = (int)*f20;
        if ((f18 & (unsigned int)f14) != 0) {
            ++f20;
            out[1] = (int)*f20;
            ++f20;
            out[2] = (int)*f20;
            ++f20;
            out[3] = (int)*f20;
            ++f20;
            ++f4;
            f18 <<= 1;
            out[4] = 4;
            return 4;
        } else {
            ++f20;
            out[1] = (int)*f20;
            ++f20;
            ++f4;
            f18 <<= 1;
            out[4] = 2;
            return 2;
        }
    }
}

// FUNCTION: DAO 0x00945e70
void Obj545e70::fn_00545e70() {
    unsigned short off = f14;
    unsigned char* base = (unsigned char*)((unsigned int)f8 - (unsigned int)off);
    int edx = (int)f4 - (int)base - 8;
    if (edx < *(int*)(base + 4)) return;
    unsigned char* next = *(unsigned char**)base;
    if (next == 0) {
        f4 = 0;
        return;
    }
    unsigned char* p = next + 8;
    f4 = p;
    f8 = p;
    f14 = (unsigned short)((unsigned int)p - (unsigned int)next);
}
