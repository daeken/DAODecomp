struct RbNode {
    RbNode* left;
    RbNode* right;
    RbNode* parent;
    unsigned char color;
    unsigned char pad[3];
};

struct Pool {
    void* first;
    void* unused;
    void* base;
    void* end;
    unsigned int stride;
    void fn_00021500(void**);
    void fn_000258f0(void*);
};

struct Container {
    unsigned char pad[0x2c];
    unsigned char* start;
    unsigned char* end;
    void* fn_00025020(unsigned int);
};

struct Holder {
    unsigned char pad[0x7c];
    void* value;
};

struct Outer {
    unsigned int unused;
    Holder* holder;
    void* fn_00031850();
};

// FUNCTION: DAO 0x004211B0
RbNode* __cdecl fn_000211b0(RbNode* x, RbNode* root)
{
    RbNode* y = x->right;
    x->right = y->left;
    if (y->left != 0)
        y->left->parent = x;
    y->parent = x->parent;
    if (x == root) {
        y->left = x;
        x->parent = y;
        return y;
    }
    RbNode* p = x->parent;
    if (x == p->left) {
        p->left = y;
        y->left = x;
        x->parent = y;
        return root;
    }
    p->right = y;
    y->left = x;
    x->parent = y;
    return root;
}

// FUNCTION: DAO 0x00421200
RbNode* __cdecl fn_00021200(RbNode* x, RbNode* p, RbNode* header, int insert_left)
{
    x->parent = p;
    x->left = 0;
    x->right = 0;
    x->color = 0;
    if (insert_left != 0) {
        p->left = x;
        if (p == header->left)
            header->left = x;
    } else {
        p->right = x;
        if (p == header) {
            header->parent = x;
            header->left = x;
        } else if (p == header->right) {
            header->right = x;
        }
    }
    if (x == header->parent) {
        x->color = 1;
        return x;
    }
    while (x->parent->color == 0) {
        if (x->parent == x->parent->parent->right) {
            RbNode* y = x->parent->parent->left;
            if (y != 0 && y->color == 0) {
                x->parent->color = 1;
                y->color = 1;
                x->parent->parent->color = 0;
                x = x->parent->parent;
            } else {
                if (x == x->parent->left) {
                    RbNode* z = x->parent;
                    RbNode* yy = z->left;
                    z->left = yy->right;
                    if (yy->right != 0)
                        yy->right->parent = z;
                    yy->parent = z->parent;
                    if (z == header->parent)
                        header->parent = yy;
                    else if (z == z->parent->right)
                        z->parent->right = yy;
                    else
                        z->parent->left = yy;
                    yy->right = z;
                    z->parent = yy;
                    x = z;
                }
                x->parent->color = 1;
                x->parent->parent->color = 0;
                {
                    RbNode* z = x->parent->parent;
                    RbNode* yy = z->right;
                    z->right = yy->left;
                    if (yy->left != 0)
                        yy->left->parent = z;
                    yy->parent = z->parent;
                    if (z == header->parent)
                        header->parent = yy;
                    else if (z == z->parent->left)
                        z->parent->left = yy;
                    else
                        z->parent->right = yy;
                    yy->left = z;
                    z->parent = yy;
                }
            }
        } else {
            RbNode* y = x->parent->parent->left;
            if (y != 0 && y->color == 0) {
                x->parent->color = 1;
                y->color = 1;
                x->parent->parent->color = 0;
                x = x->parent->parent;
            } else {
                if (x == x->parent->right) {
                    RbNode* z = x->parent;
                    RbNode* yy = z->right;
                    z->right = yy->left;
                    if (yy->left != 0)
                        yy->left->parent = z;
                    yy->parent = z->parent;
                    if (z == header->parent)
                        header->parent = yy;
                    else if (z == z->parent->left)
                        z->parent->left = yy;
                    else
                        z->parent->right = yy;
                    yy->left = z;
                    z->parent = yy;
                    x = z;
                }
                x->parent->color = 1;
                x->parent->parent->color = 0;
                {
                    RbNode* z = x->parent->parent;
                    RbNode* yy = z->left;
                    z->left = yy->right;
                    if (yy->right != 0)
                        yy->right->parent = z;
                    yy->parent = z->parent;
                    if (z == header->parent)
                        header->parent = yy;
                    else if (z == z->parent->right)
                        z->parent->right = yy;
                    else
                        z->parent->left = yy;
                    yy->right = z;
                    z->parent = yy;
                }
            }
        }
        if (x == header->parent)
            break;
    }
    header->parent->color = 1;
    return header->parent;
}

// FUNCTION: DAO 0x00421500
void __thiscall Pool::fn_00021500(void** src)
{
    unsigned int b = *(unsigned int*)src;
    unsigned int p = (b + 3u) & ~3u;
    first = (void*)p;
    unsigned int limit = b + 0x364u;
    if (p < limit) {
        do {
            *(unsigned int*)p = p + 0x1cu;
            p += 0x1cu;
        } while (p < limit);
    }
    *(unsigned int*)p = 0;
    base = (void*)b;
    end = (void*)(b + 0x380u);
    stride = 0x1cu;
}

// FUNCTION: DAO 0x00425020
void* __thiscall Container::fn_00025020(unsigned int key)
{
    int n = (int)((end - start) / 0x5c);
    if (n <= 0)
        return 0;
    unsigned char* p = start;
    for (unsigned int i = 0; i < (unsigned int)n; ++i) {
        if (*(unsigned int*)p == key)
            return p;
        p += 0x5c;
    }
    return 0;
}

// FUNCTION: DAO 0x004258F0
void __thiscall Pool::fn_000258f0(void* baseArg)
{
    unsigned int b = (unsigned int)baseArg;
    unsigned int p = (b + 3u) & ~3u;
    first = (void*)p;
    unsigned int limit = b + 0x364u;
    if (p < limit) {
        do {
            *(unsigned int*)p = p + 0x1cu;
            p += 0x1cu;
        } while (p < limit);
    }
    *(unsigned int*)p = 0;
    base = (void*)b;
    end = (void*)(b + 0x380u);
    stride = 0x1cu;
}

// FUNCTION: DAO 0x0042A210
unsigned int* __cdecl fn_0002a210(unsigned int* first, unsigned int* last, unsigned int* value)
{
    int count = (int)(last - first);
    if (count <= 0)
        return first;
    unsigned int target = *value;
    while (count > 0) {
        int half = count >> 1;
        if (first[half] < target) {
            first = first + half + 1;
            count = count - half - 1;
        } else {
            count = half;
        }
    }
    return first;
}

// FUNCTION: DAO 0x00431850
void* __thiscall Outer::fn_00031850()
{
    Holder* h = holder;
    if (h != 0)
        return (char*)h->value + 0x10;
    return 0;
}
