typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

struct C_50c670 { u8 raw[0x40]; };
struct C_50cf00 { u8 raw[0x20]; };
struct C_50d8f0 { u8 raw[0x40]; };
struct C_50d9b0 { u8 raw[0x20]; };

void __fastcall fn_0010c310(void*);
void fn_000136c0(void*);
void __fastcall fn_00134a70(void*, void*, void*);
void __fastcall fn_0000d610(void*, void*, void*);
void fn_00455cf0(void*, void*);
void fn_004528a0(void*, void*);
void fn_004528d0(void*, void*, void*);
void fn_004528f0(void*, void*);
void __fastcall fn_0041eeb0(void*, void*, void*);
void __fastcall fn_0006c760(void*);
void __fastcall fn_00138f30(void*);
void* __fastcall fn_000621c0(void*);
void __fastcall fn_000f71a0(void*, void*, void*);
void __fastcall fn_00058420(void*, void*, void*);
void __fastcall fn_000c2510(void*, void*, void*);
void* fn_00467e30(void);
void __fastcall fn_000c1270(void*, void*, void*, int, int);
void fn_004e11f2(void);
extern u32 g_00c31260;

// FUNCTION: DAO 0x50C650
void* __fastcall fn_0010c650(void* self, void*, u32 flags) {
    fn_0010c310(self);
    if (flags & 1) fn_000136c0(self);
    return self;
}

// FUNCTION: DAO 0x50C670
void* __fastcall fn_0010c670(void* selfRaw, void*, void* arg) {
    C_50c670* self = (C_50c670*)selfRaw;
    *(void**)self->raw = (void*)0xaf4e28;
    fn_00134a70(self->raw + 4, 0, 0);
    fn_0000d610(self->raw + 0x10, 0, 0);
    self->raw[0x0c] = 0;
    fn_0000d610(self->raw + 0x2c, 0, 0);
    self->raw[0x20] = 0;
    self->raw[0x28] = 0;
    typedef void* (__fastcall *VFn8)(void*);
    void** vt = *(void***)arg;
    void* res = ((VFn8)vt[2])(arg);
    *(void**)(self->raw + 0x24) = res;
    fn_00455cf0(res, 0);
    fn_004528a0(res, self);
    fn_004528d0(res, (void*)0x8523f0, (void*)0x5076e0);
    fn_004528f0(res, (void*)0x472490);
    return self;
}

// FUNCTION: DAO 0x50C740
void __fastcall fn_0010c740(void* selfRaw, void*) {
    C_50c670* self = (C_50c670*)selfRaw;
    *(void**)self->raw = (void*)0xaf4e28;
    fn_0041eeb0(self->raw + 0x2c, 0, 0);
    fn_0006c760(self->raw + 0x2c);
    fn_0006c760(self->raw + 0x10);
    fn_00138f30(self->raw + 4);
    *(void**)self->raw = (void*)0xae8490;
}

// FUNCTION: DAO 0x50C7C0
void* __fastcall fn_0010c7c0(void* self, void*, u32 flags) {
    fn_0010c740(self, 0);
    if (flags & 1) fn_000136c0(self);
    return self;
}

// FUNCTION: DAO 0x50CF00
void* __fastcall fn_0010cf00(void* selfRaw, void*, void* arg) {
    C_50cf00* self = (C_50cf00*)selfRaw;
    if (self->raw[0x0c] == 0) {
        fn_00134a70(arg, 0, 0);
        return arg;
    }
    void* p4 = self->raw + 4;
    if (*(void**)p4 != 0) {
        void* obj = fn_000621c0(p4);
        void** vt = *(void***)obj;
        ((void (__fastcall *)(void*))vt[0x0c])(obj);
    }
    u8 temp[0x40];
    fn_000f71a0(temp, 0, p4);
    fn_00058420(p4, 0, 0);
    self->raw[0x0c] = 0;
    fn_000f71a0(arg, 0, temp);
    fn_00138f30(temp);
    return arg;
}

// FUNCTION: DAO 0x50D8F0
void* __fastcall fn_0010d8f0(void* selfRaw, void*, void* arg1, void* arg2) {
    C_50d8f0* self = (C_50d8f0*)selfRaw;
    *(void**)self->raw = (void*)0xaf404c;
    fn_000c2510(self->raw + 4, 0, arg1);
    self->raw[0x28] = 1;
    *(u32*)(self->raw + 0x2c) = g_00c31260;
    g_00c31260 += 1;
    void* obj = fn_00467e30();
    void** vt = *(void***)obj;
    void* res = ((void* (__fastcall *)(void*))vt[7])(obj);
    *(void**)(self->raw + 0x20) = res;
    return self;
}

// FUNCTION: DAO 0x50D9B0
void* __fastcall fn_0010d9b0(void* selfRaw, void*) {
    C_50d9b0* self = (C_50d9b0*)selfRaw;
    u8* begin = *(u8**)(self->raw + 4);
    u8* end = *(u8**)(self->raw + 8);
    if (!begin) return (void*)0xbf5e30;
    u32 diff = (u32)(end - begin);
    if (diff / 0x1c == 0) return (void*)0xbf5e30;
    if (begin > end) fn_004e11f2();
    u8* last = end - 0x1c;
    if (last > *(u8**)(self->raw + 8)) fn_004e11f2();
    if (last < *(u8**)(self->raw + 4)) fn_004e11f2();
    return last;
}

// FUNCTION: DAO 0x50DA20
void fn_0010da20(void* first, void* last) {
    u8* p = (u8*)first;
    u8* e = (u8*)last;
    while (p != e) {
        if (*(u32*)(p + 0x18) >= 8) fn_000136c0(*(void**)(p + 4));
        *(u32*)(p + 0x18) = 7;
        *(u32*)(p + 0x14) = 0;
        *(u16*)(p + 4) = 0;
        p += 0x1c;
    }
}

// FUNCTION: DAO 0x50DA60
void* fn_0010da60(void* first, void* last, void* dest) {
    u8* s = (u8*)first;
    u8* e = (u8*)last;
    u8* d = (u8*)dest;
    while (s != e) {
        fn_000c1270(d, 0, s, 0, -1);
        s += 0x1c;
        d += 0x1c;
    }
    return d;
}

// FUNCTION: DAO 0x50DAA0
void fn_0010daa0(void* dest, u32 count, void* source) {
    u8* d = (u8*)dest;
    while (count != 0) {
        *(u32*)(d + 0x18) = 7;
        *(u32*)(d + 0x14) = 0;
        *(u16*)(d + 4) = 0;
        fn_000c1270(d, 0, source, 0, -1);
        d += 0x1c;
        count -= 1;
    }
}

// FUNCTION: DAO 0x50DB60
void* fn_0010db60(void* first, void* last, void* dest, void*) {
    fn_0010da60(first, last, dest);
    return (u8*)dest + ((u8*)last - (u8*)first);
}

// FUNCTION: DAO 0x50DBE0
void fn_0010dbe0(void* first, void* last, void* arg) {
    u8* p = (u8*)first;
    u8* e = (u8*)last;
    while (p != e) {
        fn_000c1270(p, 0, arg, 0, -1);
        p += 0x1c;
    }
}
