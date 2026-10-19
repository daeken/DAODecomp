typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

extern "C" int __cdecl fn_004e0e8b(void*, u32, const void*, u32);
extern "C" void* __cdecl fn_00422a40(void*);
extern "C" void __cdecl fn_00491690(void*, int, void*);
extern "C" int __cdecl fn_004e78e7(void*, void*, u32, int, void*);
extern "C" void __cdecl fn_00405eb0(void*, u32, u32);
extern "C" void* __cdecl fn_004e98c0(void*);
extern "C" void* __cdecl fn_004e9710(void*);
extern "C" void __cdecl fn_00489550(void);
extern "C" void __cdecl fn_004136c0(void*);
extern "C" void __cdecl fn_0040d6e0(void*, void*);
extern "C" void __cdecl fn_00406880(void);
extern "C" void __cdecl fn_000f6eb0(void*, u32);
extern "C" void* __cdecl fn_0011f0d0(void*);
extern "C" void __cdecl fn_0000d610(void*, u32);
extern "C" void __cdecl fn_000c0d90(void*);
extern "C" void __cdecl fn_00088930(void*);
extern "C" void __cdecl fn_0000d670(void*, u32);
extern "C" void __cdecl fn_000cb280(void*, u32, u32);
extern "C" void __cdecl fn_0044a7d0(void*, u32);
extern "C" int __cdecl fn_004e8168(void*, void*, void*, int, int);

extern "C" int g_00c3eee0;
extern "C" unsigned char g_00c15c50[];

// FUNCTION: DAO 0x00403A60
extern "C" void* __cdecl fn_00003a60(void* dst, u32 dstCount, const void* src, u32 srcCount) {
    fn_004e0e8b(dst, dstCount * 2, src, srcCount * 2);
    return dst;
}

struct C_0040ADE0 {
    unsigned char* __thiscall fn_0000ade0(u32, u32);
};

// FUNCTION: DAO 0x0040ADE0
unsigned char* __thiscall C_0040ADE0::fn_0000ade0(u32 a, u32 b) {
    (void)a; (void)b;
    unsigned char* self = (unsigned char*)this;
    void* node = fn_00422a40(self + 4);
    *(u32*)(self + 8) = (u32)node;
    *(u32*)(self + 12) = 0;
    u32 local = 0;
    fn_00491690(self + 0x10, 9, &local);
    *(u32*)(self + 0x20) = 1;
    *(u32*)(self + 0x24) = 1;
    return self;
}

// FUNCTION: DAO 0x004C0330
extern "C" int __cdecl fn_000c0330(void* dst, u32 max, const void* fmt, ...) {
    void* args = (void*)((char*)(void*)&fmt + sizeof(fmt));
    return fn_004e78e7(dst, (void*)0, max, 0, args);
}

struct C_004C1A30 {
    unsigned char* __thiscall fn_000c1a30(u32, u32, u32, u32, const void*);
};

// FUNCTION: DAO 0x004C1A30
unsigned char* __thiscall C_004C1A30::fn_000c1a30(u32 a, u32 b, u32 c, u32 d, const void* src) {
    (void)a; (void)b; (void)d;
    unsigned char* self = (unsigned char*)this;
    u32 len = *(u32*)(self + 0x14);
    u32 cap = *(u32*)(self + 0x18);
    u32 need = len + c;
    if (cap < need) fn_00405eb0(self, need, len);
    cap = *(u32*)(self + 0x18);
    u16* buf = (cap >= 8) ? *(u16**)(self + 4) : (u16*)(self + 4);
    if (src && c) fn_004e0e8b(buf + len, (cap - len) * 2, src, c * 2);
    *(u32*)(self + 0x14) = need;
    if (*(u32*)(self + 0x18) >= 8) {
        u16* p = *(u16**)(self + 4);
        p[need] = 0;
    } else {
        ((u16*)(self + 4))[need] = 0;
    }
    return self;
}

struct C_004C5080 {
    unsigned char* __thiscall fn_000c5080(void);
};

// FUNCTION: DAO 0x004C5080
unsigned char* __thiscall C_004C5080::fn_000c5080(void) {
    unsigned char* self = (unsigned char*)this;
    fn_004e98c0(self);
    fn_004e9710(self + 8);
    *(void**)self = (void*)0xaf03e4;
    *(void**)(self + 8) = (void*)0xaf03d4;
    return self;
}

// FUNCTION: DAO 0x004E2820
extern "C" void __cdecl fn_000e2820(void) {
    fn_00489550();
}

struct C_00573ED0 {
    void __thiscall fn_00173ed0(void);
};

