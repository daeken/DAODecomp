class DAOObj {
public:
    unsigned __int64 fn_00635a70();
    int fn_00635b90(int, int, int, int, unsigned int*, unsigned int*);
    int fn_00635be0(int, int, int, int);
    int fn_00635c90(unsigned int, unsigned int, unsigned int, unsigned int);
    void fn_00635e50(unsigned char);
    unsigned int* fn_006361d0(unsigned int*);
    int fn_00636200(void*, unsigned int*);
    int fn_00636240(void*, unsigned int*);
    void* fn_006369a0(void*, unsigned int);
    void fn_0063a2e0(int, unsigned int*, unsigned int*, unsigned int*);
};
int __stdcall fn_00635c40(unsigned int, unsigned int, unsigned int);
int __stdcall fn_006361b0(unsigned int*);
int __stdcall fn_00636980(void*);
int __stdcall fn_00637e40(void*);
int __stdcall fn_00637e60(void**);
int __stdcall fn_00637e80(void**);

// FUNCTION: DAO 0x00A35A70
unsigned __int64 DAOObj::fn_00635a70()
{
    return *(unsigned __int64*)((char*)this + 0x28);
}

// FUNCTION: DAO 0x00A35B90
int DAOObj::fn_00635b90(int a1, int a2, int a3, int a4, unsigned int* out1, unsigned int* out2)
{
    int limit = *(int*)((char*)this + 0x4c);
    if (a2 >= limit) return -2;
    if (a4 >= limit) return -2;
    unsigned int uedx = (unsigned int)a3 + (unsigned int)a1;
    unsigned int ueax = (unsigned int)a4 + (unsigned int)a2;
    if (ueax >= (unsigned int)limit) {
        uedx += 1u;
        ueax -= (unsigned int)limit;
    }
    *out1 = uedx;
    *out2 = ueax;
    return 0;
}

// FUNCTION: DAO 0x00A35BE0
int DAOObj::fn_00635be0(int x1, int y1, int x2, int y2)
{
    int limit = *(int*)((char*)this + 0x4c);
    if (y1 < 0) return -2;
    if (y1 >= limit) return -2;
    if (y2 < 0) return -2;
    if (y2 >= limit) return -2;
    if (x1 == x2) {
        if (y1 > y2) return 1;
        if (y1 == y2) return 0;
        return -1;
    }
    return (x1 > x2) ? 1 : -1;
}

// FUNCTION: DAO 0x00A35C40
int __stdcall fn_00635c40(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned int eax;
    if (a > 0x7d00u) {
        eax = 0x6dec0u;
    } else {
        eax = a * 0x150u;
    }
    unsigned int edx = b - 1u;
    if (edx <= 0xbu) {
        unsigned int ecx = b - 1u;
        edx = ecx * 8u;
        edx -= ecx;
        eax += edx * 4u;
    } else {
        eax += 0x8cu;
    }
    edx = c - 1u;
    if (edx <= 0x1bu) {
        eax += c - 1u;
    }
    return (int)eax;
}

// FUNCTION: DAO 0x00A35C90
int DAOObj::fn_00635c90(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4)
{
    unsigned int eax = *(unsigned int*)((char*)this + 0x48);
    if (a1 > 0x17u) {
        eax *= 0x150ea0u;
    } else {
        eax *= a1;
        eax *= 0xea60u;
    }
    if (a2 > 0x3bu) {
        eax += 0x360420u;
    } else {
        eax += a2 * 0xea60u;
    }
    if (a3 > 0x3bu) {
        eax += 0xdac0u;
        eax += a4;
    } else {
        eax += a3 * 0x3e8u;
        eax += a4;
    }
    return (int)eax;
}

// FUNCTION: DAO 0x00A35E50
void DAOObj::fn_00635e50(unsigned char v)
{
    unsigned int val = v;
    if (val == 0) val = 1;
    *(unsigned int*)((char*)this + 0x48) = val;
    unsigned int eax = *(unsigned int*)((char*)this + 0x48);
    unsigned int edx = eax;
    eax *= 0x15f900u;
    edx *= 0x5a0u;
    *(unsigned int*)((char*)this + 0x50) = edx;
    *(unsigned int*)((char*)this + 0x4c) = eax;
}

// FUNCTION: DAO 0x00A361B0
int __stdcall fn_006361b0(unsigned int* p)
{
    if (p == 0) return 0;
    *p = 0;
    return 1;
}

