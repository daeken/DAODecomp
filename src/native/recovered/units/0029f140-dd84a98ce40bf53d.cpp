struct C69f140 {
    unsigned char pad_0[0xC95];
    unsigned char f_c95;
    unsigned char fn_0029f140();
};

struct C69f150 {
    unsigned char pad_0[0xCEC];
    int f_cec;
    unsigned char f_cf0;
    unsigned char fn_0029f150();
};

struct C69fb10 {
    unsigned char pad_0[4];
    unsigned char* f_4;
    unsigned char* f_8;
    int fn_0029fb10();
};

struct C6a0590 {
    unsigned char pad_0[0xB6C];
    unsigned char f_b6c;
    unsigned int fn_002a0590();
};

struct C6a05a0 {
    unsigned char pad_0[0xB6C];
    unsigned char f_b6c;
    unsigned int fn_002a05a0();
};

struct C6a2570 {
    unsigned char pad_0[0xA40];
    void* f_a40;
    void* fn_002a2570();
};

struct C6a2580 {
    unsigned char pad_0[0xC60];
    int* f_c60;
    unsigned char fn_002a2580();
};

struct C6a2d10 {
    unsigned char pad_0[0x2B8];
    void* f_2b8;
    unsigned char pad_1[0xA30];
    int f_cec;
    unsigned char f_cf0;
    void fn_002a2d10();
};

struct C6a3650 {
    unsigned char pad_0[0x7B0];
    void* f_7b0;
    unsigned char fn_002a3650();
};

struct C6a3c30 {
    unsigned char pad_0[0xC60];
    void* f_c60;
    void* fn_002a3c30();
};

struct C6a91c0 {
    unsigned char pad_0[0x74];
    unsigned char* f_74;
    unsigned char* f_78;
    int fn_002a91c0();
};

struct C6a95d0 {
    unsigned char pad_0[0x10];
    void* f_10;
    int fn_002a95d0();
};

struct C73c5f0 {
    unsigned char pad_0[0x2DC];
    void* f_2dc;
    void* fn_0033c5f0();
};

struct C665cf0 {
    unsigned char pad_0[0x3C];
    unsigned int f_3c;
    unsigned int f_40;
    unsigned char pad_1[0x20];
    unsigned int f_64;
    unsigned char f_68;
    unsigned char f_69;
    unsigned char f_6a;
    void fn_00665cf0();
};

// FUNCTION: DAO 0x0069F140
unsigned char C69f140::fn_0029f140()
{
    return f_c95;
}

// FUNCTION: DAO 0x0069F150
unsigned char C69f150::fn_0029f150()
{
    unsigned char g = (f_cec > 0) ? 1 : 0;
    f_cf0 = g;
    return (g == 0) ? 1 : 0;
}

// FUNCTION: DAO 0x0069F530
int __stdcall fn_0029f530(int a, int b)
{
    int ecx = a;
    int zero = 0;
    if (ecx == 2)
        ecx = zero + 1;
    int edx = b;
    if (edx == 2) {
        edx = 1;
        if (ecx == 0)
            return edx;
    } else {
        if (edx == 0)
            return ecx;
        if (ecx == 0)
            return edx;
    }
    if (ecx == 1) {
        if (edx == ecx || edx == 3)
            return 1;
        return zero;
    }
    if (ecx == 3) {
        if (edx == 1)
            return 1;
        if (edx != ecx)
            return zero;
        return ecx;
    }
    if (ecx == 4)
        return 1;
    return zero;
}

// FUNCTION: DAO 0x0069FB10
int C69fb10::fn_0029fb10()
{
    unsigned char* begin = f_4;
    if (begin == 0)
        return 0;
    unsigned char* end = f_8;
    int diff = (int)(end - begin);
    return diff / 76;
}

// FUNCTION: DAO 0x006A0590
unsigned int C6a0590::fn_002a0590()
{
    return (unsigned int)(f_b6c & 0x0F);
}

// FUNCTION: DAO 0x006A05A0
unsigned int C6a05a0::fn_002a05a0()
{
    return ((unsigned int)f_b6c) >> 4;
}

// FUNCTION: DAO 0x006A2570
void* C6a2570::fn_002a2570()
{
    return f_a40;
}

// FUNCTION: DAO 0x006A2580
unsigned char C6a2580::fn_002a2580()
{
    return (*(int*)f_c60 == 1) ? 1 : 0;
}

// FUNCTION: DAO 0x006A2D10
void C6a2d10::fn_002a2d10()
{
    if (f_cf0 != 0) {
        int* p = (int*)f_2b8;
        f_cec -= p[2];
    }
}

// FUNCTION: DAO 0x006A3650
unsigned char C6a3650::fn_002a3650()
{
    return *(unsigned char*)((unsigned char*)f_7b0 + 0x50);
}

// FUNCTION: DAO 0x006A3C30
void* C6a3c30::fn_002a3c30()
{
    if (f_c60 != 0)
        return *(void**)((unsigned char*)f_c60 + 0x5C);
    return 0;
}

// FUNCTION: DAO 0x006A4D50
unsigned short __cdecl fn_002a4d50(void* a, unsigned int b)
{
    unsigned int base = *(unsigned int*)((unsigned char*)a + 8);
    return *(unsigned short*)((unsigned char*)base + b);
}

// FUNCTION: DAO 0x006A91C0
int C6a91c0::fn_002a91c0()
{
    unsigned char* begin = f_74;
    if (begin == 0)
        return 0;
    unsigned char* end = f_78;
    int diff = (int)(end - begin);
    return diff / 12;
}

// FUNCTION: DAO 0x006A95D0
int C6a95d0::fn_002a95d0()
{
    unsigned char* p = (unsigned char*)f_10;
    unsigned char* a = (unsigned char*)(*(void**)(p + 0x14));
    unsigned char* begin = *(unsigned char**)(a + 0x74);
    if (begin == 0)
        return 0;
    unsigned char* end = *(unsigned char**)(a + 0x78);
    int diff = (int)(end - begin);
    return diff / 12;
}

// FUNCTION: DAO 0x0073C5F0
void* C73c5f0::fn_0033c5f0()
{
    return *(void**)f_2dc;
}

// FUNCTION: DAO 0x00A65CF0
void C665cf0::fn_00665cf0()
{
    if (f_40 != 0) {
        f_3c = 0;
        f_40 = 0;
        f_64 = 0;
        f_68 = 0;
        f_69 = 0;
        f_6a = 0;
    }
}
