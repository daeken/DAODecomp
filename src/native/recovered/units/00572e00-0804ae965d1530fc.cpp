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
class C13 { public: unsigned int field0; unsigned int field4; unsigned char pad8[0x14]; unsigned char field1c; unsigned char pad1d[1]; unsigned char pad1e[0xc]; unsigned char field2a; void* fn_005af320(); };

// FUNCTION: DAO 0x00972590
unsigned int C1::fn_00572590()
{
    unsigned int v = (unsigned int)field2;
    if (((field6 >> 6) & 1) == 1)
        v = 0u - v;
    return v;
}

// FUNCTION: DAO 0x00972830
unsigned int C2::fn_00572830(const unsigned int* p, unsigned int idx)
{
    unsigned char* base = (unsigned char*)this->base;
    C2Node* n = (C2Node*)(base + 8 + idx * 12u);
    unsigned int result = idx;
    if (n->next == 0xFFFFFFFEu) goto fail;
    if (n->key != idx) goto fail;
    for (;;) {
        if (n->key == idx) {
            if (n->value == *p)
                return result;
        }
        unsigned int next = n->next;
        if (next == 0xFFFFFFFFu) goto fail;
        result = next;
        n = (C2Node*)(base + 8 + next * 12u);
    }
fail:
    return 0xFFFFFFFFu;
}

// FUNCTION: DAO 0x009729c0
unsigned int C3::fn_005729c0()
{
    C3Outer* outer = this->outer;
    C3Header* h = outer->header;
    unsigned int idx = this->cursor;
    if (idx > h->count) return idx;
    idx++;
    this->cursor = idx;
    h = outer->header;
    if (idx > h->count) return idx;
    for (;;) {
        C3Elem* e = (C3Elem*)((unsigned char*)h + 8 + idx * 28u);
        if (e->sentinel != 0xFFFFFFFEu) break;
        idx++;
        this->cursor = idx;
        h = outer->header;
        if (idx > h->count) break;
    }
    return idx;
}

// FUNCTION: DAO 0x00972c50
unsigned int C4::fn_00572c50(const unsigned int* key)
{
    C4Table* t = this->table;
    if (t == 0) goto fail;
    unsigned int value = *key;
    unsigned int h = (value ^ (value >> 6)) & t->mask;
    C4Node* n = &t->nodes[h];
    if (n->next == 0xFFFFFFFEu) goto fail;
    if (n->key != h) goto fail;
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
        if (cur == 0xFFFFFFFFu) goto fail;
        n = &t->nodes[cur];
    }
fail:
    return 0xFFFFFFFFu;
}

// FUNCTION: DAO 0x00972e00
void C5::fn_00572e00(C5Item* item)
{
    C5Node* n = item->node;
    n->next->prev = n->prev;
    n->prev->next = n->next;
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
    if (n->next == 0xFFFFFFFEu) goto fail;
    unsigned int mask = t->mask;
    unsigned int key = n->key;
    unsigned int val = n->value;
    if (((key ^ (key >> 6) ^ val) & mask) != h) goto fail;
    for (;;) {
        key = n->key;
        val = n->value;
        if (((key ^ (key >> 6) ^ val) & mask) == h) {
            if (key == keypair[0] && val == keypair[1])
                return result;
        }
        unsigned int next = n->next;
        if (next == 0xFFFFFFFFu) goto fail;
        result = next;
        n = (C6Node*)((unsigned char*)t + 8 + next * 28u);
    }
fail:
    return 0xFFFFFFFFu;
}

// FUNCTION: DAO 0x00973830
unsigned int C7::fn_00573830(const C7Key* k, unsigned int h)
{
    C7Table* t = this->table;
    C7Node* n = (C7Node*)((unsigned char*)t + 8 + h * 16u);
    unsigned int result = h;
    if (n->next == 0xFFFFFFFEu) goto fail;
    unsigned int mask = t->mask;
    unsigned int hash = ((n->key ^ (n->key >> 6) ^ (unsigned int)n->w ^ (unsigned int)n->a ^ (unsigned int)n->b) & mask);
    if (hash != h) goto fail;
    for (;;) {
        hash = ((n->key ^ (n->key >> 6) ^ (unsigned int)n->w ^ (unsigned int)n->a ^ (unsigned int)n->b) & mask);
        if (hash == h) {
            if (n->key == k->key && n->w == k->w && n->a == k->a && n->b == k->b)
                return result;
        }
        unsigned int next = n->next;
        if (next == 0xFFFFFFFFu) goto fail;
        result = next;
        n = (C7Node*)((unsigned char*)t + 8 + next * 16u);
    }
fail:
    return 0xFFFFFFFFu;
}

// FUNCTION: DAO 0x009af320
void* C13::fn_005af320()
{
    unsigned int bit = (field0 >> 31) & 1;
    unsigned int base;
    if (bit != 0)
        base = (unsigned int)(void*)((char*)this + 0x1e);
    else
        base = (unsigned int)(void*)((char*)this + 0x2a);
    unsigned int count;
    if (bit != 0)
        count = (unsigned int)field1c;
    else
        count = field4;
    return (void*)((base + count * 8u + 3u) & 0xFFFFFFFCu);
}