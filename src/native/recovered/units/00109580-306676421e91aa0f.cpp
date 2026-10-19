typedef unsigned int uint32;

struct StrMap { int fn_000c0aa0(const char*); };
struct Base050 { void fn_0010f250(); };
struct Sub24 { void fn_000c0db0(); void fn_000c2ab0(); };
struct Sub8 { void fn_000c0db0(); };
struct Sub14 { void fn_0006c3b0(int); };
struct AllocObj { void fn_000f6bc0(); void fn_000f6e80(void*); void fn_000f6d60(void*); void fn_000f6aa0(void*); void fn_000f6ab0(); void fn_000f6cd0(); };
struct SomeOther { void* fn_00106d40(void*); };
struct Some507330 { void fn_00107330(); };
struct ArgObj { int fn_000c0990(); };

typedef void (__thiscall *VCall_NoArg)(void*);
typedef void (__thiscall *VCall_Int)(void*, int);
typedef void (__thiscall *VCall_VoidPtr)(void*, void*);
typedef void (__thiscall *VCall_UShort)(void*, unsigned short);
typedef void* (__thiscall *VCall_NoArgRet)(void*);

extern "C" void* __cdecl fn_00013660(unsigned int);
extern "C" unsigned char g_006f4484[];
extern "C" unsigned char g_006f43d4[];
extern "C" unsigned char g_006f4470[];
extern "C" unsigned char g_006f4454[];
extern "C" unsigned char g_006f443c[];
extern "C" unsigned char g_006f4520[];
extern "C" unsigned char g_006f4598[];
extern "C" unsigned char g_006f5000[];
extern "C" unsigned char g_006f5034[];
extern "C" unsigned char g_006f5060[];
extern "C" unsigned char g_006f508c[];
extern "C" unsigned int g_007f5a14;

struct Texture : Base050 { void fn_0010f320(); };
struct Float : Base050 { void fn_0010f270(); };
struct Matrix4x4f : Base050 { void fn_0010f290(); };
struct Vector4fArray : Base050 { void fn_0010f4e0(); void* fn_0010f070(void*); void* fn_00106cd0(); };
struct Factory { void* fn_001093d0(); void fn_00109580(); };
struct FlagsObj { void fn_001095a0(ArgObj*); };
struct Small { void fn_001095f0(void*); };
struct TailObj { void fn_00109610(); };
struct BigObj { void fn_00109630(); void fn_001096e0(); };

// FUNCTION: DAO 0x5093D0
void* __thiscall Factory::fn_001093d0()
{
    char* base = (char*)this;
    StrMap* map = (StrMap*)(base + 8);
    if (map->fn_000c0aa0((const char*)g_006f4484)) {
        Texture* p = (Texture*)fn_00013660(0x34);
        if (p) { p->fn_0010f320(); return p; }
        return 0;
    }
    if (map->fn_000c0aa0((const char*)g_006f43d4)) {
        Float* p = (Float*)fn_00013660(0x1c);
        if (p) { p->fn_0010f270(); return p; }
        return 0;
    }
    if (map->fn_000c0aa0((const char*)g_006f4470) || map->fn_000c0aa0((const char*)g_006f4454)) {
        Vector4fArray* p = (Vector4fArray*)fn_00013660(0x28);
        if (!p) return 0;
        p->fn_0010f4e0();
        *(void**)((char*)p + 0x10) = *(void**)(base + 0x5c);
        ((VCall_VoidPtr)(*(void***)p)[4])(p, (void*)(base + 0x9c));
        ((VCall_UShort)(*(void***)p)[3])(p, *(unsigned short*)(base + 0x98));
        p->fn_0010f070((void*)(base + 0x24));
        ((VCall_VoidPtr)(*(void***)p)[5])(p, (void*)(base + 0x40));
        ((VCall_VoidPtr)(*(void***)p)[6])(p, (void*)(base + 0x60));
        ((VCall_VoidPtr)(*(void***)p)[7])(p, (void*)(base + 0x7c));
        ((VCall_NoArg)(*(void***)p)[8])(p);
        return p;
    }
    if (map->fn_000c0aa0((const char*)g_006f443c)) {
        Matrix4x4f* p = (Matrix4x4f*)fn_00013660(0x60);
        if (p) { p->fn_0010f290(); return p; }
        return 0;
    }
    return 0;
}

