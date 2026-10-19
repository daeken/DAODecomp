struct FUN_00248b70_Out { unsigned char pad00[0x10]; unsigned int f10; unsigned int f14; };
struct FUN_00248b70_Obj { unsigned char pad00[0x20]; unsigned int f20; unsigned char pad24[4]; int f28; };
void __stdcall fn_00248b70(FUN_00248b70_Out *out, FUN_00248b70_Obj *obj);

struct FUN_00248c30_Obj { unsigned char pad00[4]; int f04; int f08; bool __thiscall fn_00248c30() const; };

struct FUN_0024a5c0_Inner { unsigned char pad00[8]; unsigned int f08; };
struct FUN_0024a5c0_Obj { FUN_0024a5c0_Inner *p00; unsigned int __thiscall fn_0024a5c0() const; };

struct FUN_0024a5e0_Node { FUN_0024a5e0_Node *p00; unsigned char pad04[4]; unsigned int f08; };
struct FUN_0024a5e0_Obj { FUN_0024a5e0_Node *p00; unsigned int __thiscall fn_0024a5e0() const; };

struct FUN_0024a600_Inner { unsigned char pad00[4]; unsigned int f04; };
struct FUN_0024a600_Obj { FUN_0024a600_Inner *p00; unsigned int __thiscall fn_0024a600() const; };

struct FUN_0024a610_Inner { unsigned int f00; };
struct FUN_0024a610_Obj { FUN_0024a610_Inner *p00; bool __thiscall fn_0024a610() const; };

struct FUN_0024b570_Obj { int f00; int f04; void __thiscall fn_0024b570(); };

struct FUN_0024dd40_Obj { unsigned char pad00[0xc]; unsigned int *p0c; void __thiscall fn_0024dd40(unsigned int index, unsigned int value); };

struct FUN_00252340_Pair { unsigned int a; unsigned int b; };
struct FUN_00252340_Obj { unsigned int f00; unsigned int f04; unsigned int f08; unsigned int f0c; unsigned int f10; unsigned int f14; void __thiscall fn_00252340(const FUN_00252340_Pair *p); };

struct FUN_0027a260_Obj { unsigned char pad00[0x5d8]; unsigned int f5d8; unsigned int f5dc; void __thiscall fn_0027a260(); };

struct FUN_0027a270_Node { unsigned char pad00[0xc]; FUN_0027a270_Node *f0c; FUN_0027a270_Node *f10; };
void __cdecl fn_0027a270(FUN_0027a270_Node **array, unsigned int count, int flag);

struct FUN_0027a350_Obj { unsigned char pad00[4]; unsigned int f04; unsigned int f08; void __thiscall fn_0027a350(unsigned int *out) const; };

struct FUN_0027a390_Obj { unsigned char pad00[4]; int f04; int f08; int __thiscall fn_0027a390() const; };

struct FUN_0027a400_Obj { unsigned char pad00[0x10]; unsigned int mask[4]; bool __thiscall fn_0027a400(const FUN_0027a400_Obj *other) const; };

struct FUN_0027a640_Pair { unsigned int lo; unsigned int hi; };
bool __stdcall fn_0027a640(const FUN_0027a640_Pair *a, const FUN_0027a640_Pair *b);

struct FUN_0027a670_Obj { unsigned char pad00[0x638]; unsigned char f638; bool __thiscall fn_0027a670() const; };

// FUNCTION: DAO 0x648B70
void __stdcall fn_00248b70(FUN_00248b70_Out *out, FUN_00248b70_Obj *obj)
{
    unsigned int v = obj->f20;
    if ((v & 3u) != 0u) goto fail;
    if ((v & 0x20000u) != 0u) goto fail;
    if (((v >> 2) & 1u) != 0u) goto fail;
    if (((v >> 5) & 1u) != 0u) goto set_one;
    if (((v >> 3) & 1u) == 0u) return;
set_one:
    out->f10 = 1u;
    return;
fail:
    if (obj->f28 != -1) {
        out->f10 = 2u;
        out->f14 = (unsigned int)obj->f28;
    }
}

