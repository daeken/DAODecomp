typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

int fn_000c0d90(...);
int fn_000e4990(...);
int fn_000c2ab0(...);
int fn_00438210(...);
int fn_000c2510(...);
int fn_000c3030(...);
int fn_000c0db0(...);
int fn_000c2ad0(...);
int fn_004e1613(...);
int fn_004e11f2(...);
void* fn_00013660(unsigned int);
int fn_00001670(...);
int fn_000019d0(...);
int fn_004e1202(...);
int fn_003d6ff0(...);
int fn_0047cc80(...);
int fn_0027ba40(...);
int fn_000bbe60(...);
int fn_0040e140(...);
int fn_0047cec0(...);
int fn_004e18c1(...);
int fn_004efedf(...);
int fn_004ecad8(...);
int fn_004e8ea0(...);
int fn_004e47aa(...);
int fn_004e19e0(...);
int fn_004eac58(...);
int fn_0050026c(...);
int fn_005002b3(...);
int fn_004e1a5a(...);

extern unsigned int g_00815234;
extern unsigned int g_0081D08C;
extern unsigned int g_00832938;
extern unsigned int g_0083F954;
extern unsigned int g_007190A4;
extern int (*g_006DA228)(...);
extern int (*g_006DA148)(...);
extern int (*g_006DA0D8)(...);
extern int (*g_006DA224)(...);

struct C_d1d50 { void fn_000d1d50(); };
struct C_d4f60 { void fn_003d4f60(unsigned int n); };
struct C_d7b80 { C_d7b80* fn_003d7b80(C_d7b80* other); };
struct C_d80be0 { int fn_00480be0(void* other); };
struct C_d7b840 { void* fn_0047b840(void* key); };
struct C_d7d090 { void* fn_0047d090(void* a, void* b, void* c, void* d); };
struct C_d80c00 { int fn_00480c00(void* other); };
struct C_d80f10 { void fn_00480f10(void* key, void* out); };

// FUNCTION: DAO 0x004d1d50
void C_d1d50::fn_000d1d50()
{
    u8* self = (u8*)this;
    u8 tmp[0x40];
    fn_000c0d90(tmp);
    if (g_0081D08C != 0) {
        u8* eax = (u8*)g_0081D08C;
        eax[0x1c] = self[0x24];
        void* edi = *(void**)(self + 4);
        int ok = fn_000e4990(edi, tmp, (void*)0);
        if (ok != 0) {
            fn_000c2ab0(self + 8, tmp);
            if (g_00832938 != 0) {
                int al = fn_00438210((u8*)g_00832938 + 0x674);
                if (al != 0) {
                    void* eax2 = *(void**)(self + 4);
                    if (eax2 != (void*)-1 && eax2 != 0 && *(u32*)(self + 0x1c) != 0) {
                        u8 tmp2[0x20];
                        fn_000c2510(tmp2, self + 8);
                        void* p = tmp2;
                        if (*(u32*)(tmp2 + 0x14) >= 8) p = *(void**)(tmp2 + 0x0c);
                        fn_000c3030(self + 8, (void*)0x00af0db0, eax2, p);
                        fn_000c0db0(tmp2);
                        self[0] = 1;
                        self[0x25] = 1;
                    }
                }
            }
        }
    } else {
        fn_000c2ad0(self + 8, (void*)0x00adef14);
        self[0] = 0;
        self[0x25] = 0;
    }
    fn_000c0db0(tmp);
    fn_004e1613(0);
}

// FUNCTION: DAO 0x00504500
void __cdecl fn_00104500(void* p1, void* p2, void* p3, void* p4, void* p5)
{
    u32* first = (u32*)p2;
    u32* last = (u32*)p3;
    u32* dest = (u32*)p4;
    u32* alloc = (u32*)p5;
    u32* out = (u32*)p3;
    if (first != last) {
        u32* cur = first;
        while (cur != last) {
            if (dest == 0) fn_004e11f2();
            if (dest < (u32*)((u8*)alloc + 8)) fn_004e11f2();
            *dest = *cur;
            cur++;
            dest++;
        }
        out[0] = (u32)alloc;
        out[1] = (u32)dest;
    }
}

// FUNCTION: DAO 0x00538a00
void* __stdcall fn_00138a00(void* a, void* b, void* c)
{
    u8* p = (u8*)fn_00013660(0xc);
    if (p != 0) {
        *(void**)p = a;
        *(void**)(p + 4) = b;
        if (c != 0) *(void**)(p + 8) = *(void**)c;
        else *(void**)(p + 8) = 0;
    }
    return p;
}

// FUNCTION: DAO 0x007d4f60
void C_d4f60::fn_003d4f60(unsigned int n)
{
    u8* self = (u8*)this;
    u32 cur = *(u32*)(self + 8);
    if (0x3fffffff - cur < n) {
        u8 tmp[0x40];
        fn_00001670(tmp, (void*)0x00aded54, (void*)0x10);
        fn_000019d0(&tmp[0x10], &tmp[0], (void*)0x00b93184);
        fn_004e1202((void*)0x00b93184, tmp);
    } else {
        *(u32*)(self + 8) = cur + n;
    }
}

