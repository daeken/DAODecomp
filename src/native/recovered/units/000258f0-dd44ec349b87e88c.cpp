struct RbNode {
    RbNode* left;
    RbNode* right;
    RbNode* parent;
    unsigned char color;
    unsigned char pad[3];
};

struct Pool {
    void* first;
    unsigned int unused;
    void* base;
    void* end;
    unsigned int stride;
    Pool* fn_00021500(void** src);
    Pool* fn_000258f0(void* base);
};

struct Container {
    unsigned char pad[0x2c];
    unsigned char* start;
    unsigned char* end;
    void* fn_00025020(unsigned int key);
};

// FUNCTION: DAO 0x00421200
void __cdecl fn_00021200(RbNode* x, RbNode* p, RbNode* header, int insert_left)
{
    RbNode* y;
    RbNode* w;
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
        header->parent->color = 1;
        return;
    }
    while (x != header->parent && x->parent->color == 0) {
        if (x->parent == x->parent->parent->right) {
            y = x->parent->parent->left;
            if (y != 0 && y->color == 0) {
                x->parent->color = 1;
                y->color = 1;
                x->parent->parent->color = 0;
                x = x->parent->parent;
            } else {
                if (x == x->parent->left) {
                    x = x->parent;
                    w = x->left;
                    x->left = w->right;
                    if (w->right != 0)
                        w->right->parent = x;
                    w->parent = x->parent;
                    if (x == header->parent)
                        header->parent = w;
                    else if (x == x->parent->right)
                        x->parent->right = w;
                    else
                        x->parent->left = w;
                    w->right = x;
                    x->parent = w;
                }
                x->parent->color = 1;
                x->parent->parent->color = 0;
                {
                    RbNode* z = x->parent->parent;
                    w = z->right;
                    z->right = w->left;
                    if (w->left != 0)
                        w->left->parent = z;
                    w->parent = z->parent;
                    if (z == header->parent)
                        header->parent = w;
                    else if (z == z->parent->left)
                        z->parent->left = w;
                    else
                        z->parent->right = w;
                    w->left = z;
                    z->parent = w;
                }
            }
        } else {
            y = x->parent->parent->right;
            if (y != 0 && y->color == 0) {
                x->parent->color = 1;
                y->color = 1;
                x->parent->parent->color = 0;
                x = x->parent->parent;
            } else {
                if (x == x->parent->right) {
                    x = x->parent;
                    w = x->right;
                    x->right = w->left;
                    if (w->left != 0)
                        w->left->parent = x;
                    w->parent = x->parent;
                    if (x == header->parent)
                        header->parent = w;
                    else if (x == x->parent->left)
                        x->parent->left = w;
                    else
                        x->parent->right = w;
                    w->left = x;
                    x->parent = w;
                }
                x->parent->color = 1;
                x->parent->parent->color = 0;
                {
                    RbNode* z = x->parent->parent;
                    w = z->left;
                    z->left = w->right;
                    if (w->right != 0)
                        w->right->parent = z;
                    w->parent = z->parent;
                    if (z == header->parent)
                        header->parent = w;
                    else if (z == z->parent->right)
                        z->parent->right = w;
                    else
                        z->parent->left = w;
                    w->right = z;
                    z->parent = w;
                }
            }
        }
    }
    header->parent->color = 1;
}

// FUNCTION: DAO 0x00421500
Pool* __thiscall Pool::fn_00021500(void** src)
{
    Pool* self = this;
    unsigned int base = *(unsigned int*)*src;
    unsigned int p = (base + 3u) & ~3u;
    unsigned int limit = base + 0x364u;
    self->first = (void*)p;
    if (p < limit) {
        do {
            *(unsigned int*)p = p + 0x1cu;
            p += 0x1cu;
        } while (p < limit);
    }
    *(unsigned int*)p = 0;
    self->base = (void*)base;
    self->end = (void*)(base + 0x380u);
    self->stride = 0x1cu;
    return self;
}

// FUNCTION: DAO 0x00425020
void* __thiscall Container::fn_00025020(unsigned int key)
{
    int n = (int)(end - start) / 0x5c;
    unsigned int i = 0;
    if (n == 0)
        return 0;
    unsigned char* p = start;
    do {
        if (*(unsigned int*)p == key)
            return p;
        ++i;
        p += 0x5c;
    } while (i < (unsigned int)n);
    return 0;
}

// FUNCTION: DAO 0x004258F0
Pool* __thiscall Pool::fn_000258f0(void* base)
{
    Pool* self = this;
    unsigned int b = (unsigned int)base;
    unsigned int p = (b + 3u) & ~3u;
    unsigned int limit = b + 0x364u;
    self->first = (void*)p;
    if (p < limit) {
        do {
            *(unsigned int*)p = p + 0x1cu;
            p += 0x1cu;
        } while (p < limit);
    }
    *(unsigned int*)p = 0;
    self->base = (void*)b;
    self->end = (void*)(b + 0x380u);
    self->stride = 0x1cu;
    return self;
}
