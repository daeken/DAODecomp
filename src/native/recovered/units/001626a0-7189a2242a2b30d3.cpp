struct C1626A0 {
    unsigned int pad0[0x38 / 4];
    int field38;
    unsigned int pad3C[2];
    int field44;
    int fn_001626a0();
};

// FUNCTION: DAO 0x005626A0
int C1626A0::fn_001626a0()
{
    return field44 * field38;
}

struct C1626B0 {
    unsigned int pad0[0x38 / 4];
    int field38;
    unsigned int pad3C;
    int field40;
    int fn_001626b0();
};

// FUNCTION: DAO 0x005626B0
int C1626B0::fn_001626b0()
{
    return field40 * field38;
}

struct Node162700 {
    Node162700* left;
    Node162700* parent;
    Node162700* right;
    unsigned int key;
    unsigned char pad10[5];
    unsigned char flag15;
};

struct C162700 {
    unsigned int pad0;
    Node162700* field4;
    void fn_00162700(void* out, const unsigned int* key);
};

// FUNCTION: DAO 0x00562700
void C162700::fn_00162700(void* out, const unsigned int* key)
{
    Node162700* edx = field4;
    Node162700* eax = edx->parent;
    if (eax->flag15 == 0) {
        for (;;) {
            unsigned int k = *key;
            if (k < eax->key) {
                edx = eax;
                eax = eax->left;
            } else {
                eax = eax->right;
            }
            if (eax->flag15 != 0) {
                break;
            }
        }
    }
    Node162700* esi = field4;
    eax = esi->parent;
    if (eax->flag15 == 0) {
        unsigned int k = *key;
        do {
            if (eax->key >= k) {
                esi = eax;
                eax = eax->left;
            } else {
                eax = eax->right;
            }
        } while (eax->flag15 == 0);
    }
    ((void**)out)[0] = this;
    ((void**)out)[1] = esi;
    ((void**)out)[2] = this;
    ((void**)out)[3] = edx;
}

struct C163550 {
    unsigned char pad0[0x3d8];
    unsigned int field3d8;
    unsigned char field3dc;
    bool fn_00163550(unsigned int, unsigned int value, unsigned char flag);
};

// FUNCTION: DAO 0x00563550
bool C163550::fn_00163550(unsigned int, unsigned int value, unsigned char flag)
{
    field3d8 = value;
    field3dc = flag;
    return true;
}

struct C163620 {
    unsigned char pad0[0x494];
    unsigned int field494;
    void fn_00163620(unsigned int value);
};

// FUNCTION: DAO 0x00563620
void C163620::fn_00163620(unsigned int value)
{
    field494 = value;
}

struct C163780 {
    unsigned char pad0[0x450];
    unsigned char field450;
    unsigned char* fn_00163780();
};

// FUNCTION: DAO 0x00563780
unsigned char* C163780::fn_00163780()
{
    return &field450;
}

struct Pair163FD0 {
    unsigned int key;
    unsigned int value;
};

// FUNCTION: DAO 0x00563FD0
void fn_00163fd0(Pair163FD0* a, Pair163FD0* b, Pair163FD0* c)
{
    if (b->key < a->key) {
        Pair163FD0 t = *a;
        *a = *b;
        *b = t;
    }
    if (c->key < b->key) {
        Pair163FD0 t = *b;
        *b = *c;
        *c = t;
    }
    if (b->key < a->key) {
        Pair163FD0 t = *a;
        *a = *b;
        *b = t;
    }
}

struct Pair164030 {
    unsigned int key;
    unsigned int value;
};

// FUNCTION: DAO 0x00564030
void fn_00164030(Pair164030* arr, int hole, int top, unsigned int key, unsigned int value)
{
    int parent = (hole - 1) / 2;
    if (top >= hole) {
        arr[hole].key = key;
        arr[hole].value = value;
        return;
    }
    while (arr[parent].key < key) {
        arr[hole] = arr[parent];
        hole = parent;
        parent = (hole - 1) / 2;
        if (top >= hole) {
            break;
        }
    }
    arr[hole].key = key;
    arr[hole].value = value;
}

struct Elem1658F0 {
    unsigned int a;
    unsigned int b;
    unsigned int c;
};

// FUNCTION: DAO 0x005658F0
void fn_001658f0(Elem1658F0* first, Elem1658F0* middle, Elem1658F0* last)
{
    int count1 = (int)(middle - first);
    int count2 = (int)(last - first);
    int g = count2;
    int s = count1;
    while (s != 0) {
        int r = g % s;
        g = s;
        s = r;
    }
    if (g >= count2 || g <= 0) {
        return;
    }
    Elem1658F0* start = first + g;
    for (; g > 0; --g, --start) {
        Elem1658F0 temp = *start;
        Elem1658F0* hole = start;
        Elem1658F0* next = start + count1;
        if (next == last) {
            next = first;
        }
        while (next != start) {
            *hole = *next;
            hole = next;
            int remaining = (int)(last - next);
            if (count1 < remaining) {
                next = next + count1;
            } else {
                next = first + (count1 - remaining);
            }
        }
        *hole = temp;
    }
}

struct C165A70 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fC;
    void* p10;
    void fn_00165a70(void* src);
};

// FUNCTION: DAO 0x00565A70
void C165A70::fn_00165a70(void* src)
{
    p10 = src;
    unsigned int* s = (unsigned int*)src;
    f0 = s[0];
    f4 = s[1];
    f8 = s[2];
    fC = s[3];
}

struct Elem165B30 {
    unsigned int a;
    unsigned int key;
    unsigned int c;
};

// FUNCTION: DAO 0x00565B30
void fn_00165b30(Elem165B30* a, Elem165B30* b, Elem165B30* c)
{
    if (b->key < a->key) {
        Elem165B30 t = *a;
        *a = *b;
        *b = t;
    }
    if (c->key < b->key) {
        Elem165B30 t = *b;
        *b = *c;
        *c = t;
    }
    if (b->key < a->key) {
        Elem165B30 t = *a;
        *a = *b;
        *b = t;
    }
}

struct C168C20 {
    unsigned int pad0;
    unsigned int field4;
    unsigned int field8;
    bool fn_00168c20(unsigned int value);
};

// FUNCTION: DAO 0x00568C20
bool C168C20::fn_00168c20(unsigned int value)
{
    return field8 == value;
}

struct C168C30 {
    unsigned int field0;
    unsigned int field4;
    unsigned int field8;
    void fn_00168c30();
};

// FUNCTION: DAO 0x00568C30
void C168C30::fn_00168c30()
{
    field8 = 0;
    field4 = 0;
}

struct C168F20 {
    unsigned char pad0[0x180];
    unsigned int field180;
    void fn_00168f20(unsigned int value);
};

// FUNCTION: DAO 0x00568F20
void C168F20::fn_00168f20(unsigned int value)
{
    field180 = value;
}

struct C169130 {
    unsigned int field0;
    bool fn_00169130(const unsigned int* p);
};

// FUNCTION: DAO 0x00569130
bool C169130::fn_00169130(const unsigned int* p)
{
    return field0 == *p;
}

struct C171500 {
    unsigned char pad0[0x40];
    unsigned char field40;
    void* fn_00171500();
};

// FUNCTION: DAO 0x00571500
void* C171500::fn_00171500()
{
    return &field40;
}
