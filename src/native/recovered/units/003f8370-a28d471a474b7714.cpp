struct E_003f6990 { unsigned int skip; unsigned int a; unsigned int b; unsigned int c; };

struct Obj_003f8370 { unsigned char pad0[4]; unsigned char* begin; unsigned char* end; int fn_003f8370(); };

struct Node_003f8390 { Node_003f8390* f0; Node_003f8390* f4; Node_003f8390* f8; unsigned char pad[0x15 - 0x0c]; unsigned char f15; };
struct Tree_003f8390 { unsigned char pad0[4]; Node_003f8390* root; void fn_003f8390(Node_003f8390*); };

struct Obj_003f89c0 { unsigned char pad0[0x64]; unsigned char* begin; unsigned char* end; int fn_003f89c0(); };

struct Obj_003ff550 { unsigned char pad0[4]; unsigned char* begin; unsigned char* end; void fn_003ff550(); };

struct Obj_003ff970 { unsigned char pad0[0x2c4]; unsigned char* begin; unsigned char* end; int fn_003ff970(); };

struct Obj_003ff990 { unsigned char pad0[4]; unsigned char* begin; unsigned char* end; void fn_003ff990(unsigned int); };

struct Node_0040e1d0 { unsigned char pad0[8]; Node_0040e1d0* child; unsigned char pad1[0x31 - 0x0c]; unsigned char flag31; };

struct Obj_00411bd0 { unsigned char pad0[0x2e]; unsigned short f2e; unsigned short fn_00411bd0(); };

struct Obj_00418630 { unsigned char* fn_00418630(); };

struct Obj_004197d0 { unsigned char pad0[0x14]; unsigned int f14; void fn_004197d0(); };

struct Obj_0041b2c0 { unsigned char pad0[0xfc]; unsigned int ffc; unsigned int fn_0041b2c0(); };

struct Obj_0041c470 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; Obj_0041c470* fn_0041c470(); };

struct Obj_0041c740 { unsigned int f0; unsigned int f4; void fn_0041c740(); };

struct Q_0041c790 { unsigned char pad0[8]; unsigned char flag8; };
struct Holder_0041c790 { unsigned char pad0[4]; Q_0041c790* q; };

struct Q_0041c7b0 { unsigned int f0; };
struct Holder_0041c7b0 { unsigned char pad0[4]; Q_0041c7b0* q; };

// FUNCTION: DAO 0x007f6990
E_003f6990* fn_003f6990(E_003f6990* first, E_003f6990* last, E_003f6990* dest)
{
    while (first != last) {
        dest->a = first->a;
        dest->b = first->b;
        dest->c = first->c;
        ++first;
        ++dest;
    }
    return dest;
}

// FUNCTION: DAO 0x007f8370
int Obj_003f8370::fn_003f8370()
{
    unsigned char* b = begin;
    if (!b)
        return 0;
    unsigned char* e = end;
    return (int)((e - b) / 136);
}

// FUNCTION: DAO 0x007f8390
void Tree_003f8390::fn_003f8390(Node_003f8390* x)
{
    Node_003f8390* y = x->f0;
    Node_003f8390* z = y->f8;
    x->f0 = z;
    z = y->f8;
    if (z->f15 == 0)
        z->f4 = x;
    Node_003f8390* w = x->f4;
    y->f4 = w;
    Node_003f8390* r = root;
    if (x == r->f4) {
        r->f4 = y;
        y->f8 = x;
        x->f4 = y;
        return;
    }
    Node_003f8390* p = x->f4;
    if (x == p->f8) {
        p->f8 = y;
        y->f8 = x;
        x->f4 = y;
        return;
    }
    p->f0 = y;
    y->f8 = x;
    x->f4 = y;
}

// FUNCTION: DAO 0x007f89c0
int Obj_003f89c0::fn_003f89c0()
{
    unsigned char* b = begin;
    if (!b)
        return 0;
    unsigned char* e = end;
    return (int)((e - b) / 136);
}

// FUNCTION: DAO 0x007ff550
void Obj_003ff550::fn_003ff550()
{
    unsigned char* b = begin;
    if (!b)
        return;
    unsigned char* e = end;
    if (((unsigned int)(e - b) >> 2) == 0)
        return;
    end = e - 4;
}

// FUNCTION: DAO 0x007ff970
int Obj_003ff970::fn_003ff970()
{
    if (!begin)
        return 0;
    return (int)((end - begin) / 32);
}

// FUNCTION: DAO 0x007ff990
void Obj_003ff990::fn_003ff990(unsigned int)
{
    unsigned char* b = begin;
    if (!b)
        return;
    unsigned char* e = end;
    if (((unsigned int)(e - b) >> 2) == 0)
        return;
    end = e - 4;
}

// FUNCTION: DAO 0x0080e1d0
Node_0040e1d0* fn_0040e1d0(Node_0040e1d0* arg)
{
    Node_0040e1d0* eax = arg;
    Node_0040e1d0* ecx = arg->child;
    if (ecx->flag31 != 0)
        return eax;
    do {
        eax = ecx;
        ecx = eax->child;
    } while (ecx->flag31 == 0);
    return eax;
}

// FUNCTION: DAO 0x00811bd0
unsigned short Obj_00411bd0::fn_00411bd0()
{
    return f2e;
}

// FUNCTION: DAO 0x00818630
unsigned char* Obj_00418630::fn_00418630()
{
    return reinterpret_cast<unsigned char*>(this) + 0x10;
}

// FUNCTION: DAO 0x008197d0
void Obj_004197d0::fn_004197d0()
{
    f14 = 0;
}

// FUNCTION: DAO 0x0081b2c0
unsigned int Obj_0041b2c0::fn_0041b2c0()
{
    return ffc;
}

// FUNCTION: DAO 0x0081c470
Obj_0041c470* Obj_0041c470::fn_0041c470()
{
    f0 = 0xffffffffu;
    f4 = 0;
    fc = 0;
    f8 = 0xffffffffu;
    return this;
}

// FUNCTION: DAO 0x0081c740
void Obj_0041c740::fn_0041c740()
{
    f4 = 0;
    f0 = 0xffffffffu;
}

// FUNCTION: DAO 0x0081c790
unsigned char fn_0041c790(Holder_0041c790* p)
{
    if (!p)
        return 1;
    Q_0041c790* q = p->q;
    if (!q)
        return 1;
    return q->flag8;
}

// FUNCTION: DAO 0x0081c7b0
unsigned int fn_0041c7b0(Holder_0041c7b0* p)
{
    if (!p)
        return 0;
    Q_0041c7b0* q = p->q;
    if (!q)
        return 0;
    return q->f0;
}
