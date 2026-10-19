struct C005CE260 { unsigned char pad0[0x11]; unsigned char f11; unsigned short f12; unsigned char* f14; unsigned int fn_005ce260(); };
struct C005D0900 { unsigned char pad0[0x58]; unsigned char* f58; bool fn_005d0900(const unsigned char* other); };
struct C005D1C40 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; unsigned int f10; unsigned int f14; unsigned int f18; unsigned int f1c; unsigned int f20; unsigned int f24; void fn_005d1c40(); };
struct C005D6AB0 { unsigned char b0; unsigned char b1; unsigned char b2; unsigned char b3; unsigned short w4; unsigned short w6; unsigned int d8; void fn_005d6ab0(const C005D6AB0* src); };
struct C005D8190Node { int next; int bucket; unsigned short key; unsigned short pad; };
struct C005D8190 { unsigned int* f0; int fn_005d8190(const unsigned short* key, unsigned int start); };
struct C005D82D0Inner { unsigned char pad0[0xc]; unsigned int** table; };
struct C005D82D0 { unsigned char pad0[0x10]; C005D82D0Inner* f10; unsigned char pad14[0x74]; unsigned int f88; void fn_005d82d0(int a, int b, int c); };
struct C005DAC90Elem { unsigned int f0; unsigned int f4; };
struct C005DAC90Target { unsigned char pad0[0x18]; int f18; };
struct C005DAC90 { C005DAC90Elem* f0; unsigned int f4; int fn_005dac90(); };
struct C005DBE60 { unsigned char pad0[4]; unsigned int f4; unsigned int f8; int fn_005dbe60(); };

// FUNCTION: DAO 0x009CE260
unsigned int __thiscall C005CE260::fn_005ce260()
{
    unsigned int acc = f11;
    unsigned int count = f12;
    if (count > 0) {
        unsigned char* p = f14;
        do {
            unsigned int d = *(unsigned int*)(p + 4);
            unsigned int b = p[0];
            unsigned int e = (d >> 16) ^ b ^ d;
            acc ^= e;
            p += 8;
            --count;
        } while (count != 0);
    }
    return acc;
}

// FUNCTION: DAO 0x009D0900
bool __thiscall C005D0900::fn_005d0900(const unsigned char* other)
{
    const unsigned char* a = f58;
    if (a == 0)
        return false;
    const unsigned char* b = other;
    unsigned int n = 0x4c;
    while (n >= 4) {
        unsigned int x = *(const unsigned int*)a;
        unsigned int y = *(const unsigned int*)b;
        if (x != y)
            break;
        n -= 4;
        a += 4;
        b += 4;
    }
    if (n == 0)
        return true;
    int diff = (int)*a - (int)*b;
    if (diff == 0) {
        ++a; ++b; --n;
        if (n != 0) {
            diff = (int)*a - (int)*b;
            if (diff == 0) {
                ++a; ++b; --n;
                if (n != 0) {
                    diff = (int)*a - (int)*b;
                    if (diff == 0) {
                        ++a; ++b; --n;
                        if (n != 0) {
                            diff = (int)*a - (int)*b;
                        }
                    }
                }
            }
        }
    }
    if (diff == 0)
        return true;
    return false;
}

// FUNCTION: DAO 0x009D1C40
void __thiscall C005D1C40::fn_005d1c40()
{
    C005D1C40* p = this;
    unsigned int z = 0;
    p->f14 = z;
    p->f18 = z;
    p->f1c = z;
    p->f20 = z;
    p->f24 = z;
    unsigned int m = 0xffffffff;
    p->f0 = z;
    p->f4 = m;
    p->f8 = m;
    p->fc = m;
    p->f10 = z;
}

// FUNCTION: DAO 0x009D6AB0
void __thiscall C005D6AB0::fn_005d6ab0(const C005D6AB0* src)
{
    C005D6AB0* dst = this;
    const C005D6AB0* s = src;
    dst->b0 = s->b0;
    dst->b1 = s->b1;
    dst->b2 = s->b2;
    dst->b3 = s->b3;
    dst->w4 = s->w4;
    dst->w6 = s->w6;
    dst->d8 = s->d8;
}

// FUNCTION: DAO 0x009D8190
int __thiscall C005D8190::fn_005d8190(const unsigned short* key, unsigned int start)
{
    unsigned int index = start;
    C005D8190Node* base = (C005D8190Node*)((unsigned char*)f0 + 8);
    C005D8190Node* node = base + index;
    if (node->next == -2)
        return -1;
    if (node->bucket != (int)start)
        return -1;
    for (;;) {
        if (node->bucket == (int)start) {
            if (node->key == *key)
                return (int)index;
        }
        int next = node->next;
        if (next == -1)
            return -1;
        index = (unsigned int)next;
        node = base + index;
    }
}

// FUNCTION: DAO 0x009D82D0
void __thiscall C005D82D0::fn_005d82d0(int a, int b, int c)
{
    {
        unsigned int addr = f88 + 4;
        ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)a;
        ++addr;
        ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)(a >> 8);
    }
    {
        unsigned int addr = f88 + 6;
        ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)b;
        ++addr;
        ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)(b >> 8);
    }
    {
        unsigned int addr = f88 + 8;
        ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)c;
        ++addr;
        ((unsigned char*)f10->table[addr >> 12])[addr & 0xfff] = (unsigned char)(c >> 8);
    }
}

// FUNCTION: DAO 0x009DAC90
int __thiscall C005DAC90::fn_005dac90()
{
    if (f4 != 0) {
        C005DAC90Elem* e = f0 + (f4 - 1);
        C005DAC90Target* t = (C005DAC90Target*)e->f4;
        return t->f18;
    }
    return -1;
}

// FUNCTION: DAO 0x009DBE60
int __thiscall C005DBE60::fn_005dbe60()
{
    return (f4 >= f8) ? 1 : 0;
}
