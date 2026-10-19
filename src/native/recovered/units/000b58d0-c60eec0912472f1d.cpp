// Reconstructed functions for DAOrigins.exe
// Target: Microsoft VC8 x86 C++98

#pragma pack(push, 1)

struct NameObj5530 { char pad[8]; char name[1]; };
struct Node5530 {
    char pad0[0x20];
    NameObj5530* name;
    char pad1[4];
    Node5530* next;
};
struct List5530 {
    char pad0[0x28];
    Node5530* head;
    Node5530* fn_000b5530(const char* s);
};

struct NameObjB { char pad[8]; char name[1]; };
struct NodeB {
    char pad0[0x14];
    NameObjB* name;
    char pad1[4];
    NodeB* prev;
    NodeB* next;
    void fn_000b58d0(NodeB* n);
    NodeB* fn_000b58f0(const char* s);
};

struct FreeBlock { unsigned int size; unsigned int pad; FreeBlock* next; };

struct NodeC {
    int size;
    char pad0[3];
    unsigned char flag7;
    NodeC* next8;
    NodeC* prevC;
};
struct BinList {
    unsigned int field0;
    NodeC* bins[20];
    void fn_000b9b20(NodeC* node);
};

struct NodeD {
    char pad0[8];
    NodeD* next;
    char pad1[0x19];
    unsigned char flag25;
};

struct NodeE {
    NodeE* field0;
    NodeE* field4;
    NodeE* field8;
    unsigned int key;
    char pad[0x15];
    unsigned char flag25;
};
struct Tree;
struct TreePair { Tree* first; NodeE* second; };
struct Tree {
    unsigned int field0;
    NodeE* field4;
    void fn_000bc170(TreePair* out, const unsigned int* key);
};

struct Class38 {
    char pad0[0x38];
    unsigned short field38;
    void fn_000be8d0();
};

struct WString {
    char pad0[4];
    char data[4];
    char pad1[12];
    int length;
    int capacity;
};

struct IterCD { void* field0; void* field4; unsigned char field8; };
struct ClassCD5E0 {
    char pad0[4];
    void* field4;
    void* field8;
    unsigned int count;
    void fn_000cd5e0(IterCD* out);
};

struct FlagClass {
    char pad0[4];
    unsigned char field4;
    unsigned char fn_000ecf60();
};

#pragma pack(pop)

// FUNCTION: DAO 0x004b5530
Node5530* List5530::fn_000b5530(const char* s) {
    Node5530* n = head;
    while (n) {
        const char* p = (const char*)((char*)n->name + 8);
        const char* q = s;
        while (*p == *q) {
            if (*p == 0) return n;
            ++p; ++q;
        }
        n = n->next;
    }
    return 0;
}

// FUNCTION: DAO 0x004b58d0
void NodeB::fn_000b58d0(NodeB* n) {
    n->next = this;
    n->prev = this->prev;
    this->prev->next = n;
    this->prev = n;
}

// FUNCTION: DAO 0x004b58f0
NodeB* NodeB::fn_000b58f0(const char* s) {
    NodeB* n = this->next;
    if (n == this) return 0;
    do {
        const char* p = (const char*)((char*)n->name + 8);
        const char* q = s;
        while (*p == *q) {
            if (*p == 0) return n;
            ++p; ++q;
        }
        n = n->next;
    } while (n != this);
    return 0;
}

// FUNCTION: DAO 0x004b9770
FreeBlock* __stdcall fn_000b9770(FreeBlock* head, unsigned int req, unsigned int align_shift) {
    unsigned int mask = (1u << (align_shift & 31)) - 1u;
    FreeBlock* best = 0;
    FreeBlock* b = head;
    while (b) {
        unsigned int sz = b->size;
        unsigned int overhead = ((mask - (unsigned int)b - 0x0Fu) & mask) + 0x18u;
        unsigned int need = overhead + req;
        if (sz >= need) {
            unsigned int avail = sz - overhead;
            if (avail == req) return b;
            if (best == 0 || sz < best->size) {
                if (avail > req) best = b;
            }
        }
        b = b->next;
    }
    return best;
}

