typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct C46;

extern void __fastcall fn_0040d610(void*, int, int);
extern void __fastcall fn_004c0d90(void*, int);
extern void __fastcall fn_0086b9a0(void*, int, int);
extern u8 __fastcall fn_0046ef40(void*, int, void*);
extern void __fastcall fn_0046c790(void*, int, void*, void*);
extern void* __cdecl fn_00413660(u32);
extern void __fastcall fn_0049d170(void*, int, void**);
extern void __fastcall fn_0046c740(void*, int, int);
extern void __fastcall fn_0046c970(void*, int, int);
extern void __fastcall fn_0046c720(void*, int);
extern u8 __fastcall fn_0046eba0(void*, int);
extern void __fastcall fn_0046c760(void*, int);
extern void __fastcall fn_004c0db0(void*, int);
extern void __fastcall fn_0046d190(void*, int);
extern void* __fastcall fn_0046ee50(void*, int);
extern void* __cdecl fn_0046e770(int, int);
extern void __fastcall fn_004723d0(void*, int, void*);
extern void __fastcall fn_004c3420(void*, int, void*, void*);
extern void __cdecl fn_004d5ba0(void**, void**, void*);
extern void* __fastcall fn_004d57b0(void*, int);
extern void* __fastcall fn_004d56d0(void*, int, void*);
extern void* __cdecl fn_00851740(void*);
extern void* __fastcall fn_00472af0(void*, int, void*, void*);
extern void __cdecl fn_00851640(void*);
extern void __fastcall fn_004d5890(void*, int);
extern void __fastcall fn_0046d170(void*, int, int);
extern void __cdecl fn_008e1613(void);
extern void __fastcall fn_004ac010(void*, int, void*, void*, void*, void*);

extern u32 g_c1f530;
extern void* g_af046c;

struct C46 {
    u8 raw[0x60];
    C46* fn_0006ca90();
    void fn_0006cb00(void* arg);
    void fn_0006cbb0(void* arg);
    C46* fn_0006cc80();
    void fn_0006cd10(int arg);
    void fn_0006cd50();
    void fn_0006cdd0();
    void fn_0006ce50();
    void fn_0006ce60();
    u8 fn_0006ce90(void* arg);
    void fn_0006cfd0();
    C46* fn_0006cff0();
};

// FUNCTION: DAO 0x46ca90
C46* C46::fn_0006ca90()
{
    fn_0040d610(this, 0, 0);
    fn_0040d610((u8*)this + 0x10, 0, 0);
    fn_004c0d90((u8*)this + 0x20, 0);
    *((u8*)this + 0x3c) = 1;
    return this;
}

// FUNCTION: DAO 0x46cb00
void C46::fn_0006cb00(void* arg)
{
    u8* a = (u8*)arg;
    fn_0086b9a0(a + 0x10, 0, 0);
    u8* v = *(u8**)((u8*)this + 0x54);
    void** begin = *(void***)(v + 4);
    void** end = *(void***)(v + 8);
    u32 count = begin ? (u32)(end - begin) : 0;
    for (u32 i = 0; i < count; ++i) {
        void* elem = begin[i];
        if (fn_0046ef40(elem, 0, arg)) break;
    }
    *(void**)(a + 0xc) = *(void**)((u8*)this + 0x40);
}

// FUNCTION: DAO 0x46cbb0
void C46::fn_0006cbb0(void* arg)
{
    u8* a = (u8*)arg;
    if (*(u32*)(a + 0xc) != *(u32*)((u8*)this + 0x40))
        fn_0006cb00(arg);
    u32 count = (*(u32*)(a + 0x18) - *(u32*)(a + 0x14)) >> 2;
    u8 tmp1[8];
    u8 tmp2[8];
    fn_0046c790(arg, 0, tmp1, tmp2);
    u8* begin = *(u8**)(a + 0x14);
    for (u32 i = 0; i < count; ++i) {
        void* elem = *(void**)(begin + i * 4);
        u8* e = (u8*)elem;
        void** b = *(void***)(e + 0x14);
        void** en = *(void***)(e + 0x18);
        if (b && (en - b) > 0)
            fn_004ac010(e + 0x10, 0, arg, elem, b, en);
    }
    ++*(u32*)((u8*)this + 0x34);
}

