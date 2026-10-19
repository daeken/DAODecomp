typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

extern "C" void* __cdecl fn_008b66e0(void*);
extern "C" void* __fastcall fn_008d6090(void*);
extern "C" bool __fastcall fn_008b6e70(char);
extern "C" unsigned int g_00c3dbe0;
extern "C" unsigned char g_00c3d3e0[];
extern "C" void __fastcall fn_008b7360(void*, void*, void*, void*);
extern "C" void __fastcall fn_008b7a60(void*, void*, void*);
extern "C" void __fastcall fn_008b7b00(void*, void*, void*);
extern "C" void __fastcall fn_008b7b50(void*, void*, void*);
extern "C" void __cdecl fn_008d8940(void);
extern "C" void* g_00c3ec28;
extern "C" void* __cdecl fn_008e47aa(unsigned int);
extern "C" void __cdecl fn_008e1a5a(void*);
extern "C" void* __cdecl fn_008e24a0(void*, const void*, unsigned int);
extern "C" void* __cdecl fn_00413660(unsigned int);
extern "C" void* __cdecl fn_008e19e0(void*, int, unsigned int);
extern "C" void __cdecl fn_004136c0(void*);
extern "C" int __cdecl fn_008d79c0(int);
extern "C" float __cdecl fn_008d7ba0(const char*, const char**);
extern "C" int __cdecl fn_008d7e80(const char*);
extern "C" unsigned char __cdecl fn_008d79d0(const char*);
extern "C" unsigned short __cdecl fn_008d7a50(const char*);
extern "C" unsigned int __cdecl fn_008d7b40(const char*);

struct C_DAO {
    void* __thiscall fn_004b67c0(const char*);
    void __thiscall fn_004b7a50(void*, void*);
    void __thiscall fn_004b7ab0(void*);
    void __thiscall fn_004b7c40(void*, unsigned int);
    void __thiscall fn_004b7ca0(void*, unsigned int);
    void __thiscall fn_004b7d00(void*, unsigned int);
    void* __thiscall fn_004d8610();
};

// FUNCTION: DAO 0x008b6780
void* __cdecl fn_004b6780(unsigned char* outFlag) {
    void* r = fn_008b66e0((void*)0);
    if (!r) { *outFlag = 0; return 0; }
    *outFlag = 1;
    void* p = *(void**)((char*)r + 0x18);
    if (!p) return 0;
    if (*(unsigned int*)((char*)p + 0x14) != 4) return 0;
    return (char*)(*(void**)((char*)p + 0x20)) + 8;
}

// FUNCTION: DAO 0x008b67c0
void* __thiscall C_DAO::fn_004b67c0(const char* name) {
    void* node = *(void**)((char*)this + 8);
    if (!node) return 0;
    void** vt = *(void***)node;
    typedef void* (__thiscall *VFn)(void*);
    VFn v = reinterpret_cast<VFn>(vt[6]);
    void* r = v(node);
    if (!r) return 0;
    void* cur = *(void**)((char*)r + 0x4c);
    void* end = (char*)r + 0x2c;
    if (cur == end || cur == 0) return 0;
    for (;;) {
        const char* a = name;
        const char* b = (const char*)(*(void**)((char*)cur + 0x14)) + 8;
        while (*a && *a == *b) { ++a; ++b; }
        if (*a == *b) return 0;
        void* next = fn_008d6090(cur);
        if (!next) return 0;
        cur = next;
    }
}

// FUNCTION: DAO 0x008b6e80
char* __cdecl fn_004b6e80(const char* s) {
    if (!s || s[0] != 'm') return (char*)s;
    char b = s[1];
    if (!fn_008b6e70(b)) return (char*)s;
    unsigned int idx = g_00c3dbe0;
    unsigned char* dst = &g_00c3d3e0[idx << 6];
    ++idx;
    g_00c3dbe0 = idx;
    if (idx == 0x20) g_00c3dbe0 = 0;
    char c = s[2];
    s += 2;
    if (!fn_008b6e70(c)) b = (char)(b + 0x20);
    dst[0] = (unsigned char)b;
    unsigned char* d = dst + 1;
    while (*s) *d++ = (unsigned char)*s++;
    *d = 0;
    return (char*)dst;
}

// FUNCTION: DAO 0x008b7a50
void __thiscall C_DAO::fn_004b7a50(void* a, void* b) {
    fn_008b7360(this, 0, a, b);
}

// FUNCTION: DAO 0x008b7ab0
void __thiscall C_DAO::fn_004b7ab0(void* ptr) {
    if (*(unsigned char*)((char*)this + 0x9f) != 0) {
        fn_008b7a60(this, 0, (char*)ptr + 3);
        fn_008b7a60(this, 0, (char*)ptr + 2);
        fn_008b7a60(this, 0, (char*)ptr + 1);
        fn_008b7a60(this, 0, ptr);
    } else {
        fn_008b7360(this, 0, ptr, (void*)4);
    }
}

// FUNCTION: DAO 0x008b7c40
void __thiscall C_DAO::fn_004b7c40(void* ptr, unsigned int count) {
    if (*(unsigned char*)((char*)this + 0x9f) != 0) {
        while (count > 0) {
            fn_004b7ab0(ptr);
            ptr = (char*)ptr + 4;
            --count;
        }
    } else {
        fn_008b7360(this, 0, ptr, (void*)(count * 4));
    }
}