// FUNCTION: DAO 0x007d7b80
C_d7b80* C_d7b80::fn_003d7b80(C_d7b80* other)
{
    fn_003d6ff0(this, other);
    *(u32*)((u8*)this + 0xc) = *(u32*)((u8*)other + 0xc);
    return this;
}

// FUNCTION: DAO 0x0087b840
void* C_d7b840::fn_0047b840(void* key)
{
    u8* self = (u8*)this;
    u8* eax = *(u8**)(self + 4);
    u8* esi = *(u8**)(eax + 4);
    u8* edi = eax;
    if (esi[0x25] == 0) {
        while (esi[0x25] == 0) {
            int al = ((C_d80be0*)(esi + 0xc))->fn_00480be0(key);
            if (al != 0) {
                esi = *(u8**)(esi + 8);
            } else {
                edi = esi;
                esi = *(u8**)esi;
            }
        }
    }
    return edi;
}

// FUNCTION: DAO 0x0087d090
void* C_d7d090::fn_0047d090(void* a, void* b, void* c, void* d)
{
    u8* self = (u8*)this;
    u8* ap = (u8*)a;
    u8* bp = (u8*)b;
    u8* cp = (u8*)c;
    u8* dp = (u8*)d;
    if (*(u32*)(self + 8) == 0) {
        fn_0047cc80(self, ap, bp, (void*)1, cp, dp);
        return cp;
    }
    u8* edx = *(u8**)(self + 4);
    u8* edi = *(u8**)edx;
    u8* ebp = ap;
    u8* ebx = bp;
    if (ebp != 0 && ebp != self) fn_004e11f2();
    if (ebx != edi) {
        if (((C_d80be0*)(ebx + 0xc))->fn_00480be0(cp)) {
            fn_0047cc80(self, ebx, edi, (void*)0, cp, dp);
            return cp;
        }
    } else {
        if (((C_d80be0*)(ebx + 0xc))->fn_00480be0(cp)) {
            fn_0047cc80(self, edi, ebx, (void*)1, cp, dp);
            return cp;
        }
    }
    u8 local[0x20];
    *(void**)local = ebp;
    *(void**)(local + 4) = ebx;
    fn_0027ba40(local);
    if (((C_d80be0*)(*(u8**)(local + 4) + 0xc))->fn_00480be0(cp)) {
        fn_0047cc80(self, ebp, ebx, (void*)0, cp, dp);
        return cp;
    }
    if (*(u8*)(*(u8**)(*(u8**)(local + 4) + 8) + 0x25) == 0) {
        fn_0047cc80(self, ebp, *(void**)(local + 4), (void*)0, cp, dp);
        return cp;
    }
    u8 tmp2[0x20];
    *(void**)tmp2 = ebp;
    *(void**)(tmp2 + 4) = ebx;
    *(void**)(tmp2 + 8) = *(void**)(self + 4);
    *(void**)(tmp2 + 0xc) = self;
    fn_000bbe60(tmp2);
    if (fn_0040e140(tmp2, local)) {
        if (((C_d80be0*)(*(u8**)(local + 4) + 0xc))->fn_00480be0(cp)) {
            fn_0047cc80(self, ebp, *(void**)(local + 4), (void*)1, cp, dp);
            return cp;
        }
    } else {
        if (((C_d80be0*)(*(u8**)(local + 4) + 0xc))->fn_00480be0(cp)) {
            fn_0047cc80(self, *(void**)(local + 4), ebx, (void*)0, cp, dp);
            return cp;
        }
    }
    fn_0047cec0(self, local, cp);
    return cp;
}

// FUNCTION: DAO 0x00880be0
int C_d80be0::fn_00480be0(void* other)
{
    u32 a = *(u32*)this;
    u32 b = *(u32*)other;
    if (a != b) return 0;
    u32 c = *(u32*)((u8*)this + 4);
    u32 d = *(u32*)((u8*)other + 4);
    return (c < d) ? 1 : 0;
}

// FUNCTION: DAO 0x00880c00
int C_d80c00::fn_00480c00(void* other)
{
    return (*(u32*)this == *(u32*)other && *(u32*)((u8*)this + 4) == *(u32*)((u8*)other + 4)) ? 1 : 0;
}

