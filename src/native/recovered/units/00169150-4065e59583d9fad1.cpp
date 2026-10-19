struct HeapItem_00165cf0 { unsigned int x; unsigned int key; unsigned int z; };

struct Node_00172700 {
    Node_00172700* left;
    Node_00172700* parent;
    Node_00172700* right;
    unsigned char pad_0C[0x35 - 0x0C];
    unsigned char color;
};

class Tree_00172700 {
public:
    void fn_00172740(Node_00172700* x);
    void fn_001731b0(Node_00172700* x);
private:
    unsigned int m_pad0;
    Node_00172700* mHeader;
};

class C_00169150 {
public:
    int fn_00169150();
private:
    unsigned int m_pad0;
    unsigned char* mBegin;
    unsigned char* mEnd;
};

class C_00171510 {
public:
    void* fn_00171510();
private:
    unsigned char m_pad0[0xC0];
};

class C_001728b0 {
public:
    void* fn_001728b0(unsigned int index);
private:
    unsigned char* mBase;
};

class C_0017B9 {
public:
    unsigned int fn_0017b930();
    void fn_0017b940(unsigned int v);
    unsigned int fn_0017b950();
private:
    unsigned char m_pad0[0x180];
    unsigned int m180;
    unsigned int m184;
};

class C_0017E3E0 {
public:
    int fn_0017e3e0();
private:
    unsigned char m_pad0[0x24];
    int m24;
    unsigned char m_pad28[0x4c - 0x28];
    int m4c;
};

class C_0017E3F0 {
public:
    unsigned int fn_0017e3f0();
private:
    unsigned char m_pad0[0x2c];
    unsigned int m2c;
    unsigned char m_pad30[0x34 - 0x30];
    unsigned int m34;
};

class C_0017F620 {
public:
    void fn_0017f620(unsigned int v);
private:
    unsigned char m_pad0[0x24];
    unsigned int m24;
};

class C_00183300 {
public:
    void* fn_00183300(unsigned int index);
private:
    unsigned char* mBase;
};

class C_00186460 {
public:
    void fn_00186460(unsigned char v);
private:
    unsigned char m_pad0[0x52];
    unsigned char m52;
};

// FUNCTION: DAO 0x565cf0
void fn_00165cf0(HeapItem_00165cf0* first, int hole, int top, HeapItem_00165cf0 value)
{
    int parent = (hole - 1) / 2;
    if (top < hole) {
        while (first[parent].key < value.key) {
            first[hole] = first[parent];
            hole = parent;
            parent = (hole - 1) / 2;
            if (top >= hole) break;
        }
    }
    first[hole] = value;
}

// FUNCTION: DAO 0x569150
int C_00169150::fn_00169150()
{
    if (mBegin == 0) return 0;
    return (int)(mEnd - mBegin) / 84;
}

// FUNCTION: DAO 0x571510
void* C_00171510::fn_00171510()
{
    return (void*)m_pad0;
}

// FUNCTION: DAO 0x572700
Node_00172700* fn_00172700(Node_00172700* node)
{
    Node_00172700* n = node->right;
    if (n->color != 0) return node;
    do {
        node = n;
        n = node->right;
    } while (n->color == 0);
    return node;
}

// FUNCTION: DAO 0x572720
Node_00172700* fn_00172720(Node_00172700* node)
{
    Node_00172700* n = node->left;
    if (n->color != 0) return node;
    do {
        node = n;
        n = node->left;
    } while (n->color == 0);
    return node;
}

// FUNCTION: DAO 0x572740
void Tree_00172700::fn_00172740(Node_00172700* x)
{
    Node_00172700* y = x->left;
    x->left = y->right;
    if (y->right->color != 0) y->right->parent = x;
    y->parent = x->parent;
    if (x == mHeader->parent) {
        mHeader->parent = y;
    } else if (x == x->parent->right) {
        x->parent->right = y;
    } else {
        x->parent->left = y;
    }
    y->right = x;
    x->parent = y;
}

// FUNCTION: DAO 0x5728b0
void* C_001728b0::fn_001728b0(unsigned int index)
{
    unsigned int offset = index << 4;
    return (void*)(mBase + offset);
}

// FUNCTION: DAO 0x5731b0
void Tree_00172700::fn_001731b0(Node_00172700* x)
{
    Node_00172700* y = x->right;
    x->right = y->left;
    if (y->left->color != 0) y->left->parent = x;
    y->parent = x->parent;
    if (x == mHeader->parent) {
        mHeader->parent = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }
    y->left = x;
    x->parent = y;
}

// FUNCTION: DAO 0x57b930
unsigned int C_0017B9::fn_0017b930()
{
    return m180;
}

// FUNCTION: DAO 0x57b940
void C_0017B9::fn_0017b940(unsigned int v)
{
    m184 = v;
}

// FUNCTION: DAO 0x57b950
unsigned int C_0017B9::fn_0017b950()
{
    return m184;
}

// FUNCTION: DAO 0x57e3e0
int C_0017E3E0::fn_0017e3e0()
{
    return m4c * m24;
}

// FUNCTION: DAO 0x57e3f0
unsigned int C_0017E3F0::fn_0017e3f0()
{
    unsigned int r = m2c;
    if (m34 == 0) return r + r;
    if (m34 == 1) { r = r + r; return r + r; }
    return 0;
}

// FUNCTION: DAO 0x57f620
void C_0017F620::fn_0017f620(unsigned int v)
{
    m24 = v;
}

// FUNCTION: DAO 0x583300
void* C_00183300::fn_00183300(unsigned int index)
{
    unsigned int offset = (index + index + index) << 5;
    return (void*)(mBase + offset);
}

// FUNCTION: DAO 0x586460
void C_00186460::fn_00186460(unsigned char v)
{
    m52 = v;
}
