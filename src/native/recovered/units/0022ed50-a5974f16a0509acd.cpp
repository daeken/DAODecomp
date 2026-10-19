struct C_0022ed50 { unsigned char pad[0x48c]; void* fn_0022ed50(); };
struct N_0022eec0 { N_0022eec0* next; unsigned char pad[0x19]; unsigned char flag; };
struct N_0022f6b0 { N_0022f6b0* left; N_0022f6b0* parent; N_0022f6b0* right; unsigned char pad[5]; unsigned char color; };
struct T_0022f6b0 { unsigned char pad[4]; N_0022f6b0* header; void fn_0022f6b0(N_0022f6b0* x); };
struct C_0022f9d0 { unsigned char pad[0x238]; unsigned int* begin; unsigned int* end; int fn_0022f9d0(); };
struct N_002314d0 { N_002314d0* left; N_002314d0* parent; N_002314d0* right; unsigned int key; unsigned char pad[13]; unsigned char flag; };
struct I_002314d0 { void* tree; N_002314d0* node; };
struct P_002314d0 { I_002314d0 first; I_002314d0 second; };
struct T_002314d0 { unsigned char pad[4]; N_002314d0* header; void fn_002314d0(I_002314d0* out, const unsigned int* key); void fn_00231540(P_002314d0* out, const unsigned int* key); };
struct S_00231650 { unsigned int a0; unsigned int a1; void* p8; unsigned char flag12; unsigned char pad[3]; };
struct C_00240060 { unsigned char pad[0x74]; void* p; int fn_00240060(); };
struct C_00240070 { unsigned char pad[0x78]; unsigned int v; int fn_00240070(); };
struct E_00240330 { unsigned int a[4]; };
struct C_00240330 { unsigned int pad; E_00240330* begin; E_00240330* end; int fn_00240330(); };
struct C_00242df0 { unsigned char pad[8]; unsigned int offset; void fn_00242df0(void* dst, const unsigned int* src); };
struct C_00242e10 { unsigned char pad[8]; unsigned int value; void fn_00242e10(unsigned int* out); };
struct C_00243400 { unsigned char pad[8]; unsigned int offset; };

// FUNCTION: DAO 0x62ED50
void* C_0022ed50::fn_0022ed50() { return (void*)((unsigned char*)this + 0x48c); }

// FUNCTION: DAO 0x62EEC0
N_0022eec0* fn_0022eec0(N_0022eec0** p) {
    N_0022eec0* result = (N_0022eec0*)p;
    N_0022eec0* cur = *p;
    if (cur->flag == 0) {
        do {
            result = cur;
            cur = cur->next;
        } while (cur->flag == 0);
    }
    return result;
}

// FUNCTION: DAO 0x62F6B0
void T_0022f6b0::fn_0022f6b0(N_0022f6b0* x) {
    N_0022f6b0* y = x->right;
    x->right = y->left;
    if (y->left != 0) y->left->parent = x;
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

// FUNCTION: DAO 0x62F9D0
int C_0022f9d0::fn_0022f9d0() {
    if (begin == 0) return 0;
    return (int)(end - begin);
}

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
    N_002314d0* h = this->header;
    if (y == h || *key < y->key) {
        out->tree = this;
        out->node = h;
    } else {
        out->tree = this;
        out->node = y;
    }
}

// FUNCTION: DAO 0x631540
void T_002314d0::fn_00231540(P_002314d0* out, const unsigned int* key) {
    N_002314d0* header = this->header;
    N_002314d0* x = header->parent;
    N_002314d0* lower = header;
    while (x->flag == 0) {
        if (*key < x->key) {
            lower = x;
            x = x->left;
        } else {
            x = x->right;
        }
    }
    N_002314d0* h2 = this->header;
    N_002314d0* y = h2->parent;
    N_002314d0* upper = h2;
    while (y->flag == 0) {
        if (y->key < *key) {
            y = y->right;
        } else {
            upper = y;
            y = y->left;
        }
    }
    out->first.tree = this;
    out->first.node = upper;
    out->second.tree = this;
    out->second.node = lower;
}

// FUNCTION: DAO 0x631650
void fn_00231650(S_00231650* first, S_00231650* last, S_00231650* dst) {
    while (first != last) {
        dst->flag12 = first ? first->flag12 : 0;
        dst->p8 = first ? first->p8 : 0;
        ++first;
        ++dst;
    }
}

// FUNCTION: DAO 0x631690
void fn_00231690(S_00231650* begin, S_00231650* end, S_00231650* dstEnd) {
    while (end != begin) {
        --end;
        --dstEnd;
        dstEnd->flag12 = end ? end->flag12 : 0;
        dstEnd->p8 = end ? end->p8 : 0;
    }
}

// FUNCTION: DAO 0x631D50
void fn_00231d50(S_00231650* first, S_00231650* last, const S_00231650* value) {
    while (first != last) {
        first->flag12 = value ? value->flag12 : 0;
        first->p8 = value ? value->p8 : 0;
        ++first;
    }
}

// FUNCTION: DAO 0x640060
int C_00240060::fn_00240060() {
    if (p == 0) return -1;
    return *(int*)((char*)p + 0x5c);
}

// FUNCTION: DAO 0x640070
int C_00240070::fn_00240070() {
    return v == 9;
}

// FUNCTION: DAO 0x640330
int C_00240330::fn_00240330() {
    int n = 0;
    if (begin != 0) n = (int)(end - begin);
    return n == 0;
}

// FUNCTION: DAO 0x642DF0
void C_00242df0::fn_00242df0(void* dst, const unsigned int* src) {
    unsigned int off = offset;
    unsigned int* p = (unsigned int*)((char*)dst + off);
    p[0] = src[0];
    p[1] = src[1];
}

// FUNCTION: DAO 0x642E10
void C_00242e10::fn_00242e10(unsigned int* out) {
    *out = value;
}

// FUNCTION: DAO 0x643400
unsigned __int64 fn_00243400(const C_00243400* obj, const unsigned int* base) {
    return *(const unsigned __int64*)((const char*)base + obj->offset);
}

// FUNCTION: DAO 0x6454D0
int fn_002454d0(const void* p, unsigned int size) {
    if (p == 0 || size <= 0x1c) return 0;
    const unsigned int* d = (const unsigned int*)p;
    if (d[0] != 0x20464647 || d[1] != 0x302e3456) return 0;
    return d[2] == 0x20204350;
}
