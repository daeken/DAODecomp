struct C005CE260 { unsigned char pad0[0x11]; unsigned char f11; unsigned short f12; unsigned char* f14; unsigned int fn_005ce260(); };
struct C005D0900 { unsigned char pad0[0x58]; unsigned char* f58; bool fn_005d0900(const void* arg); };
struct C005D1C40 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; unsigned int f10; unsigned int f14; unsigned int f18; unsigned int f1c; unsigned int f20; unsigned int f24; void fn_005d1c40(); };
struct C005D6AB0 { unsigned char b0; unsigned char b1; unsigned char b2; unsigned char b3; unsigned short w4; unsigned short w6; unsigned int d8; void fn_005d6ab0(const C005D6AB0* src); };
struct C005D78C0 { unsigned char pad0[0x60]; unsigned int f60; unsigned char pad64[8]; unsigned int** f6c; void fn_005d78c0(unsigned int index, unsigned short value); };
struct C005D7A10Inner { unsigned char pad0[0xc]; unsigned int** table; };
struct C005D7A10 { unsigned int* f0; void fn_005d7a10(unsigned int addr, unsigned int value); };
struct C005D8190Node { int next; int bucket; unsigned short key; unsigned short pad; };
struct C005D8190 { unsigned int* f0; int fn_005d8190(const unsigned short* key, unsigned int start); };
struct C005D82D0Inner { unsigned char pad0[0xc]; unsigned int** table; };
struct C005D82D0 { unsigned char pad0[0x10]; C005D82D0Inner* f10; unsigned char pad14[0x74]; unsigned int f88; void fn_005d82d0(unsigned int a, unsigned int b, unsigned int c); };
struct C005DAC90Elem { unsigned int f0; unsigned int f4; };
struct C005DAC90Target { unsigned char pad0[0x18]; int f18; };
struct C005DAC90 { C005DAC90Elem* f0; unsigned int f4; int fn_005dac90(); };
struct C005DB770 { unsigned char pad0[0x14]; unsigned int f14; unsigned int f18; void fn_005db770(); };
struct C005DB930Inner { unsigned char pad0[0x6c]; unsigned int f6c; };
struct C005DB930 { unsigned char pad0[0x10]; C005DB930Inner* f10; unsigned char pad14[8]; unsigned int f1c; int fn_005db930(); };
struct C005DB950Inner { unsigned char pad0[0x2c]; unsigned char flags; };
struct C005DB950 { unsigned char pad0[0x10]; C005DB950Inner* f10; void fn_005db950(unsigned char flag); };
struct C005DBE60 { unsigned int f4; unsigned int f8; int fn_005dbe60(); };
struct C005F0EF0 { unsigned int pad0; unsigned int f4; unsigned char pad8[0x10]; unsigned int f18; unsigned char pad1c[0x30]; unsigned int f4c; unsigned char pad50[8]; unsigned int f58; void fn_005f0ef0(); };

// FUNCTION: DAO 0x009CE260
unsigned int __thiscall C005CE260::fn_005ce260()
{
    unsigned int acc = f11;
    unsigned int count = f12;
    if (count != 0) {
        unsigned char* p = f14;
        do {
            unsigned int d = *(unsigned int*)(p + 4);
            unsigned int b = p[0];
            unsigned int e = d >> 16;
            e ^= b;
            e ^= d;
            acc ^= e;
            p += 8;
            --count;
        } while (count != 0);
    }
    return acc;
}

// FUNCTION: DAO 0x009D0900
bool __thiscall C005D0900::fn_005d0900(const void* arg)
{
    unsigned char* a = f58;
    if (a == 0) return false;
    const unsigned char* b = (const unsigned char*)arg;
    unsigned int n = 0x4c;
    while (n != 0) {
        if (*a != *b) return false;
        ++a;
        ++b;
        --n;
    }
    return true;
}

// FUNCTION: DAO 0x009D1C40
void __thiscall C005D1C40::fn_005d1c40()
{
    f14 = 0;
    f18 = 0;
    f1c = 0;
    f20 = 0;
    f24 = 0;
    f0 = 0;
    f4 = 0xffffffff;
    f8 = 0xffffffff;
    fc = 0xffffffff;
    f10 = 0;
}

