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

// FUNCTION: DAO 0x565cf0
void fn_00165cf0(HeapItem_00165cf0* first, int hole, int top, HeapItem_00165cf0 value)
{
    int parent = (hole - 1) / 2;
    while (top < hole && first[parent].key < value.key) {
        first[hole] = first[parent];
        hole = parent;
        parent = (hole - 1) / 2;
    }
    first[hole] = value;
}

// FUNCTION: DAO 0x572700
Node_00172700* fn_00172700(Node_00172700* node)
{
    Node_00172700* n = node->right;
    while (n->color == 0) {
        node = n;
        n = *(Node_00172700**)((char*)node + 8);
    }
    return node;
}

// FUNCTION: DAO 0x572720
Node_00172700* fn_00172720(Node_00172700* node)
{
    Node_00172700* n = node->left;
    while (n->color == 0) {
        node = n;
        n = *(Node_00172700**)((char*)node + 0);
    }
    return node;
}
