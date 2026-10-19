struct Key4 { unsigned int a; unsigned int b; unsigned int c; int d; };

struct Key3 { int a; int b; int c; bool __thiscall fn_00475300(const Key3* other) const; };

struct Node { Node* left; Node* parent; Node* right; unsigned int pad0; unsigned int pad1; unsigned int pad2; unsigned int pad3; unsigned char pad4; unsigned char isnil; };

struct Vec48 { unsigned int pad0; unsigned char* begin; unsigned char* end; bool __thiscall fn_004777d0() const; };

// FUNCTION: DAO 0x86BF10
void __cdecl fn_0046bf10(Key4* p1, Key4* p2, Key4* p3)
{
    Key4 tmp;

    if (p2->a > p1->a) goto swap12;
    if (p2->a < p1->a) goto skip12;
    if (p2->b > p1->b) goto swap12;
    if (p2->b < p1->b) goto skip12;
    if (p2->d > p1->d) goto swap12;
    if (p2->d < p1->d) goto skip12;
    if (p2->c > p1->c) goto swap12;
    goto skip12;
swap12:
    tmp = *p2;
    *p2 = *p1;
    *p1 = tmp;
skip12:

    if (p3->a > p2->a) goto swap23;
    if (p3->a < p2->a) goto skip23;
    if (p3->b > p2->b) goto swap23;
    if (p3->b < p2->b) goto skip23;
    if (p3->d > p2->d) goto swap23;
    if (p3->d < p2->d) goto skip23;
    if (p3->c > p2->c) goto swap23;
    goto skip23;
swap23:
    tmp = *p3;
    *p3 = *p2;
    *p2 = tmp;
skip23:

    if (p2->a > p1->a) goto swap12b;
    if (p2->a < p1->a) goto skip12b;
    if (p2->b > p1->b) goto swap12b;
    if (p2->b < p1->b) goto skip12b;
    if (p2->d > p1->d) goto swap12b;
    if (p2->d < p1->d) goto skip12b;
    if (p2->c > p1->c) goto swap12b;
    goto skip12b;
swap12b:
    tmp = *p2;
    *p2 = *p1;
    *p1 = tmp;
skip12b:
    ;
}

// FUNCTION: DAO 0x875300
bool __thiscall Key3::fn_00475300(const Key3* other) const
{
    return this->a < other->a ||
           (this->a == other->a && this->b < other->b) ||
           (this->a == other->a && this->b == other->b && this->c < other->c);
}

// FUNCTION: DAO 0x875340
Node* __cdecl fn_00475340(Node* x)
{
    Node* y = x->right;
    while (y->isnil == 0) {
        x = y;
        y = x->right;
    }
    return x;
}

// FUNCTION: DAO 0x8777D0
bool __thiscall Vec48::fn_004777d0() const
{
    if (this->begin == 0)
        return this->begin == 0;
    return (int)(this->end - this->begin) / 48 == 0;
}

// FUNCTION: DAO 0x87DE50
int __fastcall fn_0047de50(unsigned int index, unsigned int /*unused*/, unsigned char** p)
{
    unsigned char value = ((unsigned char*)(*p))[index + 0x3d];
    return (int)((((unsigned int)value) >> 7) % 2u);
}

// FUNCTION: DAO 0x87E320
void __cdecl fn_0047e320(unsigned short* dst, unsigned int count, const unsigned short* src)
{
    if (count != 0) {
        const unsigned short* s = src;
        unsigned short* d = dst;
        do {
            if (d != 0)
                *d = *s;
            --count;
            ++d;
        } while (count != 0);
    }
}

// FUNCTION: DAO 0x87E390
unsigned short* __cdecl fn_0047e390(unsigned short* begin, unsigned short* end, unsigned short* dst)
{
    unsigned int len = end - begin;
    unsigned short* result = dst - len;
    unsigned int offset = (unsigned int)dst - (unsigned int)end;
    while (end != begin) {
        --end;
        unsigned short v = *end;
        *reinterpret_cast<unsigned short*>((unsigned int)end + offset) = v;
    }
    return result;
}