// FUNCTION: DAO 0x009D6AB0
void __thiscall C005D6AB0::fn_005d6ab0(const C005D6AB0* src)
{
    b0 = src->b0;
    b1 = src->b1;
    b2 = src->b2;
    b3 = src->b3;
    w4 = src->w4;
    w6 = src->w6;
    d8 = src->d8;
}

// FUNCTION: DAO 0x009D78C0
void __thiscall C005D78C0::fn_005d78c0(unsigned int index, unsigned short value)
{
    if (index >= f60) return;
    unsigned int* page = f6c[index >> 6];
    unsigned int off = (index & 0x3f) * 8 + 2;
    *(unsigned short*)((unsigned char*)page + off) = value;
}

// FUNCTION: DAO 0x009D7A10
void __thiscall C005D7A10::fn_005d7a10(unsigned int addr, unsigned int value)
{
    unsigned int a;
    C005D7A10Inner* p;
    a = addr;
    p = (C005D7A10Inner*)f0;
    ((unsigned char*)p->table[a >> 12])[a & 0xfff] = (unsigned char)value;
    a = addr + 1;
    p = (C005D7A10Inner*)f0;
    ((unsigned char*)p->table[a >> 12])[a & 0xfff] = (unsigned char)(value >> 8);
    a = addr + 2;
    p = (C005D7A10Inner*)f0;
    ((unsigned char*)p->table[a >> 12])[a & 0xfff] = (unsigned char)(value >> 16);
    a = addr + 3;
    p = (C005D7A10Inner*)f0;
    ((unsigned char*)p->table[a >> 12])[a & 0xfff] = (unsigned char)(value >> 24);
}

// FUNCTION: DAO 0x009D8190
int __thiscall C005D8190::fn_005d8190(const unsigned short* key, unsigned int start)
{
    C005D8190Node* base = (C005D8190Node*)((unsigned char*)f0 + 8);
    C005D8190Node* node = base + start;
    if (node->next == -2) return -1;
    if (node->bucket != (int)start) return -1;
    for (;;) {
        if (node->bucket == (int)start) {
            if (node->key == *key) return (int)start;
        }
        int next = node->next;
        if (next == -1) return -1;
        node = base + next;
    }
}

// FUNCTION: DAO 0x009D82D0
void __thiscall C005D82D0::fn_005d82d0(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned int addr;
    addr = f88 + 4;
    ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)a;
    addr = f88 + 5;
    ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)(a >> 8);
    addr = f88 + 6;
    ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)b;
    addr = f88 + 7;
    ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)(b >> 8);
    addr = f88 + 8;
    ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)c;
    addr = f88 + 9;
    ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)(c >> 8);
}

// FUNCTION: DAO 0x009DAC90
int __thiscall C005DAC90::fn_005dac90()
{
    if (f4 == 0) return -1;
    C005DAC90Elem* e = f0 + (f4 - 1);
    C005DAC90Target* t = (C005DAC90Target*)e->f4;
    return t->f18;
}

// FUNCTION: DAO 0x009DB770
void __thiscall C005DB770::fn_005db770()
{
    f14 = 0;
    f18 = 0;
}

// FUNCTION: DAO 0x009DB930
int __thiscall C005DB930::fn_005db930()
{
    if (f10->f6c != 0 && f1c != 0) return 0;
    return 1;
}

// FUNCTION: DAO 0x009DB950
void __thiscall C005DB950::fn_005db950(unsigned char flag)
{
    if (flag != 0) f10->flags |= 8;
    else f10->flags &= 0xf7;
}

// FUNCTION: DAO 0x009DBE60
int __thiscall C005DBE60::fn_005dbe60()
{
    return (f4 >= f8) ? 1 : 0;
}

// FUNCTION: DAO 0x009F0EF0
void __thiscall C005F0EF0::fn_005f0ef0()
{
    f4 = 0;
    f18 = 0;
    f4c = 0;
    f58 = 0;
}
