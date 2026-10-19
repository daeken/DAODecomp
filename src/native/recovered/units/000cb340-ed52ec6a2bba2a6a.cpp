typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef __int64 i64;

extern void __cdecl fn_004136c0(void*);
extern void __cdecl fn_008e11f2();
extern i64 __cdecl fn_004bfff0();
extern void __fastcall fn_004c0db0(void*);
extern const u32 g_af07e0[256];
extern const double g_af0c00;

struct CDe0 { u8 fn_004c0de0(void* arg); };
struct C5D { void fn_005d4b90(); };
struct C86 { u8 fn_0086bee0(); };
struct CB310 { void fn_004cb310(); };

typedef void (__thiscall *VoidThiscallInt)(void*, int);

struct C710 { u8 fn_000ca710(void* arg); };
struct CCac60 { void fn_000cac60(); };
struct CB160 { double fn_000cb160(float arg); };

int* __cdecl fn_000caa20(int* first, int* last, int (__cdecl* pred)(int));
void __cdecl fn_000caa60(void** out, int* first, int* last, void* container, int* dest, int (__cdecl* pred)(int));

// FUNCTION: DAO 0x004CA590
void __fastcall fn_000ca590(void* self)
{
    u8* p = (u8*)self;
    void* node = *(void**)p;
    while (node) {
        void* next = *(void**)((u8*)node + 0x38);
        *(void**)p = next;
        fn_004c0db0((u8*)node + 0x1c);
        fn_004c0db0(node);
        fn_004136c0(node);
        node = *(void**)p;
    }
    *(void**)p = 0;
}

// FUNCTION: DAO 0x004CA710
u8 C710::fn_000ca710(void* arg)
{
    u8* base = (u8*)this;
    u8* b = (u8*)arg;
    u8 al = 0;
    if (*(u32*)(b + 0x14) <= 0)
        return al;
    u8* prev = 0;
    u8* node = *(u8**)base;
    while (node) {
        if (((CDe0*)node)->fn_004c0de0(arg)) {
            u8* next = *(u8**)(node + 0x38);
            if (prev)
                *(u8**)(prev + 0x38) = next;
            else
                *(u8**)base = next;
            ((C5D*)node)->fn_005d4b90();
            fn_004136c0(node);
            return 1;
        }
        prev = node;
        node = *(u8**)(node + 0x38);
    }
    return al;
}

// FUNCTION: DAO 0x004CA910
int __stdcall fn_000ca910(void* arg)
{
    u8* a = (u8*)arg;
    u32 n = *(u32*)(a + 0x14);
    if (n <= 4)
        return 0;
    u32 idx = n - 4;
    if (idx > n)
        fn_008e11f2();
    u16* data;
    if (*(u32*)(a + 0x18) >= 8)
        data = *(u16**)(a + 4);
    else
        data = (u16*)(a + 4);
    if (idx > n)
        fn_008e11f2();
    return data[idx] == 0x2e ? 1 : 0;
}

// FUNCTION: DAO 0x004CA960
u32 __cdecl fn_000ca960(const u8* data, u32 len)
{
    u32 eax = 0xffffffffu;
    u32 i = 0;
    if (len) {
        while (i < len) {
            u32 edi = data[i];
            edi ^= (eax & 0xffu);
            eax >>= 8;
            eax ^= g_af07e0[edi];
            ++i;
        }
    }
    return ~eax;
}

// FUNCTION: DAO 0x004CAA20
int* __cdecl fn_000caa20(int* first, int* last, int (__cdecl* pred)(int))
{
    while (first != last && !pred(*first))
        ++first;
    return first;
}

// FUNCTION: DAO 0x004CAA60
void __cdecl fn_000caa60(void** out, int* first, int* last, void* container, int* dest, int (__cdecl* pred)(int))
{
    u8* c = (u8*)container;
    int* src = first;
    int* dst = dest;
    while (src != last) {
        if (pred(*src))
            break;
        if (!c)
            fn_008e11f2();
        int* limit = *(int**)(c + 8);
        if ((u32)dst >= (u32)limit)
            fn_008e11f2();
        int* old = dst;
        ++dst;
        if (!c)
            fn_008e11f2();
        if ((u32)old >= (u32)limit)
            fn_008e11f2();
        *old = *src;
        ++src;
    }
    out[0] = container;
    out[1] = dst;
}

