struct C005b39e0 {
    unsigned int v[8];
    void fn_005b39e0(unsigned int seed);
};

struct C005b3ab0 {
    unsigned int v[8];
    unsigned int f20;
    unsigned int f24;
    void fn_005b3ab0();
};

struct C005b3b70 {
    unsigned char data[0x64C];
    void fn_005b3b70(unsigned short a, unsigned char b, unsigned int c, unsigned int d, unsigned char e);
};

struct C005b3c50 {
    unsigned char data[0x679];
    bool fn_005b3c50(unsigned int index);
};

struct C005b3c90 {
    unsigned char data[0x67C];
    unsigned char fn_005b3c90(unsigned int code);
};

struct C005b3cd0 {
    unsigned char data[0x67C];
    void fn_005b3cd0(unsigned int code, unsigned char value);
};

struct C005b5d70 {
    void* ptr;
    void fn_005b5d70(void* p);
    void fn_005b5d80();
};

struct C005b6050 {
    unsigned char pad[0x34];
    unsigned int* arr;
    int count;
    void fn_005b6050();
};

struct C005d0730 {
    int a;
    int b;
    int c;
    int d;
    void fn_005d0730(int a_, int b_, int c_, int d_);
};

struct C005d7590 {
    unsigned char pad[0x20];
    unsigned int f20;
    unsigned char pad2[0x10];
    unsigned int f34;
    int fn_005d7590();
};

struct C005db760 {
    unsigned char pad[0x1c];
    unsigned int f1c;
    unsigned char pad2[0x6D];
    unsigned char f8d;
    int fn_005db760();
};

// FUNCTION: DAO 0x009AF3F0
int __cdecl fn_005af3f0(void* object, int* key)
{
    unsigned char* base = (unsigned char*)object;
    int count = *(int*)(base + 4);
    int lo = 0;
    if (count <= 0)
        return lo;
    void** array = *(void***)base;
    int target = *key;
    int hi = count;
    while (hi > 0) {
        int half = hi >> 1;
        int mid = (int)((unsigned int)half + (unsigned int)lo);
        unsigned char* elem = (unsigned char*)array[mid];
        int value = *(int*)(elem + 0);
        int lower = *(int*)(elem + 8);
        if (value < 0) {
            lower = (int)((unsigned int)lower & 0xFFFFFFU);
            if (lower == 0xFFFFFF)
                lower = -1;
        }
        if (target < lower) {
            unsigned int diff = (unsigned int)lower - (unsigned int)target;
            if ((diff & 0x80000000U) == 0U) {
                hi = half;
            } else {
                lo = (int)((unsigned int)mid + 1U);
                hi = (int)((unsigned int)hi + 0xFFFFFFFFU - (unsigned int)half);
            }
        } else {
            unsigned int len;
            if (value < 0)
                len = (unsigned int)*(unsigned char*)(elem + 0x0B);
            else
                len = *(unsigned int*)(elem + 0x20);
            unsigned int upperU = (unsigned int)lower + len;
            int upper = (int)upperU;
            if (target < upper) {
                hi = half;
            } else {
                unsigned int diff = (unsigned int)lower - (unsigned int)target;
                if ((diff & 0x80000000U) == 0U) {
                    hi = half;
                } else {
                    lo = (int)((unsigned int)mid + 1U);
                    hi = (int)((unsigned int)hi + 0xFFFFFFFFU - (unsigned int)half);
                }
            }
        }
    }
    return lo;
}

// FUNCTION: DAO 0x009B39E0
void C005b39e0::fn_005b39e0(unsigned int seed)
{
    unsigned int x = seed;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    v[0] = x;
    for (int i = 1; i < 8; ++i) {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        v[i] = x;
    }
}

