struct C6a95d0 {
    unsigned char pad_0[0x10];
    void* f_10;
    int fn_002a95d0();
};

struct C6a95d0_tail {
    unsigned int pad_0;
    unsigned char* begin;
    unsigned char* end;
};

// FUNCTION: DAO 0x0069F530
unsigned int __stdcall fn_0029f530(unsigned int a, unsigned int b)
{
    unsigned int result = 0;
    unsigned int x = a;
    unsigned int y = b;

    if (x == 2)
        x = result + 1;

    if (y == 2) {
        y = 1;
    } else if (y == 0) {
        return x;
    }

    if (x == 0)
        return y;

    if (x == 1) {
        if (y == x || y == 3)
            return 1;
        return result;
    }

    if (x == 3) {
        if (y == 1)
            return 1;
        if (y != x)
            return result;
        return x;
    }

    if (x == 4)
        return 1;

    return result;
}

// FUNCTION: DAO 0x006A95D0
int C6a95d0::fn_002a95d0()
{
    unsigned char* p = (unsigned char*)f_10;
    unsigned char* q = *(unsigned char**)(p + 0x14);
    C6a95d0_tail* t = (C6a95d0_tail*)(q + 0x70);
    unsigned char* begin = t->begin;
    if (begin == 0)
        return 0;
    int diff = (int)(t->end - begin);
    return diff / 12;
}
