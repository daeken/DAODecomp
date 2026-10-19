typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

extern u32 g_c15234;
extern u8 g_c1ebb0[];
extern u32 g_c327ec;

extern void* fn_005278c0(void);
extern void* fn_00867e30(void);
extern void* fn_004f77c0(void);
extern void* fn_00413660(u32);
extern void* fn_004c0010(void*);
extern bool fn_004c9010(void*, u32);
extern void fn_008e1613(void);
extern void* fn_004c3030(void*, ...);

struct C_4C2480 { void fn_004c2480(void*); };
struct C_4C0DB0 { void fn_004c0db0(); };
struct C_45A410 { void fn_0045a410(u32); };
struct C_534A70 { void fn_00534a70(u32); };
struct C_45A3B0 { void fn_0045a3b0(u32); };
struct C_4572D0 { void fn_004572d0(u32); };
struct C_458420 { void fn_00458420(u32); };
struct C_4F79E0 { void* fn_004f79e0(const void*); };
struct C_4F2750 { void fn_004f2750(const void*); };
struct C_468D00 { void fn_00468d00(void*); };
struct C_4C2510 { void fn_004c2510(void*); };
struct C_4C2AB0 { void fn_004c2ab0(void*); };
struct C_4C36C0 { void fn_004c36c0(void*); };
struct C_4C36A0 { void fn_004c36a0(void*); };
struct C_4C2AD0 { void fn_004c2ad0(void*); };
struct C_4C4140 { void fn_004c4140(const void*); };
struct C_4CA8D0 { void* fn_004ca8d0(); };
struct C_5D57C0 { bool fn_005d57c0(); };
struct C_45A4F0 { void fn_0045a4f0(void*); };
struct C_4C0D90 { void fn_004c0d90(); };
struct C_5279D0 { void fn_005279d0(u32,u32,u32,u32,u32,u32,u32,u32,u32,u32,u32,u32,u32,u32,u32,u32); };

struct C_45A500 { void fn_0005a500(); };
struct C_45A7E0 { void fn_0005a7e0(u32,u32,u32,u32,u32,u32,u32,u32,u32); };
struct C_245FC0 { bool fn_00245fc0(); };
struct C_7F3120 { void fn_003f3120(); };
struct C_7F3AB0 { void fn_003f3ab0(void*); };

// FUNCTION: DAO 0x0045a500
void C_45A500::fn_0005a500()
{
    char* self = (char*)this;
    char* vec = self + 0x2c;
    u32* begin = *(u32**)(vec + 4);
    u32* end = *(u32**)(vec + 8);
    if (!begin) {
        ((C_45A410*)vec)->fn_0045a410(0);
        return;
    }
    u32 count = (u32)((char*)end - (char*)begin) >> 6;
    for (u32 i = 0; i < count; ++i) {
        u32 tmp = (u32)fn_005278c0();
        (void)tmp;
        void** vt = *(void***)self;
        typedef void (__thiscall *VFn)(void*);
        VFn v = (VFn)vt[0x28/4];
        v(self);
        char buf[64];
        ((C_4C2480*)buf)->fn_004c2480((void*)g_c1ebb0);
        ((C_4C0DB0*)buf)->fn_004c0db0();
    }
    ((C_45A410*)vec)->fn_0045a410(0);
}

// FUNCTION: DAO 0x0045a7e0
void C_45A7E0::fn_0005a7e0(u32 a1,u32 a2,u32 a3,u32 a4,u32 a5,u32 a6,u32 a7,u32 a8,u32 a9)
{
    char* self=(char*)this;
    *(u32*)self=0xae7564;
    *(u32*)(self+8)=a1;
    ((C_534A70*)(self+0x14))->fn_00534a70(0);
    ((C_534A70*)(self+0x20))->fn_00534a70(0);
    ((C_45A3B0*)(self+0x2c))->fn_0045a3b0(0);
    *(u32*)(self+0x28)=0;
    *(u8*)(self+0x45)=(u8)a5;
    *(u8*)(self+0x46)=(u8)a6;
    *(u32*)(self+0x3c)=0;
    *(u8*)(self+0x41)=1;
    *(u8*)(self+0x44)=1;
    *(float*)(self+0x50)=0.0f;
    *(float*)(self+0x54)=0.0f;
    *(float*)(self+0x58)=0.0f;
    *(float*)(self+0x5c)=1.0f;
    ((C_4572D0*)(self+0x60))->fn_004572d0(3);
    *(u32*)(self+0x74)=0;
    *(u32*)(self+0x78)=0;
    *(u8*)(self+0x7c)=1;
    u32 o=(u32)fn_00867e30();
    *(u32*)(self+4)=o;
    if (!o) return;
    u32 ecx8=*(u32*)(self+8);
    if (!ecx8) return;
    void** vt=*(void***)ecx8;
    typedef void (__thiscall *V1)(void*, u32);
    V1 v=(V1)vt[0x10/4];
    v((void*)ecx8, a9);
    ((C_458420*)(self+0x14))->fn_00458420(0);
    ((C_458420*)(self+0x20))->fn_00458420(0);
    *(u32*)(self+0x10)=0;
    *(u32*)(self+0x1c)=0;
    *(u8*)(self+0x40)=1;
    if (!*(u32*)(self+8)) return;
    if ((u8)a4 != 1) return;
    u32 q=(u32)fn_004f77c0();
    u32 old=*(u32*)(self+0x28);
    if (old) {
        void** ov=*(void***)old;
        void (__thiscall *vd)(void*,u32)=(void (__thiscall *)(void*,u32))ov[0];
        vd((void*)old,1);
    }
    C_4F79E0* p=(C_4F79E0*)q;
    void* r=p->fn_004f79e0((void*)0xc1eb74);
    *(u32*)(self+0x28)=(u32)r;
    if (r) ((C_4F2750*)r)->fn_004f2750((void*)0xc1eb90);
    void* mem=fn_00413660(0xa0);
    if (mem) ((C_468D00*)mem)->fn_00468d00((void*)*(u32*)(self+8));
}

