struct HeapItem_00165cf0 {
    unsigned int x;
    unsigned int key;
    unsigned int z;
};

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

class C_00171510 {
public:
    void* fn_00171510();
};

// FUNCTION: DAO 0x565cf0
void fn_00165cf0(HeapItem_00165cf0* first, int hole, int top, unsigned int valueX, unsigned int valueKey, unsigned int valueZ)
{
    int parent = (hole - 1) / 2;
    if (top < hole) {
        while (first[parent].key < valueKey) {
            first[hole] = first[parent];
            hole = parent;
            parent = (hole - 1) / 2;
            if (top >= hole)
                break;
        }
    }
    first[hole].x = valueX;
    first[hole].key = valueKey;
    first[hole].z = valueZ;
}

// FUNCTION: DAO 0x571510
void* C_00171510::fn_00171510()
{
    return (void*)((unsigned char*)this + 0xC0);
}

// FUNCTION: DAO 0x572700
Node_00172700* fn_00172700(Node_00172700* node)
{
    Node_00172700* n = node->right;
    if (n->color != 0)
        return node;
    do {
        node = n;
        n = *(Node_00172700**)((char*)node + 8);
    } while (n->color == 0);
    return node;
}

// FUNCTION: DAO 0x572720
Node_00172700* fn_00172720(Node_00172700* node)
{
    Node_00172700* n = node->left;
    if (n->color != 0)
        return node;
    do {
        node = n;
        n = *(Node_00172700**)node;
    } while (n->color == 0);
    return node;
}

// FUNCTION: DAO 0x572740
void Tree_00172700::fn_00172740(Node_00172700* x)
{
    Node_00172700* y = x->left;
    x->left = y->right;
    if (y->right->color == 0)
        y->right->parent = x;
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

// FUNCTION: DAO 0x5731b0
void Tree_00172700::fn_001731b0(Node_00172700* x)
{
    Node_00172700* y = x->right;
    x->right = y->left;
    if (y->left->color == 0)
        y->left->parent = x;
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
