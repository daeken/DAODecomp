typedef unsigned int u32;
typedef unsigned char u8;

extern u32 g_0081eb48;
extern u8 g_0081eb50;
extern u32 g_007fa340[];
extern u8 g_00832abc[];
extern u8 g_0081d23c[];
extern u8 g_00832a30[];
extern void* g_0083293c;
extern void* g_00832938;

void __fastcall fn_000c0d90(void*, void*);
void __fastcall fn_00083920(void*, void*);
void __fastcall fn_0008a880(void*, void*);
void __fastcall fn_000e2830(void*, void*, void*);
void __fastcall fn_00245a50(void*, void*);
void __fastcall fn_000823d0(void*, void*);
void __fastcall fn_000c0db0(void*, void*);
void __fastcall fn_000e2820(void*, void*);
void __fastcall fn_000c2ad0(void*, void*, void*);
void __cdecl fn_002ea8f0(void);
void* __fastcall fn_002796e0(void*, void*, void*);
void* __fastcall fn_000c2480(void*, void*, void*);
void* __fastcall fn_000c3420(void*, void*, void*, void*);
unsigned char __fastcall fn_000e1bf0(void*, void*, void*, void*, void*, void*);
void __fastcall fn_000e1cd0(void*, void*, void*, void*, void*, void*);
int __fastcall fn_0013cc40(void*, void*);
void* __fastcall fn_001dd870(void*, void*, int, void*);
void* __fastcall fn_00003c70(void*, void*);
float __fastcall fn_00078290(void*, void*);
unsigned char __fastcall fn_00438210(void*, void*);
void* __cdecl fn_00002ca0(void);
void __fastcall fn_0008a900(void*, void*);
void __fastcall fn_001c7d60(void*, void*, void*);
int __fastcall fn_001c7dd0(void*, void*);
void* __fastcall fn_001c7e10(void*, void*);
void __fastcall fn_001c7db0(void*, void*);
void __fastcall fn_001c7d90(void*, void*);
void* __fastcall fn_001c7e50(void*, void*);
void __fastcall fn_000c4140(void*, void*, void*);
void __fastcall fn_0008a9d0(void*, void*);
void __fastcall fn_002f9f60(void*, void*);

// FUNCTION: DAO 0x00458e90
void __cdecl fn_00058e90(u32 value)
{
    if (g_0081eb48 != value)
        g_0081eb48 = value;
}

// FUNCTION: DAO 0x0048a970
void* __fastcall fn_0008a970(void* self, void* dummy)
{
    unsigned char temp[0x44];
    (void)dummy;
    fn_000c0d90(self, 0);
    fn_00083920(temp, 0);
    fn_0008a880((unsigned char*)self + 0x1c, 0);
    return self;
}

// FUNCTION: DAO 0x004e2900
void __fastcall fn_000e2900(void* self, void* dummy)
{
    unsigned char tmp[0x44];
    unsigned char obj[0x44];
    (void)dummy;
    while (*(u32*)((unsigned char*)self + 0x24) != 0)
    {
        fn_000e2830((unsigned char*)self + 0x1c, 0, tmp);
        fn_00245a50(obj, 0);
        fn_000823d0(obj, 0);
        fn_000c0db0(tmp, 0);
        if (*(u32*)((unsigned char*)self + 0x24) == 0)
            break;
    }
    fn_000e2820((unsigned char*)self + 0x1c, 0);
    fn_000c2ad0(self, 0, (void*)0xadef14);
}