// FUNCTION: DAO 0x648C30
bool __thiscall FUN_00248c30_Obj::fn_00248c30() const
{
    int a = f04;
    if (a == 0) return true;
    int n = (f08 - a) >> 6;
    return n == 0;
}

// FUNCTION: DAO 0x64A5C0
unsigned int __thiscall FUN_0024a5c0_Obj::fn_0024a5c0() const
{
    return p00->f08;
}

// FUNCTION: DAO 0x64A5E0
unsigned int __thiscall FUN_0024a5e0_Obj::fn_0024a5e0() const
{
    FUN_0024a5e0_Node *p = p00;
    FUN_0024a5e0_Node *q = p->p00;
    if (q == 0) return 0u;
    return q->f08;
}

// FUNCTION: DAO 0x64A600
unsigned int __thiscall FUN_0024a600_Obj::fn_0024a600() const
{
    return p00->f04;
}

// FUNCTION: DAO 0x64A610
bool __thiscall FUN_0024a610_Obj::fn_0024a610() const
{
    return p00->f00 == 0u;
}

// FUNCTION: DAO 0x64B570
void __thiscall FUN_0024b570_Obj::fn_0024b570()
{
    f00 = -1;
    f04 = 0;
}

// FUNCTION: DAO 0x64DD40
void __thiscall FUN_0024dd40_Obj::fn_0024dd40(unsigned int index, unsigned int value)
{
    p0c[index] = value;
}

// FUNCTION: DAO 0x652340
void __thiscall FUN_00252340_Obj::fn_00252340(const FUN_00252340_Pair *p)
{
    f00 = 0u;
    f04 = 0u;
    f08 = p->a;
    f0c = p->b;
    f10 = 0xFFFFFFFFu;
    f14 = 0xFFFFFFFFu;
}

// FUNCTION: DAO 0x67A260
void __thiscall FUN_0027a260_Obj::fn_0027a260()
{
    f5d8 = 0u;
    f5dc = 0u;
}

// FUNCTION: DAO 0x67A270
void __cdecl fn_0027a270(FUN_0027a270_Node **array, unsigned int count, int flag)
{
    unsigned int n = count - 1u;
    if (flag == 0) {
        for (unsigned int i = 0u; i < n; ++i) {
            array[i]->f10 = array[i + 1];
        }
    } else {
        for (unsigned int i = 0u; i < n; ++i) {
            array[i]->f0c = array[i + 1];
        }
    }
}

// FUNCTION: DAO 0x67A350
void __thiscall FUN_0027a350_Obj::fn_0027a350(unsigned int *out) const
{
    out[0] = f04;
    out[1] = f08;
}

// FUNCTION: DAO 0x67A390
int __thiscall FUN_0027a390_Obj::fn_0027a390() const
{
    int a = f04;
    if (a == 0) return 0;
    return (f08 - a) / 20;
}

// FUNCTION: DAO 0x67A400
bool __thiscall FUN_0027a400_Obj::fn_0027a400(const FUN_0027a400_Obj *other) const
{
    for (int i = 0; i < 2; ++i) {
        unsigned int a = mask[i * 2] & other->mask[i * 2];
        unsigned int b = mask[i * 2 + 1] & other->mask[i * 2 + 1];
        if ((a | b) != 0u) return true;
    }
    return false;
}

// FUNCTION: DAO 0x67A640
bool __stdcall fn_0027a640(const FUN_0027a640_Pair *a, const FUN_0027a640_Pair *b)
{
    if (a->hi < b->hi) return true;
    if (a->hi != b->hi) return false;
    return a->lo < b->lo;
}

// FUNCTION: DAO 0x67A670
bool __thiscall FUN_0027a670_Obj::fn_0027a670() const
{
    unsigned char v = f638;
    return v == 1u || v == 8u;
}
