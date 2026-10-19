typedef unsigned int uint32;
typedef unsigned char byte;

struct Str;
struct TreeNode;
struct TreeIter;
struct UnknownObj;
struct FacetObj;
struct AllocObj;
struct Counter;
struct Guard;

struct Str {
    unsigned f00;
    unsigned char buf[16];
    unsigned len;
    unsigned cap;
    void fn_00001590(const void*, unsigned, unsigned);
    void fn_000012a0(unsigned, unsigned);
    void fn_000017a0(const void*);
    void fn_00001670(unsigned, unsigned);
};

struct TreeNode {
    TreeNode* left;
    TreeNode* right;
    TreeNode* parent;
    unsigned char pad[0x39 - 12];
    unsigned char color;
};

struct TreeIter {
    void* root;
    TreeNode* node;
    void fn_00002980();
};

struct Counter {
    unsigned f0;
    unsigned f4;
    void fn_00003540();
};

struct Guard {
    unsigned dummy;
    void fn_004dffe1(void*);
    void fn_004e0002();
};

struct UnknownObj {
    void fn_004e0ee6();
    void* fn_00006d50(void*);
};

struct AllocObj {
    void fn_000075f0(void*);
    void fn_000083f0(void*);
    void fn_00008ee0(void*);
};

struct FacetObj {
    void* fn_004e0fc0(void**);
    void fn_004e0ef7(void**);
};

typedef void (__stdcall *FnAda)(void*, void*, void*, void*);

extern "C" void __cdecl fn_004dfd0c(void);
extern "C" int __cdecl fn_004e0e10(void*, unsigned, const void*, unsigned);
extern "C" void __cdecl fn_004e11f2(void);
extern "C" void* __cdecl fn_00013660(unsigned);
extern "C" void __cdecl fn_004e0d86(void*);
extern "C" int __cdecl fn_004ec4a5(void*, void*);
extern "C" void* g_00C3ECE0;
extern "C" void* g_00C3ECDC;
extern "C" unsigned g_00B3A160[8];
extern "C" FnAda g_00ADA0CC;

// FUNCTION: DAO 0x00401670
void Str::fn_00001670(unsigned a1, unsigned a2)
{
    unsigned cap = this->cap;
    unsigned char* base = (cap >= 0x10u) ? *(unsigned char**)&this->buf : (unsigned char*)&this->buf;
    if (a1 >= (unsigned)base) {
        unsigned end = (unsigned)base + this->len;
        if (a1 < end) {
            unsigned char* data = (this->cap >= 0x10u) ? *(unsigned char**)&this->buf : (unsigned char*)&this->buf;
            this->fn_00001590(this, a1 - (unsigned)data, a2);
            return;
        }
    }
    if (a2 > 0xFFFFFFFEu) fn_004dfd0c();
    if (this->cap < a2) this->fn_000012a0(a2, this->len);
    if (a2 != 0) {
        unsigned char* dst = (this->cap >= 0x10u) ? *(unsigned char**)&this->buf : (unsigned char*)&this->buf;
        fn_004e0e10(dst, this->cap, (const void*)a1, a2);
        this->len = a2;
        unsigned char* d2 = (this->cap >= 0x10u) ? *(unsigned char**)&this->buf : (unsigned char*)&this->buf;
        d2[a2] = 0;
    } else {
        this->len = 0;
        unsigned char* d2 = (this->cap >= 0x10u) ? *(unsigned char**)&this->buf : (unsigned char*)&this->buf;
        *d2 = 0;
    }
}

// FUNCTION: DAO 0x00402980
void TreeIter::fn_00002980()
{
    if (this->root == 0) fn_004e11f2();
    TreeNode* n = this->node;
    if (n != 0) {
        if (n->color != 0) { fn_004e11f2(); return; }
        TreeNode* c = n->parent;
        if (c->color == 0) {
            TreeNode* a = c->left;
            while (a->color == 0) { c = a; a = c->left; }
            this->node = c;
            return;
        }
        TreeNode* a = n->right;
        while (a->color == 0) {
            if (this->node == a->parent) {
                this->node = a;
                TreeNode* d = a->right;
                if (d->color != 0) { this->node = d; return; }
                a = d;
            } else {
                break;
            }
        }
        this->node = a;
    }
}