// FUNCTION: DAO 0x00880f10
void C_d80f10::fn_00480f10(void* key, void* out)
{
    u8* self = (u8*)this;
    u8* edx = *(u8**)(self + 4);
    u8* eax = *(u8**)(edx + 4);
    u8* edi = (u8*)key;
    while (eax[0x39] == 0) {
        u32 k = *(u32*)edi;
        if (*(u32*)(eax + 0xc) < k) {
            eax = *(u8**)(eax + 8);
        } else {
            edx = eax;
            eax = *(u8**)eax;
        }
    }
    u8* chosen = edx;
    u8* chosen2 = eax;
    if (edx != *(u8**)(self + 4)) {
        u32 k = *(u32*)edi;
        if (k >= *(u32*)(edx + 0xc)) {
            chosen = edx;
            chosen2 = eax;
        } else {
            u8 local[8];
            *(u32*)(local + 0) = (u32)self;
            *(u32*)(local + 4) = (u32)edx;
            chosen = *(u8**)local;
            chosen2 = *(u8**)(local + 4);
        }
    }
    *(u32*)out = (u32)chosen;
    *(u32*)((u8*)out + 4) = (u32)chosen2;
}

// FUNCTION: DAO 0x008f8750
unsigned short __cdecl fn_004f8750(unsigned short c, void* locale)
{
    if (c == 0xffff) return c;
    u8 tmp[0x20];
    fn_004e18c1(tmp, locale);
    u8* loc = *(u8**)tmp;
    u32 v = *(u32*)(loc + 0x14);
    if (v == 0) {
        if ((u16)(c - 0x41) <= 0x19) c += 0x20;
        return c;
    }
    if (c < 0x100) {
        int ok = fn_004efedf((void*)(unsigned int)c, (void*)1, tmp);
        if (ok != 0) {
            u8* table = *(u8**)(*(u8**)tmp + 0xcc);
            return (unsigned short)table[c];
        }
        return c;
    }
    unsigned short out = c;
    fn_004ecad8(tmp, (void*)0, (void*)0, &out, (void*)1, (void*)1, tmp, *(void**)(loc + 4));
    if (*(u8*)(tmp + 0x14) != 0) {
        u8* ecx = *(u8**)(tmp + 0x0c);
        *(u32*)(ecx + 0x70) &= 0xfffffffd;
    }
    return out;
}

// FUNCTION: DAO 0x00900465
int __cdecl fn_00500465(void* p1, unsigned int p2, char* p3, int p4, unsigned short* p5, int p6, int p7, int p8)
{
    u8* ebp8 = (u8*)p1;
    unsigned int ebp0c = p2;
    char* ebp10 = p3;
    int ebp14 = p4;
    unsigned short* ebp18 = p5;
    int ebp1c = p6;
    int ebp20 = p7;
    int ebp24 = p8;
    if (*(u16*)ebp8 == 0xffff) return 0;
    u8 tmp[0x40];
    fn_004e18c1(tmp, (void*)ebp0c);
    u8* loc = *(u8**)tmp;
    if (*(u32*)(loc + 0x14) == 0) {
        u16 c = *(u16*)ebp8;
        if ((u16)(c - 0x41) <= 0x19) c += 0x20;
        return c;
    }
    if (g_0083F954 == 0) {
        u8 tmp2[4];
        if (g_006DA228((void*)0x007190A4, (void*)1, tmp2) != 0) {
            g_0083F954 = 1;
        } else if (g_006DA148() == 0x78) {
            g_0083F954 = 2;
        } else {
            g_0083F954 = 0;
        }
    }
    if (g_0083F954 == 1) {
        if (ebp20 == 0) ebp18 = (unsigned short*)(*(u8**)(ebp8) + 4);
        int ok = g_006DA0D8(ebp18, ebp14, ebp10, ebp0c, ebp20, ebp1c);
        if (ok == 0) return 0;
        if (ok > 0 && ok <= 0x7ffffff0) {
            u8* buf;
            unsigned int sz = (unsigned int)(ok + ok + 8);
            if (sz > 0x400) buf = (u8*)fn_004e47aa(sz);
            else buf = (u8*)fn_004e8ea0(sz);
            if (buf == 0) return 0;
            *(u32*)buf = 0xcccc;
            buf += 8;
            fn_004e19e0(buf, (void*)0, (void*)(ok + ok));
            int ok2 = g_006DA0D8(buf, ok, ebp10, ebp0c, 1, ebp1c);
            if (ok2 != 0) {
                int r = g_006DA228(buf, ok2, ebp14, ebp20);
                fn_004eac58(buf);
                return r;
            }
            fn_004eac58(buf);
            return 0;
        }
    } else if (g_0083F954 == 2 || g_0083F954 == 0) {
        if (ebp1c == 0) ebp1c = *(int*)(*(u8**)ebp8 + 0x14);
        if (ebp18 == 0) ebp18 = (unsigned short*)(*(u8**)(ebp8) + 4);
        int r = fn_0050026c(ebp1c);
        if (r == -1) return 0;
        if (r != (int)(unsigned int)ebp18) {
            int s = fn_005002b3((void*)ebp0c, ebp10, &ebp10, (void*)r, ebp18, (void*)0);
            if (s == 0) return 0;
            ebp10 = (char*)s;
        }
        int res = g_006DA224(ebp8, ebp0c, ebp10, ebp14, ebp18, ebp1c);
        if (ebp10 != 0) fn_004e1a5a(ebp10);
        fn_004e1613(0);
        return res;
    }
    fn_004e1613(0);
    return 0;
}
