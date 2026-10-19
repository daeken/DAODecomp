struct Node162700 {
    Node162700* left;
    Node162700* parent;
    Node162700* right;
    unsigned int key;
    unsigned char pad10[5];
    unsigned char flag15;
};

struct Out162700 {
    Node162700* p0;
    Node162700* p1;
    Node162700* p2;
    Node162700* p3;
};

struct C162700 {
    unsigned int pad0;
    Node162700* field4;
    void fn_00162700(Out162700* out, const unsigned int* key);
};

// FUNCTION: DAO 0x00562700
void C162700::fn_00162700(Out162700* out, const unsigned int* key)
{
    Node162700* lower = field4;
    Node162700* node = lower->parent;
    if (node->flag15 == 0) {
        do {
            if (*key < node->key) {
                lower = node;
                node = node->left;
            } else {
                node = node->right;
            }
        } while (node->flag15 == 0);
    }

    Node162700* upper = *(Node162700* volatile*)&field4;
    node = upper->parent;
    if (node->flag15 == 0) {
        unsigned int k = *key;
        do {
            if (node->key >= k) {
                upper = node;
                node = node->left;
            } else {
                node = node->right;
            }
        } while (node->flag15 == 0);
    }

    out->p1 = upper;
    out->p0 = (Node162700*)this;
    out->p2 = (Node162700*)this;
    out->p3 = lower;
}

struct Pair163FD0 {
    unsigned int key;
    unsigned int value;
};

// FUNCTION: DAO 0x00563FD0
void fn_00163fd0(Pair163FD0* a, Pair163FD0* b, Pair163FD0* c)
{
    if (b->key < a->key) {
        Pair163FD0 t = *b;
        *b = *a;
        *a = t;
    }
    if (c->key < b->key) {
        Pair163FD0 t = *c;
        *c = *b;
        *b = t;
    }
    if (b->key < a->key) {
        Pair163FD0 t = *b;
        *b = *a;
        *a = t;
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
    if (top < hole) {
        do {
            if (arr[parent].key >= key)
                break;
            arr[hole] = arr[parent];
            hole = parent;
            parent = (hole - 1) / 2;
        } while (top < hole);
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
    if (g >= count2 || g <= 0)
        return;

    int stride = count1 * 12;
    Elem1658F0* start = first + g;
    for (; g > 0; --g, --start) {
        Elem1658F0 temp = *start;
        Elem1658F0* hole = start;
        Elem1658F0* next = (Elem1658F0*)((char*)start + stride);
        if (next == last)
            next = first;
        while (next != start) {
            *hole = *next;
            hole = next;
            int remaining = (int)(last - next);
            if (count1 < remaining) {
                next = (Elem1658F0*)((char*)next + stride);
            } else {
                next = first + (count1 - remaining);
            }
        }
        *hole = temp;
    }
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
        Elem165B30 t = *b;
        *b = *a;
        *a = t;
    }
    if (c->key < b->key) {
        Elem165B30 t = *c;
        *c = *b;
        *b = t;
    }
    if (b->key < a->key) {
        Elem165B30 t = *b;
        *b = *a;
        *a = t;
    }
}
