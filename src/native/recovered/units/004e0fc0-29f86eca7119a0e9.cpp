typedef unsigned char uchar;

struct Str {
    unsigned f00;
    union { uchar buf[16]; uchar* ptr; } u;
    unsigned len;
    unsigned cap;
    void fn_00001590(const Str*, unsigned, unsigned);
    void fn_000012a0(unsigned, unsigned);
    void fn_000017a0(const void*);
    void fn_00001670(unsigned, unsigned);
};

struct TreeNode {
    TreeNode* left;
    TreeNode* parent;
    TreeNode* right;
    uchar pad[0x39 - 12];
    uchar isnil;
};

struct TreeIter {
    void* root;
    TreeNode* node;
    void fn_00002980();
};

struct AllocObj {
    void fn_000075f0(void*);
    void fn_000083f0(void*);
    void fn_00008ee0(void*);
};

struct UnknownObj {
    void* vptr;
    unsigned pad[2];
    Str str;
    void fn_004e0ee6();
    void* fn_00006d50(const Str*);
};

struct FacetObj {
    void* vptr;
    void fn_004e0ef7(void**);
    void* fn_004e0fc0(void*);
};

typedef void (__stdcall *FnAda)(void*, void*, void*, void*);

extern "C" void fn_004dfd0c();
extern "C" int fn_004e0e10(void*, unsigned, const void*, unsigned);
extern "C" void fn_004e11f2();
extern "C" void* fn_00013660(unsigned);
extern "C" void fn_004e0d86(void*);
extern "C" void* fn_004ec4a5(void*, void*);
extern "C" void* g_00C3ECE0;
extern "C" void* g_00C3ECDC;
extern "C" unsigned g_00B3A160[8];
extern "C" FnAda g_00ADA0CC;

// FUNCTION: DAO 0x00401670
void Str::fn_00001670(unsigned a1, unsigned a2)
{
    uchar* data = (this->cap >= 0x10u) ? this->u.ptr : this->u.buf;
    if (a1 >= (unsigned)data && a1 < (unsigned)data + this->len) {
        uchar* data2 = (this->cap >= 0x10u) ? this->u.ptr : this->u.buf;
        this->fn_00001590(this, a1 - (unsigned)data2, a2);
        return;
    }
    if (a2 > 0xFFFFFFFEu) {
        fn_004dfd0c();
    }
    if (this->cap < a2) {
        this->fn_000012a0(a2, this->len);
    }
    if (a2 != 0) {
        uchar* dst = (this->cap >= 0x10u) ? this->u.ptr : this->u.buf;
        fn_004e0e10(dst, this->cap, (const void*)a1, a2);
        this->len = a2;
        uchar* d2 = (this->cap >= 0x10u) ? this->u.ptr : this->u.buf;
        d2[a2] = 0;
    } else {
        this->len = 0;
        uchar* d2 = (this->cap >= 0x10u) ? this->u.ptr : this->u.buf;
        *d2 = 0;
    }
}

// FUNCTION: DAO 0x00402980
void TreeIter::fn_00002980()
{
    if (this->root == 0) {
        fn_004e11f2();
    }
    TreeNode* p = this->node;
    if (p->isnil != 0) {
        fn_004e11f2();
        return;
    }
    if (p->right->isnil == 0) {
        TreeNode* q = p->right;
        while (q->left->isnil == 0) {
            q = q->left;
        }
        this->node = q;
    } else {
        TreeNode* parent = p->parent;
        while (parent->isnil == 0 && p == parent->right) {
            p = parent;
            parent = parent->parent;
        }
        this->node = parent;
    }
}

// FUNCTION: DAO 0x00406D50
void* UnknownObj::fn_00006d50(const Str* arg)
{
    this->fn_004e0ee6();
    this->vptr = (void*)0x00ADED00;
    this->str.len = 0;
    this->str.cap = 0xFu;
    this->str.u.buf[0] = 0;
    this->str.fn_00001590(arg, 0, 0xFFFFFFFFu);
    return this;
}

// FUNCTION: DAO 0x00407A90
extern "C" int __cdecl fn_00007a90(void** p)
{
    if (p != 0 && *p == 0) {
        void* obj = fn_00013660(0x20);
        if (obj != 0) {
            ((AllocObj*)obj)->fn_000075f0((void*)0);
        }
        *p = obj;
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
        }
        *p = obj;
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
        }
        *p = obj;
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
    if (g_00C3ECDC == 0) {
        fn_004e0d86((void*)0x008E00FA);
    }
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
extern "C" void __cdecl fn_004e02d5(void* self, void* name)
{
    void* r1 = fn_004ec4a5((void*)0, (void*)0);
    void* s1 = (r1 != 0) ? r1 : (void*)0x00ADFF52;
    ((Str*)((uchar*)self + 0x3c))->fn_000017a0(s1);

    void* s2;
    if (name != 0) {
        void* r2 = fn_004ec4a5((void*)0, name);
        s2 = (r2 != 0) ? r2 : (void*)0x00AE31DC;
    } else {
        s2 = (void*)0x00AE31DC;
    }
    ((Str*)((uchar*)self + 0x58))->fn_000017a0(s2);
}

// FUNCTION: DAO 0x008E0FC0
void* FacetObj::fn_004e0fc0(void* arg)
{
    this->fn_004e0ef7(&arg);
    this->vptr = (void*)0x00B3A140;
    return this;
}

// FUNCTION: DAO 0x008E1202
extern "C" void __stdcall fn_004e1202(void* p1, void* p2)
{
    unsigned local[8];
    for (int i = 0; i < 8; ++i) {
        local[i] = g_00B3A160[i];
    }
    local[6] = (unsigned)p1;
    local[7] = (unsigned)p2;
    if (p2 != 0 && (((uchar*)p2)[0] & 8) != 0) {
        local[5] = 0x01994000u;
        g_00ADA0CC((void*)local[0], (void*)local[1], (void*)local[4], (void*)&local[5]);
    }
}
