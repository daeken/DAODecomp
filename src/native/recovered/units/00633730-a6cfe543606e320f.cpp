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
    unsigned int n = count;
    unsigned char* p = dest;
    if (n != 0) {
        do {
            *p = *src;
            ++p;
            --n;
        } while (n != 0);
    }
    return dest + count;
}

// FUNCTION: DAO 0xA32300
unsigned int __thiscall CHash::fn_00632300(const unsigned short* s)
{
    unsigned int* table = this->table;
    if (table == 0)
        return 0;
    if (s == 0)
        return 0;
    const unsigned short* p = s;
    do {
        ++p;
    } while (p[-1] != 0);
    unsigned int len = (unsigned int)(p - (s + 1));
    unsigned int h = 0;
    for (unsigned int i = 0; i < len; ++i) {
        unsigned int v = table[s[i]];
        v ^= h;
        h = v + i + 0x200;
    }
    return h;
}

// FUNCTION: DAO 0xA32580
unsigned int __thiscall CHash::fn_00632580(const CStr* s)
{
    unsigned int h = 0;
    unsigned int* table = this->table;
    if (table == 0)
        return h;
    unsigned int len = *(const unsigned int*)(s->data + 0x14);
    const unsigned short* data;
    if (*(const unsigned int*)(s->data + 0x18) < 8)
        data = (const unsigned short*)(s->data + 4);
    else
        data = *(const unsigned short* const*)(s->data + 4);
    for (unsigned int i = 0; i < len; ++i) {
        unsigned int v = table[data[i]];
        v ^= h;
        h = v + i + 0x200;
    }
    return h;
}

// FUNCTION: DAO 0xA33730
unsigned int __thiscall CScan::fn_00633730(unsigned int key, unsigned int* out)
{
    unsigned int i = 0;
    unsigned char* p = this->data + 0x20;
    do {
        if (*(unsigned int*)(p - 8) == 1 && *(unsigned int*)p == key) {
            *out = i;
            return 1;
        }
        ++i;
        p += 0x950;
    } while (i < 4);
    return 0;
}

// FUNCTION: DAO 0xA33770
unsigned int __thiscall CScan::fn_00633770(unsigned int key, unsigned int* out)
{
    unsigned int i = 0;
    unsigned char* p = this->data + 0x1c;
    do {
        if (*(unsigned int*)(p - 4) == 1 && *(unsigned int*)p == key) {
            *out = i;
            return 1;
        }
        ++i;
        p += 0x950;
    } while (i < 4);
    return 0;
}

// FUNCTION: DAO 0xA34610
void __thiscall CCrc::fn_00634610()
{
    unsigned int i = 0;
    unsigned int* t = this->table;
    do {
        unsigned int c = i;
        int k = 8;
        do {
            if (c & 1)
                c = (c >> 1) ^ 0xEDB88320u;
            else
                c >>= 1;
        } while (--k != 0);
        *t++ = c;
        ++i;
    } while (i <= 0xff);
}
