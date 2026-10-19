class DAOObj {
public:
    int fn_00635be0(int, int, int, int);
    int fn_00635c90(unsigned int, unsigned int, unsigned int, unsigned int);
    void* fn_006369a0(void*, unsigned int);
};

int __stdcall fn_00635c40(unsigned int, unsigned int, unsigned int);
int __stdcall fn_00637e80(void**);

// FUNCTION: DAO 0x00A35BE0
int DAOObj::fn_00635be0(int x1, int y1, int x2, int y2)
{
    if (y1 < 0 || y1 >= *(int*)((char*)this + 0x4c) || y2 < 0 || y2 >= *(int*)((char*)this + 0x4c))
        return -2;
    if (x1 == x2) {
        if (y1 > y2)
            return 1;
        int r = (y1 >= y2);
        return r - 1;
    }
    return (x1 > x2) ? 1 : -1;
}

// FUNCTION: DAO 0x00A35C40
int __stdcall fn_00635c40(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned int eax;
    if (a <= 0x7d00u)
        eax = a * 0x150u;
    else
        eax = 0x6dec0u;
    if (b - 1u <= 0xbu) {
        --b;
        eax += (b * 8u - b) * 4u;
    } else {
        eax += 0x8cu;
    }
    if (c - 1u <= 0x1bu)
        eax += c - 1u;
    return (int)eax;
}

// FUNCTION: DAO 0x00A35C90
int DAOObj::fn_00635c90(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4)
{
    unsigned int eax = (a1 > 0x17u)
        ? (*(unsigned int*)((char*)this + 0x48) * 0x150ea0u)
        : (*(unsigned int*)((char*)this + 0x48) * a1 * 0xea60u);
    if (a2 > 0x3bu)
        eax += 0x360420u;
    else
        eax += a2 * 0xea60u;
    if (a3 <= 0x3bu) {
        eax += a3 * 0x3e8u;
        eax += a4;
    } else {
        eax += 0xdac0u;
        eax += a4;
    }
    return (int)eax;
}

// FUNCTION: DAO 0x00A369A0
void* DAOObj::fn_006369a0(void* arg1, unsigned int index)
{
    if (arg1 == 0)
        return 0;
    void* base = *(void**)((char*)this + 0x28);
    if (base == 0)
        return 0;
    unsigned int count = *(unsigned int*)((char*)arg1 + 8);
    if (index >= count)
        return 0;
    unsigned int value = *(unsigned int*)((char*)arg1 + 4);
    if (count != 1) {
        unsigned int addr = value + index * 4u;
        void* arr = *(void**)((char*)this + 0x40);
        if (arr == 0)
            return 0;
        void* c = *(void**)((char*)this + 0x1c);
        if (addr + 4u > *(unsigned int*)((char*)c + 0x2c))
            return 0;
        if (c == 0)
            return 0;
        unsigned int v = *(unsigned int*)((char*)arr + addr);
        if (v >= *(unsigned int*)((char*)c + 0x14))
            return 0;
        return (char*)base + v * 12u;
    } else {
        void* c = *(void**)((char*)this + 0x1c);
        if (value >= *(unsigned int*)((char*)c + 0x14))
            return 0;
        return (char*)base + value * 12u;
    }
}

// FUNCTION: DAO 0x00A37E80
int __stdcall fn_00637e80(void** pp)
{
    void* p = *pp;
    if (p == 0)
        return 0;
    if (*(unsigned int*)p == 0) {
        *pp = 0;
        return 0;
    }
    void* next = *(void**)p;
    *pp = next;
    return *(int*)((char*)next + 8);
}