// FUNCTION: DAO 0x00A361D0
unsigned int* DAOObj::fn_006361d0(unsigned int* p)
{
    if (p == 0) return 0;
    unsigned int* edx = *(unsigned int**)((char*)this + 0x1c);
    if (edx == 0) return 0;
    unsigned int* ecx = *(unsigned int**)((char*)this + 0x20);
    if (ecx == 0) return 0;
    unsigned int idx = *p;
    if (idx >= *(unsigned int*)((char*)edx + 0xc)) return 0;
    return (unsigned int*)((char*)ecx + idx * 12u);
}

// FUNCTION: DAO 0x00A36200
int DAOObj::fn_00636200(void* p, unsigned int* out)
{
    if (p == 0) return 0;
    if (*(unsigned int*)((char*)this + 0x38) == 0) return 0;
    void* eaxp = *(void**)((char*)this + 0x1c);
    unsigned int eax = *(unsigned int*)((char*)eaxp + 0x24);
    unsigned int v = *(unsigned int*)((char*)p + 8);
    if (v >= eax) return 0;
    *out = eax - v;
    return (int)(v + *(unsigned int*)((char*)this + 0x38));
}

// FUNCTION: DAO 0x00A36240
int DAOObj::fn_00636240(void* p, unsigned int* out)
{
    if (p == 0) return 0;
    if (*(unsigned int*)((char*)this + 0x4c) == 0) return 0;
    void* eaxp = *(void**)((char*)this + 0x1c);
    unsigned int eax = *(unsigned int*)((char*)eaxp + 0x34);
    unsigned int v = *(unsigned int*)((char*)p + 8);
    if (v >= eax) return 0;
    *out = eax - v;
    return (int)(v + *(unsigned int*)((char*)this + 0x4c));
}

// FUNCTION: DAO 0x00A36980
int __stdcall fn_00636980(void* p)
{
    if (p == 0) return -1;
    return *(int*)((char*)p + 8);
}

// FUNCTION: DAO 0x00A369A0
void* DAOObj::fn_006369a0(void* arg1, unsigned int index)
{
    if (arg1 == 0) return 0;
    void* base = *(void**)((char*)this + 0x28);
    if (base == 0) return 0;
    unsigned int count = *(unsigned int*)((char*)arg1 + 8);
    if (index >= count) return 0;
    unsigned int value;
    if (count == 1) {
        value = *(unsigned int*)((char*)arg1 + 4);
        void* c = *(void**)((char*)this + 0x1c);
        if (value >= *(unsigned int*)((char*)c + 0x14)) return 0;
    } else {
        unsigned int off = *(unsigned int*)((char*)arg1 + 4);
        unsigned int addr = off + index * 4u;
        void* arr = *(void**)((char*)this + 0x40);
        if (arr == 0) return 0;
        void* c = *(void**)((char*)this + 0x1c);
        if (addr + 4u > *(unsigned int*)((char*)c + 0x2c)) return 0;
        value = *(unsigned int*)((char*)arr + addr);
        if (value >= *(unsigned int*)((char*)c + 0x14)) return 0;
    }
    return (char*)base + value * 12u;
}

// FUNCTION: DAO 0x00A37E40
int __stdcall fn_00637e40(void* p)
{
    if (p == 0) return 0;
    return *(int*)((char*)p + 8);
}

// FUNCTION: DAO 0x00A37E60
int __stdcall fn_00637e60(void** pp)
{
    void* p = *pp;
    if (p == 0) return 0;
    void* next = *(void**)((char*)p + 4);
    if (next == 0) {
        *pp = 0;
        return 0;
    }
    *pp = next;
    return *(int*)((char*)next + 8);
}

// FUNCTION: DAO 0x00A37E80
int __stdcall fn_00637e80(void** pp)
{
    void* p = *pp;
    if (p == 0) return 0;
    void* next = *(void**)p;
    if (next == 0) {
        *pp = 0;
        return 0;
    }
    *pp = next;
    return *(int*)((char*)next + 8);
}

// FUNCTION: DAO 0x00A3A2E0
void DAOObj::fn_0063a2e0(int value, unsigned int* out1, unsigned int* out2, unsigned int* out3)
{
    unsigned int shiftA = *(unsigned int*)((char*)this + 0x44);
    unsigned int shiftB = *(unsigned int*)((char*)this + 0x4c);
    unsigned int shiftC = *(unsigned int*)((char*)this + 0x48);
    int s1 = value >> ((shiftA + shiftB) & 31u);
    unsigned int maskC = (1u << (shiftC & 31u)) - 1u;
    *out1 = (unsigned int)s1 & maskC;
    int s2 = value >> (shiftA & 31u);
    unsigned int maskB = (1u << (shiftB & 31u)) - 1u;
    *out2 = (unsigned int)s2 & maskB;
    unsigned int maskA = (1u << (shiftA & 31u)) - 1u;
    *out3 = (unsigned int)value & maskA;
}
