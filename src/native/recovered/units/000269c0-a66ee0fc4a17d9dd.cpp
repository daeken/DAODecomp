typedef unsigned int u32;
typedef unsigned char u8;

extern "C" void* g_0081d9e0;
extern "C" void* g_0081da08;
extern "C" void* g_0081d9e4;
extern "C" void* g_0081d9e8;
extern "C" unsigned char g_0081d9fc;
extern "C" unsigned char g_0081d9fd;
extern "C" unsigned char g_006e3960[];
extern "C" unsigned char g_006e2dd4[];
extern "C" unsigned char g_0001cdd0[];
extern "C" unsigned char g_0001cde0[];

extern "C" void __cdecl fn_00034fd0(void);
extern "C" void* __cdecl fn_004e47aa(unsigned int);
extern "C" void __cdecl fn_00447470(void*);
extern "C" void __cdecl fn_00447330(void*);
extern "C" void __cdecl fn_004e11f2(void);
extern "C" void __fastcall fn_00081950(void*, int, void*, void*, void*, void*, void*);
extern "C" void __cdecl fn_0007cc10(void*, void*, void*, void*);
extern "C" void __cdecl fn_000136c0(void*);
extern "C" void __fastcall fn_00074130(void*);
extern "C" void __fastcall fn_00083c40(void*, int, int);
extern "C" void __fastcall fn_00494230(void*);
extern "C" void __cdecl fn_0061d850(void*);
extern "C" void __fastcall fn_0001fe20(void*);
extern "C" void __fastcall fn_000244c0(void*);
extern "C" void __fastcall fn_0006c760(void*);
extern "C" void __fastcall fn_000cb310(void*);
extern "C" void __fastcall fn_00092b70(void*);
extern "C" void __fastcall fn_00092ab0(void*);
extern "C" void __fastcall fn_000c0db0(void*);
extern "C" void __fastcall fn_000a2850(void*);
extern "C" void __fastcall fn_000a29e0(void*, int, int);
extern "C" void __fastcall fn_0009bc50(void*);
extern "C" void __fastcall fn_000a2090(void*);
extern "C" void __fastcall fn_000a4ad0(void*);
extern "C" void __fastcall fn_000a4bd0(void*);
extern "C" void __cdecl fn_0050a3e6(void);
extern "C" void __fastcall fn_000a6f50(void*);
extern "C" void __fastcall fn_000a7020(void*);
extern "C" void* __cdecl fn_00001f30(void);
extern "C" void __fastcall fn_00002900(void*);
extern "C" void* __fastcall fn_00003c70(void*, int, int);
extern "C" void __fastcall fn_000ac7f0(void*);
extern "C" void __fastcall fn_000aa960(void*);
extern "C" void __fastcall fn_000df390(void*);
extern "C" void __fastcall fn_000ddc20(void*);
extern "C" void __cdecl fn_0061e150(void*, void*);
extern "C" void __cdecl fn_004e19e0(void*, int, unsigned int);

// FUNCTION: DAO 0x004269c0
extern "C" void __cdecl fn_000269c0(void)
{
    void* p = g_0081d9e0;
    if (!p) return;
    void* q = g_0081da08;
    if (q)
    {
        void** vtbl = *(void***)q;
        typedef void (__thiscall *Fn1)(void*, int);
        ((Fn1)vtbl[0x3c / 4])(q, 1);
        p = g_0081d9e0;
        g_0081da08 = 0;
    }
    typedef void (__cdecl *Fn2)(void*, int);
    ((Fn2)(*(void**)((char*)p + 8)))(p, 0);
    g_0081d9e0 = 0;
}

// FUNCTION: DAO 0x00426a10
extern "C" void __cdecl fn_00026a10(void* alloc, void* ctx)
{
    if (g_0081d9e0) return;
    if (alloc)
    {
        typedef void* (__cdecl *AllocFn)(unsigned int, const char*, int);
        void* mem = ((AllocFn)alloc)(0xc, (const char*)g_006e3960, 0);
        if (mem)
        {
            *(void**)((char*)mem + 4) = alloc;
            *(void**)((char*)mem + 8) = ctx;
            *(void**)mem = (void*)g_006e2dd4;
            g_0081d9e0 = mem;
            return;
        }
    }
    void* mem2 = fn_004e47aa(0xc);
    if (!mem2)
    {
        g_0081d9e0 = 0;
        return;
    }
    *(void**)((char*)mem2 + 4) = (void*)g_0001cdd0;
    *(void**)((char*)mem2 + 8) = (void*)g_0001cde0;
    *(void**)mem2 = (void*)g_006e2dd4;
    g_0081d9e0 = mem2;
}

