struct Pair { unsigned int first; unsigned int second; };

struct C_0059B7F0 {
    unsigned int* f00;
    Pair* fn_0059b7f0(Pair* out);
};

struct C_0059B870_Key { unsigned int pad[4]; unsigned int hash; };
struct C_0059B870_Table { unsigned int f00; unsigned int mask; };
struct C_0059B870_Node { unsigned int next; C_0059B870_Key* key; };
struct C_0059B870 {
    C_0059B870_Table* f00;
    unsigned int fn_0059b870(C_0059B870_Key** key, unsigned int bucket);
};

struct C_0059B9D0_Key { unsigned int pad[4]; unsigned int hash; };
struct C_0059B9D0_Table { unsigned int f00; unsigned int mask; };
struct C_0059B9D0_Node { unsigned int next; C_0059B9D0_Key* key; };
struct C_0059B9D0 {
    C_0059B9D0_Table* f00;
    unsigned int fn_0059b9d0(C_0059B9D0_Key** key, unsigned int bucket);
};

struct C_0059E9A0_Entry { unsigned int pad0; unsigned int pad1; unsigned int status; };
struct C_0059E9A0_Array { unsigned int f00; unsigned int count; };
struct C_0059E9A0_Container { C_0059E9A0_Array* array; };
struct C_0059E9A0_Iterator {
    C_0059E9A0_Container* f00;
    unsigned int index;
    void fn_0059e9a0();
};

struct C_0059EE00 {
    unsigned int* f00;
    Pair* fn_0059ee00(Pair* out);
};

struct C_005A02D0 {
    unsigned char pad[0x10];
    unsigned int* f10;
    unsigned int* fn_005a02d0(unsigned int* out);
};

struct C_005A9120_Entry { unsigned int pad0; unsigned int pad1; unsigned int status; unsigned int pad3; unsigned int pad4; };
struct C_005A9120_Array { unsigned int f00; unsigned int count; };
struct C_005A9120_Container { C_005A9120_Array* array; };
struct C_005A9120_Iterator {
    C_005A9120_Container* f00;
    unsigned int index;
    void fn_005a9120();
};

struct C_005AC2F0 {
    unsigned char pad[0x20];
    unsigned int f20;
    unsigned char pad2[0x06];
    unsigned char f2a;
    unsigned int fn_005ac2f0();
};

struct C_005ADD30 {
    unsigned int* f00;
    Pair* fn_005add30(Pair* out);
};

struct C_005AF350 {
    unsigned int f00;
    unsigned int f04;
    unsigned char pad08[0x14];
    unsigned char f1c;
    unsigned char pad1d;
    unsigned char data[0x5A];
    unsigned int fn_005af350();
};

struct C_005AF6D0_Item {
    unsigned int flags;
    unsigned char pad[0x12];
    unsigned short v16;
    unsigned int v18;
};
struct C_005AF6D0 {
    C_005AF6D0_Item** f00;
    unsigned int f04;
    unsigned int fn_005af6d0();
};

// FUNCTION: DAO 0x99b7f0
Pair* __thiscall C_0059B7F0::fn_0059b7f0(Pair* out)
{
    unsigned int* table = this->f00;
    if (!table) {
        out->second = 0;
        out->first = 0;
        return out;
    }
    unsigned int n = table[1];
    unsigned int count = 0;
    unsigned int* p = (unsigned int*)((unsigned char*)table + 8);
    while (*p == 0xFFFFFFFEu) {
        ++count;
        p = (unsigned int*)((unsigned char*)p + 0x18);
        if (count > n)
            break;
    }
    out->second = count;
    out->first = (unsigned int)this;
    return out;
}

// FUNCTION: DAO 0x99b870
unsigned int __thiscall C_0059B870::fn_0059b870(C_0059B870_Key** key, unsigned int bucket)
{
    C_0059B870_Table* table = this->f00;
    unsigned int mask;
    unsigned int idx = bucket;
    C_0059B870_Node* node = (C_0059B870_Node*)((unsigned char*)table + 8 + bucket * 0x18);
    if (node->next == 0xFFFFFFFEu)
        return 0xFFFFFFFFu;
    mask = table->mask;
    if ((node->key->hash & mask) != bucket)
        return 0xFFFFFFFFu;
    for (;;) {
        C_0059B870_Key* k = node->key;
        if ((k->hash & mask) == bucket) {
            if (k == *key)
                return idx;
        }
        if (node->next == 0xFFFFFFFFu)
            return 0xFFFFFFFFu;
        idx = node->next;
        node = (C_0059B870_Node*)((unsigned char*)table + 8 + idx * 0x18);
    }
}

// FUNCTION: DAO 0x99b9d0
unsigned int __thiscall C_0059B9D0::fn_0059b9d0(C_0059B9D0_Key** key, unsigned int bucket)
{
    C_0059B9D0_Table* table = this->f00;
    unsigned int mask;
    unsigned int idx = bucket;
    C_0059B9D0_Node* node = (C_0059B9D0_Node*)((unsigned char*)table + 8 + bucket * 0x24);
    if (node->next == 0xFFFFFFFEu)
        return 0xFFFFFFFFu;
    mask = table->mask;
    if ((node->key->hash & mask) != bucket)
        return 0xFFFFFFFFu;
    for (;;) {
        C_0059B9D0_Key* k = node->key;
        if ((k->hash & mask) == bucket) {
            if (k == *key)
                return idx;
        }
        if (node->next == 0xFFFFFFFFu)
            return 0xFFFFFFFFu;
        idx = node->next;
        node = (C_0059B9D0_Node*)((unsigned char*)table + 8 + idx * 0x24);
    }
}

