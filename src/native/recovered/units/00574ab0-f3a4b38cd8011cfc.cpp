struct C2Node { unsigned int next; unsigned int key; unsigned int value; };
class C1 { public: unsigned char pad0[2]; unsigned short field2; unsigned char pad4[2]; unsigned char field6; unsigned int fn_00572590(); };
class C2 { public: void* base; unsigned int fn_00572830(const unsigned int* p, unsigned int idx); };
struct C3Header { unsigned int unknown0; unsigned int count; };
struct C3Elem { unsigned int sentinel; unsigned int pad[6]; };
struct C3Outer { C3Header* header; };
class C3 { public: C3Outer* outer; unsigned int cursor; unsigned int fn_005729c0(); };
struct C4Node { unsigned int next; unsigned int key; unsigned int value; };
struct C4Table { unsigned int count; unsigned int mask; C4Node nodes[1]; };
class C4 { public: C4Table* table; unsigned int fn_00572c50(const unsigned int* key); };
struct C5Node { C5Node* next; C5Node* prev; };
struct C5Item { unsigned char pad[0xc]; C5Node* node; };
class C5 { public: unsigned char pad[0x2c]; C5Node head; void fn_00572e00(C5Item* item); };
struct C6Node { unsigned int next; unsigned int key; unsigned int value; unsigned int pad[4]; };
struct C6Table { unsigned int unknown0; unsigned int mask; C6Node nodes[1]; };
class C6 { public: C6Table* table; unsigned int fn_005737b0(const unsigned int* keypair, unsigned int h); };
struct C7Node { unsigned int next; unsigned int key; unsigned short w; unsigned char a; unsigned char b; unsigned int pad; };
struct C7Table { unsigned int unknown0; unsigned int mask; C7Node nodes[1]; };
struct C7Key { unsigned int key; unsigned short w; unsigned char a; unsigned char b; };
class C7 { public: C7Table* table; unsigned int fn_00573830(const C7Key* k, unsigned int h); };
class C8 { public: unsigned int d0; unsigned int d1; unsigned int d2; unsigned int d3; unsigned int d4; unsigned int d5; unsigned int d6; unsigned int d7; unsigned int d8; unsigned char b24; unsigned char b25; C8* fn_00574ab0(); };
class C9 { public: unsigned char pad[0x8c]; unsigned short flags; void fn_0057afa0(unsigned char enable); void fn_0057afc0(unsigned char enable); };
class C11 { public: unsigned int pad0; unsigned int field4; void fn_0057b350(); };
class C12 { public: unsigned char pad[0x2d]; unsigned char field2d; void fn_0059adf0(); };
class C13 { public: unsigned int field0; unsigned int field4; unsigned char pad8[0x14]; unsigned char field1c; unsigned char pad1d[1]; unsigned char pad1e[0xc]; unsigned char field2a; void* fn_005af320(); };

// FUNCTION: DAO 0x00972590
unsigned int C1::fn_00572590()
{
    unsigned char b = field6;
    unsigned int v = (unsigned int)field2;
    if (((b >> 6) & 1u) != 0u)
        v = 0u - v;
    return v;
}

// FUNCTION: DAO 0x00972830
unsigned int C2::fn_00572830(const unsigned int* p, unsigned int idx)
{
    unsigned char* base = (unsigned char*)this->base;
    C2Node* n = (C2Node*)(base + 8 + idx * 12u);
    unsigned int result = idx;
    if (n->next == 0xFFFFFFFEu)
        return 0xFFFFFFFFu;
    if (n->key != idx)
        return 0xFFFFFFFFu;
    for (;;) {
        if (n->key == idx) {
            if (n->value == *p)
                return result;
        }
        unsigned int next = n->next;
        if (next == 0xFFFFFFFFu)
            return 0xFFFFFFFFu;
        result = next;
        n = (C2Node*)(base + 8 + next * 12u);
    }
}

// FUNCTION: DAO 0x009729c0
unsigned int C3::fn_005729c0()
{
    C3Header* h = *(C3Header**)this->outer;
    unsigned int idx = this->cursor;
    if (idx > h->count)
        return idx;
    idx++;
    this->cursor = idx;
    h = *(C3Header**)this->outer;
    if (idx > h->count)
        return idx;
    for (;;) {
        C3Elem* e = (C3Elem*)((unsigned char*)h + 8 + idx * 28u);
        if (e->sentinel != 0xFFFFFFFEu)
            break;
        idx++;
        this->cursor = idx;
        h = *(C3Header**)this->outer;
        if (idx > h->count)
            break;
    }
    return idx;
}

