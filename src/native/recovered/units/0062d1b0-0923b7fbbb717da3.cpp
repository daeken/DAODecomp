class CNode {
public:
    unsigned int tag;
    unsigned int* ptr;
    unsigned int __thiscall fn_0062d330();
    unsigned int __thiscall fn_0062d350();
    unsigned int __thiscall fn_0062d370();
    unsigned int __thiscall fn_0062d390();
    unsigned int __thiscall fn_0062d3b0();
    unsigned int __thiscall fn_0062d3d0();
};

class CObjA {
public:
    unsigned char pad[0x58];
    unsigned int field58;
    unsigned int field5c;
    int __thiscall fn_0062d1b0(unsigned int* a, unsigned int* b);
};

class CObjB {
public:
    unsigned char pad[0x196c];
    unsigned int field196c;
    void __thiscall fn_0062d230(unsigned int v);
};

class CStr {
public:
    unsigned char data[0x1c];
};

class CHash {
public:
    unsigned char pad[0xff0];
    unsigned int* table;
    unsigned int __thiscall fn_00632300(const unsigned short* s);
    unsigned int __thiscall fn_00632580(const CStr* s);
};

class CScan {
public:
    unsigned char data[0x1C10];
    unsigned int __thiscall fn_00633730(unsigned int key, unsigned int* out);
    unsigned int __thiscall fn_00633770(unsigned int key, unsigned int* out);
};

class CCrc {
public:
    unsigned char pad[0x42954];
    unsigned int table[256];
    void __thiscall fn_00634610();
};

class CBig {
public:
    unsigned char pad[0x43188];
    unsigned int* base;
    unsigned char pad2[0x14];
    unsigned int divisor;
    unsigned int flags[4];
    void __thiscall fn_006356c0(unsigned int a, unsigned int b);
};

// FUNCTION: DAO 0xA2D1B0
int __thiscall CObjA::fn_0062d1b0(unsigned int* a, unsigned int* b)
{
    if (this->field58 != 3)
        return 0;
    *a = 3;
    *b = this->field5c;
    return 1;
}

// FUNCTION: DAO 0xA2D230
void __thiscall CObjB::fn_0062d230(unsigned int v)
{
    this->field196c = v;
}

// FUNCTION: DAO 0xA2D330
unsigned int __thiscall CNode::fn_0062d330()
{
    if (this->tag == 0x40 && this->ptr != 0)
        return *this->ptr;
    return 0;
}

// FUNCTION: DAO 0xA2D350
unsigned int __thiscall CNode::fn_0062d350()
{
    if (this->tag == 0x41 && this->ptr != 0)
        return *this->ptr;
    return 0;
}

// FUNCTION: DAO 0xA2D370
unsigned int __thiscall CNode::fn_0062d370()
{
    if (this->tag == 0x42 && this->ptr != 0)
        return *this->ptr;
    return 0;
}

// FUNCTION: DAO 0xA2D390
unsigned int __thiscall CNode::fn_0062d390()
{
    if (this->tag == 0x44 && this->ptr != 0)
        return *this->ptr;
    return 0;
}

// FUNCTION: DAO 0xA2D3B0
unsigned int __thiscall CNode::fn_0062d3b0()
{
    if (this->tag == 0x43 && this->ptr != 0)
        return *this->ptr;
    return 0;
}

// FUNCTION: DAO 0xA2D3D0
unsigned int __thiscall CNode::fn_0062d3d0()
{
    if (this->ptr == 0)
        return 0;
    unsigned int t = this->tag;
    if (t == 0x50 || t == 0x51 || t == 0x52 || t == 0x53 || t == 0x54 ||
        t == 0x55 || t == 0x56 || t == 0x57 || t == 0x58 || t == 0x59)
        return *this->ptr;
    return 0;
}

// FUNCTION: DAO 0xA2DB30
void __cdecl fn_0062db30(unsigned char* dest, unsigned char* end, const unsigned char* src)
{
    if (dest == end)
        return;
    unsigned char v = *src;
    do {
        *dest++ = v;
    } while (dest != end);
}

// FUNCTION: DAO 0xA2DFA0
unsigned char* __stdcall fn_0062dfa0(unsigned char* dest, unsigned int count, const unsigned char* src)
{
    unsigned char* p = dest;
    unsigned int n = count;
    if (n != 0) {
        unsigned char v = *src;
        do {
            *p++ = v;
        } while (--n != 0);
    }
    return dest + count;
}

// FUNCTION: DAO 0xA32300
unsigned int __thiscall CHash::fn_00632300(const unsigned short* s)
{
    if (this->table == 0 || s == 0)
        return 0;
    const unsigned short* p = s;
    while (*p != 0)
        ++p;
    unsigned int len = (unsigned int)(p - s);
    unsigned int eax = 0;
    for (unsigned int i = 0; i < len; ++i) {
        unsigned int ebx = s[i];
        ebx = this->table[ebx];
        ebx ^= eax;
        eax = ebx + i + 0x200;
    }
    return eax;
}

// FUNCTION: DAO 0xA32580
unsigned int __thiscall CHash::fn_00632580(const CStr* s)
{
    if (this->table == 0)
        return 0;
    unsigned int len = *reinterpret_cast<const unsigned int*>(s->data + 0x14);
    const unsigned short* data;
    if (*reinterpret_cast<const unsigned int*>(s->data + 0x18) < 8)
        data = reinterpret_cast<const unsigned short*>(s->data + 4);
    else
        data = *reinterpret_cast<const unsigned short* const*>(s->data + 4);
    unsigned int eax = 0;
    for (unsigned int i = 0; i < len; ++i) {
        unsigned int ebx = data[i];
        ebx = this->table[ebx];
        ebx ^= eax;
        eax = ebx + i + 0x200;
    }
    return eax;
}

// FUNCTION: DAO 0xA33730
unsigned int __thiscall CScan::fn_00633730(unsigned int key, unsigned int* out)
{
    for (unsigned int i = 0; i < 4; ++i) {
        unsigned int off = 0x20 + i * 0x950;
        if (*reinterpret_cast<unsigned int*>(this->data + off - 8) == 1 &&
            *reinterpret_cast<unsigned int*>(this->data + off) == key) {
            *out = i;
            return 1;
        }
    }
    return 0;
}

// FUNCTION: DAO 0xA33770
unsigned int __thiscall CScan::fn_00633770(unsigned int key, unsigned int* out)
{
    for (unsigned int i = 0; i < 4; ++i) {
        unsigned int off = 0x1c + i * 0x950;
        if (*reinterpret_cast<unsigned int*>(this->data + off - 4) == 1 &&
            *reinterpret_cast<unsigned int*>(this->data + off) == key) {
            *out = i;
            return 1;
        }
    }
    return 0;
}

// FUNCTION: DAO 0xA34610
void __thiscall CCrc::fn_00634610()
{
    for (unsigned int i = 0; i <= 0xff; ++i) {
        unsigned int c = i;
        for (int k = 0; k < 8; ++k) {
            if (c & 1)
                c = (c >> 1) ^ 0xEDB88320;
            else
                c >>= 1;
        }
        this->table[i] = c;
    }
}

// FUNCTION: DAO 0xA356C0
void __thiscall CBig::fn_006356c0(unsigned int a, unsigned int b)
{
    if (b == 1) {
        unsigned int q = a / this->divisor;
        this->flags[q] = 1;
    }
    unsigned char* p = reinterpret_cast<unsigned char*>(this->base);
    unsigned int offset = a * 0x8c + 0x60;
    *reinterpret_cast<unsigned int*>(p + offset) = b;
}
