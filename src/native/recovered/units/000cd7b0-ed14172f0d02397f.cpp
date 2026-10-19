typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;
typedef float f32;

extern u32 g_00815234;
extern void* g_008327ec;
extern void* g_0081d090;
extern u32 g_008021c4;
extern f32 g_006e7104;
extern u8 g_006de368[];
extern u8 g_006feb60[];
extern u8 g_006feb74[];
extern u8 g_006feb2c[];
extern u8 g_007004e0[];
extern u8 g_0067adac[];

extern int fn_00006030(...);
extern int fn_00008280(...);
extern int fn_00008320(...);
extern int fn_0001e870(...);
extern int fn_000799e0(...);
extern int fn_000c0d90(...);
extern int fn_000c0db0(...);
extern int fn_000c0e80(...);
extern int fn_000c2480(...);
extern int fn_000c2510(...);
extern int fn_000c2ab0(...);
extern int fn_000c31a0(...);
extern int fn_000c3360(...);
extern int fn_000c36c0(...);
extern int fn_000c4140(...);
extern int fn_000c8f60(...);
extern int fn_000c8f90(...);
extern int fn_000c9a90(...);
extern int fn_000cd6c0(...);
extern int fn_000da0c0(...);
extern int fn_000db5b0(...);
extern int fn_000df580(...);
extern int fn_001389f0(...);
extern int fn_001b7540(...);
extern int fn_001b9020(...);
extern int fn_001ba100(...);
extern int fn_001bc7f0(...);
extern int fn_001d4fc0(...);
extern int fn_001d5540(...);
extern int fn_001d7080(...);
extern int fn_001fe630(...);
extern int fn_00240070(...);
extern int fn_002402f0(...);
extern int fn_00242ef0(...);
extern int fn_0024ba50(...);
extern int fn_002931e0(...);
extern int fn_00293290(...);
extern int fn_0029d2e0(...);
extern int fn_002ed770(...);
extern int fn_002fcae0(...);
extern int fn_002fe900(...);
extern int fn_002fefa0(...);
extern int fn_00300fe0(...);
extern int fn_00305a70(...);
extern int fn_00438210(...);
extern int fn_004e1613(...);
extern int fn_00629f40(...);
extern int fn_006582c0(...);

struct C_5d6740 { void fn_001d6740(u32, u8); };
struct C_5fec00 { void fn_001fec00(); };
struct C_642bd0 { bool fn_00242bd0(); };
struct C_694ce0 { void fn_00294ce0(void*); };
struct C_6cb330 { bool fn_002cb330(float); };

// FUNCTION: DAO 0x004c9b10
u8 fn_000c9b10(void* a0, u32 a1, u32 a2, u32 a3, u32 a4) {
    u8 objA[0x100];
    u8 objB[0x100];
    u8 objC[0x100];
    u8 objD[0x100];
    u8 objE[0x100];
    u32 flag = 0;
    u8 result = 0;
    fn_000c0d90(objA);
    fn_000c0d90(objB);
    fn_00008280(objC);
    fn_001389f0(objD);
    fn_000c0d90(objE);
    fn_000c2510(objE, a0);
    fn_000c31a0(objE, 1, &flag);
    if (fn_000c0e80(objE, g_006de368)) {
        fn_000c36c0(objE, g_006de368);
    }
    fn_000c9a90(objA, objE, &flag);
    fn_001d7080(objE, &flag);
    fn_000c2ab0(objC, &flag);
    if (a1 == 1 && a2 == 1) {
        if (a3 == 1 && a4 == 1) {
            result = (u8)fn_000c9b10(objA, a1, a2, a3, a4);
        }
    } else {
        fn_000c3360(objE, objB, objA);
        result = (u8)fn_000c8f60(objB);
        fn_000c0db0(objB);
    }
    fn_000c0db0(objD);
    fn_000c0db0(objC);
    fn_000c8f90(objE, &flag);
    fn_00008320(objE);
    fn_00006030(objE, &flag);
    fn_000c0db0(objE);
    fn_004e1613((u32)result);
    return result;
}

// FUNCTION: DAO 0x004cd7b0
void fn_000cd7b0() {
    fn_000cd6c0();
}

