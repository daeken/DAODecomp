struct N_0022eec0 { N_0022eec0* next; unsigned char pad[0x19]; unsigned char flag; };

// FUNCTION: DAO 0x62EEC0
N_0022eec0* fn_0022eec0(N_0022eec0** p) {
    N_0022eec0* result = (N_0022eec0*)p;
    N_0022eec0* cur = *p;
    if (cur->flag == 0) {
        do {
            result = cur;
            cur = *(N_0022eec0**)result;
        } while (cur->flag == 0);
    }
    return result;
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
        unsigned int k = *key;
        if (x->key < k) {
            x = x->right;
        } else {
            y = x;
            x = x->left;
        }
    }
    N_002314d0* h = this->header;
    I_002314d0 lower;
    lower.tree = this;
    lower.node = y;
    I_002314d0 upper;
    upper.tree = this;
    upper.node = h;
    *out = (y == h || *key < y->key) ? upper : lower;
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
    N_002314d0* y = header->parent;
    N_002314d0* lower = header;
    while (y->flag == 0) {
        if (y->key < *key) {
            y = y->right;
        } else {
            lower = y;
            y = y->left;
        }
    }
    out->first.tree = this;
    out->first.node = lower;
    out->second.tree = this;
    out->second.node = upper;
}

struct S_00231650 { unsigned int a0; unsigned int a1; void* p8; unsigned char flag12; unsigned char pad[3]; };

// FUNCTION: DAO 0x631650
void fn_00231650(S_00231650* first, S_00231650* last, S_00231650* dst) {
    S_00231650* f = first;
    S_00231650* d = dst;
    while (f != last) {
        unsigned char* pf = f ? (unsigned char*)f + 0xc : 0;
        d->flag12 = *pf;
        void** pp = f ? (void**)((unsigned char*)f + 4) : 0;
        d->p8 = *(void**)((unsigned char*)pp + 4);
        ++f;
        ++d;
    }
}

// FUNCTION: DAO 0x631690
void fn_00231690(S_00231650* begin, S_00231650* end, S_00231650* dstEnd) {
    S_00231650* e = end;
    S_00231650* d = dstEnd;
    while (begin != e) {
        --e;
        --d;
        unsigned char* pf = e ? (unsigned char*)e + 0xc : 0;
        d->flag12 = *pf;
        void** pp = e ? (void**)((unsigned char*)e + 4) : 0;
        d->p8 = *(void**)((unsigned char*)pp + 4);
    }
}

struct E_00240330 { unsigned int a[4]; };
struct C_00240330 { unsigned int pad; E_00240330* begin; E_00240330* end; bool fn_00240330(); };

// FUNCTION: DAO 0x640330
bool C_00240330::fn_00240330() {
    int n;
    if (this->begin == 0) {
        n = 0;
    } else {
        n = (int)(this->end - this->begin);
    }
    return n == 0;
}

struct C_00242df0 { unsigned char pad[8]; unsigned int offset; void fn_00242df0(void* dst, const unsigned int* src); };

// FUNCTION: DAO 0x642DF0
void C_00242df0::fn_00242df0(void* dst, const unsigned int* src) {
    unsigned int off = this->offset;
    unsigned int* d = (unsigned int*)dst;
    unsigned int v0 = src[0];
    *(unsigned int*)((unsigned char*)d + off) = v0;
    unsigned int v1 = src[1];
    *(unsigned int*)((unsigned char*)d + off + 4) = v1;
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
    const unsigned int* d = (const unsigned int*)p;
    if (p == 0) goto fail;
    if (size <= 0x1c) goto fail;
    if (d[0] != 0x20464647) goto fail;
    if (d[1] != 0x302e3456) goto fail;
    return d[2] == 0x20204350;
fail:
    return false;
}