// FUNCTION: DAO 0x00403540
void Counter::fn_00003540()
{
    Guard guard;
    guard.fn_004dffe1((void*)0);
    unsigned v = *(unsigned*)((unsigned char*)this + 4);
    if (v < 0xFFFFFFFFu) { v++; *(unsigned*)((unsigned char*)this + 4) = v; }
    guard.fn_004e0002();
}

// FUNCTION: DAO 0x00406D50
void* UnknownObj::fn_00006d50(void* arg)
{
    this->fn_004e0ee6();
    *(void**)this = (void*)0x00ADED00;
    Str* s = (Str*)((unsigned char*)this + 0xc);
    s->len = 0;
    s->cap = 0xFu;
    s->buf[0] = 0;
    s->fn_00001590(arg, 0, 0xFFFFFFFFu);
    return this;
}

// FUNCTION: DAO 0x00407A90
extern "C" int __cdecl fn_00007a90(void** p)
{
    if (p != 0 && *p == 0) {
        void* obj = fn_00013660(0x20);
        if (obj != 0) {
            ((AllocObj*)obj)->fn_000075f0((void*)0);
            *p = obj;
        } else {
            *p = 0;
        }
    }
    return 2;
}

// FUNCTION: DAO 0x0040A1D0
extern "C" int __cdecl fn_0000a1d0(void** p)
{
    if (p != 0 && *p == 0) {
        void* obj = fn_00013660(0x10);
        if (obj != 0) {
            ((AllocObj*)obj)->fn_000083f0((void*)0);
            *p = obj;
        } else {
            *p = 0;
        }
    }
    return 4;
}

// FUNCTION: DAO 0x0040A240
extern "C" int __cdecl fn_0000a240(void** p)
{
    if (p != 0 && *p == 0) {
        void* obj = fn_00013660(0x10);
        if (obj != 0) {
            ((AllocObj*)obj)->fn_00008ee0((void*)0);
            *p = obj;
        } else {
            *p = 0;
        }
    }
    return 4;
}

// FUNCTION: DAO 0x008E006F
extern "C" void* __cdecl fn_004e006f(void)
{
    return g_00C3ECE0;
}

// FUNCTION: DAO 0x008E013D
extern "C" void __cdecl fn_004e013d(void* p)
{
    if (g_00C3ECDC == 0) fn_004e0d86((void*)0x008E00FA);
    void* old = g_00C3ECDC;
    void* obj = fn_00013660(8);
    if (obj != 0) {
        *(void**)obj = old;
        *((void**)obj + 1) = p;
    } else {
        obj = 0;
    }
    g_00C3ECDC = obj;
}

// FUNCTION: DAO 0x008E02D5
extern "C" void __cdecl fn_004e02d5(void* obj, void* name)
{
    int r = fn_004ec4a5((void*)0, (void*)0);
    void* s = (r != 0) ? (void*)r : (void*)0x00ADFF52;
    ((Str*)((unsigned char*)obj + 0x3c))->fn_000017a0(s);
    void* s2;
    if (name != 0) {
        int r2 = fn_004ec4a5((void*)0, name);
        s2 = (r2 != 0) ? (void*)r2 : (void*)0x00AE31DC;
    } else {
        s2 = (void*)0x00AE31DC;
    }
    ((Str*)((unsigned char*)obj + 0x58))->fn_000017a0(s2);
}

// FUNCTION: DAO 0x008E0FC0
void* FacetObj::fn_004e0fc0(void** arg)
{
    this->fn_004e0ef7(arg);
    *(void**)this = (void*)0x00B3A140;
    return this;
}

// FUNCTION: DAO 0x008E1202
extern "C" void __stdcall fn_004e1202(void* p1, void* p2)
{
    unsigned local[8];
    for (int i = 0; i < 8; ++i) local[i] = g_00B3A160[i];
    local[6] = (unsigned)p1;
    local[7] = (unsigned)p2;
    if (p2 != 0 && (((unsigned char*)p2)[0] & 8) != 0) {
        local[5] = 0x01994000u;
        g_00ADA0CC((void*)local[0], (void*)local[1], (void*)local[4], (void*)&local[5]);
    }
}
