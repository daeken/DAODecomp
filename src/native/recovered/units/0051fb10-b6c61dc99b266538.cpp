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
    void __thiscall fn_0051fb70(unsigned int, const Entry16*);
    void __thiscall fn_0051fe90(const Table5*);
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
    int __thiscall fn_005188f0(unsigned int*, unsigned int);
};

struct StrAtC {
    unsigned char pad[12];
    char s[1];
};

struct HolderC {
    StrAtC* p;
    bool __thiscall fn_0051f8c0(const char*);
};

struct CStrPtr {
    const char** pp;
    bool __thiscall fn_0051f920(const char*);
};

struct Range {
    int start;
    int length;
    bool __thiscall fn_0051fae0(const int*);
    int __thiscall fn_0051fb10(int);
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
    unsigned char __thiscall fn_00520730();
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
int __thiscall HashTable::fn_005188f0(unsigned int* key, unsigned int idx) {
    HashHeader* base = h;
    unsigned int cur = idx;
    HashEntry* e = &base->entries[cur];
    if (e->next == -2)
        return -1;
    unsigned int k = e->key;
    unsigned int mask = base->mask;
    if (((k ^ (k >> 8)) & mask) != idx)
        return -1;
    for (;;) {
        k = e->key;
        if (((k ^ (k >> 8)) & mask) == idx) {
            if (k == *key)
                return (int)cur;
        }
        int n = e->next;
        if (n == -1)
            return -1;
        cur = (unsigned int)n;
        e = &base->entries[cur];
    }
}

// FUNCTION: DAO 0x0091f8a0
unsigned int __cdecl fn_0051f8a0(const unsigned short* s) {
    const unsigned short* p = s;
    const unsigned short* q = s + 1;
    while (*p++)
        ;
    return (unsigned int)(p - q);
}

// FUNCTION: DAO 0x0091f8c0
bool __thiscall HolderC::fn_0051f8c0(const char* s) {
    const char* a = p->s;
    for (;;) {
        if (*a != *s)
            return false;
        if (!*a)
            return true;
        if (a[1] != s[1])
            return false;
        a += 2;
        s += 2;
        if (!a[-1])
            return true;
    }
}

// FUNCTION: DAO 0x0091f920
bool __thiscall CStrPtr::fn_0051f920(const char* s) {
    const char* a = *pp;
    for (;;) {
        if (*a != *s)
            return false;
        if (!*a)
            return true;
        if (a[1] != s[1])
            return false;
        a += 2;
        s += 2;
        if (!a[-1])
            return true;
    }
}

// FUNCTION: DAO 0x0091fae0
bool __thiscall Range::fn_0051fae0(const int* r) {
    int a = start;
    int p0 = r[0];
    int p1 = r[1];
    int end = p1 + p0 - 1;
    if (end < a)
        return false;
    int last = a + length - 1;
    if (last < p0)
        return false;
    return true;
}

// FUNCTION: DAO 0x0091fb10
int __thiscall Range::fn_0051fb10(int x) {
    if (x < start || x > start + length - 1) {
        if (x < start)
            return start - x;
        return length - x + start;
    }
    return 0;
}

// FUNCTION: DAO 0x0091fb70
void __thiscall Table5::fn_0051fb70(unsigned int index, const Entry16* src) {
    unsigned char bit = 1;
    bit <<= index;
    Entry16* dst = entries + index;
    flags |= bit;
    dst->f0 = src->f0;
    dst->f4 = src->f4;
    dst->f8 = src->f8;
    dst->f12 = src->f12;
}

// FUNCTION: DAO 0x0091fe90
void __thiscall Table5::fn_0051fe90(const Table5* src) {
    Entry16* d = entries;
    const Entry16* s = src->entries;
    d[0].f0 = s[0].f0;
    d[0].f4 = s[0].f4;
    d[0].f8 = s[0].f8;
    d[0].f12 = s[0].f12;
    d[1].f0 = s[1].f0;
    d[1].f4 = s[1].f4;
    d[1].f8 = s[1].f8;
    d[1].f12 = s[1].f12;
    d[2].f0 = s[2].f0;
    d[2].f4 = s[2].f4;
    d[2].f8 = s[2].f8;
    d[2].f12 = s[2].f12;
    d[3].f0 = s[3].f0;
    d[3].f4 = s[3].f4;
    d[3].f8 = s[3].f8;
    d[3].f12 = s[3].f12;
    d[4].f0 = s[4].f0;
    d[4].f4 = s[4].f4;
    d[4].f8 = s[4].f8;
    d[4].f12 = s[4].f12;
    flags = src->flags;
}

// FUNCTION: DAO 0x00920150
int __cdecl fn_00520150(Array16* a, Key4* k) {
    int lo = 0;
    int hi = a->count;
    Entry16* base = a->base;
    int target = k->key;
    while (hi > 0) {
        int half = hi >> 1;
        int mid = lo + half;
        int diff = (int)base[mid].f4 - target;
        if (diff < 0) {
            lo = mid + 1;
            hi = hi - half - 1;
        } else {
            hi = half;
        }
    }
    return lo;
}

// FUNCTION: DAO 0x009201a0
int __cdecl fn_005201a0(Array16* a, const int* key) {
    int lo = 0;
    int hi = a->count;
    Entry16* base = a->base;
    int target = *key;
    while (hi > 0) {
        int half = hi >> 1;
        int mid = lo + half;
        int diff = (int)base[mid].f4 - target;
        if (diff < 0) {
            lo = mid + 1;
            hi = hi - half - 1;
        } else {
            hi = half;
        }
    }
    return lo;
}

// FUNCTION: DAO 0x00920730
unsigned char __thiscall Obj98::fn_00520730() {
    Inner64* y = p9c->q;
    if (y)
        return (unsigned char)(y->flag & 1);
    return (unsigned char)((p98->flags >> 3) & 1);
}