// FUNCTION: DAO 0x0045b000
void* fn_0005b000(void)
{
    return (void*)0xc1ec00;
}

// FUNCTION: DAO 0x005279d0
void C_5279D0::fn_005279d0(u32 a1,u32 a2,u32 a3,u32 a4,u32 a5,u32 a6,u32 a7,u32 a8,u32 a9,u32 a10,u32 a11,u32 a12,u32 a13,u32 a14,u32 a15,u32 a16)
{
    char* self=(char*)this;
    char tmp[32];
    ((C_4C2510*)tmp)->fn_004c2510((void*)(self+0x18));
    *(u32*)(self+0x1c)=a10;
    *(u32*)(self+0x20)=a11;
    *(u32*)(self+0x24)=a12;
    *(u32*)(self+0x28)=a13;
    *(u32*)(self+0x2c)=a8;
    *(u32*)(self+0x30)=a9;
    *(u32*)(self+0x34)=a14;
    *(u8*)(self+0x38)=(u8)a15;
    *(u32*)(self+0x3c)=a16;
    ((C_4C0DB0*)tmp)->fn_004c0db0();
}

// FUNCTION: DAO 0x00645fc0
bool C_245FC0::fn_00245fc0()
{
    char* self=(char*)this;
    if (*(u32*)(self+0x2c) == 0) {
        char a[32];
        ((C_4C2480*)a)->fn_004c2480((void*)0xadfbe8);
        void* p=fn_004c0010(a);
        ((C_4CA8D0*)p)->fn_004ca8d0();
        ((C_4C0DB0*)a)->fn_004c0db0();
        return false;
    }
    char b[32];
    ((C_4C2480*)b)->fn_004c2480((void*)0xadfbe8);
    void* q=fn_004c0010(b);
    void* r=((C_4CA8D0*)q)->fn_004ca8d0();
    ((C_4C0DB0*)b)->fn_004c0db0();
    return fn_004c9010(r,1);
}

// FUNCTION: DAO 0x007f3120
void C_7F3120::fn_003f3120()
{
    C_45A500* p = *(C_45A500**)((char*)this + 0x1c);
    if (p) p->fn_0005a500();
}

// FUNCTION: DAO 0x007f3ab0
void C_7F3AB0::fn_003f3ab0(void* arg)
{
    char* self=(char*)this;
    char t1[64];
    ((C_4C4140*)t1)->fn_004c4140((void*)0xb21950);
    if (g_c327ec != 0) {
        C_5D57C0* g=(C_5D57C0*)g_c327ec;
        if (g->fn_005d57c0()) {
            if (*(u32*)((char*)g+0x14c) != 0) {
                char t2[64];
                if (arg) {
                    ((C_4C2AD0*)t2)->fn_004c2ad0(arg);
                } else {
                    void* p=*(void**)((char*)g+0x14c);
                    ((C_4C2AB0*)t2)->fn_004c2ab0((void*)((char*)p+0x18));
                }
                char t3[64];
                ((C_4C4140*)t3)->fn_004c4140((void*)0xb21ca4);
                ((C_4C36A0*)t2)->fn_004c36a0(t3);
                ((C_4C0DB0*)t3)->fn_004c0db0();
                if (*(u32*)(self+0x1c) != 0 && *(u32*)(self+0xd40) != 0) {
                    char t4[64];
                    ((C_4C0D90*)t4)->fn_004c0d90();
                    char t5[64];
                    ((C_4C2480*)t5)->fn_004c2480((void*)0xadfbe8);
                    char obj[128];
                    ((C_5279D0*)obj)->fn_005279d0(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
                    ((C_45A4F0*)(*(void**)(self+0x1c)))->fn_0045a4f0(obj);
                    ((C_4C0DB0*)t5)->fn_004c0db0();
                    ((C_4C0DB0*)t4)->fn_004c0db0();
                }
                ((C_4C0DB0*)t2)->fn_004c0db0();
            }
        }
    }
    ((C_4C0DB0*)t1)->fn_004c0db0();
}
