struct Pair8 { unsigned int lo; unsigned int hi; };
struct Pair16 { unsigned int pad0; unsigned int pad1; unsigned int f8; unsigned int f12; };
struct Blob40 { unsigned char data[40]; };
struct C4D7F20 { unsigned char pad[0x10]; unsigned int value; void fn_000d7f20(int* p); };
struct C566060 { unsigned char pad[4]; Pair8* begin; Pair8* end; unsigned int fn_00166060() const; };
struct C87B6B0 { unsigned char pad[4]; Blob40* begin; Blob40* end; unsigned int fn_0047b6b0() const; };
struct C8805F0 { unsigned int flags; void fn_004805f0(unsigned int* out) const; };
struct C893810 { unsigned char pad[0x110]; unsigned int f110; unsigned int f114; void fn_00493810(unsigned int* out, int flag) const; };
struct Node80e170 { Node80e170* left; Node80e170* parent; Node80e170* right; unsigned char pad[0x25]; unsigned char color; };
struct Tree80e170 { unsigned int pad0; Node80e170* root; void fn_0040e170(Node80e170* x); };
struct Tree847a30 { unsigned int pad0; Node80e170* root; void fn_00447a30(Node80e170* x); };

// FUNCTION: DAO 0x4D7F20
void C4D7F20::fn_000d7f20(int* p) {
    if (*p == -1) {
        *p = (int)value;
        ++value;
    }
}

// FUNCTION: DAO 0x4DF6C0
void* __cdecl fn_000df6c0(void* first, void* last, void* result) {
    Pair8* f = (Pair8*)first;
    Pair8* l = (Pair8*)last;
    Pair8* r = (Pair8*)result;
    unsigned int n = (unsigned int)(l - f);
    Pair8* d = r - n;
    while (l != f) {
        --l;
        --d;
        *d = *l;
    }
    return d;
}

// FUNCTION: DAO 0x4E7880
void* __cdecl fn_000e7880(void* first, void* last, const void* source) {
    Pair8* d = (Pair8*)first;
    Pair8* l = (Pair8*)last;
    const Pair8* s = (const Pair8*)source;
    while (d != l) {
        *d = *s;
        ++d;
        ++s;
    }
    return d;
}

// FUNCTION: DAO 0x566060
unsigned int C566060::fn_00166060() const {
    if (begin == 0) return 0;
    return (unsigned int)(end - begin);
}

// FUNCTION: DAO 0x5DD930
void __cdecl fn_001dd930(Pair8* first, Pair8* middle, Pair8* last) {
    int m = (int)(last - first);
    int n = (int)(middle - first);
    if (n == 0) return;
    int a = m;
    int b = n;
    while (b != 0) {
        int r = a % b;
        a = b;
        b = r;
    }
    int g = a;
    if (g <= 0 || g >= m) return;
    Pair8* p = first + g;
    do {
        Pair8 temp = *p;
        Pair8* hole = p;
        for (;;) {
            Pair8* next = hole + n;
            if (next >= last) next = first + (next - last);
            if (next == p) break;
            *hole = *next;
            hole = next;
        }
        *hole = temp;
        --p;
        --g;
    } while (g > 0);
}

// FUNCTION: DAO 0x62AC60
Pair16* __cdecl fn_0022ac60(Pair16* first, Pair16* last, Pair16* result) {
    Pair16* d = result;
    while (first != last) {
        d->f12 = first->f12;
        d->f8 = first->f8;
        ++first;
        ++d;
    }
    return d;
}

// FUNCTION: DAO 0x768840
Pair16* __cdecl fn_00368840(Pair16* first, Pair16* last, Pair16* result_end) {
    Pair16* s = last;
    Pair16* d = result_end;
    while (s != first) {
        --s;
        --d;
        d->f12 = s->f12;
        d->f8 = s->f8;
    }
    return d;
}

// FUNCTION: DAO 0x7B4B70
Pair16* __cdecl fn_003b4b70(Pair16* first, Pair16* last, Pair16* value) {
    Pair16* d = first;
    while (d != last) {
        d->f12 = value->f12;
        d->f8 = value->f8;
        ++d;
    }
    return d;
}

// FUNCTION: DAO 0x80E170
void Tree80e170::fn_0040e170(Node80e170* x) {
    Node80e170* y = x->left;
    x->left = y->right;
    if (y->right->color == 0) y->right->parent = x;
    y->parent = x->parent;
    if (x == root) {
        root = y;
    } else if (x == x->parent->right) {
        x->parent->right = y;
    } else {
        x->parent->left = y;
    }
    y->right = x;
    x->parent = y;
}

// FUNCTION: DAO 0x847A30
void Tree847a30::fn_00447a30(Node80e170* x) {
    Node80e170* y = x->right;
    x->right = y->left;
    if (y->left->color == 0) y->left->parent = x;
    y->parent = x->parent;
    if (x == root) {
        root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }
    y->left = x;
    x->parent = y;
}

// FUNCTION: DAO 0x87B6B0
unsigned int C87B6B0::fn_0047b6b0() const {
    if (begin == 0) return 0;
    return (unsigned int)(end - begin);
}

// FUNCTION: DAO 0x8805F0
void C8805F0::fn_004805f0(unsigned int* out) const {
    *out = flags & 0xf00fffffU;
}

// FUNCTION: DAO 0x893810
void C893810::fn_00493810(unsigned int* out, int flag) const {
    *out = (flag == 0) ? f110 : f114;
}

// FUNCTION: DAO 0x8EFEC9
unsigned int __cdecl fn_004efec9(const unsigned short* s) {
    const unsigned short* p = s;
    while (*p != 0) ++p;
    return (unsigned int)(p - s);
}

// FUNCTION: DAO 0x8FC206
unsigned short* __fastcall fn_004fc206(unsigned short* out, int value) {
    int q = value / 10;
    int r = value % 10;
    out[0] = (unsigned short)(q + 0x30);
    out[1] = (unsigned short)(r + 0x30);
    return out + 2;
}
