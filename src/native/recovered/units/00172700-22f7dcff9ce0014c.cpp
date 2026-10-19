struct Node_00172700 {
    Node_00172700* left;
    Node_00172700* parent;
    Node_00172700* right;
    unsigned char pad_0C[0x35 - 0x0C];
    unsigned char color;
};

// FUNCTION: DAO 0x572700
Node_00172700* fn_00172700(Node_00172700* node)
{
    while (node->right->color == 0)
        node = node->right;
    return node;
}

// FUNCTION: DAO 0x572720
Node_00172700* fn_00172720(Node_00172700* node)
{
    while (node->left->color == 0)
        node = node->left;
    return node;
}
