struct Record16 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
};

struct CObj468210 {
    unsigned int f000, f004, f008, f00c, f010, f014, f018, f01c;
    unsigned int f020, f024, f028, f02c, f030, f034, f038, f03c;
    unsigned int f040, f044, f048, f04c, f050, f054, f058, f05c;
    unsigned int f060, f064, f068, f06c, f070, f074, f078, f07c;
    unsigned int f080, f084, f088, f08c, f090, f094, f098, f09c;
    unsigned int f0a0, f0a4, f0a8, f0ac, f0b0, f0b4, f0b8, f0bc;
    unsigned int f0c0, f0c4, f0c8, f0cc, f0d0, f0d4, f0d8, f0dc;
    unsigned int f0e0, f0e4, f0e8, f0ec, f0f0, f0f4, f0f8;
    void fn_00468210();
};

struct SrcE610 {
    unsigned char pad0[0xbc];
    unsigned int fbc;
    unsigned char pad1[0x0d];
    unsigned char fcd;
};

struct CObjE610 {
    unsigned int f0;
    unsigned char pad0[0x71a0];
    unsigned int f71a4;
    unsigned int f71a8;
    unsigned int f71ac;
    void fn_0046e610(unsigned int value, SrcE610* src);
};

struct Node470460;
struct Tree470460;

struct Result470460 {
    Tree470460* tree;
    Node470460* node;
};

struct Node470460 {
    Node470460* left;
    Node470460* parent;
    Node470460* right;
    unsigned int key;
    unsigned char pad10;
    unsigned char is_nil;
};

struct Tree470460 {
    unsigned char pad0[4];
    Node470460* header;
    void fn_00470460(Result470460* out, const unsigned int* key);
};

// FUNCTION: DAO 0x868210
void CObj468210::fn_00468210()
{
    f004 = 0u;
    f008 = 1u;
    f00c = 2u;
    f010 = 1u;
    f014 = 2u;
    f018 = 3u;
    f01c = 1u;
    f020 = 2u;
    f024 = 1u;
    f028 = 2u;
    f02c = 3u;
    f030 = 4u;
    f034 = 5u;
    f038 = 6u;
    f03c = 7u;
    f040 = 8u;
    f044 = 9u;
    f048 = 10u;
    f04c = 11u;
    f058 = 14u;
    f05c = 15u;
    f060 = 1u;
    f064 = 2u;
    f068 = 3u;
    f06c = 1u;
    f070 = 2u;
    f074 = 3u;
    f078 = 4u;
    f07c = 5u;
    f080 = 6u;
    f084 = 7u;
    f088 = 8u;
    f08c = 0u;
    f090 = 1u;
    f094 = 2u;
    f098 = 3u;
    f09c = 1u;
    f0a0 = 2u;
    f0a4 = 3u;
    f0a8 = 4u;
    f0ac = 5u;
    f0b0 = 6u;
    f0b4 = 7u;
    f0b8 = 8u;
    f0bc = 1u;
    f0c0 = 2u;
    f0c4 = 3u;
    f0c8 = 4u;
    f0cc = 5u;
    f0d0 = 1u;
    f0d4 = 2u;
    f0d8 = 3u;
    f0dc = 4u;
    f0e0 = 5u;
    f0e4 = 0u;
    f0e8 = 1u;
    f0ec = 2u;
    f0f0 = 3u;
    f0f4 = 6u;
    f0f8 = 7u;
}

// FUNCTION: DAO 0x86bd40
void __cdecl fn_0046bd40(Record16* base, int index, int lower,
                         unsigned int k0, unsigned int k1, unsigned int k2, unsigned int k3)
{
    int i = index;
    int parent = (i - 1) / 2;

    if (lower < i) {
        for (;;) {
            Record16* p = base + parent;
            bool move = false;

            if (p->f0 > k0) {
                move = true;
            } else if (p->f0 < k0) {
                break;
            } else if (p->f4 > k1) {
                move = true;
            } else if (p->f4 < k1) {
                break;
            } else if ((int)p->fc > (int)k3) {
                move = true;
            } else if ((int)p->fc < (int)k3) {
                break;
            } else if (p->f8 > k2) {
                move = true;
            } else {
                break;
            }

            if (!move) {
                break;
            }

            base[i] = *p;
            i = parent;
            parent = (i - 1) / 2;

            if (!(lower < i)) {
                break;
            }
        }
    }

    Record16* out = base + i;
    out->f0 = k0;
    out->f4 = k1;
    out->f8 = k2;
    out->fc = k3;
}

// FUNCTION: DAO 0x86bdf0
void __cdecl fn_0046bdf0(Record16* first, Record16* middle, Record16* last)
{
    int len1 = (int)(middle - first);
    int total = (int)(last - first);
    int a = total;
    int b = len1;

    if (b != 0) {
        for (;;) {
            int r = a % b;
            a = b;
            b = r;
            if (r == 0) {
                break;
            }
        }
    }

    if (a >= total || a <= 0) {
        return;
    }

    Record16* p = first + a;
    for (int n = a; n > 0; --n) {
        Record16 saved = *p;
        Record16* q = p;
        Record16* next = q + len1;
        if (next == last) {
            next = first;
        }

        while (next != p) {
            *q = *next;
            q = next;
            int remaining = (int)(last - next);
            if (len1 < remaining) {
                next += len1;
            } else {
                next = first + (len1 - remaining);
            }
        }

        *q = saved;
        --p;
    }
}

// FUNCTION: DAO 0x86c240
void __cdecl fn_0046c240(unsigned int* first, unsigned int* last, unsigned int* result_end)
{
    unsigned int* base = result_end - (last - first);
    unsigned int* p = last;

    while (p != first) {
        --p;
        base[p - first] = *p;
    }
}

// FUNCTION: DAO 0x86e610
void CObjE610::fn_0046e610(unsigned int value, SrcE610* src)
{
    SrcE610* s = src;
    f0 = value;
    f71a4 = 8u;

    int v = (s->fcd < 2) ? 4 : 16;
    if (v >= 16) {
        v = 16;
    }
    f71a8 = (unsigned int)v;

    unsigned int w = s->fbc;
    if (w >= 16u) {
        w = 16u;
    }
    f71ac = w;
}

// FUNCTION: DAO 0x870460
void Tree470460::fn_00470460(Result470460* out, const unsigned int* key)
{
    Node470460* header = this->header;
    Node470460* node = header->parent;
    Node470460* candidate = header;

    while (!node->is_nil) {
        if (node->key >= *key) {
            candidate = node;
            node = node->left;
        } else {
            node = node->right;
        }
    }

    Result470460 resultA;
    resultA.tree = this;
    resultA.node = candidate;

    Result470460 resultB;
    resultB.tree = this;
    resultB.node = header;

    Result470460 result = (candidate != header && *key >= candidate->key) ? resultA : resultB;
    *out = result;
}