// FUNCTION: DAO 0x009B3AB0
void C005b3ab0::fn_005b3ab0()
{
    unsigned int idx = (f24 + 1U) & 7U;
    f24 = idx;
    unsigned int eax = v[idx];
    unsigned __int64 product = (unsigned __int64)eax * 0x2AB5245EU;
    unsigned int low = (unsigned int)product;
    unsigned int high = (unsigned int)(product >> 32);
    unsigned __int64 sum = (unsigned __int64)low + (unsigned __int64)f20;
    low = (unsigned int)sum;
    high = high + (unsigned int)(sum >> 32);
    unsigned int edi = high + low;
    if (edi < high) {
        ++edi;
        ++high;
    }
    f20 = high;
    v[idx] = 0xFFFFFFFEU - edi;
}

// FUNCTION: DAO 0x009B3B70
void C005b3b70::fn_005b3b70(unsigned short a, unsigned char b, unsigned int c, unsigned int d, unsigned char e)
{
    unsigned int idx = *(unsigned int*)(data + 0x640);
    if (*(unsigned int*)(data + 0x648) >= 100U)
        return;
    unsigned char* p = data + (idx << 4);
    *(unsigned short*)(p + 4) = a;
    *(unsigned char*)(p + 0xC) = b;
    *(unsigned int*)(p + 0) = c;
    *(unsigned int*)(p + 8) = d;
    *(unsigned char*)(p + 0xD) = e;
    idx = idx + 1U;
    *(unsigned int*)(data + 0x640) = idx;
    if (idx >= 100U)
        *(unsigned int*)(data + 0x640) = 0;
    *(unsigned int*)(data + 0x648) = *(unsigned int*)(data + 0x648) + 1U;
}

// FUNCTION: DAO 0x009B3C50
bool C005b3c50::fn_005b3c50(unsigned int index)
{
    if (index > 0xE4U)
        return false;
    unsigned int q = index >> 3;
    unsigned int r = index - (q << 3);
    unsigned char mask = (unsigned char)(1U << r);
    return (data[0x65C + q] & mask) != 0;
}

// FUNCTION: DAO 0x009B3C90
unsigned char C005b3c90::fn_005b3c90(unsigned int code)
{
    if (code == 0x14U)
        return data[0x67A];
    if (code == 0x90U)
        return data[0x679];
    if (code == 0x91U)
        return data[0x67B];
    return 0;
}

// FUNCTION: DAO 0x009B3CD0
void C005b3cd0::fn_005b3cd0(unsigned int code, unsigned char value)
{
    if (code == 0x14U) {
        data[0x67A] = value;
        return;
    }
    if (code == 0x90U) {
        data[0x679] = value;
        return;
    }
    if (code == 0x91U)
        data[0x67B] = value;
}

// FUNCTION: DAO 0x009B5D70
void C005b5d70::fn_005b5d70(void* p)
{
    ptr = p;
    *(int*)((unsigned char*)p + 0x44) += 1;
}

// FUNCTION: DAO 0x009B5D80
void C005b5d70::fn_005b5d80()
{
    unsigned char* p = (unsigned char*)ptr;
    *(int*)(p + 0x44) -= 1;
}

// FUNCTION: DAO 0x009B6050
void C005b6050::fn_005b6050()
{
    int i = count - 1;
    if (i <= 0)
        return;
    int j = 0;
    do {
        unsigned int tmp = arr[j];
        arr[j] = arr[i];
        arr[i] = tmp;
        ++j;
        --i;
    } while (j < i);
}

// FUNCTION: DAO 0x009C0C50
int __fastcall fn_005c0c50(int year)
{
    int x = year - 1970;
    return (x + 369) / 400 - (x + 69) / 100 + (x + 1) / 4 + x * 365;
}

// FUNCTION: DAO 0x009D0730
void C005d0730::fn_005d0730(int a_, int b_, int c_, int d_)
{
    a = a_;
    b = b_;
    c = c_;
    d = d_;
}

// FUNCTION: DAO 0x009D7590
int C005d7590::fn_005d7590()
{
    f20 = 0;
    f34 = 0;
    return 0;
}

// FUNCTION: DAO 0x009DB760
int C005db760::fn_005db760()
{
    f1c = 0;
    f8d = 0;
    return 0;
}