// FUNCTION: DAO 0x008b7ca0
void __thiscall C_DAO::fn_004b7ca0(void* ptr, unsigned int count) {
    if (*(unsigned char*)((char*)this + 0x9f) != 0) {
        while (count > 0) {
            fn_008b7b00(this, 0, ptr);
            ptr = (char*)ptr + 0xc;
            --count;
        }
    } else {
        fn_008b7360(this, 0, ptr, (void*)(count * 12));
    }
}

// FUNCTION: DAO 0x008b7d00
void __thiscall C_DAO::fn_004b7d00(void* ptr, unsigned int count) {
    if (*(unsigned char*)((char*)this + 0x9f) != 0) {
        while (count > 0) {
            fn_008b7b50(this, 0, ptr);
            ptr = (char*)ptr + 0x10;
            --count;
        }
    } else {
        fn_008b7360(this, 0, ptr, (void*)(count << 4));
    }
}

// FUNCTION: DAO 0x008d8290
void* __cdecl fn_004d8290(const char* data, int* outCount, const char* format) {
    if (outCount) *outCount = 0;
    if (!format || !*format) return 0;
    unsigned int types[64];
    unsigned int total = 0;
    unsigned int count = 0;
    const char* p = format;
    while (*p && count < 64) {
        unsigned char ch = (unsigned char)*p;
        (void)fn_008d79c0((int)ch);
        unsigned int ty = 0;
        unsigned int sz = 4;
        unsigned int idx = (unsigned int)((int)ch - 0x62);
        if (idx <= 0x16) {
            switch (idx) {
                case 0: ty = 0; sz = 4; break;
                case 1: ty = 1; sz = 4; break;
                case 2: ty = 2; sz = 1; break;
                case 3: ty = 3; sz = 1; break;
                case 4: ty = 4; sz = 2; break;
                case 5: ty = 5; sz = 4; break;
                default: {
                    unsigned char ch2 = (unsigned char)p[1];
                    if (ch2 >= '1' && ch2 <= '3') {
                        ty = 6 + (ch2 - '1');
                        sz = (ch2 == '3') ? 4 : ((ch2 == '2') ? 2 : 1);
                        ++p;
                    } else {
                        ty = 0; sz = 4;
                    }
                    break;
                }
            }
        } else {
            ty = 0; sz = 4;
        }
        types[count] = ty;
        total += sz;
        ++count;
        ++p;
    }
    if (outCount) *outCount = (int)count;
    if (total == 0) total = 1;
    unsigned char* out = (unsigned char*)fn_00413660(total << 4);
    if (!out) return 0;
    fn_008e19e0(out, 0, total << 4);
    const char* s = data;
    unsigned char* dst = out;
    for (unsigned int i = 0; i < count; ++i) {
        if (!s) break;
        while (*s == 0x20 || *s == '\t' || *s == '\r' || *s == '\n' || *s == ',') ++s;
        if (!*s) break;
        unsigned int ty = types[i];
        switch (ty) {
            case 0: {
                const char* end = 0;
                float f = fn_008d7ba0(s, &end);
                *(float*)dst = f;
                dst += 4;
                s = end ? end : s;
                break;
            }
            case 1: {
                int v = fn_008d7e80(s);
                *(int*)dst = v;
                dst += 4;
                while (*s && *s != 0x20 && *s != ',' && *s != '\t' && *s != '\r' && *s != '\n') ++s;
                break;
            }
            case 2: {
                unsigned char v = fn_008d79d0(s);
                *dst = v;
                dst += 1;
                while (*s && *s != 0x20 && *s != ',' && *s != '\t' && *s != '\r' && *s != '\n') ++s;
                break;
            }
            case 3: {
                unsigned short v = fn_008d7a50(s);
                *(unsigned short*)dst = v;
                dst += 2;
                while (*s && *s != 0x20 && *s != ',' && *s != '\t' && *s != '\r' && *s != '\n') ++s;
                break;
            }
            case 4: {
                unsigned int v = fn_008d7b40(s);
                *(unsigned int*)dst = v;
                dst += 4;
                while (*s && *s != 0x20 && *s != ',' && *s != '\t' && *s != '\r' && *s != '\n') ++s;
                break;
            }
            default: {
                *(unsigned int*)dst = 0;
                dst += 4;
                while (*s && *s != 0x20 && *s != ',' && *s != '\t' && *s != '\r' && *s != '\n') ++s;
                break;
            }
        }
    }
    return out;
}

// FUNCTION: DAO 0x008d8610
void* __thiscall C_DAO::fn_004d8610() {
    *(unsigned int*)this = 0xb3996c;
    *((unsigned int*)this + 1) = 0;
    *((unsigned int*)this + 2) = 0;
    *((unsigned int*)this + 3) = 0;
    return this;
}

// FUNCTION: DAO 0x008d8a30
int __cdecl fn_004d8a30(void) {
    fn_008d8940();
    void* p = g_00c3ec28;
    if (!p) return 0;
    void** vt = *(void***)p;
    typedef int (__thiscall *VFn)(void*, int, int);
    VFn v = reinterpret_cast<VFn>(vt[3]);
    return v(p, 0, 0);
}

// FUNCTION: DAO 0x008e6c0d
void* __cdecl fn_004e6c0d(void* ptr, unsigned int size) {
    if (!ptr) return fn_008e47aa(size);
    if (!size) { fn_008e1a5a(ptr); return 0; }
    void* np = fn_008e47aa(size);
    if (!np) return 0;
    fn_008e24a0(np, ptr, size);
    fn_008e1a5a(ptr);
    return np;
}