// FUNCTION: DAO 0x005de2b0
unsigned char __fastcall fn_001de2b0(void* self, void* dummy, int index, int arg2)
{
    unsigned char* base = (unsigned char*)self;
    unsigned char buf[0x44];
    unsigned char local1[0x44];
    unsigned char local2[0x44];
    unsigned char local3[0x44];
    unsigned char result = 0;
    int loopCount = 0;
    int offset = 0;
    (void)dummy;
    fn_000c0d90(buf, 0);
    for (;;)
    {
        unsigned char* E;
        if (*(void**)(base + 0x878) != 0)
        {
            int count = (int)(((unsigned char*)*(void**)(base + 0x87c) - (unsigned char*)*(void**)(base + 0x878)) >> 4);
            if ((unsigned)index < (unsigned)count)
                E = (unsigned char*)*(void**)(base + 0x878) + index * 16;
            else
                E = (unsigned char*)g_00832abc;
        }
        else
            E = (unsigned char*)g_00832abc;
        {
            unsigned char* begin = *(unsigned char**)(E + 4);
            unsigned char* end = *(unsigned char**)(E + 8);
            int elemCount = 0;
            if (begin != 0)
                elemCount = (int)((end - begin) / 28);
            if (loopCount >= elemCount)
                break;
            {
                unsigned char* item;
                if (begin != 0 && loopCount < elemCount)
                    item = begin + offset;
                else
                    item = (unsigned char*)g_0081d23c;
                {
                    void* Pbase;
                    if (*(void**)(base + 0x570) != 0)
                    {
                        int n = (int)(((unsigned char*)*(void**)(base + 0x574) - (unsigned char*)*(void**)(base + 0x570)) >> 2);
                        if ((unsigned)index < (unsigned)n)
                            Pbase = *(void**)((unsigned char*)*(void**)(base + 0x570) + index * 4);
                        else
                            Pbase = *(void**)g_00832a30;
                    }
                    else
                        Pbase = *(void**)g_00832a30;
                    {
                        unsigned char* P = (unsigned char*)Pbase;
                        void* vobj = P + 0x1c;
                        void** vt = *(void***)vobj;
                        void* ret = 0;
                        if (vt)
                        {
                            typedef void* (__fastcall *Fn)(void*, void*, void*);
                            Fn f = (Fn)vt[0x18 / 4];
                            ret = f(vobj, 0, item);
                        }
                        fn_002796e0(P, 0, ret);
                        {
                            u32 g = g_007fa340[index];
                            void* str;
                            unsigned char ok;
                            fn_000c2480(local1, 0, (void*)g);
                            str = fn_000c3420(base + 0x550, 0, (void*)0xb00d8c, local2);
                            ok = fn_000e1bf0((void*)arg2, 0, local1, str, item, local2);
                            fn_000c0db0(local2, 0);
                            fn_000c0db0(local1, 0);
                            if (ok)
                            {
                                void** vtP = *(void***)P;
                                if (vtP)
                                {
                                    typedef void (__fastcall *Fn2)(void*, void*, void*);
                                    Fn2 f2 = (Fn2)vtP[0x28 / 4];
                                    f2(P, 0, buf);
                                }
                                result = 1;
                            }
                            else
                            {
                                void** vtP = *(void***)P;
                                if (vtP)
                                {
                                    typedef void* (__fastcall *Fn3)(void*, void*, void*);
                                    Fn3 f3 = (Fn3)vtP[0x30 / 4];
                                    f3(P, 0, local3);
                                }
                                fn_000e1cd0((void*)arg2, 0, local1, str, item, local3);
                                fn_000c0db0(local3, 0);
                                fn_000c0db0(local2, 0);
                                fn_000c0db0(local1, 0);
                            }
                        }
                    }
                }
            }
        }
        loopCount++;
        offset += 0x1c;
    }
    if (index == 2)
        fn_002ea8f0();
    fn_000c0db0(buf, 0);
    return result;
}

// FUNCTION: DAO 0x005e6360
unsigned char __fastcall fn_001e6360(void* self, void* dummy)
{
    unsigned char* base = (unsigned char*)self;
    unsigned char result = 0;
    int v;
    (void)dummy;
    v = fn_0013cc40(base + 0x58, 0);
    if (v < 0x410)
    {
        result = 1;
    }
    else
    {
        unsigned char A[0x44];
        unsigned char B[0x44];
        unsigned char C[0x44];
        unsigned char D[0x44];
        unsigned char E[0x44];
        unsigned char al;
        void* str;
        fn_0008a970(A, 0);
        fn_000c0d90(B, 0);
        fn_000c4140(C, 0, (void*)0xb01294);
        fn_000c2480(D, 0, (void*)g_007fa340[0]);
        str = fn_000c3420(base + 0x550, 0, (void*)0xb00d8c, E);
        al = fn_000e1bf0(A, 0, D, C, str, E);
        if (al == 0)
            result = 1;
        fn_000c0db0(E, 0);
        fn_000c0db0(D, 0);
        fn_000c0db0(C, 0);
        fn_000c0db0(B, 0);
        fn_0008a9d0(A, 0);
    }
    if (result == 0)
        return 0;
    v = fn_0013cc40(base + 0x58, 0);
    if (v < 0x410)
    {
        void* o = base + 0x2c0;
        void** vt = *(void***)o;
        if (vt)
        {
            typedef void (__fastcall *Fn)(void*, void*, int);
            Fn f = (Fn)vt[0x54 / 4];
            f(o, 0, 0);
            {
                typedef void (__fastcall *Fn2)(void*, void*);
                Fn2 f2 = (Fn2)(*(void***)o)[0x24 / 4];
                f2(o, 0);
            }
        }
    }
    v = fn_0013cc40(base + 0x58, 0);
    if (v < 0x3ec)
    {
        void* r1 = fn_001dd870(base + 0x884, 0, 1, (void*)0xb0126c);
        void* r2 = fn_00003c70(r1, 0);
        fn_000c2ad0(r2, 0, 0);
        r1 = fn_001dd870(base + 0x884, 0, 2, (void*)0xadef14);
        r2 = fn_00003c70(r1, 0);
        fn_000c2ad0(r2, 0, 0);
    }
    v = fn_0013cc40(base + 0x58, 0);
    if (v <= 0x3eb)
    {
        void* o = base + 0x1d8;
        void** vt = *(void***)o;
        if (vt)
        {
            typedef void (__fastcall *Fn)(void*, void*, int);
            Fn f = (Fn)vt[0x54 / 4];
            f(o, 0, 1);
        }
    }
    v = fn_0013cc40(base + 0x58, 0);
    if (v <= 0x3ea)
    {
        void* gp = g_0083293c;
        if (gp != 0)
        {
            unsigned char* p = (unsigned char*)gp + 0x78;
            *(u32*)(base + 0x84) = *(u32*)(p + 0xc);
            *(u32*)(base + 0x80) = *(u32*)(p + 4);
        }
    }
    v = fn_0013cc40(base + 0x58, 0);
    if (v <= 0x3e9)
    {
        void* o = base + 0x490;
        void* ctx = (unsigned char*)g_0083293c + 0x490;
        float fv = fn_00078290(ctx, 0);
        void** vt = *(void***)o;
        if (vt)
        {
            typedef void (__fastcall *Fn)(void*, void*, float);
            Fn f = (Fn)vt[0x54 / 4];
            f(o, 0, fv);
        }
    }
    return result;
}

