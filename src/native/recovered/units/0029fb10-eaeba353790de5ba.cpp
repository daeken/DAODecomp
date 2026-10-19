struct C69fb10 {
    unsigned char pad_0[4];
    unsigned char* f_4;
    unsigned char* f_8;
    int fn_0029fb10();
};

struct C6a95d0 {
    unsigned char pad_0[0x10];
    void* f_10;
    int fn_002a95d0();
};

// FUNCTION: DAO 0x0069F530
unsigned int __stdcall fn_0029f530(unsigned int a, unsigned int b)
{
    unsigned int result = 0;
    if (a == 2)
        a = result + 1;
    if (b == 2) {
        b = 1;
    } else if (b == 0) {
        return a;
    }
    if (a == 0)
        return b;
    if (a == 1) {
        if (b == a || b == 3)
            result = 1;
        else
            return result;
    } else if (a == 3) {
        if (b == 1)
            result = 1;
        else if (b != a)
            return result;
        else
            return a;
    } else if (a == 4) {
        result = 1;
    }
    return result;
}

// FUNCTION: DAO 0x0069FB10
int C69fb10::fn_0029fb10()
{
    unsigned char* begin = f_4;
    if (begin == 0)
        return 0;
    unsigned char* end = f_8;
    int diff = (int)(end - begin);
    return diff / 188;
}

// FUNCTION: DAO 0x006A95D0
int C6a95d0::fn_002a95d0()
{
    unsigned char* p = (unsigned char*)f_10;
    unsigned char* q = *(unsigned char**)(p + 0x14);
    unsigned char* begin = *(unsigned char**)(q + 0x74);
    unsigned char* base = q + 0x70;
    if (begin == 0)
        return 0;
    unsigned char* end = *(unsigned char**)(base + 8);
    int diff = (int)(end - begin);
    return diff / 12;
}
