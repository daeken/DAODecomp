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

// FUNCTION: DAO 0xA2DB30
void __cdecl fn_0062db30(unsigned char* dest, unsigned char* end, const unsigned char* src)
{
    if (dest == end)
        return;
    do {
        *dest = *src;
        ++dest;
    } while (dest != end);
}

// FUNCTION: DAO 0xA2DFA0
unsigned char* __stdcall fn_0062dfa0(unsigned char* dest, unsigned int count, const unsigned char* src)
{
    if (count != 0) {
        unsigned int n = count;
        unsigned char* p = dest;
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
    unsigned int* table = this->table;
    if (table == 0)
        return 0;
    if (s == 0)
        return 0;
    unsigned int h = 0;
    const unsigned short* p = s;
    while (*p++ != 0)
        ;
    unsigned int len = (unsigned int)(p - (s + 1));
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
