struct Pair003C96C0 { int field_0; int field_4; };

struct C003C96C0 {
    unsigned char pad0[0x18];
    int field_18;
    int fn_003c96c0(const Pair003C96C0* p, int* q, int* r);
};

struct C003CAD00 {
    unsigned char pad0[0x18];
    int field_18;
    void fn_003cad00();
};

struct S003CAED0 {
    unsigned char pad0[8];
    unsigned char byte_8;
    unsigned char byte_9;
    unsigned char padA[2];
    int field_c;
    int field_10;
    int field_14;
    int field_18;
    int field_1c;
};

struct C003CAFF0 {
    unsigned char pad0[0x4c];
    int field_4c;
    int fn_003caff0(int x);
};

struct Elem8 {
    unsigned char pad[8];
    unsigned char b8;
};

struct C003CB180 {
    unsigned char pad0[0x48];
    Elem8** arr;
    unsigned int count;
    void fn_003cb180();
};

struct Elem9 {
    unsigned char pad[9];
    unsigned char b9;
};

struct C003CB1A0 {
    unsigned char pad0[0x48];
    Elem9** arr;
    unsigned int count;
    void fn_003cb1a0();
};

struct C003CD010 {
    unsigned char pad0[0x99];
    unsigned char field_99;
    void fn_003cd010(unsigned char v);
};

struct C003CD290 {
    unsigned char pad0[0x18];
    unsigned char field_18;
    unsigned char pad19[0x94 - 0x19];
    int field_94;
    unsigned char pad98[0xe8 - 0x98];
    int field_e8;
    unsigned char padEC[0x11c - 0xec];
    unsigned char field_11c;
    unsigned char fn_003cd290();
};

struct TreeNode {
    TreeNode* left;
    TreeNode* parent;
    TreeNode* right;
    unsigned char pad0[0x41 - 12];
    unsigned char byte41;
    unsigned char pad1[0x65 - 0x42];
    unsigned char byte65;
};

struct C003CD460 {
    unsigned char pad0[4];
    TreeNode* field_4;
    void fn_003cd460(TreeNode* x);
};

struct C003CD4E0 {
    unsigned char pad0[4];
    TreeNode* field_4;
    void fn_003cd4e0(TreeNode* x);
};

struct C003CD730 {
    unsigned char pad0[4];
    int field_4;
    int field_8;
    int fn_003cd730();
};

struct C003CEB80 {
    unsigned char pad0[4];
    TreeNode* field_4;
    void fn_003ceb80(TreeNode* x);
};

// FUNCTION: DAO 0x7C96C0
int C003C96C0::fn_003c96c0(const Pair003C96C0* p, int* q, int* r)
{
    unsigned int sum = (unsigned int)p->field_0 + (unsigned int)p->field_4 * (unsigned int)this->field_18;
    int value = (int)sum;
    int quotient = value / 8;
    int remainder = value % 8;
    *q = quotient;
    *r = remainder;
    return quotient;
}

// FUNCTION: DAO 0x7CAD00
void C003CAD00::fn_003cad00()
{
    if (this->field_18 < 0 || this->field_18 >= 1)
        this->field_18 = 0;
}

// FUNCTION: DAO 0x7CAED0
bool __stdcall fn_003caed0(const S003CAED0* o, int v, unsigned char b)
{
    if (o->byte_8 != 0)
        return false;
    if (o->byte_9 != 0 && b == 0)
        return false;
    if (o->field_c != -1 && o->field_c != v)
        return false;
    if (o->field_14 != -1 && o->field_14 != v)
        return false;
    if (o->field_1c != -1 && o->field_1c != v)
        return false;
    if (o->field_18 != -1 && o->field_18 != v)
        return false;
    return true;
}

// FUNCTION: DAO 0x7CAFF0
int C003CAFF0::fn_003caff0(int x)
{
    if (x < 0)
        return x + this->field_4c;
    if (x <= this->field_4c - 1)
        return x;
    return x % this->field_4c;
}

// FUNCTION: DAO 0x7CB180
void C003CB180::fn_003cb180()
{
    for (unsigned int i = 0; i < this->count; ++i)
        this->arr[i]->b8 = 0;
}

// FUNCTION: DAO 0x7CB1A0
void C003CB1A0::fn_003cb1a0()
{
    for (unsigned int i = 0; i < this->count; ++i)
        this->arr[i]->b9 = 0;
}