// FUNCTION: DAO 0x99e9a0
void __thiscall C_0059E9A0_Iterator::fn_0059e9a0()
{
    C_0059E9A0_Container* c = this->f00;
    unsigned int idx = this->index;
    C_0059E9A0_Array* arr = c->array;
    if (idx > arr->count)
        return;
    ++idx;
    this->index = idx;
    arr = c->array;
    if (idx > arr->count)
        return;
    unsigned int sentinel = 0xFFFFFFFEu;
    for (;;) {
        C_0059E9A0_Entry* e = (C_0059E9A0_Entry*)((unsigned char*)c->array + idx * 0x0C);
        if (e->status != sentinel)
            break;
        ++idx;
        this->index = idx;
        if (idx > c->array->count)
            break;
    }
}

// FUNCTION: DAO 0x99ee00
Pair* __thiscall C_0059EE00::fn_0059ee00(Pair* out)
{
    unsigned int* table = this->f00;
    if (!table) {
        out->second = 0;
        out->first = 0;
        return out;
    }
    unsigned int n = table[1];
    unsigned int count = 0;
    unsigned int* p = (unsigned int*)((unsigned char*)table + 8);
    while (*p == 0xFFFFFFFEu) {
        ++count;
        p = (unsigned int*)((unsigned char*)p + 0x0C);
        if (count > n)
            break;
    }
    out->second = count;
    out->first = (unsigned int)this;
    return out;
}

// FUNCTION: DAO 0x9a02d0
unsigned int* __thiscall C_005A02D0::fn_005a02d0(unsigned int* out)
{
    if (this->f10 != 0) {
        if (out != 0)
            *out = *this->f10;
        return this->f10 + 1;
    }
    return 0;
}

// FUNCTION: DAO 0x9a9120
void __thiscall C_005A9120_Iterator::fn_005a9120()
{
    C_005A9120_Container* c = this->f00;
    unsigned int idx = this->index;
    C_005A9120_Array* arr = c->array;
    if (idx > arr->count)
        return;
    ++idx;
    this->index = idx;
    arr = c->array;
    if (idx > arr->count)
        return;
    unsigned int sentinel = 0xFFFFFFFEu;
    for (;;) {
        C_005A9120_Entry* e = (C_005A9120_Entry*)((unsigned char*)c->array + idx * 0x14);
        if (e->status != sentinel)
            break;
        ++idx;
        this->index = idx;
        if (idx > c->array->count)
            break;
    }
}

// FUNCTION: DAO 0x9ac2f0
unsigned int __thiscall C_005AC2F0::fn_005ac2f0()
{
    unsigned int result = 1;
    if ((this->f2a & 1) == 0) {
        result = 0;
    } else if (this->f20 != 0) {
        result = 0;
    }
    return result;
}

// FUNCTION: DAO 0x9add30
Pair* __thiscall C_005ADD30::fn_005add30(Pair* out)
{
    unsigned int* table = this->f00;
    if (!table) {
        out->second = 0;
        out->first = 0;
        return out;
    }
    unsigned int n = table[1];
    unsigned int count = 0;
    unsigned int* p = (unsigned int*)((unsigned char*)table + 8);
    while (*p == 0xFFFFFFFEu) {
        ++count;
        p = (unsigned int*)((unsigned char*)p + 0x14);
        if (count > n)
            break;
    }
    out->second = count;
    out->first = (unsigned int)this;
    return out;
}

// FUNCTION: DAO 0x9af350
unsigned int __thiscall C_005AF350::fn_005af350()
{
    unsigned int flags = this->f00;
    unsigned int high = (flags >> 31) & 1u;
    unsigned int n;
    if (high != 0)
        n = (unsigned int)this->f1c;
    else
        n = this->f04;
    if (n == 0)
        return 0;
    unsigned char* base;
    if (high != 0)
        base = (unsigned char*)this + 0x1E;
    else
        base = (unsigned char*)this + 0x2A;
    if ((base[n * 8 - 1] & 1) == 0)
        return 0;
    if ((*(unsigned short*)(base + n * 8 - 4) & 0xF000) == 0)
        return 0;
    return 1;
}

// FUNCTION: DAO 0x9af6d0
unsigned int __thiscall C_005AF6D0::fn_005af6d0()
{
    unsigned int count = this->f04;
    if (count == 0)
        return 0;
    int min = 0x7FFFFFFF;
    unsigned int i = 0;
    while (i < count) {
        if ((int)i < 0)
            break;
        C_005AF6D0_Item* item = this->f00[i];
        unsigned int high = (item->flags >> 31) & 1u;
        unsigned int v;
        if (high != 0)
            v = (unsigned int)item->v16;
        else
            v = item->v18;
        if ((int)v < min)
            min = (int)v;
        ++i;
    }
    return (unsigned int)min;
}
