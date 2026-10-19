typedef void (__thiscall *Fn_void_void)(void*);
typedef void (__thiscall *Fn_void_int)(void*, int);
typedef void* (__thiscall *Fn_ptr_void)(void*);
typedef void (__thiscall *Fn_void_ptr)(void*, void*);

extern "C" void* g_0081e8a4;
extern "C" void* g_0081e8a8;
extern "C" void* g_0081e8bc;
extern "C" void* g_0081e8c0;
extern "C" void* g_0081e8cc;
extern "C" void* g_0081ea84;
extern "C" void* g_0081ea88;
extern "C" unsigned char g_0081ea80[];
extern "C" unsigned char g_0081eab0[];
extern "C" unsigned char g_0081eac4[];
extern "C" unsigned char g_0081eb18[];
extern "C" unsigned char g_0081eb20[];
extern "C" unsigned char g_0081e8b5;
extern "C" unsigned char g_0081e8b6;
extern "C" unsigned char g_0081ebf5;
extern "C" void* g_0081ebf0;
extern "C" void* g_0081ebf8;
extern "C" void* g_0081ebfc;
extern "C" void* g_00c31a70;
extern "C" void* g_00c31a74;
extern "C" void* g_00c31aac;
extern "C" void* g_00c31ab0;
extern "C" void* g_00c31ab4;
extern "C" void* g_00c31ab8;
extern "C" void* g_00c31aa8;
extern "C" unsigned char g_00c31abc[];
extern "C" unsigned char g_00c31adc[];
extern "C" unsigned char g_00c31acc[];
extern "C" unsigned char g_00c31ad4[];
extern "C" unsigned char g_00c31ac4[];
extern "C" void* g_00c39cfc;
extern "C" unsigned int g_00c30968;
extern "C" unsigned char g_00c30934[];

extern "C" void* __cdecl fn_001278f0(void);
extern "C" void* __cdecl fn_00467e30(void);
extern "C" void __cdecl fn_000136c0(void*);
extern "C" void __fastcall fn_00057860(void*, void*);
extern "C" void __fastcall fn_00058420(void*, void*, void*);
extern "C" void __fastcall fn_0006c760(void*, void*);
extern "C" void __fastcall fn_0040e970(void*, void*, void*);
extern "C" void __cdecl fn_0061c6e4(void);
extern "C" void __fastcall fn_000f7f00(void*, void*, void*);
extern "C" void* __cdecl fn_000fcb70(void);
extern "C" void __fastcall fn_000fc480(void*, void*);
extern "C" void __fastcall fn_000f7ff0(void*, void*);
extern "C" void __cdecl fn_004e1746(void*);
extern "C" void __fastcall fn_00139920(void*, void*);
extern "C" void __cdecl fn_00172500(void);
extern "C" void __cdecl fn_00621800(void);

// FUNCTION: DAO 0x00458720
extern "C" void __cdecl fn_00058720(void)
{
    if (g_0081e8a4) {
        void* p = fn_001278f0();
        void* old = g_0081e8a4;
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0xD8 / 4])(p, old);
        g_0081e8a4 = 0;
    }
    if (g_0081e8c0) {
        void** pp = (void**)g_0081e8c0;
        if (*pp) {
            void* obj = *pp;
            if (obj) {
                void** vt = *(void***)obj;
                ((Fn_void_int)vt[0xC / 4])(obj, 1);
            }
        }
        fn_000136c0(g_0081e8c0);
        g_0081e8c0 = 0;
    }
    if (g_0081e8a8) {
        void* p = fn_001278f0();
        void* old = g_0081e8a8;
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0x6C / 4])(p, old);
        g_0081e8a8 = 0;
    }
    if (g_0081e8bc) {
        void* p = fn_001278f0();
        void* old = g_0081e8bc;
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0x5C / 4])(p, old);
        g_0081e8bc = 0;
    }
    fn_00057860(&g_0081eab0[0], 0);
    if (g_0081e8cc) {
        fn_0006c760(g_0081e8cc, 0);
        fn_000136c0(g_0081e8cc);
    }
    {
        void* e = g_0081ea84;
        void* arg = *(void**)((char*)e + 4);
        fn_0040e970(&g_0081ea80[0], 0, arg);
        e = g_0081ea84;
        *(void**)((char*)e + 4) = e;
        e = g_0081ea84;
        g_0081ea88 = 0;
        *(void**)e = e;
        e = g_0081ea84;
        *(void**)((char*)e + 8) = e;
    }
    fn_00057860(&g_0081eab0[0], 0);
    fn_00057860(&g_0081eac4[0], 0);
    fn_00058420(&g_0081eb18[0], 0, 0);
    fn_00058420(&g_0081eb20[0], 0, 0);
    g_0081e8b6 = 0;
    g_0081e8b5 = 0;
}