// FUNCTION: DAO 0x005e6600
unsigned char __fastcall fn_001e6600(void* self, void* dummy)
{
    unsigned char* base = (unsigned char*)self;
    unsigned char obj[0x44];
    int i;
    (void)dummy;
    base[0x93c] = 0;
    fn_0008a970(obj, 0);
    for (i = 0; i < 6; i++)
    {
        unsigned char r = fn_001de2b0(self, 0, i, (int)obj);
        if (i == 4)
            base[0x93c] = r;
    }
    fn_002f9f60(base + 0x57c, 0);
    fn_001e6360(self, 0);
    {
        u32 x = (u32)fn_0013cc40(base + 0x4d0, 0);
        fn_00058e90(x);
    }
    {
        unsigned char y = fn_00438210(base + 0x450, 0);
        g_0081eb50 = y;
    }
    {
        void* p = fn_00002ca0();
        if (p != 0)
        {
            unsigned char* pb = (unsigned char*)p;
            if (pb[0x251] != 0)
            {
                void* vt = base + 0x5f4;
                void** vtable = *(void***)vt;
                if (vtable)
                {
                    typedef void (__fastcall *Fn)(void*, void*, int);
                    Fn f = (Fn)vtable[0x54 / 4];
                    f(vt, 0, 1);
                }
            }
        }
    }
    fn_000e2900(obj, 0);
    fn_0008a900(obj + 0x1c, 0);
    fn_000c0db0(obj, 0);
    return 0;
}

// FUNCTION: DAO 0x006f9f60
void __fastcall fn_002f9f60(void* self, void* dummy)
{
    unsigned char* base = (unsigned char*)self;
    unsigned char A[0x44];
    unsigned char B[0x44];
    unsigned char it[0x44];
    unsigned char it2[0x44];
    unsigned char tmp[0x44];
    void* p;
    (void)dummy;
    fn_0008a970(A, 0);
    fn_000c0d90(B, 0);
    p = self ? (void*)(base + 0x1c) : 0;
    fn_001c7d60(it, 0, p);
    while (fn_001c7dd0(it, 0))
    {
        void* global = g_00832938;
        void* str = fn_000c3420((unsigned char*)global + 0x550, 0, (void*)0xb00d8c, tmp);
        void* key = fn_001c7e50(it, 0);
        unsigned char ok = fn_000e1bf0(A, 0, tmp, str, (void*)0xc35cb0, key);
        fn_000c0db0(tmp, 0);
        if (ok)
        {
            void* v = fn_001c7e10(it, 0);
            if (v != 0)
            {
                void** vt = *(void***)v;
                if (vt)
                {
                    typedef void (__fastcall *Fn)(void*, void*, void*);
                    Fn f = (Fn)vt[0x28 / 4];
                    f(v, 0, B);
                }
            }
        }
        fn_001c7db0(it, 0);
    }
    fn_001c7d90(it, 0);
    p = self ? (void*)(base + 0x2bc) : 0;
    fn_001c7d60(it2, 0, p);
    while (fn_001c7dd0(it2, 0))
    {
        void* global = g_00832938;
        void* str = fn_000c3420((unsigned char*)global + 0x550, 0, (void*)0xb00d8c, tmp);
        void* key = fn_001c7e50(it2, 0);
        unsigned char ok = fn_000e1bf0(A, 0, tmp, str, (void*)0xc35cb0, key);
        fn_000c0db0(tmp, 0);
        if (ok)
        {
            void* v = fn_001c7e10(it2, 0);
            if (v != 0)
            {
                void** vt = *(void***)v;
                if (vt)
                {
                    typedef void (__fastcall *Fn)(void*, void*, void*);
                    Fn f = (Fn)vt[0x28 / 4];
                    f(v, 0, B);
                }
            }
        }
        fn_001c7db0(it2, 0);
    }
    fn_001c7d90(it2, 0);
    fn_000c0db0(B, 0);
    fn_000e2900(A, 0);
    fn_0008a900(A + 0x1c, 0);
    fn_000c0db0(A, 0);
}
