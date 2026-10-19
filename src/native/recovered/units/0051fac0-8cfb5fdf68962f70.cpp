struct Entry16 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned char f12;
    unsigned char pad[3];
};
struct Table5 {
    Entry16 entries[5];
    unsigned char flags;
    void fn_0051fb70(unsigned int, const Entry16*);
    void fn_0051fe90(const Table5*);
};
struct HashEntry {
    int next;
    unsigned int key;
    unsigned int pad0;
    unsigned int pad1;
};
struct HashHeader {
    unsigned int pad0;
    unsigned int mask;
    HashEntry entries[1];
};
struct HashTable {
    HashHeader* h;
    int fn_005188f0(unsigned int*, unsigned int);
};
struct StrAtC {
    unsigned char pad[12];
    char s[1];
};
struct HolderC {
    StrAtC* p;
    bool fn_0051f8c0(const char*);
};
struct CStrPtr {
    const char** pp;
    bool fn_0051f920(const char*);
};
struct Counter {
    unsigned int pad0;
    unsigned int count;
    unsigned int fn_0051fac0(unsigned int);
};
struct Range {
    int start;
    int length;
    bool fn_0051fae0(const int*);
    int fn_0051fb10(int);
};
struct Status {
    unsigned char pad[0xc4];
    unsigned short flags;
    void fn_0051fe30(bool);
    void fn_0051fe50(bool);
    void fn_0051fe70(bool);
};
struct Inner64 {
    unsigned char pad[0x64];
    unsigned char flag;
};
struct Inner11C {
    unsigned char pad[0x11c];
    Inner64* q;
};
struct Inner50 {
    unsigned char pad[0x50];
    unsigned char flags;
};
struct Obj98 {
    unsigned char pad[0x98];
    Inner50* p98;
    Inner11C* p9c;
    bool fn_00520730();
};
struct Array16 {
    Entry16* base;
    int count;
};
struct Key4 {
    int pad0;
    int key;
};

// FUNCTION: DAO 0x009188f0
int HashTable::fn_005188f0(unsigned int* key, unsigned int idx) {
    HashEntry* base = h->entries;
    unsigned int mask = h->mask;
    unsigned int cur = idx;
    if (base[cur].next == -2) return -1;
    unsigned int k = base[cur].key;
    if (((k ^ (k >> 8)) & mask) != idx) return -1;
    for (;;) {
        k = base[cur].key;
        if (((k ^ (k >> 8)) & mask) == idx) {
            if (k == *key) return (int)cur;
        }
        int n = base[cur].next;
        if (n == -1) return -1;
        cur = (unsigned int)n;
    }
}

// FUNCTION: DAO 0x0091f8a0
unsigned int fn_0051f8a0(const unsigned short* s) {
    const unsigned short* p = s;
    while (*p) ++p;
    return (unsigned int)(p - s);
}

// FUNCTION: DAO 0x0091f8c0
bool HolderC::fn_0051f8c0(const char* s) {
    const char* a = p->s;
    while (*a == *s) {
        if (!*a) return true;
        ++a;
        ++s;
    }
    return false;
}

// FUNCTION: DAO 0x0091f920
bool CStrPtr::fn_0051f920(const char* s) {
    const char* a = *pp;
    while (*a == *s) {
        if (!*a) return true;
        ++a;
        ++s;
    }
    return false;
}

// FUNCTION: DAO 0x0091fac0
unsigned int Counter::fn_0051fac0(unsigned int amount) {
    if (amount > count) count = 0;
    else count -= amount;
    return count;
}

// FUNCTION: DAO 0x0091fae0
bool Range::fn_0051fae0(const int* r) {
    int a = start;
    int b = length;
    int p0 = r[0];
    int p1 = r[1];
    int end = p1 + p0 - 1;
    if (end < a) return false;
    int t = b + a - 1;
    if (t < p0) return false;
    return true;
}

// FUNCTION: DAO 0x0091fb10
int Range::fn_0051fb10(int x) {
    int a = start;
    int b = length;
    if (x < a) return a - x;
    int end = b + a - 1;
    if (x <= end) return 0;
    return b - x + a;
}

// FUNCTION: DAO 0x0091fb70
void Table5::fn_0051fb70(unsigned int index, const Entry16* src) {
    unsigned char bit = (unsigned char)(1u << (index & 31u));
    flags |= bit;
    Entry16* dst = &entries[index];
    dst->f0 = src->f0;
    dst->f4 = src->f4;
    dst->f8 = src->f8;
    dst->f12 = src->f12;
}

// FUNCTION: DAO 0x0091fe30
void Status::fn_0051fe30(bool v) {
    if (v) flags |= 2;
    else flags &= 0xfffd;
}

// FUNCTION: DAO 0x0091fe50
void Status::fn_0051fe50(bool v) {
    if (v) flags |= 4;
    else flags &= 0xfffb;
}

// FUNCTION: DAO 0x0091fe70
void Status::fn_0051fe70(bool v) {
    if (v) flags |= 0x80;
    else flags &= 0xff7f;
}

// FUNCTION: DAO 0x0091fe90
void Table5::fn_0051fe90(const Table5* src) {
    for (int i = 0; i < 5; ++i) {
        entries[i].f0 = src->entries[i].f0;
        entries[i].f4 = src->entries[i].f4;
        entries[i].f8 = src->entries[i].f8;
        entries[i].f12 = src->entries[i].f12;
    }
    flags = src->flags;
}

// FUNCTION: DAO 0x00920150
int fn_00520150(Array16* a, Key4* k) {
    int lo = 0;
    int hi = a->count;
    int target = k->key;
    while (hi > 0) {
        int half = hi >> 1;
        int mid = lo + half;
        int v = (int)a->base[mid].f4;
        if (v >= target) {
            hi = half;
        } else {
            lo = mid + 1;
            hi = hi - half - 1;
        }
    }
    return lo;
}

// FUNCTION: DAO 0x009201a0
int fn_005201a0(Array16* a, const int* key) {
    int lo = 0;
    int hi = a->count;
    int target = *key;
    while (hi > 0) {
        int half = hi >> 1;
        int mid = lo + half;
        int v = (int)a->base[mid].f4;
        if (v >= target) {
            hi = half;
        } else {
            lo = mid + 1;
            hi = hi - half - 1;
        }
    }
    return lo;
}

// FUNCTION: DAO 0x00920730
bool Obj98::fn_00520730() {
    Inner11C* x = p9c;
    if (x) {
        Inner64* y = x->q;
        if (y) return (y->flag & 1) != 0;
    }
    return ((p98->flags >> 3) & 1) != 0;
}