// FUNCTION: DAO 0x00573ED0
void __thiscall C_00573ED0::fn_00173ed0(void) {
    unsigned char* self = (unsigned char*)this;
    u32* head = *(u32**)(self + 4);
    u32* first = (u32*)*head;
    *head = (u32)head;
    head[1] = (u32)head;
    *(u32*)(self + 8) = 0;
    while (first != head) {
        u32* next = (u32*)*first;
        fn_004136c0(first);
        first = next;
    }
    fn_004136c0(head);
    *(u32*)(self + 4) = 0;
}

struct C_005C5C20 {
    unsigned char* __thiscall fn_001c5c20(void*);
};

// FUNCTION: DAO 0x005C5C20
unsigned char* __thiscall C_005C5C20::fn_001c5c20(void* arg) {
    unsigned char* self = (unsigned char*)this;
    *(void**)self = (void*)0xaddcfc;
    fn_0040d6e0(self + 0x0c, arg);
    *(u32*)(self + 8) = 0;
    *(void**)(self + 4) = (void*)0xade300;
    *(void**)self = (void*)0xaffb64;
    *(void**)(self + 4) = (void*)0xaffb50;
    return self;
}

// FUNCTION: DAO 0x00645A50
extern "C" void __cdecl fn_00245a50(void) {
    fn_00406880();
}

struct C_00843F90 {
    unsigned char* __thiscall fn_00443f90(void);
};

// FUNCTION: DAO 0x00843F90
unsigned char* __thiscall C_00843F90::fn_00443f90(void) {
    unsigned char* self = (unsigned char*)this;
    *(void**)self = (void*)0xb2b174;
    fn_000f6eb0(self + 4, 0);
    void* n1 = fn_0011f0d0(self + 0x30);
    *(u32*)(self + 0x34) = (u32)n1;
    *((u8*)n1 + 0x15) = 1;
    ((u32*)n1)[1] = (u32)n1;
    ((u32*)n1)[0] = (u32)n1;
    ((u32*)n1)[2] = (u32)n1;
    *(u32*)(self + 0x38) = 0;
    *(u32*)(self + 0x40) = 0;
    void* n2 = fn_0011f0d0(self + 0x44);
    *(u32*)(self + 0x48) = (u32)n2;
    *((u8*)n2 + 0x15) = 1;
    ((u32*)n2)[1] = (u32)n2;
    ((u32*)n2)[0] = (u32)n2;
    ((u32*)n2)[2] = (u32)n2;
    *(u32*)(self + 0x4c) = 0;
    *(u32*)(self + 0x54) = 0;
    fn_0000d610(self + 0x58, 0);
    fn_0000d610(self + 0x68, 0);
    u8 tmp[0x1c];
    fn_000c0d90(tmp);
    fn_00088930(self + 0x80);
    fn_0000d670(self + 0xac, 0);
    fn_0000d670(self + 0xbc, 0);
    fn_0000d670(self + 0xcc, 0);
    fn_0000d610(self + 0xdc, 0);
    fn_000c0d90(self + 0xf8);
    fn_000cb280(self + 0x118, 1, 0);
    *(u8*)(self + 0xec) = 0;
    *(u8*)(self + 0xee) = 0;
    *(u8*)(self + 0xed) = 0;
    *(u32*)(self + 0xf0) = 0;
    *(u32*)(self + 0xf4) = 0;
    *(u8*)(self + 0x138) = 0;
    *(u32*)(self + 0x114) = 0;
    *(u32*)(self + 0x13c) = 0;
    *(u8*)(self + 0x140) = 0;
    return self;
}

struct C_0084D7E0 {
    unsigned char* __thiscall fn_0044d7e0(void);
};

// FUNCTION: DAO 0x0084D7E0
unsigned char* __thiscall C_0084D7E0::fn_0044d7e0(void) {
    unsigned char* self = (unsigned char*)this;
    *(void**)self = (void*)0xb2b4ec;
    *(u8*)(self + 4) = 0;
    *(u8*)(self + 5) = 0;
    fn_0044a7d0(self + 8, 0);
    fn_0000d610(self + 0x50, 0);
    fn_0044a7d0(self + 0x60, 0);
    fn_000cb280(self + 0xa8, 1, 0);
    *(u8*)(self + 0xc8) = 0;
    return self;
}

// FUNCTION: DAO 0x008E8388
extern "C" unsigned long __cdecl fn_004e8388(void* s, void* end, int radix) {
    void* flag = (g_00c3eee0 != 0) ? (void*)g_00c15c50 : (void*)0;
    return (unsigned long)fn_004e8168(flag, s, end, radix, 1);
}