// FUNCTION: DAO 0x46cc80
C46* C46::fn_0006cc80()
{
    C46* obj = 0;
    void* mem = fn_00413660(0x40);
    if (mem) obj = ((C46*)mem)->fn_0006ca90();
    void* tmp = obj;
    fn_0049d170((u8*)this + 8, 0, (void**)&tmp);
    fn_0046c740(this, 0, 0);
    *(u32*)((u8*)this + 0x38) |= 1;
    return obj;
}

// FUNCTION: DAO 0x46cd10
void C46::fn_0006cd10(int arg)
{
    fn_0046c970((u8*)this + 8, 0, arg);
    fn_0086b9a0((u8*)this + 0x44, 0, 0);
    fn_0046c740(this, 0, 0);
    *(u32*)((u8*)this + 0x34) = 0;
    fn_0046c720(this, 0);
}

// FUNCTION: DAO 0x46cd50
void C46::fn_0006cd50()
{
    fn_0086b9a0((u8*)this + 0x44, 0, 0);
    void** begin = *(void***)((u8*)this + 0xc);
    void** end = *(void***)((u8*)this + 0x10);
    u32 count = begin ? (u32)(end - begin) : 0;
    for (u32 i = 0; i < count; ++i) {
        void* elem = begin[i];
        if (fn_0046eba0(elem, 0))
            fn_0049d170((u8*)this + 0x44, 0, &begin[i]);
    }
}

// FUNCTION: DAO 0x46cdd0
void C46::fn_0006cdd0()
{
    *(void**)this = (void*)0xae804c;
    fn_0006cd10(1);
    fn_0046c760((u8*)this + 0x44, 0);
    fn_004c0db0((u8*)this + 0x18, 0);
    fn_0046c760((u8*)this + 8, 0);
    fn_0046d190(this, 0);
}

// FUNCTION: DAO 0x46ce50
void C46::fn_0006ce50()
{
    fn_0006cd10(0);
}

// FUNCTION: DAO 0x46ce60
void C46::fn_0006ce60()
{
    fn_0006cd10(0);
    C46* obj = fn_0006cc80();
    void* r = fn_0046ee50(obj, 0);
    void* a = fn_0046e770(0, 0);
    fn_004723d0(r, 0, a);
}

// FUNCTION: DAO 0x46ce90
u8 C46::fn_0006ce90(void* arg)
{
    u8 buf[0x28];
    fn_004c3420(arg, 0, buf, (void*)0xae8064);
    void* p1 = 0;
    void* p2 = 0;
    fn_004d5ba0(&p1, &p2, g_af046c);
    u8 bl = 0;
    if (p1) {
        void* v = fn_004d57b0(&p1, 0);
        void* w = fn_004d56d0(&p2, 0, v);
        void* edi = fn_00851740(w);
        void* mem = fn_00413660(0x44);
        void* esi = 0;
        if (mem) esi = fn_00472af0(mem, 0, this, edi);
        void** vt = *(void***)edi;
        typedef u8 (__fastcall *F4)(void*, int);
        bl = ((F4)vt[1])(edi, 0);
        if (bl == 1) bl = (*(void**)((u8*)esi + 0x40) == 0);
        fn_00851640(edi);
        if (esi) {
            void** vt2 = *(void***)esi;
            typedef void (__fastcall *F0)(void*, int, int);
            ((F0)vt2[0])(esi, 0, 1);
        }
        if (bl != 1) fn_0006ce60();
        fn_004d5890(&p1, 0);
        fn_004c0db0(&p2, 0);
    }
    return bl;
}

// FUNCTION: DAO 0x46cfd0
void C46::fn_0006cfd0()
{
    if (*(u32*)((u8*)this + 0x38) & 1) {
        fn_0006cd50();
        fn_0046c740(this, 0, 1);
        *(u32*)((u8*)this + 0x38) &= ~1u;
    }
}

// FUNCTION: DAO 0x46cff0
C46* C46::fn_0006cff0()
{
    fn_0046d170(this, 0, 1);
    *(void**)this = (void*)0xae804c;
    fn_0040d610((u8*)this + 8, 0, 0);
    fn_004c0d90((u8*)this + 0x18, 0);
    *(u32*)((u8*)this + 0x34) = 0;
    *(u32*)((u8*)this + 0x38) = 0;
    *(u32*)((u8*)this + 0x3c) = 0;
    fn_0040d610((u8*)this + 0x44, 0, 0);
    u32 v = g_c1f530;
    *(u32*)((u8*)this + 0x40) = v << 16;
    g_c1f530 = (v + 1) & 0xffff;
    fn_0046c740(this, 0, 0);
    fn_0006ce60();
    return this;
}
