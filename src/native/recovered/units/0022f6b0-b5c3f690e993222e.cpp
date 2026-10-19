struct N_0022eec0 { N_0022eec0* next; unsigned char pad[0x19]; unsigned char flag; };

// FUNCTION: DAO 0x62EEC0
N_0022eec0* fn_0022eec0(N_0022eec0** p) {
    N_0022eec0* result = (N_0022eec0*)p;
    N_0022eec0* cur = *p;
    if (cur->flag == 0) {
        do {
            result = cur;
            cur = result->next;
        } while (cur->flag == 0);
    }
    return result;
}

struct N_0022f6b0 { N_0022f6b0* left; N_0022f6b0* parent; N_0022f6b0* right; unsigned char pad[5]; unsigned char flag; };
struct T_0022f6b0 { unsigned char pad[4]; N_0022f6b0* header; void fn_0022f6b0(N_0022f6b0* x); };

// FUNCTION: DAO 0x62F6B0
void T_0022f6b0::fn_0022f6b0(N_0022f6b0* x) {
    N_0022f6b0* y = x->right;
    x->right = y->left;
    if (y->left->flag == 0) y->left->parent = x;
    y->parent = x->parent;
    N_0022f6b0* h = this->header;
    if (x == h->parent) {
        h->parent = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }
    y->left = x;
    x->parent = y;
}

struct N_002314d0 { N_002314d0* left; N_002314d0* parent; N_002314d0* right; unsigned int key; unsigned char pad[13]; unsigned char flag; };
struct I_002314d0 { void* tree; N_002314d0* node; };
struct P_002314d0 { I_002314d0 first; I_002314d0 second; };
struct T_002314d0 { unsigned char pad[4]; N_002314d0* header; void fn_002314d0(I_002314d0* out, const unsigned int* key); void fn_00231540(P_002314d0* out, const unsigned int* key); };

// FUNCTION: DAO 0x6314D0
void T_002314d0::fn_002314d0(I_002314d0* out, const unsigned int* key) {
    N_002314d0* header = this->header;
    N_002314d0* x = header->parent;
    N_002314d0* y = header;
    while (x->flag == 0) {
        if (x->key < *key) {
            x = x->right;
        } else {
            y = x;
            x = x->left;
        }
    }
    I_002314d0 result;
    N_002314d0* h = this->header;
    if (y == h || *key < y->key) {
        result.tree = this;
        result.node = h;
    } else {
        result.tree = this;
        result.node = y;
    }
    out->tree = result.tree;
    out->node = result.node;
}

// FUNCTION: DAO 0x631540
void T_002314d0::fn_00231540(P_002314d0* out, const unsigned int* key) {
    N_002314d0* header = this->header;
    N_002314d0* x = header->parent;
    N_002314d0* upper = header;
    while (x->flag == 0) {
        if (*key < x->key) {
            upper = x;
            x = x->left;
        } else {
            x = x->right;
        }
    }
    N_002314d0* h = this->header;
    N_002314d0* y = h->parent;
    N_002314d0* lower = h;
    while (y->flag == 0) {
        if (y->key < *key) {
            y = y->right;
        } else {
            lower = y;
            y = y->left;
        }
    }
    P_002314d0 result;
    result.first.tree = this;
    result.first.node = lower;
    result.second.tree = this;
    result.second.node = upper;
    *out = result;
}

struct S_00231650 { unsigned int a0; unsigned int a1; void* p8; unsigned char flag12; unsigned char pad[3]; };

// FUNCTION: DAO 0x631650
void fn_00231650(S_00231650* first, S_00231650* last, S_00231650* dst) {
    while (first != last) {
        unsigned char* pf = first ? (unsigned char*)first + 0xc : 0;
        dst->flag12 = *pf;
        void** pp = first ? (void**)((unsigned char*)first + 4) : 0;
        dst->p8 = *(void**)((unsigned char*)pp + 4);
        ++first;
        ++dst;
    }
}

// FUNCTION: DAO 0x631690
void fn_00231690(S_00231650* begin, S_00231650* end, S_00231650* dstEnd) {
    while (begin != end) {
        --end;
        --dstEnd;
        unsigned char* pf = end ? (unsigned char*)end + 0xc : 0;
        dstEnd->flag12 = *pf;
        void** pp = end ? (void**)((unsigned char*)end + 4) : 0;
        dstEnd->p8 = *(void**)((unsigned char*)pp + 4);
    }
}

// FUNCTION: DAO 0x631D50
void fn_00231d50(S_00231650* first, S_00231650* last, const S_00231650* value) {
    while (first != last) {
        unsigned char* pf = value ? (unsigned char*)value + 0xc : 0;
        first->flag12 = *pf;
        void** pp = value ? (void**)((unsigned char*)value + 4) : 0;
        first->p8 = *(void**)((unsigned char*)pp + 4);
        ++first;
    }
}

struct C_00240060 { unsigned char pad[0x74]; void* p; int fn_00240060(); };

// FUNCTION: DAO 0x640060
int C_00240060::fn_00240060() {
    if (p != 0) return *(int*)((unsigned char*)p + 0x5c);
    return -1;
}

struct E_00240330 { unsigned int a[4]; };
struct C_00240330 { unsigned int pad; E_00240330* begin; E_00240330* end; bool fn_00240330(); };

// FUNCTION: DAO 0x640330
bool C_00240330::fn_00240330() {
    if (begin == 0) {
        int n = 0;
        return n == 0;
    }
    int n = (int)(end - begin);
    return n == 0;
}

struct C_00242df0 { unsigned char pad[8]; unsigned int offset; void fn_00242df0(void* dst, const unsigned int* src); };

// FUNCTION: DAO 0x642DF0
void C_00242df0::fn_00242df0(void* dst, const unsigned int* src) {
    unsigned int off = offset;
    *(unsigned int*)((unsigned char*)dst + off) = src[0];
    *(unsigned int*)((unsigned char*)dst + off + 4) = src[1];
}

struct C_00242e10 { unsigned char pad[8]; unsigned int value; void fn_00242e10(unsigned int* out); };

// FUNCTION: DAO 0x642E10
void C_00242e10::fn_00242e10(unsigned int* out) {
    unsigned int v = this->value;
    unsigned int* p = out;
    *p = v;
}

// FUNCTION: DAO 0x6454D0
bool fn_002454d0(const void* p, unsigned int size) {
    if (p == 0) return false;
    if (size <= 0x1c) return false;
    const unsigned int* d = (const unsigned int*)p;
    if (d[0] != 0x20464647) return false;
    if (d[1] != 0x302e3456) return false;
    return d[2] == 0x20204350;
}
