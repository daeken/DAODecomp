struct Node {
    Node* left;
    Node* parent;
    Node* right;
    unsigned char pad[0x11];
    unsigned char isnil;
};

struct Vec12 {
    unsigned int pad0;
    unsigned char* begin;
    unsigned char* end;
    bool __thiscall fn_004777d0() const;
};

// FUNCTION: DAO 0x875340
Node* __cdecl fn_00475340(Node* x)
{
    while (x->right->isnil == 0)
        x = x->right;
    return x;
}

// FUNCTION: DAO 0x8777D0
bool __thiscall Vec12::fn_004777d0() const
{
    return this->begin == 0 || (int)(this->end - this->begin) / 12 == 0;
}

// FUNCTION: DAO 0x87DE50
int __fastcall fn_0047de50(unsigned int index, unsigned int /*unused*/, unsigned char** p)
{
    unsigned int value = (unsigned int)((unsigned char*)(*p))[index + 0x3d];
    value >>= 7;
    return (int)(value % 2u);
}

// FUNCTION: DAO 0x87E320
void __cdecl fn_0047e320(unsigned short* dst, unsigned int count, const unsigned short* src)
{
    if (count > 0) {
        unsigned int s = (unsigned int)src;
        unsigned int d = (unsigned int)dst;
        do {
            if (d != 0)
                *(unsigned short*)d = *(const unsigned short*)s;
            --count;
            d += 2;
        } while (count > 0);
    }
}

// FUNCTION: DAO 0x87E390
unsigned short* __cdecl fn_0047e390(unsigned short* begin, unsigned short* end, unsigned short* dst)
{
    unsigned short* result = dst - (end - begin);
    if (end != begin) {
        unsigned int off = (unsigned int)dst - (unsigned int)end;
        do {
            unsigned short v = *(end - 1);
            --end;
            *(unsigned short*)((unsigned int)end + off) = v;
        } while (end != begin);
    }
    return result;
}
