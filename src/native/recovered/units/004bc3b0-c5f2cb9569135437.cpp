typedef unsigned int u32;
typedef unsigned char u8;

// FUNCTION: DAO 0x8BC310
void* __cdecl fn_004bc310(void* obj, const char* name, u32* outIndex)
{
    void* result = 0;
    u8* base = (u8*)obj;

    if (obj && name)
    {
        if (((*(u32*)(base + 0xA4) - *(u32*)(base + 0xA0)) >> 2) != 0)
        {
            u32* begin = *(u32**)(base + 0xA0);
            u32 i = 0;
            do
            {
                u8* element = (u8*)*begin;
                const char* s1 = *(const char**)element;
                if (s1)
                {
                    const char* s2 = name;
                    for (;;)
                    {
                        u8 a = (u8)s1[0];
                        u8 b = (u8)s2[0];
                        if (a != b) break;
                        if (a == 0)
                        {
                            *outIndex = i;
                            return element;
                        }
                        u8 c = (u8)s1[1];
                        u8 d = (u8)s2[1];
                        if (c != d) break;
                        s1 += 2;
                        s2 += 2;
                        if (c == 0)
                        {
                            *outIndex = i;
                            return element;
                        }
                    }
                }
                ++i;
                ++begin;
            }
            while (i < ((*(u32*)(base + 0xA4) - *(u32*)(base + 0xA0)) >> 2));
        }
    }
    return result;
}

// FUNCTION: DAO 0x8BC3B0
void __stdcall fn_004bc3b0(void* out, void* src)
{
    u8* s = (u8*)src;
    u8* d = (u8*)out;

    *(u32*)(d + 0x00) = (u32)((int)(*(u32*)(s + 0x04) - *(u32*)(s + 0x00)) / 12);
    *(u32*)(d + 0x04) = (u32)((int)(*(u32*)(s + 0x14) - *(u32*)(s + 0x10)) / 12);
    *(u32*)(d + 0x08) = 12;
    *(u32*)(d + 0x0C) = 12;

    if (*(u32*)(d + 0x00) != 0)
        *(u32*)(d + 0x10) = *(u32*)(s + 0x00);
    if (*(u32*)(d + 0x04) != 0)
        *(u32*)(d + 0x14) = *(u32*)(s + 0x10);
}

// FUNCTION: DAO 0x8BC440
void __stdcall fn_004bc440(void* out, void* src)
{
    u8* s = (u8*)src;
    u8* d = (u8*)out;

    if ((*(u32*)(s + 0x44) - *(u32*)(s + 0x40)) & 0xFFFFFFFC)
    {
        *(u32*)(d + 0x28) = *(u32*)(s + 0x40);
        *(u32*)(d + 0x20) = 4;
    }
    else
    {
        *(u32*)(d + 0x28) = 0;
        *(u32*)(d + 0x20) = 0;
    }

    if ((*(u32*)(s + 0x34) - *(u32*)(s + 0x30)) & 0xFFFFFFFC)
    {
        *(u32*)(d + 0x1C) = 4;
        *(u32*)(d + 0x24) = *(u32*)(s + 0x30);
    }
    else
    {
        *(u32*)(d + 0x1C) = 0;
        *(u32*)(d + 0x24) = 0;
    }

    *(u32*)(d + 0x18) |= *(u32*)(s + 0x50) & 0x100;
    *(u32*)(d + 0x18) |= *(u32*)(s + 0x50) & 0x200;
}

