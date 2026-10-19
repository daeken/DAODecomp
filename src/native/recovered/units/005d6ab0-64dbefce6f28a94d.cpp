extern "C" int __cdecl memcmp(const void*, const void*, unsigned int);
#pragma intrinsic(memcmp)

struct C005D0900 {
    unsigned char pad0[0x58];
    const unsigned char* f58;
    bool fn_005d0900(const void* arg);
};

struct C005D1C40 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int f1c;
    unsigned int f20;
    unsigned int f24;
    C005D1C40* fn_005d1c40();
};

struct C005D6AB0 {
    unsigned char b0;
    unsigned char b1;
    unsigned char b2;
    unsigned char b3;
    unsigned short w4;
    unsigned short w6;
    unsigned int d8;
    C005D6AB0* fn_005d6ab0(const C005D6AB0* src);
};

struct C005D8190Node {
    int next;
    int bucket;
    unsigned short key;
    unsigned short pad;
};

struct C005D8190 {
    unsigned int* f0;
    int fn_005d8190(const unsigned short* key, unsigned int start);
};

// FUNCTION: DAO 0x009D0900
bool __thiscall C005D0900::fn_005d0900(const void* arg)
{
    const unsigned char* p = f58;
    if (p == 0) {
        return false;
    }
    return memcmp(p, arg, 0x4c) == 0;
}

// FUNCTION: DAO 0x009D1C40
C005D1C40* __thiscall C005D1C40::fn_005d1c40()
{
    unsigned int zero = 0;
    f14 = zero;
    f18 = zero;
    f1c = zero;
    f20 = zero;
    f24 = zero;
    unsigned int mask = 0xffffffff;
    f0 = zero;
    f4 = mask;
    f8 = mask;
    fc = mask;
    f10 = zero;
    return this;
}

// FUNCTION: DAO 0x009D6AB0
C005D6AB0* __thiscall C005D6AB0::fn_005d6ab0(const C005D6AB0* src)
{
    b0 = src->b0;
    b1 = src->b1;
    b2 = src->b2;
    b3 = src->b3;
    w4 = src->w4;
    w6 = src->w6;
    d8 = src->d8;
    return this;
}

// FUNCTION: DAO 0x009D8190
int __thiscall C005D8190::fn_005d8190(const unsigned short* key, unsigned int start)
{
    unsigned int index = start;
    C005D8190Node* node = (C005D8190Node*)((unsigned char*)f0 + 8 + index * 12);
    if (node->next == -2) {
        return -1;
    }
    if (node->bucket != (int)index) {
        return -1;
    }
    for (;;) {
        if (node->bucket == (int)index) {
            if (node->key == *key) {
                return (int)index;
            }
        }
        int next = node->next;
        if (next == -1) {
            return -1;
        }
        index = (unsigned int)next;
        node = (C005D8190Node*)((unsigned char*)f0 + 8 + index * 12);
    }
}
