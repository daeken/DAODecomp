struct C004bc1d0 {
    unsigned int field0;
    void* field4;
    void* fn_004bc1d0(const char* name);
};

struct C004c9290 {
    unsigned int field0;
    C004c9290* fn_004c9290(unsigned int value);
};

// FUNCTION: DAO 0x8B7620
extern "C" void* __cdecl fn_004b7620(void* obj, const char* name)
{
    unsigned char* base = (unsigned char*)obj;
    unsigned int start = *(unsigned int*)(base + 0x40);
    unsigned int end = *(unsigned int*)(base + 0x44);
    unsigned int count = (end - start) >> 2;
    if (count == 0) return 0;
    void** arr = (void**)start;
    for (unsigned int i = 0; i < count; ++i) {
        unsigned char* entry = (unsigned char*)arr[i];
        const char* s = *(const char**)(entry + 0x28);
        if (s != 0) {
            const char* a = s;
            const char* b = name;
            while (*a == *b) {
                if (*a == 0) return entry;
                ++a;
                ++b;
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8B76A0
extern "C" void* __cdecl fn_004b76a0(void* obj, const char* name)
{
    if (obj == 0 || name == 0) return 0;
    unsigned char* base = (unsigned char*)obj;
    unsigned int start = *(unsigned int*)(base + 0x100);
    unsigned int end = *(unsigned int*)(base + 0x104);
    unsigned int count = (end - start) >> 2;
    if (count == 0) return 0;
    void** arr = (void**)start;
    for (unsigned int i = 0; i < count; ++i) {
        unsigned char* entry = (unsigned char*)arr[i];
        const char* s = *(const char**)entry;
        if (s != 0) {
            const char* a = s;
            const char* b = name;
            while (*a == *b) {
                if (*a == 0) return entry;
                ++a;
                ++b;
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8BC0F0
extern "C" void __stdcall fn_004bc0f0(void* out, void* src)
{
    unsigned char* s = (unsigned char*)src;
    unsigned char* o = (unsigned char*)out;
    if (*(unsigned int*)(s + 8) != 0) {
        *(void**)(o + 0x2c) = (void*)(s + 0x3c);
    }
}

// FUNCTION: DAO 0x8BC110
extern "C" void __stdcall fn_004bc110(void* out, void* src)
{
    unsigned char* s = (unsigned char*)src;
    unsigned char* o = (unsigned char*)out;
    if (*(unsigned int*)(s + 8) != 0) {
        *(void**)(o + 0x38) = (void*)(s + 0x64);
    }
    if (*(unsigned int*)(s + 0xc) != 0) {
        *(void**)(o + 0x3c) = (void*)(s + 0x7c);
    }
}

// FUNCTION: DAO 0x8BC150
extern "C" void __stdcall fn_004bc150(void* out, void* src)
{
    unsigned char* s = (unsigned char*)src;
    unsigned char* o = (unsigned char*)out;
    int c1 = (int)(*(unsigned int*)(s + 0xc) - *(unsigned int*)(s + 8)) / 12;
    int c2 = (int)(*(unsigned int*)(s + 0x1c) - *(unsigned int*)(s + 0x18)) / 12;
    *(int*)(o + 0) = c1;
    *(int*)(o + 4) = c2;
    *(int*)(o + 8) = 12;
    *(int*)(o + 0xc) = 12;
    if (c1 != 0) {
        *(void**)(o + 0x10) = *(void**)(s + 8);
    }
    if (c2 != 0) {
        *(void**)(o + 0x14) = *(void**)(s + 0x18);
    }
}

// FUNCTION: DAO 0x8BC1B0
extern "C" void __stdcall fn_004bc1b0(void* out, void* src)
{
    unsigned char* s = (unsigned char*)src;
    unsigned char* o = (unsigned char*)out;
    if (*(unsigned int*)(s + 0x64) == 0) {
        *(unsigned int*)(o + 0x1c) = 4;
        *(unsigned int*)(o + 0x20) = *(unsigned int*)(s + 0x30);
    }
}

// FUNCTION: DAO 0x8BC1D0
void* __thiscall C004bc1d0::fn_004bc1d0(const char* name)
{
    void* inner = this->field4;
    if (inner == 0 || name == 0) return 0;
    unsigned char* base = (unsigned char*)inner;
    unsigned int start = *(unsigned int*)(base + 0x100);
    unsigned int end = *(unsigned int*)(base + 0x104);
    unsigned int count = (end - start) >> 2;
    if (count == 0) return 0;
    void** arr = (void**)start;
    for (unsigned int i = 0; i < count; ++i) {
        unsigned char* entry = (unsigned char*)arr[i];
        const char* s = *(const char**)entry;
        if (s != 0) {
            const char* a = s;
            const char* b = name;
            while (*a == *b) {
                if (*a == 0) return *(void**)(entry + 0xf8);
                ++a;
                ++b;
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8BC270
extern "C" void* __cdecl fn_004bc270(void* obj, const char* name, unsigned int* outIndex)
{
    if (obj == 0 || name == 0) return 0;
    unsigned char* base = (unsigned char*)obj;
    unsigned int start = *(unsigned int*)(base + 0x90);
    unsigned int end = *(unsigned int*)(base + 0x94);
    unsigned int count = (end - start) >> 2;
    if (count == 0) return 0;
    void** arr = (void**)start;
    for (unsigned int i = 0; i < count; ++i) {
        unsigned char* entry = (unsigned char*)arr[i];
        const char* s = *(const char**)entry;
        if (s != 0) {
            const char* a = s;
            const char* b = name;
            while (*a == *b) {
                if (*a == 0) {
                    *outIndex = i;
                    return entry;
                }
                ++a;
                ++b;
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8BC410
extern "C" void __stdcall fn_004bc410(void* out, void* src)
{
    unsigned char* s = (unsigned char*)src;
    unsigned char* o = (unsigned char*)out;
    *(unsigned int*)(o + 0xc) = 4;
    unsigned int diff = *(unsigned int*)(s + 0x14) - *(unsigned int*)(s + 0x10);
    if ((diff & 0xfffffffcU) != 0) {
        *(void**)(o + 0x10) = *(void**)(s + 0x10);
    }
}

// FUNCTION: DAO 0x8C9290
C004c9290* __thiscall C004c9290::fn_004c9290(unsigned int value)
{
    this->field0 = value;
    return this;
}

// FUNCTION: DAO 0x8CB1B0
extern "C" unsigned int* __cdecl fn_004cb1b0(unsigned int* p, unsigned int a, unsigned int b, unsigned int c)
{
    p[0] = a;
    p[1] = b;
    p[2] = c;
    return p + 3;
}

// FUNCTION: DAO 0x8EC610
extern "C" void __fastcall fn_004ec610(unsigned int* p)
{
    p[0x1c] &= 0xffffffefU;
}