// FUNCTION: DAO 0x8BC4B0
void __stdcall fn_004bc4b0(void* out, void* src)
{
    u8* s = (u8*)src;
    u8* d = (u8*)out;

    if ((int)(*(u32*)(s + 0x08) - *(u32*)(s + 0x04)) / 12 == 0)
        return;

    u32* p64 = (u32*)(s + 0x64);
    *(u32*)d = (u32)p64;
    *p64 = (u32)((int)(*(u32*)(s + 0x08) - *(u32*)(s + 0x04)) / 12);
    *(u32*)(d + 0x04) = *(u32*)(s + 0x04);
    *(u32*)(d + 0x20) = 12;

    if ((int)(*(u32*)(s + 0x18) - *(u32*)(s + 0x14)) / 12 == *p64)
    {
        *(u32*)(d + 0x08) = *(u32*)(s + 0x14);
        *(u32*)(d + 0x24) = 12;
    }
    else
    {
        *(u32*)(d + 0x08) = 0;
        *(u32*)(d + 0x24) = 0;
    }

    if (((*(u32*)(s + 0x28) - *(u32*)(s + 0x24)) >> 2) == *p64)
    {
        *(u32*)(d + 0x0C) = *(u32*)(s + 0x24);
        *(u32*)(d + 0x28) = 4;
    }
    else
    {
        *(u32*)(d + 0x0C) = 0;
        *(u32*)(d + 0x28) = 0;
    }

    if (((*(u32*)(s + 0x38) - *(u32*)(s + 0x34)) >> 2) == *p64)
    {
        *(u32*)(d + 0x10) = *(u32*)(s + 0x34);
        *(u32*)(d + 0x2C) = 4;
    }
    else
    {
        *(u32*)(d + 0x10) = 0;
        *(u32*)(d + 0x2C) = 0;
    }

    if (((*(u32*)(s + 0x48) - *(u32*)(s + 0x44)) >> 2) == *p64)
    {
        *(u32*)(d + 0x14) = *(u32*)(s + 0x44);
        *(u32*)(d + 0x30) = 4;
    }
    else
    {
        *(u32*)(d + 0x14) = 0;
        *(u32*)(d + 0x30) = 0;
    }

    if (((*(u32*)(s + 0x58) - *(u32*)(s + 0x54)) >> 2) == *p64)
    {
        *(u32*)(d + 0x18) = *(u32*)(s + 0x54);
        *(u32*)(d + 0x34) = 4;
    }
    else
    {
        *(u32*)(d + 0x18) = 0;
        *(u32*)(d + 0x34) = 0;
    }
}

class CObjectTable
{
public:
    unsigned int __thiscall fn_004bc700(unsigned int key);
    unsigned int __thiscall fn_004bc750(const char* name);

private:
    unsigned int m_p;
};

// FUNCTION: DAO 0x8BC700
unsigned int __thiscall CObjectTable::fn_004bc700(unsigned int key)
{
    unsigned int p = m_p;
    unsigned int result = 0;

    if (p && key)
    {
        if (((*(u32*)((char*)p + 0x34) - *(u32*)((char*)p + 0x30)) >> 2) != 0)
        {
            u32* cur = *(u32**)((char*)p + 0x30);
            u32 i = 0;
            do
            {
                u8* elem = (u8*)*cur;
                if (*(u32*)(elem + 0x40) == key)
                    return *(u32*)elem;
                ++i;
                ++cur;
            }
            while (i < ((*(u32*)((char*)p + 0x34) - *(u32*)((char*)p + 0x30)) >> 2));
        }
    }
    return result;
}

// FUNCTION: DAO 0x8BC750
unsigned int __thiscall CObjectTable::fn_004bc750(const char* name)
{
    unsigned int p = m_p;
    unsigned int result = 0;

    if (p && name)
    {
        if (((*(u32*)((char*)p + 0x44) - *(u32*)((char*)p + 0x40)) >> 2) != 0)
        {
            u32* cur = *(u32**)((char*)p + 0x40);
            u32 i = 0;
            do
            {
                u8* elem = (u8*)*cur;
                const char* s1 = *(const char**)(elem + 0x28);
                const char* s2 = name;
                for (;;)
                {
                    u8 a = (u8)s1[0];
                    u8 b = (u8)s2[0];
                    if (a != b) break;
                    if (a == 0)
                        return *(u32*)(elem + 0x78);
                    u8 c = (u8)s1[1];
                    u8 d = (u8)s2[1];
                    if (c != d) break;
                    s1 += 2;
                    s2 += 2;
                    if (c == 0)
                        return *(u32*)(elem + 0x78);
                }
                ++i;
                ++cur;
            }
            while (i < ((*(u32*)((char*)p + 0x44) - *(u32*)((char*)p + 0x40)) >> 2));
        }
    }
    return result;
}
