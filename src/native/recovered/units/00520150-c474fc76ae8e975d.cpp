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
    void __thiscall fn_0051fb70(unsigned int index, const Entry16* src);
    void __thiscall fn_0051fe90(const Table5* src);
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
    int __thiscall fn_005188f0(unsigned int* key, unsigned int idx);
};

struct StrAtC {
    unsigned char pad[12];
    char s[1];
};

struct HolderC {
    StrAtC* p;
    bool __thiscall fn_0051f8c0(const char* s);
};

struct CStrPtr {
    const char** pp;
    bool __thiscall fn_0051f920(const char* s);
};

struct Range {
    int start;
    int length;
    bool __thiscall fn_0051fae0(const int* r);
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
int __thiscall HashTable::fn_005188f0(unsigned int* key, unsigned int idx)
{
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
unsigned int __cdecl fn_0051f8a0(const unsigned short* s)
{
    const unsigned short* p = s;
    while (*p++)
        ;
    return (unsigned int)(p - (s + 1));
}

// FUNCTION: DAO 0x0091f8c0
bool __thiscall HolderC::fn_0051f8c0(const char* s)
{
    const char* a = p->s;
    for (;;) {
        char c = *a;
        if (c != *s)
            return false;
        if (c == 0)
            return true;
        c = a[1];
        if (c != s[1])
            return false;
        a += 2;
        s += 2;
        if (c == 0)
            return true;
    }
}

// FUNCTION: DAO 0x0091f920
bool __thiscall CStrPtr::fn_0051f920(const char* s)
{
    const char* a = *pp;
    for (;;) {
        char c = *a;
        if (c != *s)
            return false;
        if (c == 0)
            return true;
        c = a[1];
        if (c != s[1])
            return false;
        a += 2;
        s += 2;
        if (c == 0)
            return true;
    }
}

// FUNCTION: DAO 0x0091fae0
bool __thiscall Range::fn_0051fae0(const int* r)
{
    int end = r[1] + r[0] - 1;
    if (end < start)
        return false;
    int last = start + length - 1;
    if (last < r[0])
        return false;
    return true;
}

// FUNCTION: DAO 0x0091fb70
void __thiscall Table5::fn_0051fb70(unsigned int index, const Entry16* src)
{
    unsigned char bit = 1;
    bit <<= index;
    Entry16* dst = &entries[index];
    flags |= bit;
    dst->f0 = src->f0;
    dst->f4 = src->f4;
    dst->f8 = src->f8;
    dst->f12 = src->f12;
}

// FUNCTION: DAO 0x0091fe90
void __thiscall Table5::fn_0051fe90(const Table5* src)
{
    entries[0].f0 = src->entries[0].f0;
    entries[0].f4 = src->entries[0].f4;
    entries[0].f8 = src->entries[0].f8;
    entries[0].f12 = src->entries[0].f12;
    entries[1].f0 = src->entries[1].f0;
    entries[1].f4 = src->entries[1].f4;
    entries[1].f8 = src->entries[1].f8;
    entries[1].f12 = src->entries[1].f12;
    entries[2].f0 = src->entries[2].f0;
    entries[2].f4 = src->entries[2].f4;
    entries[2].f8 = src->entries[2].f8;
    entries[2].f12 = src->entries[2].f12;
    entries[3].f0 = src->entries[3].f0;
    entries[3].f4 = src->entries[3].f4;
    entries[3].f8 = src->entries[3].f8;
    entries[3].f12 = src->entries[3].f12;
    entries[4].f0 = src->entries[4].f0;
    entries[4].f4 = src->entries[4].f4;
    entries[4].f8 = src->entries[4].f8;
    entries[4].f12 = src->entries[4].f12;
    flags = src->flags;
}

// FUNCTION: DAO 0x00920150
int __cdecl fn_00520150(Array16* a, Key4* k)
{
    int lo = 0;
    int hi = a->count;
    if (hi > 0) {
        Entry16* base = a->base;
        int target = k->key;
        do {
            int half = hi >> 1;
            int mid = lo + half;
            int diff = (int)base[mid].f4 - target;
            if (diff < 0) {
                lo = mid + 1;
                hi = hi - half - 1;
            } else {
                hi = half;
            }
        } while (hi > 0);
    }
    return lo;
}

// FUNCTION: DAO 0x009201a0
int __cdecl fn_005201a0(Array16* a, const int* key)
{
    int lo = 0;
    int hi = a->count;
    if (hi > 0) {
        Entry16* base = a->base;
        int target = *key;
        do {
            int half = hi >> 1;
            int mid = lo + half;
            int diff = (int)base[mid].f4 - target;
            if (diff < 0) {
                lo = mid + 1;
                hi = hi - half - 1;
            } else {
                hi = half;
            }
        } while (hi > 0);
    }
    return lo;
}

// FUNCTION: DAO 0x00920730
unsigned char __thiscall Obj98::fn_00520730()
{
    unsigned char r;
    Inner64* y = p9c->q;
    if (y) {
        r = y->flag;
        r &= 1;
        return r;
    }
    r = p98->flags;
    r >>= 3;
    r &= 1;
    return r;
}
