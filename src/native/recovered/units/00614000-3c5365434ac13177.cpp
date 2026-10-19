struct C005eb170 {
    unsigned int f00, f04, f08, f0c, f10, f14, f18, f1c, f20, f24, f28, f2c, f30, f34, f38, f3c, f40, f44, f48, f4c, f50, f54, f58, f5c, f60, f64, f68, f6c, f70, f74, f78, f7c, f80;
    void fn_005eb170();
};
// FUNCTION: DAO 0x9EB170
void C005eb170::fn_005eb170() {
    this->f00 = 0; this->f04 = 0; this->f08 = 0; this->f0c = 0;
    this->f10 = 0x40u; this->f14 = 0; this->f18 = 0; this->f1c = 0; this->f20 = 0;
    this->f24 = 0x40u; this->f28 = 0; this->f2c = 0; this->f30 = 0; this->f34 = 0;
    this->f38 = 0x40u; this->f3c = 0; this->f40 = 0; this->f44 = 0; this->f48 = 0; this->f4c = 0; this->f50 = 0; this->f54 = 0;
    this->f58 = 0x40u; this->f5c = 0; this->f60 = 0; this->f64 = 0; this->f68 = 0;
    this->f6c = 0x40u; this->f70 = 0; this->f74 = 0; this->f78 = 0; this->f7c = 0;
    this->f80 = 0x40u;
}

struct Run005f0f00 {
    unsigned int start;
    unsigned int count;
};
struct Pair005f0f00 {
    unsigned short x;
    unsigned short y;
};
struct C005f0f00 {
    unsigned int f00;
    unsigned int count;
    unsigned int f08;
    unsigned int f0c;
    Run005f0f00** runs;
    unsigned int f14, f18, f1c, f20;
    Pair005f0f00** vals;
    void fn_005f0f00();
};
// FUNCTION: DAO 0x9F0F00
void C005f0f00::fn_005f0f00() {
    unsigned int i = 0;
    if (this->count == 0) return;
    do {
        Run005f0f00* e = this->runs[i >> 6] + (i & 0x3f);
        unsigned int n = e->count;
        if (n > 2) {
            unsigned int s = e->start;
            Pair005f0f00* p0 = this->vals[s >> 6] + (s & 0x3f);
            unsigned int last = s + n - 1;
            Pair005f0f00* p1 = this->vals[last >> 6] + (last & 0x3f);
            if (p0->x == p1->x && p0->y == p1->y) {
                e->count = n - 1;
            }
        }
        ++i;
    } while (i < this->count);
}

struct Entry005f1a60 {
    int a;
    int b;
    int c;
};
struct Core005f1a60 {
    unsigned int p00;
    unsigned int p04;
    unsigned int p08;
    Entry005f1a60** arr;
};
struct Node005f1a60 {
    unsigned int i0;
    unsigned int i1;
    unsigned int i2;
};
struct C005f1a60 {
    Core005f1a60* core;
    bool fn_005f1a60(const Node005f1a60* x, const Node005f1a60* y);
};
// FUNCTION: DAO 0x9F1A60
bool C005f1a60::fn_005f1a60(const Node005f1a60* x, const Node005f1a60* y) {
    int a0 = this->core->arr[x->i0 >> 6][x->i0 & 0x3f].c;
    int b0 = this->core->arr[y->i0 >> 6][y->i0 & 0x3f].c;
    if (a0 != b0) return a0 < b0;
    int a1 = this->core->arr[x->i1 >> 6][x->i1 & 0x3f].c;
    int b1 = this->core->arr[y->i1 >> 6][y->i1 & 0x3f].c;
    if (a1 != b1) return a1 < b1;
    int a2 = this->core->arr[x->i2 >> 6][x->i2 & 0x3f].c;
    int b2 = this->core->arr[y->i2 >> 6][y->i2 & 0x3f].c;
    return a2 < b2;
}

struct C005f22f0 {
    unsigned int count;
    unsigned int f04;
    unsigned int f08;
    unsigned int** arr;
    void fn_005f22f0(unsigned int index);
};
// FUNCTION: DAO 0x9F22F0
void C005f22f0::fn_005f22f0(unsigned int index) {
    if (this->count == 0) return;
    unsigned int i = index + 1;
    if (i < this->count) {
        do {
            this->arr[i >> 6][i & 0x3f] = this->arr[(i - 1) >> 6][(i - 1) & 0x3f];
            ++i;
        } while (i < this->count);
    }
    --this->count;
}

struct C005f2750 {
    unsigned int count;
    unsigned int f04;
    unsigned int f08;
    unsigned int** arr;
};
// FUNCTION: DAO 0x9F2750
void __cdecl fn_005f2750(C005f2750* obj) {
    if (obj->count < 2) return;
    unsigned int end = obj->count - 1;
    unsigned int i = 0;
    while (i < end) {
        unsigned int* p0 = obj->arr[i >> 6] + (i & 0x3f);
        unsigned int* p1 = obj->arr[end >> 6] + (end & 0x3f);
        unsigned int tmp = *p0;
        *p0 = *p1;
        *p1 = tmp;
        ++i;
        --end;
    }
}

struct Entry005f27a0 {
    unsigned int key0;
    unsigned int key1;
    unsigned int value;
};
struct A005f27a0 {
    unsigned int count;
    unsigned int f04;
    unsigned int* indices;
};
struct Target005f27a0 {
    unsigned int key0;
    unsigned int key1;
};
struct C005f27a0 {
    unsigned int f00;
    unsigned int f04;
    unsigned int f08;
    Entry005f27a0** arr;
};
// FUNCTION: DAO 0x9F27A0
unsigned int __cdecl fn_005f27a0(const A005f27a0* a, const Target005f27a0* target, unsigned int unused, const C005f27a0* c) {
    unsigned int high = a->count;
    unsigned int low = 0;
    while (high > 0) {
        unsigned int half = high >> 1;
        unsigned int mid = low + half;
        unsigned int idx = a->indices[mid];
        const Entry005f27a0* e = c->arr[idx >> 6] + (idx & 0x3f);
        bool less;
        if (e->key0 != target->key0) {
            less = e->key0 < target->key0;
        } else {
            less = e->key1 < target->key1;
        }
        if (less) {
            low = mid + 1;
            high = high - (half + 1);
        } else {
            high = half;
        }
    }
    return low;
}

// FUNCTION: DAO 0xA026F0
int __fastcall fn_006026f0(int a, int b) {
    return (b * 0x1fe + a + 0xff) / (a + a);
}

struct C00614000 {
    unsigned int pad[14];
    unsigned int field38;
    unsigned int fn_00614000(unsigned int index);
};
// FUNCTION: DAO 0xA14000
unsigned int C00614000::fn_00614000(unsigned int index) {
    return this->field38 + (index << 5);
}