// FUNCTION: DAO 0x00427e20
extern "C" void __cdecl fn_00027e20(void)
{
    fn_00034fd0();
    if (g_0081d9e4)
    {
        void** vt = *(void***)g_0081d9e4;
        typedef void (__thiscall *FnV)(void*, int);
        ((FnV)vt[0])(g_0081d9e4, 1);
        g_0081d9e4 = 0;
    }
    if (g_0081da08)
    {
        void** vt = *(void***)g_0081da08;
        typedef void (__thiscall *FnV)(void*, int);
        ((FnV)vt[0x3c / 4])(g_0081da08, 1);
        g_0081da08 = 0;
    }
    if (g_0081d9fd)
    {
        void* p = g_0081d9e8;
        if (p)
        {
            void** vt = *(void***)p;
            typedef void (__thiscall *FnV)(void*, int);
            ((FnV)vt[0x2c / 4])(p, 1);
            g_0081d9e8 = 0;
        }
    }
    void* ecx = g_0081da08;
    if (g_0081d9fc)
    {
        void* p = g_0081d9e0;
        if (p)
        {
            if (ecx)
            {
                void** vt = *(void***)ecx;
                typedef void (__thiscall *FnV)(void*, int);
                ((FnV)vt[0x3c / 4])(ecx, 1);
            }
            p = g_0081d9e0;
            g_0081da08 = 0;
            typedef void (__cdecl *FnP)(void*, int);
            ((FnP)(*(void**)((char*)p + 8)))(p, 0);
            g_0081d9e0 = 0;
        }
    }
}

// FUNCTION: DAO 0x00485340
extern "C" void __fastcall fn_00085340(void* self, int, unsigned char arg)
{
    if (arg)
    {
        void* end = *(void**)((char*)self + 8);
        if (*(void**)((char*)self + 4) > end) fn_004e11f2();
        void* begin = *(void**)((char*)self + 4);
        if (begin > *(void**)((char*)self + 8)) fn_004e11f2();
        unsigned char tmp[8];
        fn_00081950(self, 0, (void*)tmp, begin, begin, end, end);
        void* old4 = *(void**)((char*)self + 4);
        void* old8 = *(void**)((char*)self + 8);
        *(void**)((char*)self + 4) = 0;
        *(void**)((char*)self + 8) = 0;
        *(void**)((char*)self + 0xc) = 0;
        if (old4)
        {
            unsigned char local[0x40];
            fn_0007cc10(old4, old8, local, (void*)(int)arg);
        }
        fn_000136c0(old4);
        return;
    }
    void* p = *(void**)((char*)self + 4);
    if (p)
    {
        void* q = *(void**)((char*)self + 8);
        int count = (int)(((char*)q - (char*)p) >> 6);
        if (count != 0)
        {
            unsigned char tmp[0x40];
            fn_00074130(tmp);
            fn_00083c40(self, 0, 0);
        }
    }
}

// FUNCTION: DAO 0x0048f720
extern "C" void __fastcall fn_0008f720(void* self)
{
    void* p = *(void**)self;
    if (p) fn_00447470(p);
}

// FUNCTION: DAO 0x00490c20
extern "C" void __fastcall fn_00090c20(void* self)
{
    fn_00085340((char*)self + 0x54, 0, 0);
    void* p = *(void**)self;
    if (p)
    {
        fn_00447330(p);
        *(void**)self = 0;
    }
}

// FUNCTION: DAO 0x00495a50
extern "C" void __fastcall fn_00095a50(void* self)
{
    fn_00494230(self);
    void* p = *(void**)((char*)self + 0x20);
    if (p)
    {
        fn_0061d850(p);
        *(void**)((char*)self + 0x20) = 0;
    }
    void* q = *(void**)((char*)self + 0x2924);
    if (q) fn_0001fe20(q);
    void* r = *(void**)((char*)self + 0x2928);
    if (r) fn_0001fe20(r);
    *(void**)self = 0;
    void* s = *(void**)((char*)self + 0x28f8);
    if (s)
    {
        void** vt = *(void***)s;
        typedef void (__thiscall *FnV)(void*, int);
        ((FnV)vt[0])(s, 1);
        *(void**)((char*)self + 0x28f8) = 0;
    }
    void* t = *(void**)((char*)self + 0x28fc);
    if (t)
    {
        fn_000136c0(t);
        *(void**)((char*)self + 0x28fc) = 0;
    }
}