// FUNCTION: DAO 0x004CAC60
void CCac60::fn_000cac60()
{
    u8* p = (u8*)this;
    while (((C86*)p)->fn_0086bee0() == 0) {
        u8* edi = *(u8**)(p + 8);
        if (*(u32*)(p + 4) > (u32)edi)
            fn_008e11f2();
        u8* eax = edi - 4;
        if ((u32)eax > *(u32*)(p + 8))
            fn_008e11f2();
        if ((u32)eax < *(u32*)(p + 4))
            fn_008e11f2();
        edi -= 4;
        if ((u32)edi < *(u32*)(p + 8))
            fn_008e11f2();
        void* obj = *(void**)edi;
        if (obj) {
            void** vtbl = *(void***)obj;
            ((VoidThiscallInt)vtbl[0])(obj, 1);
        }
        u8* begin = *(u8**)(p + 4);
        if (begin) {
            u8* end = *(u8**)(p + 8);
            u32 diff = (u32)(end - begin);
            diff >>= 2;
            if (diff) {
                end -= 4;
                *(u8**)(p + 8) = end;
            }
        }
    }
    ((CB310*)(p + 0x30))->fn_004cb310();
    ((CB310*)(p + 0x10))->fn_004cb310();
    void* mem = *(void**)(p + 4);
    if (mem)
        fn_004136c0(mem);
    *(void**)(p + 4) = 0;
    *(void**)(p + 8) = 0;
    *(void**)(p + 0xc) = 0;
}

// FUNCTION: DAO 0x004CAD50
void* __cdecl fn_000cad50(void* out, void* arg2, void* arg3, void* arg4, void* arg5, int (__cdecl* pred)(int))
{
    u8* result = (u8*)fn_000caa20((int*)arg3, (int*)arg5, pred);
    u8* container = (u8*)arg2;
    if (container && container != (u8*)arg4)
        fn_008e11f2();
    if (result == (u8*)arg5) {
        ((void**)out)[1] = result;
        ((void**)out)[0] = container;
        return out;
    }
    if (!container)
        fn_008e11f2();
    if ((u32)result >= *(u32*)(container + 8))
        fn_008e11f2();
    fn_000caa60((void**)out, (int*)(result + 4), (int*)arg5, container, (int*)result, pred);
    return out;
}

// FUNCTION: DAO 0x004CB130
void* __fastcall fn_000cb130(void* self)
{
    u8* p = (u8*)self;
    *(float*)(p + 0x10) = 0.0f;
    *(void**)p = (void*)0xaf0be4;
    *(double*)(p + 0x18) = 0.0;
    i64 t = fn_004bfff0();
    *(u32*)(p + 8) = (u32)t;
    *(u32*)(p + 0xc) = (u32)(t >> 32);
    return self;
}

// FUNCTION: DAO 0x004CB160
double CB160::fn_000cb160(float arg)
{
    u8* p = (u8*)this;
    i64 now = fn_004bfff0();
    u32 lo = (u32)now;
    u32 hi = (u32)(now >> 32);
    u32 prevLo = *(u32*)(p + 8);
    u32 prevHi = *(u32*)(p + 0xc);
    if (!((int)hi < (int)prevHi || ((int)hi == (int)prevHi && lo < prevLo))) {
        i64 prev = ((i64)prevHi << 32) | prevLo;
        i64 diff = now - prev;
        *(float*)(p + 0x10) = (float)((double)diff / g_af0c00);
    }
    if (arg > 0.0f)
        *(float*)(p + 0x10) = 1.0f / arg;
    double r = (double)*(float*)(p + 0x10) + *(double*)(p + 0x18);
    *(u32*)(p + 8) = lo;
    *(u32*)(p + 0xc) = hi;
    *(double*)(p + 0x18) = r;
    return r;
}

// FUNCTION: DAO 0x004CB1D0
float __fastcall fn_000cb1d0(void* self)
{
    u8* p = (u8*)self;
    i64 now = fn_004bfff0();
    i64 prev = ((i64)*(u32*)(p + 0xc) << 32) | *(u32*)(p + 8);
    i64 diff = now - prev;
    return (float)((double)diff / g_af0c00);
}

// FUNCTION: DAO 0x004CB340
bool __cdecl fn_000cb340(const float* a, const float* b)
{
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2] && a[3] == b[3];
}
