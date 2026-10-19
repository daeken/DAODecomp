struct Key3 {
    unsigned int a;
    unsigned int b;
    unsigned int c;
    bool __thiscall fn_00475300(const Key3* other) const;
};

struct Node {
    Node* left;
    Node* parent;
    Node* right;
    unsigned int pad0;
    unsigned int pad1;
    unsigned int pad2;
    unsigned int pad3;
    unsigned char pad4;
    unsigned char isnil;
};

struct Tree {
    unsigned int pad0;
    Node* header;
    void __thiscall fn_00475590(Node* x);
    void __thiscall fn_004755e0(Node* x);
};

struct Vec12 {
    unsigned int pad0;
    unsigned char* begin;
    unsigned char* end;
    bool __thiscall fn_004777d0() const;
    void __thiscall fn_0047df00(const unsigned int* p);
};

struct ByteHolder {
    unsigned char pad[0x2c];
    unsigned char value;
    void __thiscall fn_0048e690(unsigned char v);
};

// FUNCTION: DAO 0x86BF10
void __cdecl fn_0046bf10(unsigned int* p1, unsigned int* p2, unsigned int* p3)
{
    if (*p2 > *p1 || (*p2 == *p1 && (p2[1] > p1[1] || (p2[1] == p1[1] && (p2[3] > p1[3] || (p2[3] == p1[3] && p2[2] > p1[2])))))) {
        unsigned int t0 = p1[0]; p1[0] = p2[0]; p2[0] = t0;
        unsigned int t1 = p1[1]; p1[1] = p2[1]; p2[1] = t1;
        unsigned int t2 = p1[2]; p1[2] = p2[2]; p2[2] = t2;
        unsigned int t3 = p1[3]; p1[3] = p2[3]; p2[3] = t3;
    }
    if (*p3 > *p2 || (*p3 == *p2 && (p3[1] > p2[1] || (p3[1] == p2[1] && (p3[3] > p2[3] || (p3[3] == p2[3] && p3[2] > p2[2])))))) {
        unsigned int t0 = p2[0]; p2[0] = p3[0]; p3[0] = t0;
        unsigned int t1 = p2[1]; p2[1] = p3[1]; p3[1] = t1;
        unsigned int t2 = p2[2]; p2[2] = p3[2]; p3[2] = t2;
        unsigned int t3 = p2[3]; p2[3] = p3[3]; p3[3] = t3;
    }
    if (*p2 > *p1 || (*p2 == *p1 && (p2[1] > p1[1] || (p2[1] == p1[1] && (p2[3] > p1[3] || (p2[3] == p1[3] && p2[2] > p1[2])))))) {
        unsigned int t0 = p1[0]; p1[0] = p2[0]; p2[0] = t0;
        unsigned int t1 = p1[1]; p1[1] = p2[1]; p2[1] = t1;
        unsigned int t2 = p1[2]; p1[2] = p2[2]; p2[2] = t2;
        unsigned int t3 = p1[3]; p1[3] = p2[3]; p2[3] = t3;
    }
}

// FUNCTION: DAO 0x875300
bool __thiscall Key3::fn_00475300(const Key3* other) const
{
    if (this->a < other->a) return true;
    if (this->a > other->a) return false;
    if (this->b < other->b) return true;
    if (this->b > other->b) return false;
    return this->c < other->c;
}

// FUNCTION: DAO 0x875340
Node* __cdecl fn_00475340(Node* x)
{
    Node* y = x->right;
    while (y->isnil == 0) {
        x = y;
        y = x->right;
    }
    return x;
}

// FUNCTION: DAO 0x875590
void __thiscall Tree::fn_00475590(Node* x)
{
    Node* y = x->right;
    x->right = y->left;
    if (y->left->isnil == 0)
        y->left->parent = x;
    y->parent = x->parent;
    if (x == this->header->parent)
        this->header->parent = y;
    else if (x == x->parent->left)
        x->parent->left = y;
    else
        x->parent->right = y;
    y->left = x;
    x->parent = y;
}

// FUNCTION: DAO 0x8755E0
void __thiscall Tree::fn_004755e0(Node* x)
{
    Node* y = x->left;
    x->left = y->right;
    if (y->right->isnil == 0)
        y->right->parent = x;
    y->parent = x->parent;
    if (x == this->header->parent)
        this->header->parent = y;
    else if (x == x->parent->right)
        x->parent->right = y;
    else
        x->parent->left = y;
    y->right = x;
    x->parent = y;
}

// FUNCTION: DAO 0x8777D0
bool __thiscall Vec12::fn_004777d0() const
{
    if (this->begin == 0)
        return true;
    int n = (int)(this->end - this->begin) / 12;
    return n == 0;
}

// FUNCTION: DAO 0x87DE50
int __fastcall fn_0047de50(unsigned int index, unsigned int /*unused*/, unsigned char** p)
{
    return (((unsigned char*)(*p))[index + 0x3d] >> 7) & 1;
}

// FUNCTION: DAO 0x87DF00
void __thiscall Vec12::fn_0047df00(const unsigned int* p)
{
    this->begin = (unsigned char*)p[0];
    this->end = (unsigned char*)p[1];
}

// FUNCTION: DAO 0x87DF60
int __stdcall fn_0047df60(const unsigned int* p)
{
    unsigned int v = *p;
    if (v == 0x36 || v == 0x2a || v == 0xb8 || v == 0x38 || v == 0x9d || v == 0x1d)
        return 1;
    return 0;
}

// FUNCTION: DAO 0x87E300
void __cdecl fn_0047e300(unsigned short* dst, unsigned short* end, const unsigned short* src)
{
    while (dst != end) {
        *dst = *src;
        ++dst;
    }
}

// FUNCTION: DAO 0x87E320
void __cdecl fn_0047e320(unsigned short* dst, unsigned int count, const unsigned short* src)
{
    unsigned int d = (unsigned int)dst;
    unsigned int s = (unsigned int)src;
    while (count != 0) {
        if (d != 0)
            *(unsigned short*)d = *(const unsigned short*)s;
        --count;
        d += 2;
    }
}

// FUNCTION: DAO 0x87E390
void __cdecl fn_0047e390(unsigned short* begin, unsigned short* end, unsigned short* dst)
{
    while (end != begin) {
        --end;
        --dst;
        *dst = *end;
    }
}

// FUNCTION: DAO 0x88E690
void __thiscall ByteHolder::fn_0048e690(unsigned char v)
{
    this->value = v;
}