// FUNCTION: DAO 0x004593c0
extern "C" void __cdecl fn_000593c0(void)
{
    void* p = fn_00467e30();
    void** vt = *(void***)p;
    ((Fn_void_void)vt[0x18 / 4])(p);
}

// FUNCTION: DAO 0x004593d0
extern "C" void __cdecl fn_000593d0(void* p)
{
    if (p) {
        void** vt = *(void***)p;
        ((Fn_void_int)vt[0x40 / 4])(p, 1);
    }
}

// FUNCTION: DAO 0x0045b010
extern "C" void __cdecl fn_0005b010(void)
{
    if (g_0081ebf5 == 0)
        return;
    g_0081ebf5 = 0;
    fn_0061c6e4();
    void* p = fn_00467e30();
    void** vt = *(void***)p;
    void* obj = ((Fn_ptr_void)vt[0x1C / 4])(p);
    void** vt2 = *(void***)obj;
    ((Fn_void_ptr)vt2[0x168 / 4])(obj, g_0081ebfc);
    g_0081ebfc = 0;
    if (g_0081ebf8) {
        void** v = *(void***)g_0081ebf8;
        ((Fn_void_int)v[0])(g_0081ebf8, 1);
    }
    g_0081ebf8 = 0;
    if (g_0081ebf0) {
        void** v = *(void***)g_0081ebf0;
        ((Fn_void_int)v[0])(g_0081ebf0, 1);
    }
    g_0081ebf0 = 0;
}

// FUNCTION: DAO 0x004f8060
extern "C" void __fastcall fn_000f8060(void* thisptr, void* edx)
{
    fn_000f7f00((char*)thisptr + 4, 0, 0);
    void* p = fn_000fcb70();
    fn_000fc480(p, 0);
}

// FUNCTION: DAO 0x004f8080
extern "C" unsigned char* __cdecl fn_000f8080(void)
{
    if ((g_00c30968 & 1) == 0) {
        g_00c30968 |= 1;
        fn_000f7ff0(&g_00c30934[0], 0);
        fn_004e1746((void*)0xAD59F0);
    }
    return &g_00c30934[0];
}

// FUNCTION: DAO 0x00539f30
extern "C" void __cdecl fn_00139f30(void* p)
{
    if (p) {
        fn_00139920(p, 0);
        fn_000136c0(p);
    }
}

// FUNCTION: DAO 0x0054ffa0
extern "C" void __cdecl fn_0014ffa0(void)
{
    if (g_00c31a74) {
        void** vt = *(void***)g_00c31a74;
        ((Fn_void_int)vt[0])(g_00c31a74, 1);
    }
    if (g_00c31a70) {
        void** vt = *(void***)g_00c31a70;
        ((Fn_void_int)vt[0])(g_00c31a70, 1);
    }
}

// FUNCTION: DAO 0x00555810
extern "C" void __cdecl fn_00155810(void)
{
    fn_00172500();
}

// FUNCTION: DAO 0x00556c50
extern "C" void __cdecl fn_00156c50(void)
{
    fn_00058420(&g_00c31abc[0], 0, 0);
    fn_00058420(&g_00c31adc[0], 0, 0);
    fn_00058420(&g_00c31acc[0], 0, 0);
    fn_00058420(&g_00c31acc[0], 0, 0);
    fn_00058420(&g_00c31ad4[0], 0, 0);
    fn_00058420(&g_00c31ac4[0], 0, 0);
    void* p = fn_001278f0();
    if (g_00c31aac) {
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0x5C / 4])(p, g_00c31aac);
        g_00c31aac = 0;
    }
    if (g_00c31ab0) {
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0x5C / 4])(p, g_00c31ab0);
        g_00c31ab0 = 0;
    }
    if (g_00c31ab4) {
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0x5C / 4])(p, g_00c31ab4);
        g_00c31ab4 = 0;
    }
    if (g_00c31ab8) {
        void** vt = *(void***)p;
        ((Fn_void_ptr)vt[0x5C / 4])(p, g_00c31ab8);
        g_00c31ab8 = 0;
    }
    g_00c31aa8 = 0;
}

// FUNCTION: DAO 0x00844f10
extern "C" void __cdecl fn_00444f10(void)
{
    if (g_00c39cfc) {
        void** vt = *(void***)g_00c39cfc;
        ((Fn_void_int)vt[0])(g_00c39cfc, 1);
        g_00c39cfc = 0;
    }
}

// FUNCTION: DAO 0x00a21850
extern "C" void __cdecl fn_00621850(void)
{
    fn_00621800();
}
