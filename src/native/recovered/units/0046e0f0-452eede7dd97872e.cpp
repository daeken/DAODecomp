struct Record16 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; };
struct CObj468210 { unsigned int f000, f004, f008, f00c, f010, f014, f018, f01c, f020, f024, f028, f02c, f030, f034, f038, f03c, f040, f044, f048, f04c, f050, f054, f058, f05c, f060, f064, f068, f06c, f070, f074, f078, f07c, f080, f084, f088, f08c, f090, f094, f098, f09c, f0a0, f0a4, f0a8, f0ac, f0b0, f0b4, f0b8, f0bc, f0c0, f0c4, f0c8, f0cc, f0d0, f0d4, f0d8, f0dc, f0e0, f0e4, f0e8, f0ec, f0f0, f0f4, f0f8; void fn_00468210(); };
struct SrcE610 { unsigned char pad0[0xbc]; unsigned int fbc; unsigned char pad1[0x0d]; unsigned char fcd; };
struct CObjE610 { unsigned int f0; unsigned char pad0[0x71a0]; unsigned int f71a4; unsigned int f71a8; unsigned int f71ac; void fn_0046e610(unsigned int value, SrcE610* src); };
struct CObjE0F0 { unsigned int pad[48]; unsigned int f_c0; unsigned int fn_0046e0f0(); };
struct Node470460; struct Tree470460; struct Result470460 { Tree470460* tree; Node470460* node; };
struct Node470460 { Node470460* left; Node470460* parent; Node470460* right; unsigned int key; unsigned char pad10; unsigned char is_nil; };
struct Tree470460 { unsigned char pad0[4]; Node470460* header; void fn_00470460(Result470460* out, const unsigned int* key); };
struct CObj75210 { unsigned int pad[16]; unsigned int f40; unsigned int fn_00475210(); };
struct CObj7de40 { unsigned char pad[0x150]; unsigned char data; unsigned char* fn_0047de40(); };
struct CObj80620 { unsigned int f0; unsigned int fn_00480620(); };
// FUNCTION: DAO 0x868210
void CObj468210::fn_00468210()
{
    f034 = 5u; f07c = 5u; f0ac = 5u; f0cc = 5u; f0e0 = 5u;
    f018 = 3u; f02c = 3u; f068 = 3u; f074 = 3u; f098 = 3u; f0a4 = 3u; f0c4 = 3u; f0d8 = 3u; f0f0 = 3u;
    f03c = 7u; f084 = 7u; f0b4 = 7u; f0f8 = 7u;
    f030 = 4u; f078 = 4u; f0a8 = 4u; f0c8 = 4u; f0dc = 4u;
    f004 = 0u; f008 = 1u; f00c = 2u; f010 = 1u; f014 = 2u; f01c = 1u; f020 = 2u; f024 = 1u; f028 = 2u;
    f038 = 6u; f040 = 8u; f044 = 9u; f048 = 10u; f04c = 11u; f058 = 14u; f05c = 15u;
    f060 = 1u; f064 = 2u; f06c = 1u; f070 = 2u;
    f080 = 6u; f088 = 8u; f08c = 0u; f090 = 1u; f094 = 2u; f09c = 1u; f0a0 = 2u;
    f0b0 = 6u; f0b8 = 8u; f0bc = 1u; f0c0 = 2u;
    f0d0 = 1u; f0d4 = 2u;
    f0e4 = 0u; f0e8 = 1u; f0ec = 2u; f0f4 = 6u;
}
// FUNCTION: DAO 0x86bd40
void __cdecl fn_0046bd40(Record16* base, int index, int lower, unsigned int k0, unsigned int k1, unsigned int k2, int k3)
{
    int ecx = index;
    if (lower >= ecx) {
        Record16* out = base + ecx;
        out->f0 = k0; out->f4 = k1; out->f8 = k2; out->fc = (unsigned int)k3;
        return;
    }
    int parent = (ecx - 1) / 2;
    for (;;) {
        Record16* p = base + parent;
        bool move = false;
        if (p->f0 > k0) move = true;
        else if (p->f0 < k0) break;
        else if (p->f4 > k1) move = true;
        else if (p->f4 < k1) break;
        else if ((int)p->fc > k3) move = true;
        else if ((int)p->fc < k3) break;
        else if (p->f8 > k2) move = true;
        else break;
        if (!move) break;
        base[ecx] = *p;
        ecx = parent;
        parent = (ecx - 1) / 2;
    }
    Record16* out = base + ecx;
    out->f0 = k0; out->f4 = k1; out->f8 = k2; out->fc = (unsigned int)k3;
}
// FUNCTION: DAO 0x86bdf0
void __cdecl fn_0046bdf0(Record16* first, Record16* middle, Record16* last)
{
    unsigned int len1 = (unsigned int)(middle - first);
    unsigned int total = (unsigned int)(last - first);
    unsigned int g = total;
    unsigned int b = len1;
    if (b != 0u) {
        for (;;) {
            unsigned int rem = g % b;
            g = b;
            b = rem;
            if (rem == 0u) break;
        }
    }
    if ((int)g >= (int)total || (int)g <= 0) return;
    Record16* p = first + g;
    for (unsigned int n = g; n > 0u; --n) {
        Record16 saved = *p;
        Record16* q = p;
        Record16* next = q + len1;
        if (next == last) next = first;
        while (next != p) {
            *q = *next;
            q = next;
            unsigned int remaining = (unsigned int)(last - next);
            if (len1 < remaining) next = next + len1;
            else next = first + (len1 - remaining);
        }
        *q = saved;
        --p;
    }
}
// FUNCTION: DAO 0x86c240
void __cdecl fn_0046c240(unsigned int* first, unsigned int* last, unsigned int* result_end)
{
    while (last != first) {
        --last;
        --result_end;
        *result_end = *last;
    }
}
// FUNCTION: DAO 0x86e0f0
unsigned int CObjE0F0::fn_0046e0f0()
{
    return f_c0;
}
// FUNCTION: DAO 0x86e610
void CObjE610::fn_0046e610(unsigned int value, SrcE610* src)
{
    f0 = value;
    f71a4 = 8u;
    f71a8 = (src->fcd < 2u) ? 4u : 16u;
    unsigned int v = src->fbc;
    if (v >= 16u) v = 16u;
    f71ac = v;
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
    if (candidate != header && !(*key < candidate->key)) {
        out->tree = this;
        out->node = candidate;
    } else {
        out->tree = this;
        out->node = header;
    }
}
// FUNCTION: DAO 0x875210
unsigned int CObj75210::fn_00475210()
{
    return f40;
}
// FUNCTION: DAO 0x87de40
unsigned char* CObj7de40::fn_0047de40()
{
    return &data;
}
// FUNCTION: DAO 0x880620
unsigned int CObj80620::fn_00480620()
{
    return f0 & 0x0ff00000u;
}