// FUNCTION: DAO 0x00496fb0
extern "C" void __fastcall fn_00096fb0(void* self)
{
    fn_00095a50(self);
    void* e = *(void**)((char*)self + 0x2924);
    if (e)
    {
        fn_000244c0(e);
        fn_000136c0(e);
        *(void**)((char*)self + 0x2924) = 0;
    }
    void* f = *(void**)((char*)self + 0x2928);
    if (f)
    {
        fn_000244c0(f);
        fn_000136c0(f);
        *(void**)((char*)self + 0x2928) = 0;
    }
    fn_0006c760((char*)self + 0x29a4);
    fn_000cb310((char*)self + 0x2984);
    fn_000cb310((char*)self + 0x2964);
    fn_00092b70((char*)self + 0x2914);
    fn_00092ab0((char*)self + 0x2904);
    fn_000c0db0((char*)self + 4);
}

// FUNCTION: DAO 0x004a2ae0
extern "C" void __fastcall fn_000a2ae0(void* self)
{
    fn_000a2850(self);
    fn_000a29e0((char*)self + 0x10, 0, 0);
    fn_0009bc50((char*)self + 0x80);
    fn_0009bc50((char*)self + 0x70);
    fn_0006c760((char*)self + 0x60);
    fn_0006c760((char*)self + 0x50);
    fn_0006c760((char*)self + 0x40);
    fn_0006c760((char*)self + 0x30);
    fn_000a2090((char*)self + 0x20);
    fn_000a2090((char*)self + 0x10);
    fn_000a2090(self);
}

// FUNCTION: DAO 0x004a7950
extern "C" void __fastcall fn_000a7950(void* self)
{
    int state = *(int*)((char*)self + 0x1c);
    if (state == 2)
        fn_000a4ad0(self);
    else if (state == 4)
        fn_000a4bd0(self);
    if (*(int*)((char*)self + 0x1c) != 1) fn_0050a3e6();
    fn_000a6f50(self);
    fn_000a7020(self);
    void* p = fn_00001f30();
    if (p)
    {
        void* t = fn_00001f30();
        fn_00002900(t);
        void* ebx = *(void**)((char*)t + 0x6d20);
        if (ebx)
        {
            void* esi = (char*)ebx + 0xa4;
            void* z = fn_00003c70(esi, 0, 0);
            fn_000ac7f0(z);
            void** vt = *(void***)esi;
            typedef void (__thiscall *FnV)(void*);
            ((FnV)vt[0x24 / 4])(esi);
            fn_000aa960(ebx);
        }
    }
    *(int*)((char*)self + 0x1c) = 1;
}

// FUNCTION: DAO 0x004df490
extern "C" void __fastcall fn_000df490(void* self)
{
    fn_000df390(self);
    fn_000ddc20((char*)self + 0x1c);
}

// FUNCTION: DAO 0x00a1dee0
extern "C" void __cdecl fn_0061dee0(void* arg)
{
    void* esi = arg;
    int state = *(int*)((char*)esi + 0x62ee0);
    if (state == 6 || state == 3)
    {
        void* val = *(void**)((char*)esi + 0x62e70);
        void* ctx = *(void**)((char*)esi + 4);
        fn_0061e150(ctx, val);
    }
    void* p = *(void**)esi;
    fn_00447470(p);
    void* dst = (char*)esi + 0x62ccc;
    fn_004e19e0(dst, 0, 0x194);
    *(int*)((char*)esi + 0x62ee0) = 0;
    *(int*)((char*)esi + 0x62e80) = 0;
    *(int*)((char*)esi + 0x62e84) = 0;
    *(int*)((char*)esi + 0x62e88) = 0;
    *(int*)((char*)esi + 0x62e8c) = 0;
    *(int*)((char*)esi + 0x62e60) = -1;
}
