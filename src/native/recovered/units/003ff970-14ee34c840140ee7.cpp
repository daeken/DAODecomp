struct E_003f6990 { unsigned int skip; unsigned int a; unsigned int b; unsigned int c; };

struct Obj_003ff550 { unsigned char pad0[4]; unsigned char* begin; unsigned char* end; void fn_003ff550(); };

struct Obj_003ff970 { unsigned char pad0[0x2c4]; unsigned char* begin; unsigned char* end; int fn_003ff970(); };

struct Obj_003ff990 { unsigned char pad0[4]; unsigned char* begin; unsigned char* end; void fn_003ff990(unsigned int); };

struct Node_0040e1d0 { unsigned char pad0[8]; Node_0040e1d0* child; unsigned char pad1[0x31 - 0x0c]; unsigned char flag31; };

struct Q_0041c790 { unsigned char pad0[8]; unsigned char flag8; };
struct Holder_0041c790 { unsigned char pad0[4]; Q_0041c790* q; };

struct Q_0041c7b0 { unsigned int f0; };
struct Holder_0041c7b0 { unsigned char pad0[4]; Q_0041c7b0* q; };

// FUNCTION: DAO 0x007f6990
E_003f6990* fn_003f6990(E_003f6990* first, E_003f6990* last, E_003f6990* dest)
{
    E_003f6990* result = dest + (last - first);
    while (first != last) {
        dest->a = first->a;
        dest->b = first->b;
        dest->c = first->c;
        ++first;
        ++dest;
    }
    return result;
}

// FUNCTION: DAO 0x007ff550
void Obj_003ff550::fn_003ff550()
{
    if (begin) {
        unsigned char* e = end;
        if ((e - begin) / 4) {
            end = e - 4;
        }
    }
}

// FUNCTION: DAO 0x007ff970
int Obj_003ff970::fn_003ff970()
{
    if (!begin)
        return 0;
    return ((int)(end - begin)) >> 5;
}

// FUNCTION: DAO 0x007ff990
void Obj_003ff990::fn_003ff990(unsigned int)
{
    if (begin) {
        unsigned char* e = end;
        int n = (int)(e - begin) / 4;
        if (n) {
            if (n) {
                end = e - 4;
            }
        }
    }
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

// FUNCTION: DAO 0x0081c790
unsigned char fn_0041c790(Holder_0041c790* p)
{
    if (p && p->q)
        return p->q->flag8;
    return 1;
}

// FUNCTION: DAO 0x0081c7b0
unsigned int fn_0041c7b0(Holder_0041c7b0* p)
{
    if (p && p->q)
        return p->q->f0;
    return 0;
}
