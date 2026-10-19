struct FUN_00248b70_Out { unsigned char pad00[0x10]; unsigned int f10; unsigned int f14; };
struct FUN_00248b70_Obj { unsigned char pad00[0x20]; unsigned int f20; unsigned char pad24[4]; int f28; };
void __stdcall fn_00248b70(FUN_00248b70_Out *out, FUN_00248b70_Obj *obj);

struct FUN_00248c30_Obj { unsigned char pad00[4]; int f04; int f08; bool __thiscall fn_00248c30() const; };

struct FUN_0024a5e0_Node { FUN_0024a5e0_Node *p00; unsigned char pad04[4]; unsigned int f08; };
struct FUN_0024a5e0_Obj { FUN_0024a5e0_Node *p00; unsigned int __thiscall fn_0024a5e0() const; };

struct FUN_0024a610_Inner { unsigned int f00; };
struct FUN_0024a610_Obj { FUN_0024a610_Inner *p00; unsigned int __thiscall fn_0024a610() const; };

struct FUN_0024b570_Obj { int f00; int f04; void __thiscall fn_0024b570(); };

struct FUN_0024dd40_Obj { unsigned char pad00[0xc]; unsigned int *p0c; void __thiscall fn_0024dd40(unsigned int index, unsigned int value, unsigned int unused); };

struct FUN_00252340_Pair { unsigned int a; unsigned int b; };
struct FUN_00252340_Obj { unsigned int f00; unsigned int f04; unsigned int f08; unsigned int f0c; unsigned int f10; unsigned int f14; void __thiscall fn_00252340(const FUN_00252340_Pair *p); };

struct FUN_0027a390_Obj { unsigned char pad00[4]; int f04; int f08; int __thiscall fn_0027a390() const; };

struct FUN_0027a400_Obj { unsigned char pad00[0x10]; unsigned int mask[4]; bool __thiscall fn_0027a400(const FUN_0027a400_Obj *other) const; };

struct FUN_0027a640_Pair { unsigned int lo; unsigned int hi; };
bool __stdcall fn_0027a640(const FUN_0027a640_Pair *a, const FUN_0027a640_Pair *b);

// FUNCTION: DAO 0x648b70
void __stdcall fn_00248b70(FUN_00248b70_Out *out, FUN_00248b70_Obj *obj)
{
    unsigned int v = obj->f20;
    if ((v & 3u) != 0u) goto fail;
    if ((v & 0x20000u) != 0u) goto fail;
    {
        unsigned int t = v;
        t >>= 2;
        if ((t & 1u) != 0u) goto fail;
    }
    {
        unsigned int t = v;
        t >>= 5;
        if ((t & 1u) != 0u) goto set_one;
    }
    {
        unsigned int t = v;
        t >>= 3;
        if ((t & 1u) == 0u) return;
    }
set_one:
    out->f10 = 1u;
    return;
fail:
    if (obj->f28 != -1) {
        out->f10 = 2u;
        out->f14 = (unsigned int)obj->f28;
    }
}

// FUNCTION: DAO 0x648c30
bool __thiscall FUN_00248c30_Obj::fn_00248c30() const
{
    int a = f04;
    int n = 0;
    if (a != 0) {
        n = (f08 - a) >> 6;
    }
    return n == 0;
}

// FUNCTION: DAO 0x64a5e0
unsigned int __thiscall FUN_0024a5e0_Obj::fn_0024a5e0() const
{
    FUN_0024a5e0_Node *p = this->p00;
    FUN_0024a5e0_Node *q = p->p00;
    if (q == 0) return 0u;
    return q->f08;
}

// FUNCTION: DAO 0x64a610
unsigned int __thiscall FUN_0024a610_Obj::fn_0024a610() const
{
    return (unsigned int)(p00->f00 == 0u);
}

// FUNCTION: DAO 0x64b570
void __thiscall FUN_0024b570_Obj::fn_0024b570()
{
    unsigned int *p = reinterpret_cast<unsigned int*>(this);
    p[0] = 0xFFFFFFFFu;
    p[1] = 0u;
}

// FUNCTION: DAO 0x64dd40
void __thiscall FUN_0024dd40_Obj::fn_0024dd40(unsigned int index, unsigned int value, unsigned int)
{
    p0c[index] = value;
}

// FUNCTION: DAO 0x652340
void __thiscall FUN_00252340_Obj::fn_00252340(const FUN_00252340_Pair *p)
{
    FUN_00252340_Obj *self = this;
    const FUN_00252340_Pair *pp = p;
    self->f00 = 0u;
    self->f04 = 0u;
    self->f08 = pp->a;
    self->f0c = pp->b;
    self->f10 = 0xFFFFFFFFu;
    self->f14 = 0xFFFFFFFFu;
}

// FUNCTION: DAO 0x67a390
int __thiscall FUN_0027a390_Obj::fn_0027a390() const
{
    int a = f04;
    if (a == 0) return 0;
    return (f08 - a) / 80;
}

// FUNCTION: DAO 0x67a400
bool __thiscall FUN_0027a400_Obj::fn_0027a400(const FUN_0027a400_Obj *other) const
{
    for (int i = 0; i < 2; ++i) {
        unsigned int a = other->mask[i*2] & mask[i*2];
        unsigned int b = other->mask[i*2+1] & mask[i*2+1];
        if ((a | b) != 0u) return true;
    }
    return false;
}

// FUNCTION: DAO 0x67a640
bool __stdcall fn_0027a640(const FUN_0027a640_Pair *a, const FUN_0027a640_Pair *b)
{
    if (a->hi < b->hi) return true;
    if (a->hi > b->hi) return false;
    if (a->lo >= b->lo) return false;
    return true;
}