// FUNCTION: DAO 0x00972c50
unsigned int C4::fn_00572c50(const unsigned int* key)
{
    C4Table* t = this->table;
    if (t == 0)
        return 0xFFFFFFFFu;
    unsigned int value = *key;
    unsigned int h = (value ^ (value >> 6)) & t->mask;
    C4Node* n = &t->nodes[h];
    if (n->next == 0xFFFFFFFEu)
        return 0xFFFFFFFFu;
    if (n->key != h)
        return 0xFFFFFFFFu;
    unsigned int prev = 0xFFFFFFFFu;
    unsigned int cur = h;
    for (;;) {
        if (n->key == h) {
            if (n->value == value) {
                if (cur == h) {
                    unsigned int next = n->next;
                    if (next == 0xFFFFFFFFu) {
                        n->next = 0xFFFFFFFEu;
                    } else {
                        C4Node* nextn = &t->nodes[next];
                        n->next = nextn->next;
                        n->key = nextn->key;
                        n->value = nextn->value;
                        nextn->next = 0xFFFFFFFEu;
                    }
                } else {
                    C4Node* prevn = &t->nodes[prev];
                    prevn->next = n->next;
                    n->next = 0xFFFFFFFEu;
                }
                t->count--;
                return (unsigned int)(void*)t;
            }
        }
        prev = cur;
        cur = n->next;
        if (cur == 0xFFFFFFFFu)
            return 0xFFFFFFFFu;
        n = &t->nodes[cur];
    }
}

// FUNCTION: DAO 0x00972e00
void C5::fn_00572e00(C5Item* item)
{
    C5Node* n = item->node;
    n->prev->next = n->next;
    n->next->prev = n->prev;
    C5Node* head = &this->head;
    n->next = head->next;
    n->prev = head;
    head->next->prev = n;
    head->next = n;
}

// FUNCTION: DAO 0x009737b0
unsigned int C6::fn_005737b0(const unsigned int* keypair, unsigned int h)
{
    C6Table* t = this->table;
    C6Node* n = (C6Node*)((unsigned char*)t + 8 + h * 28u);
    unsigned int result = h;
    if (n->next == 0xFFFFFFFEu)
        return 0xFFFFFFFFu;
    unsigned int mask = t->mask;
    unsigned int key = n->key;
    unsigned int val = n->value;
    if (((key ^ (key >> 6) ^ val) & mask) != h)
        return 0xFFFFFFFFu;
    for (;;) {
        key = n->key;
        val = n->value;
        if (((key ^ (key >> 6) ^ val) & mask) == h) {
            if (key == keypair[0] && val == keypair[1])
                return result;
        }
        unsigned int next = n->next;
        if (next == 0xFFFFFFFFu)
            return 0xFFFFFFFFu;
        result = next;
        n = (C6Node*)((unsigned char*)t + 8 + next * 28u);
    }
}

// FUNCTION: DAO 0x00973830
unsigned int C7::fn_00573830(const C7Key* k, unsigned int h)
{
    C7Table* t = this->table;
    C7Node* n = (C7Node*)((unsigned char*)t + 8 + h * 16u);
    unsigned int result = h;
    if (n->next == 0xFFFFFFFEu)
        return 0xFFFFFFFFu;
    unsigned int mask = t->mask;
    unsigned int hash = ((n->key ^ (n->key >> 6) ^ (unsigned int)n->w ^ (unsigned int)n->a ^ (unsigned int)n->b) & mask);
    if (hash != h)
        return 0xFFFFFFFFu;
    for (;;) {
        hash = ((n->key ^ (n->key >> 6) ^ (unsigned int)n->w ^ (unsigned int)n->a ^ (unsigned int)n->b) & mask);
        if (hash == h) {
            if (n->key == k->key && n->w == k->w && n->a == k->a && n->b == k->b)
                return result;
        }
        unsigned int next = n->next;
        if (next == 0xFFFFFFFFu)
            return 0xFFFFFFFFu;
        result = next;
        n = (C7Node*)((unsigned char*)t + 8 + next * 16u);
    }
}

// FUNCTION: DAO 0x00974ab0
C8* C8::fn_00574ab0()
{
    d0 = 0; d1 = 0; d2 = 0; d3 = 0; d4 = 0; d5 = 0; d6 = 0; d7 = 0; d8 = 0;
    b24 = 0; b25 = 0;
    return this;
}

// FUNCTION: DAO 0x0097afa0
void C9::fn_0057afa0(unsigned char enable)
{
    if (enable != 0)
        flags = (unsigned short)(flags | 0x10u);
    else
        flags = (unsigned short)(flags & 0xFFEFu);
}

// FUNCTION: DAO 0x0097afc0
void C9::fn_0057afc0(unsigned char enable)
{
    if (enable != 0) {
        flags = (unsigned short)(flags | 0x60u);
    } else {
        unsigned short ax = flags;
        ax = (unsigned short)(ax & 0xFFDFu);
        ax = (unsigned short)(ax | 0x40u);
        flags = ax;
    }
}

// FUNCTION: DAO 0x0097b350
void C11::fn_0057b350()
{
    field4 = 0;
}

// FUNCTION: DAO 0x0099adf0
void C12::fn_0059adf0()
{
    field2d = 0;
}

// FUNCTION: DAO 0x009af320
void* C13::fn_005af320()
{
    unsigned int base;
    unsigned int count;
    if ((field0 & 0x80000000u) != 0u) {
        base = (unsigned int)(void*)((char*)this + 0x1e);
        count = (unsigned int)field1c;
    } else {
        base = (unsigned int)(void*)((char*)this + 0x2a);
        count = field4;
    }
    return (void*)((base + count * 8u + 3u) & 0xFFFFFFFCu);
}
