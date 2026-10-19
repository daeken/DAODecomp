struct E_003f6990 {
    unsigned int skip;
    unsigned int a;
    unsigned int b;
    unsigned int c;
};

struct Obj_003ff550 {
    unsigned char pad0[4];
    unsigned char* begin;
    unsigned char* end;
    void fn_003ff550();
};

struct Obj_003ff990 {
    unsigned char pad0[4];
    unsigned char* begin;
    unsigned char* end;
    void fn_003ff990(unsigned int);
};

struct Node_0040e1d0 {
    unsigned char pad0[8];
    Node_0040e1d0* child;
    unsigned char pad1[0x31 - 0x0c];
    unsigned char flag31;
};

// FUNCTION: DAO 0x007f6990
E_003f6990* fn_003f6990(E_003f6990* first, E_003f6990* last, E_003f6990* dest)
{
    E_003f6990* result = dest + (last - first);
    E_003f6990* s = first;
    E_003f6990* d = dest;
    while (s != last) {
        d->a = s->a;
        d->b = s->b;
        d->c = s->c;
        ++s;
        ++d;
    }
    return result;
}

// FUNCTION: DAO 0x007ff550
void Obj_003ff550::fn_003ff550()
{
    if (begin) {
        unsigned char* e = end;
        int n = (int)(e - begin) >> 2;
        if (n == 0)
            return;
        end = e - 4;
    }
}

// FUNCTION: DAO 0x007ff990
void Obj_003ff990::fn_003ff990(unsigned int)
{
    if (begin) {
        unsigned char* e = end;
        int n = (int)(e - begin) >> 2;
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