// FUNCTION: DAO 0x7CD010
void C003CD010::fn_003cd010(unsigned char v)
{
    if (v != 0)
        this->field_99 &= 1;
    else
        this->field_99 &= 0xFE;
}

// FUNCTION: DAO 0x7CD290
unsigned char C003CD290::fn_003cd290()
{
    if (this->field_94 == 6)
        return 1;
    if (this->field_11c == 0)
        return this->field_18;
    if (this->field_18 == 0)
        return 0;
    if (this->field_e8 != 0)
        return 0;
    return 1;
}

// FUNCTION: DAO 0x7CD460
void C003CD460::fn_003cd460(TreeNode* x)
{
    TreeNode* y = x->left;
    x->left = y->right;
    if (y->right->byte65 == 0)
        y->right->parent = x;
    y->parent = x->parent;
    TreeNode* header = this->field_4;
    if (x == header->parent) {
        header->parent = y;
        y->right = x;
        x->parent = y;
    } else {
        TreeNode* p = x->parent;
        if (x == p->right) {
            p->right = y;
            y->right = x;
            x->parent = y;
        } else {
            p->left = y;
            y->right = x;
            x->parent = y;
        }
    }
}

// FUNCTION: DAO 0x7CD4C0
TreeNode* __cdecl fn_003cd4c0(TreeNode* node)
{
    TreeNode* eax = node;
    TreeNode* ecx = node->left;
    if (ecx->byte41 != 0)
        return eax;
    while (ecx->byte41 == 0) {
        eax = ecx;
        ecx = eax->left;
    }
    return eax;
}

// FUNCTION: DAO 0x7CD4E0
void C003CD4E0::fn_003cd4e0(TreeNode* x)
{
    TreeNode* y = x->left;
    x->left = y->right;
    if (y->right->byte41 == 0)
        y->right->parent = x;
    y->parent = x->parent;
    TreeNode* header = this->field_4;
    if (x == header->parent) {
        header->parent = y;
        y->right = x;
        x->parent = y;
    } else {
        TreeNode* p = x->parent;
        if (x == p->right) {
            p->right = y;
            y->right = x;
            x->parent = y;
        } else {
            p->left = y;
            y->right = x;
            x->parent = y;
        }
    }
}

// FUNCTION: DAO 0x7CD540
TreeNode* __cdecl fn_003cd540(TreeNode* node)
{
    TreeNode* eax = node;
    TreeNode* ecx = node->right;
    if (ecx->byte65 != 0)
        return eax;
    while (ecx->byte65 == 0) {
        eax = ecx;
        ecx = eax->right;
    }
    return eax;
}

// FUNCTION: DAO 0x7CD560
TreeNode* __cdecl fn_003cd560(TreeNode* node)
{
    TreeNode* eax = node;
    TreeNode* ecx = node->left;
    if (ecx->byte65 != 0)
        return eax;
    while (ecx->byte65 == 0) {
        eax = ecx;
        ecx = eax->left;
    }
    return eax;
}

// FUNCTION: DAO 0x7CD680
TreeNode* __cdecl fn_003cd680(TreeNode* node)
{
    TreeNode* eax = node;
    TreeNode* ecx = node->right;
    if (ecx->byte41 != 0)
        return eax;
    while (ecx->byte41 == 0) {
        eax = ecx;
        ecx = eax->right;
    }
    return eax;
}

// FUNCTION: DAO 0x7CD730
int C003CD730::fn_003cd730()
{
    if (this->field_4 == 0)
        return 0;
    return (this->field_8 - this->field_4) / 76;
}

// FUNCTION: DAO 0x7CEB80
void C003CEB80::fn_003ceb80(TreeNode* x)
{
    TreeNode* y = x->right;
    x->right = y->left;
    if (y->left->byte65 == 0)
        y->left->parent = x;
    y->parent = x->parent;
    TreeNode* header = this->field_4;
    if (x == header->parent) {
        header->parent = y;
        y->left = x;
        x->parent = y;
    } else {
        TreeNode* p = x->parent;
        if (x == p->left) {
            p->left = y;
            y->left = x;
            x->parent = y;
        } else {
            p->right = y;
            y->left = x;
            x->parent = y;
        }
    }
}
