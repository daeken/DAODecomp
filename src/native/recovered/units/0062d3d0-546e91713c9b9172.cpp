class CNode {
public:
    unsigned int tag;
    unsigned int* ptr;
    unsigned int __thiscall fn_0062d3d0();
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

// FUNCTION: DAO 0xA2D3D0
unsigned int __thiscall CNode::fn_0062d3d0()
{
    if (this->ptr != 0) {
        unsigned int t = this->tag;
        if (t == 0x50 || t == 0x51 || t == 0x52 || t == 0x53 || t == 0x54 ||
            t == 0x55 || t == 0x56 || t == 0x57 || t == 0x58 || t == 0x59)
            return *this->ptr;
    }
    return 0;
}

// FUNCTION: DAO 0xA2DB30
void __cdecl fn_0062db30(unsigned char* dest, unsigned char* end, const unsigned char* src)
{
    const unsigned char* s = src;
    unsigned char v = *s;
    if (dest == end)
        return;
    do {
        *dest = v;
        ++dest;
    } while (dest != end);
}

// FUNCTION: DAO 0xA2DFA0
unsigned char* __stdcall fn_0062dfa0(unsigned char* dest, unsigned int count, const unsigned char* src)
{
    unsigned char* p = dest;
    unsigned int n = count;
    if (n != 0) {
        do {
            *p = *src;
            ++p;
        } while (--n != 0);
    }
    return dest + count;
}

// FUNCTION: DAO 0xA32300
unsigned int __thiscall CHash::fn_00632300(const unsigned short* s)
{
    if (this->table == 0)
        return 0;
    if (s == 0)
        return 0;
    const unsigned short* p = s;
    while (*p != 0)
        ++p;
    unsigned int len = (unsigned int)(p - s);
    unsigned int h = 0;
    for (unsigned int i = 0; i < len; ++i) {
        unsigned int v = this->table[s[i]];
        v ^= h;
        h = v + i + 0x200;
    }
    return h;
}

// FUNCTION: DAO 0xA32580
unsigned int __thiscall CHash::fn_00632580(const CStr* s)
{
    unsigned int result = 0;
    if (this->table == 0)
        return result;
    unsigned int len = *(const unsigned int*)(s->data + 0x14);
    const unsigned short* data;
    if (*(const unsigned int*)(s->data + 0x18) < 8)
        data = (const unsigned short*)(s->data + 4);
    else
        data = *(const unsigned short* const*)(s->data + 4);
    for (unsigned int i = 0; i < len; ++i) {
        unsigned int v = this->table[data[i]];
        v ^= result;
        result = v + i + 0x200;
    }
    return result;
}

// FUNCTION: DAO 0xA33730
unsigned int __thiscall CScan::fn_00633730(unsigned int key, unsigned int* out)
{
    unsigned char* p = this->data + 0x20;
    for (unsigned int i = 0; i < 4; ++i) {
        if (*(unsigned int*)(p - 8) == 1 && *(unsigned int*)p == key) {
            *out = i;
            return 1;
        }
        p += 0x950;
    }
    return 0;
}

// FUNCTION: DAO 0xA33770
unsigned int __thiscall CScan::fn_00633770(unsigned int key, unsigned int* out)
{
    unsigned char* p = this->data + 0x1c;
    for (unsigned int i = 0; i < 4; ++i) {
        if (*(unsigned int*)(p - 4) == 1 && *(unsigned int*)p == key) {
            *out = i;
            return 1;
        }
        p += 0x950;
    }
    return 0;
}

// FUNCTION: DAO 0xA34610
void __thiscall CCrc::fn_00634610()
{
    unsigned int* t = this->table;
    for (unsigned int i = 0; i <= 0xffu; ++i) {
        unsigned int c = i;
        int k = 8;
        do {
            if (c & 1)
                c = (c >> 1) ^ 0xEDB88320u;
            else
                c >>= 1;
        } while (--k != 0);
        t[i] = c;
    }
}