// FUNCTION: DAO 0x509580
void __thiscall Factory::fn_00109580()
{
    *(void**)((char*)this + 0xd4) = this->fn_001093d0();
}

// FUNCTION: DAO 0x5095A0
void __thiscall FlagsObj::fn_001095a0(ArgObj* arg)
{
    int r = arg->fn_000c0990();
    if (r == 3) {
        *(unsigned int*)((char*)this + 8) |= 1u;
        return;
    }
    if (r == 2) {
        *(unsigned int*)((char*)this + 8) |= (unsigned int)r;
        unsigned int v = *(unsigned int*)((char*)this + 8);
        if (v & 0x1cu) {
            v &= 0xffffffe3u;
            *(unsigned int*)((char*)this + 8) = v;
        }
    }
}

// FUNCTION: DAO 0x5095F0
void __thiscall Small::fn_001095f0(void* arg)
{
    *(void**)this = (void*)g_006f4520;
    *(void**)((char*)this + 4) = arg;
}

// FUNCTION: DAO 0x509610
void __thiscall TailObj::fn_00109610()
{
    ((Sub24*)((char*)this + 0x24))->fn_000c2ab0();
}

// FUNCTION: DAO 0x509630
void __thiscall BigObj::fn_00109630()
{
    char* base = (char*)this;
    AllocObj* p = (AllocObj*)fn_00013660(0x40);
    if (p) { p->fn_000f6bc0(); }
    *(void**)(base + 0x44) = p;
    p->fn_000f6e80((void*)(base + 8));
    p->fn_000f6d60((void*)(base + 0x24));
    void* f40 = *(void**)(base + 0x40);
    if (f40) {
        void* edi = ((VCall_NoArgRet)(*(void***)f40)[5])(f40);
        ((Some507330*)edi)->fn_00107330();
        p->fn_000f6aa0(edi);
    }
    p->fn_000f6ab0();
    p->fn_000f6cd0();
}

// FUNCTION: DAO 0x5096E0
void __thiscall BigObj::fn_001096e0()
{
    char* d = (char*)this;
    *(void**)d = (void*)g_006f4598;
    void* p = *(void**)(d + 0x40);
    if (p) {
        ((VCall_Int)(*(void***)p)[0])(p, 1);
    }
    ((Sub24*)(d + 0x24))->fn_000c0db0();
    ((Sub8*)(d + 8))->fn_000c0db0();
    *(void**)d = (void*)g_006f4520;
}

// FUNCTION: DAO 0x50F070
void* __thiscall Vector4fArray::fn_0010f070(void* arg)
{
    void* tmp = this->fn_00106cd0();
    void* res = ((SomeOther*)tmp)->fn_00106d40(arg);
    *(void**)((char*)this + 8) = res;
    return res;
}

// FUNCTION: DAO 0x50F270
void __thiscall Float::fn_0010f270()
{
    char* d = (char*)this;
    ((Base050*)this)->fn_0010f250();
    *(float*)(d + 0x10) = 1.0f;
    *(void**)d = (void*)g_006f5000;
    *(float*)(d + 0x14) = 0.0f;
    *(float*)(d + 0x18) = 1.0f;
}

// FUNCTION: DAO 0x50F290
void __thiscall Matrix4x4f::fn_0010f290()
{
    char* d = (char*)this;
    ((Base050*)this)->fn_0010f250();
    *(void**)d = (void*)g_006f5034;
}

// FUNCTION: DAO 0x50F320
void __thiscall Texture::fn_0010f320()
{
    char* d = (char*)this;
    ((Base050*)this)->fn_0010f250();
    *(void**)d = (void*)g_006f5060;
    *(unsigned short*)(d + 0x10) = 0xffffu;
    *(unsigned int*)(d + 0x28) = 0u;
    *(unsigned int*)(d + 0x2c) = 0xfu;
    *(unsigned char*)(d + 0x18) = 0;
    *(unsigned int*)(d + 0x30) = g_007f5a14;
}

// FUNCTION: DAO 0x50F4E0
void __thiscall Vector4fArray::fn_0010f4e0()
{
    char* d = (char*)this;
    ((Base050*)this)->fn_0010f250();
    *(void**)d = (void*)g_006f508c;
    ((Sub14*)(d + 0x14))->fn_0006c3b0(0);
    *(unsigned char*)(d + 0x24) = 0;
}