// FUNCTION: DAO 0x005d6740
void C_5d6740::fn_001d6740(u32 a0, u8 a1) {
    u8* self = (u8*)this;
    u8 b = (u8)a0;
    u8 obj[0x100];
    u8* g = (u8*)g_008327ec;
    if ((u8)fn_00438210(self + 0xd8) == b) {
        return;
    }
    if (b == 0) {
        if (fn_001d4fc0(g) != 0) {
            u32* p = (u32*)fn_001d4fc0(g);
            if (p != 0 && p[0x498 / 4] != 0) {
                u8* q = (u8*)p[0x498 / 4];
                if (*(u32*)(q + 0x88) != 0 && *(u32*)(q + 0x9c) == 0x42d) {
                    fn_00293290(0, 0x42d);
                }
            }
        }
    }
    fn_001d5540(self, b);
    fn_002402f0(*(void**)(self + 0x114), b);
    if (b == 0) {
        fn_002931e0();
        return;
    }
    {
        u8* p = *(u8**)(self + 0x114);
        u32 mode = *(u32*)(p + 0x78);
        if (mode == 1 || mode == 0 || mode == 2 || mode == 4 || mode == 5) {
            fn_000c2480(obj, g_006feb60);
            fn_001b9020(obj, 0, 0);
            fn_000c0db0(obj);
        }
        if (mode == 3) {
            fn_000c2480(obj, g_006feb60);
            fn_001b9020(obj, 0);
            fn_001b7540(obj);
            fn_000c0db0(obj);
            fn_000c2480(obj, g_006feb74);
            fn_001b9020(obj, 0);
            fn_001b7540(obj);
            fn_000c0db0(obj);
            fn_000c2480(obj, g_006feb2c);
            fn_001b9020(obj, 0);
            fn_001b7540(obj);
            fn_000c0db0(obj);
        }
        if (mode == 5) {
            fn_000c2480(obj, g_007004e0);
            fn_001b9020(obj, 0);
            fn_001ba100(obj);
            fn_000c0db0(obj);
        }
    }
    {
        u32* vt = *(u32**)(self + 0xd8);
        ((void (__thiscall*)(void*, u32))vt[0x54 / 4])(self + 0xd8, (u32)b);
    }
    {
        u32* vt = *(u32**)(self + 0xe8);
        ((void (__thiscall*)(void*, u32))vt[0x54 / 4])(self + 0xe8, *(u32*)(self + 0xf8));
    }
    if (b != 0) {
        if (a1 != 0) {
            *(u32*)(self + 0xf8) = (u32)fn_0001e870();
        }
    } else {
        if (*(u32*)(self + 0xf8) != 0) {
            u32 now = (u32)fn_0001e870();
            *(u32*)(self + 0xfc) += now - *(u32*)(self + 0xf8);
        }
    }
}

// FUNCTION: DAO 0x005fec00
void C_5fec00::fn_001fec00() {
    u8* self = (u8*)this;
    u8 obj[0x100];
    u32 tmp = 0;
    u8* gp = (u8*)g_008327ec;
    fn_00242ef0(gp + 0x14c, &tmp);
    if (tmp == 0) {
        return;
    }
    fn_006582c0(self, &tmp);
    fn_000799e0(self + 0x230, 0x3e8e);
    if (*(u32*)(self + 0x2cc) != 0 && g_008327ec != 0) {
        u8* p = *(u8**)(self + 0x2cc);
        u32* vt = *(u32**)p;
        u8* q = (u8*)((int (__thiscall*)(void*))vt[0x10 / 4])(p);
        if (q != 0) {
            u32* vt2 = *(u32**)q;
            u8* r = (u8*)((int (__thiscall*)(void*))vt2[0xa0 / 4])(q);
            if (r != 0) {
                u8 b[0x50];
                for (u32 i = 0; i < 0x50; i++) b[i] = *(u8*)(p + 0x68 + i);
                fn_00629f40(b);
                fn_000c4140(obj, b);
                fn_000c2510(obj, r + 0x180);
                fn_000c0db0(obj);
            }
        }
        fn_000c0db0(obj);
    } else {
        fn_000c4140(obj, self + 0xd0);
        fn_000c2510(obj, self + 0x114);
        fn_001fe630(obj, self + 0x150, 0x42ce);
        fn_001fe630(obj, self + 0x160, 0x42cf);
        fn_000c0db0(obj);
    }
    fn_00240070(g_0081d090 ? *(void**)((u8*)g_0081d090 + 4) : 0, 0x120);
    fn_000df580();
    fn_000c0db0(obj);
    fn_000c0db0(obj);
    fn_0024ba50(*(void**)(gp + 0x1b0), &tmp);
    fn_002fefa0(&tmp);
    fn_002fe900();
    fn_002ed770(*(void**)(self + 0x490), &tmp);
    fn_00300fe0(*(void**)(self + 0x48c), &tmp);
    fn_002fcae0(*(void**)(self + 0x494), &tmp);
    fn_00305a70(self + 0x394, &tmp);
    fn_004e1613((u32)tmp);
}

// FUNCTION: DAO 0x00642bd0
bool C_642bd0::fn_00242bd0() {
    u8* self = (u8*)this;
    void* p = *(void**)(self + 0x10);
    if (p != 0) {
        fn_000db5b0(p);
        return false;
    }
    return true;
}

// FUNCTION: DAO 0x00694ce0
void C_694ce0::fn_00294ce0(void* src) {
    u8* self = (u8*)this;
    u32* s = (u32*)src;
    *(u32*)(self + 0x130) = s[0];
    *(u32*)(self + 0x134) = s[1];
    *(u32*)(self + 0x138) = s[2];
    *(u32*)(self + 0x13c) = s[3];
    {
        u32* vt = *(u32**)self;
        ((void (__thiscall*)(void*))vt[0x80 / 4])(self);
    }
}

// FUNCTION: DAO 0x006cb330
bool C_6cb330::fn_002cb330(float v) {
    u8* p = (u8*)this;
    float sum = v + *(float*)(p + 0x16c);
    *(float*)(p + 0x16c) = sum;
    if (sum > g_006e7104) {
        *(float*)(p + 0x16c) = 0.0f;
        return true;
    }
    return false;
}