// FUNCTION: DAO 0x004b97f0
void* __stdcall fn_000b97f0(void* p) {
    if (!p) return 0;
    unsigned int sz = *(unsigned int*)p;
    return (char*)p + sz - 8;
}

// FUNCTION: DAO 0x004b9820
unsigned int __stdcall fn_000b9820(unsigned int base, unsigned int align_shift) {
    unsigned int mask = (1u << (align_shift & 31)) - 1u;
    return (base + mask + 0x10u) & ~mask;
}

// FUNCTION: DAO 0x004b9b20
void BinList::fn_000b9b20(NodeC* node) {
    if (!node) return;
    int sz = node->size;
    unsigned int idx = 0;
    if (sz > 0) {
        int v = sz;
        do {
            v >>= 1;
            ++idx;
        } while (v > 0);
        if (idx >= 0x14u) idx = 0x13u;
    }
    node->flag7 = 0;
    NodeC* old = bins[idx];
    bins[idx] = node;
    if (old) {
        old->prevC = node;
        node->next8 = old;
    }
}

// FUNCTION: DAO 0x004bbe40
NodeD* __cdecl fn_000bbe40(NodeD* n) {
    NodeD* eax = n;
    NodeD* ecx = n->next;
    if (ecx->flag25 != 0) return eax;
    do {
        eax = ecx;
        ecx = eax->next;
    } while (ecx->flag25 == 0);
    return eax;
}

// FUNCTION: DAO 0x004bc170
void Tree::fn_000bc170(TreePair* out, const unsigned int* key) {
    NodeE* header = this->field4;
    NodeE* eax = header->field4;
    NodeE* edx = header;
    if (eax->flag25 == 0) {
        do {
            unsigned int k = *key;
            if (eax->key <= k) {
                edx = eax;
                eax = eax->field0;
            } else {
                eax = eax->field8;
            }
        } while (eax->flag25 == 0);
    }
    NodeE* header2 = this->field4;
    if (edx == header2 || *key > edx->key) {
        out->first = this;
        out->second = header2;
    } else {
        out->first = this;
        out->second = edx;
    }
}

// FUNCTION: DAO 0x004be8d0
void Class38::fn_000be8d0() {
    field38++;
}

// FUNCTION: DAO 0x004c55f0
bool __cdecl fn_000c55f0(const WString* s, char c) {
    int len = s->length;
    if (len == 0 || len > 0x20) return false;
    if (len <= 0) return false;
    const wchar_t* data;
    if ((unsigned int)s->capacity < 8u) {
        data = (const wchar_t*)((const char*)s + 4);
    } else {
        data = *(wchar_t* const*)((const char*)s + 4);
    }
    int dot = -1;
    int i = 0;
    do {
        wchar_t ch = data[i];
        if (ch == L'.') {
            if (dot > 0 && c == 1) return false;
            dot = i;
        } else if ((ch >= L'a' && ch <= L'z') ||
                   (ch >= L'A' && ch <= L'Z') ||
                   (ch >= L'0' && ch <= L'9') ||
                   ch == L'_' || ch == L'-' || ch == L'(' ||
                   ch == L')' || ch == L' ') {
        } else {
            return false;
        }
        ++i;
    } while (i < len);
    if (dot < 1) return false;
    if (len - dot > 4) return false;
    return true;
}

// FUNCTION: DAO 0x004cd5e0
void ClassCD5E0::fn_000cd5e0(IterCD* out) {
    if (this->count == 0) {
        out->field8 = 0;
    } else {
        void* eax = (char*)this + 4;
        void* ecx = *(void**)((char*)this + 8);
        void* edx = *(void**)ecx;
        out->field0 = eax;
        out->field4 = edx;
        out->field8 = 1;
    }
}

// FUNCTION: DAO 0x004ecf60
unsigned char FlagClass::fn_000ecf60() {
    return field4;
}
