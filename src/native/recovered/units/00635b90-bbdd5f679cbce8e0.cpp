class DAOObj {
public:
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
int __stdcall fn_00637e80(void**);

// FUNCTION: DAO 0x00A35B90
int DAOObj::fn_00635b90(int a1, int a2, int a3, int a4, unsigned int* out1, unsigned int* out2)
{
    int limit = *(int*)((char*)this + 0x4c);
    if (a2 < limit) {
        if (a4 < limit) {
            unsigned int edx = (unsigned int)a3 + (unsigned int)a1;
            unsigned int eax = (unsigned int)a4 + (unsigned int)a2;
            if (eax >= (unsigned int)limit) {
                edx += 1u;
                eax -= (unsigned int)limit;
            }
            *out1 = edx;
            *out2 = eax;
            return 0;
        }
    }
    return -2;
}

// FUNCTION: DAO 0x00A35BE0
int DAOObj::fn_00635be0(int x1, int y1, int x2, int y2)
{
    if (y1 < 0) return -2;
    int limit = *(int*)((char*)this + 0x4c);
    if (y1 >= limit) return -2;
    if (y2 < 0) return -2;
    if (y2 >= limit) return -2;
    if (x1 == x2) {
        if (y1 > y2) return 1;
        int r = (y1 >= y2);
        return r - 1;
    }
    return (x1 > x2) ? 1 : -1;
}

// FUNCTION: DAO 0x00A35C40
int __stdcall fn_00635c40(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned int eax;
    if (a <= 0x7d00u) {
        eax = a * 0x150u;
    } else {
        eax = 0x6dec0u;
    }
    if (b - 1u <= 0xbu) {
        unsigned int x = b - 1u;
        eax += (x * 8u - x) * 4u;
    } else {
        eax += 0x8cu;
    }
    if (c - 1u <= 0x1bu) {
        eax += c - 1u;
    }
    return (int)eax;
}

// FUNCTION: DAO 0x00A35C90
int DAOObj::fn_00635c90(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4)
{
    unsigned int edx = a1;
    unsigned int eax = *(unsigned int*)((char*)this + 0x48);
    if (edx <= 0x17u) {
        eax *= edx;
        eax *= 0xea60u;
    } else {
        eax *= 0x150ea0u;
    }
    if (a2 <= 0x3bu) {
        eax += a2 * 0xea60u;
    } else {
        eax += 0x360420u;
    }
    if (a3 <= 0x3bu) {
        eax += a3 * 0x3e8u;
        eax += a4;
        return (int)eax;
    }
    eax += 0xdac0u;
    eax += a4;
    return (int)eax;
}

// FUNCTION: DAO 0x00A35E50
void DAOObj::fn_00635e50(unsigned char v)
{
    unsigned char c = v;
    *(unsigned int*)((char*)this + 0x48) = c;
    if (c == 0) *(unsigned int*)((char*)this + 0x48) = 1;
    unsigned int eax = *(unsigned int*)((char*)this + 0x48);
    unsigned int edx = eax;
    eax *= 0x15f900u;
    edx *= 0x5a0u;
    *(unsigned int*)((char*)this + 0x50) = edx;
    *(unsigned int*)((char*)this + 0x4c) = eax;
}

// FUNCTION: DAO 0x00A361D0
unsigned int* DAOObj::fn_006361d0(unsigned int* p)
{
    if (p) {
        unsigned int* edx = *(unsigned int**)((char*)this + 0x1c);
        if (edx) {
            unsigned int* ecx = *(unsigned int**)((char*)this + 0x20);
            if (ecx) {
                unsigned int idx = *p;
                if (idx < *(unsigned int*)((char*)edx + 0xc)) {
                    return (unsigned int*)((char*)ecx + idx * 12u);
                }
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x00A36200
int DAOObj::fn_00636200(void* p, unsigned int* out)
{
    if (p) {
        if (*(unsigned int*)((char*)this + 0x38)) {
            void* obj = *(void**)((char*)this + 0x1c);
            unsigned int limit = *(unsigned int*)((char*)obj + 0x24);
            if (*(unsigned int*)((char*)p + 8) < limit) {
                *out = limit - *(unsigned int*)((char*)p + 8);
                return (int)(*(unsigned int*)((char*)p + 8) + *(unsigned int*)((char*)this + 0x38));
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x00A36240
int DAOObj::fn_00636240(void* p, unsigned int* out)
{
    if (p) {
        if (*(unsigned int*)((char*)this + 0x4c)) {
            void* obj = *(void**)((char*)this + 0x1c);
            unsigned int limit = *(unsigned int*)((char*)obj + 0x34);
            if (*(unsigned int*)((char*)p + 8) < limit) {
                *out = limit - *(unsigned int*)((char*)p + 8);
                return (int)(*(unsigned int*)((char*)p + 8) + *(unsigned int*)((char*)this + 0x4c));
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x00A369A0
void* DAOObj::fn_006369a0(void* arg1, unsigned int index)
{
    if (arg1) {
        void* base = *(void**)((char*)this + 0x28);
        if (base) {
            unsigned int count = *(unsigned int*)((char*)arg1 + 8);
            if (index < count) {
                if (count == 1) {
                    unsigned int value = *(unsigned int*)((char*)arg1 + 4);
                    void* c = *(void**)((char*)this + 0x1c);
                    if (value < *(unsigned int*)((char*)c + 0x14)) {
                        return (char*)base + value * 12u;
                    }
                } else {
                    unsigned int off = *(unsigned int*)((char*)arg1 + 4);
                    unsigned int addr = off + index * 4u;
                    void* arr = *(void**)((char*)this + 0x40);
                    if (arr) {
                        void* c = *(void**)((char*)this + 0x1c);
                        if (addr + 4u <= *(unsigned int*)((char*)c + 0x2c) && c != 0) {
                            unsigned int value = *(unsigned int*)((char*)arr + addr);
                            if (value < *(unsigned int*)((char*)c + 0x14)) {
                                return (char*)base + value * 12u;
                            }
                        }
                    }
                }
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x00A37E80
int __stdcall fn_00637e80(void** pp)
{
    void* p = *pp;
    if (p == 0) return 0;
    if (*(void**)p == 0) {
        *pp = 0;
        return 0;
    }
    void* next = *(void**)p;
    *pp = next;
    return *(int*)((char*)next + 8);
}

// FUNCTION: DAO 0x00A3A2E0
void DAOObj::fn_0063a2e0(int value, unsigned int* out1, unsigned int* out2, unsigned int* out3)
{
    *out1 = (unsigned int)(value >> (*(unsigned int*)((char*)this + 0x44) + *(unsigned int*)((char*)this + 0x4c))) & ((1u << *(unsigned int*)((char*)this + 0x48)) - 1u);
    *out2 = (unsigned int)(value >> *(unsigned int*)((char*)this + 0x44)) & ((1u << *(unsigned int*)((char*)this + 0x4c)) - 1u);
    *out3 = (unsigned int)value & ((1u << *(unsigned int*)((char*)this + 0x44)) - 1u);
}
