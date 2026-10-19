typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

struct C_000c0d90 { void __thiscall fn_000c0d90(); };
struct C_000c2ab0 { void __thiscall fn_000c2ab0(void*); };
struct C_00403c70 { void* __thiscall fn_00003c70(); };
struct C_004dffe1 { int locktype; void __thiscall fn_004dffe1(int); void __thiscall fn_004e0002(); };
struct C_004e03dd { void __thiscall fn_004e03dd(); };
struct C_004e11f2 { void __thiscall fn_004e11f2(); };
struct C_00003310 { void __thiscall fn_00003310(); };
struct C_000039f0 { void __thiscall fn_000039f0(); };
struct C_004e03c5 { void __thiscall fn_004e03c5(); };

void __cdecl fn_000136c0(void*);
void* __cdecl fn_00013660(u32);
void* __cdecl fn_004e023b();
void* __cdecl fn_004e006f();

struct C_00403480 { void* __thiscall fn_00003480(void*); };
struct C_00403570 { void* __thiscall fn_00003570(); };
struct C_004035c0 { void __thiscall fn_000035c0(); };
struct C_00403720 { void __thiscall fn_00003720(); };
struct C_00403790 { void __thiscall fn_00003790(); };
struct C_00403850 { u16 __thiscall fn_00003850(); };
struct C_00403900 { void* __thiscall fn_00003900(u32); };
struct C_00403990 { void __thiscall fn_00003990(); };
struct C_00403a90 { void* __thiscall fn_00003a90(u32); };
struct C_00403ab0 { void* __thiscall fn_00003ab0(u32); };
struct C_00403ad0 { int __thiscall fn_00003ad0(C_00403ad0*); };
struct C_00403b10 { void* __thiscall fn_00003b10(); };

// FUNCTION: DAO 0x00403480
void* __thiscall C_00403480::fn_00003480(void* param) {
    ((C_000c0d90*)param)->fn_000c0d90();
    void* p = ((C_00403c70*)this)->fn_00003c70();
    ((C_000c2ab0*)param)->fn_000c2ab0(p);
    return param;
}

// FUNCTION: DAO 0x00403570
void* __thiscall C_00403570::fn_00003570() {
    C_004dffe1 lock;
    lock.fn_004dffe1(0);
    u32 n = *(u32*)((char*)this + 4);
    if (n > 0u && n < 0xFFFFFFFFu) {
        *(u32*)((char*)this + 4) = n - 1u;
    }
    void* result = (*(u32*)((char*)this + 4) == 0u) ? (void*)this : 0;
    lock.fn_004e0002();
    return result;
}

// FUNCTION: DAO 0x004035C0
void __thiscall C_004035c0::fn_000035c0() {
    C_004dffe1 lock;
    void* edi = *(void**)this;
    if (!edi) return;
    lock.fn_004dffe1(0);
    u32 n = *(u32*)((char*)edi + 4);
    if (n > 0u && n < 0xFFFFFFFFu) {
        *(u32*)((char*)edi + 4) = n - 1u;
    }
    void* esi = (*(u32*)((char*)edi + 4) == 0u) ? edi : 0;
    lock.fn_004e0002();
    if (esi) {
        void** vt = *(void***)esi;
        typedef void (__thiscall *Dtor)(void*, int);
        ((Dtor)vt[0])(esi, 1);
    }
}

// FUNCTION: DAO 0x00403720
void __thiscall C_00403720::fn_00003720() {
    char* base = (char*)this;
    *(void**)(base + 0x20) = base + 0x18;
    *(void**)(base + 0x24) = base + 0x1c;
    *(void**)(base + 0x10) = base + 0x8;
    *(void**)(base + 0x30) = base + 0x28;
    char* q = base + 0xc;
    *(void**)(base + 0x14) = q;
    *(void**)(base + 0x34) = base + 0x2c;
    *(u32*)q = 0;
    *(u32*)(*(void**)(base + 0x24)) = 0;
    *(u32*)(*(void**)(base + 0x34)) = 0;
    *(u32*)(*(void**)(base + 0x10)) = 0;
    *(u32*)(*(void**)(base + 0x20)) = 0;
    *(u32*)(*(void**)(base + 0x30)) = 0;
}

// FUNCTION: DAO 0x00403790
void __thiscall C_00403790::fn_00003790() {
    C_004dffe1 lock;
    void* ebx = *(void**)((char*)this + 0x38);
    *(void**)this = (void*)0xade570;
    if (ebx) {
        void* edi = *(void**)ebx;
        if (edi) {
            lock.fn_004dffe1(0);
            u32 n = *(u32*)((char*)edi + 4);
            if (n > 0u && n < 0xFFFFFFFFu) {
                *(u32*)((char*)edi + 4) = n - 1u;
            }
            void* esi = (*(u32*)((char*)edi + 4) == 0u) ? edi : 0;
            lock.fn_004e0002();
            if (esi) {
                void** vt = *(void***)esi;
                typedef void (__thiscall *Dtor)(void*, int);
                ((Dtor)vt[0])(esi, 1);
            }
        }
        fn_000136c0(ebx);
    }
    ((C_004e03dd*)((char*)this + 4))->fn_004e03dd();
}

// FUNCTION: DAO 0x00403850
u16 __thiscall C_00403850::fn_00003850() {
    void** vt = *(void***)this;
    typedef u16 (__thiscall *Get16)(void*);
    Get16 get = (Get16)vt[4];
    u16 ax = get(this);
    if (ax == 0xffff) return 0xffff;
    int* cnt = *(int**)((char*)this + 0x30);
    *cnt = *cnt - 1;
    u16** pp = *(u16***)((char*)this + 0x20);
    u16* p = *pp;
    *pp = p + 1;
    return *p;
}

// FUNCTION: DAO 0x00403900
void* __thiscall C_00403900::fn_00003900(u32 flags) {
    ((C_00403790*)this)->fn_00003790();
    if (flags & 1u) fn_000136c0(this);
    return this;
}

// FUNCTION: DAO 0x00403990
void __thiscall C_00403990::fn_00003990() {
    char* base = (char*)this;
    if (*(u8*)(base + 0x40) & 1u) {
        void* p = *(void**)(*(void**)(base + 0x10));
        fn_000136c0(p);
    }
    *(u32*)(*(void**)(base + 0x10)) = 0;
    *(u32*)(*(void**)(base + 0x20)) = 0;
    *(u32*)(*(void**)(base + 0x30)) = 0;
    *(u32*)(*(void**)(base + 0x14)) = 0;
    *(u32*)(*(void**)(base + 0x24)) = 0;
    *(u32*)(*(void**)(base + 0x34)) = 0;
    *(u32*)(base + 0x40) &= ~1u;
    *(u32*)(base + 0x3c) = 0;
}

// FUNCTION: DAO 0x00403A90
void* __thiscall C_00403a90::fn_00003a90(u32 flags) {
    ((C_00003310*)this)->fn_00003310();
    if (flags & 1u) fn_000136c0(this);
    return this;
}

// FUNCTION: DAO 0x00403AB0
void* __thiscall C_00403ab0::fn_00003ab0(u32 flags) {
    ((C_000039f0*)this)->fn_000039f0();
    if (flags & 1u) fn_000136c0(this);
    return this;
}

// FUNCTION: DAO 0x00403AD0
int __thiscall C_00403ad0::fn_00003ad0(C_00403ad0* other) {
    if (*(void**)this && *(void**)this != *(void**)other) {
        ((C_004e11f2*)this)->fn_004e11f2();
    }
    int diff = *(int*)((char*)this + 4) - *(int*)((char*)other + 4);
    return diff / 28;
}

// FUNCTION: DAO 0x00403B10
void* __thiscall C_00403b10::fn_00003b10() {
    C_004dffe1 lock;
    char* base = (char*)this;
    *(void**)base = (void*)0xade570;
    ((C_004e03c5*)(base + 4))->fn_004e03c5();
    void* esi = fn_00013660(4u);
    if (esi) {
        *(void**)esi = fn_004e023b();
        void* edi = fn_004e006f();
        lock.fn_004dffe1(0);
        u32 n = *(u32*)((char*)edi + 4);
        if (n < 0xFFFFFFFFu) {
            *(u32*)((char*)edi + 4) = n + 1u;
        }
        lock.fn_004e0002();
    } else {
        esi = 0;
    }
    *(void**)(base + 0x38) = esi;
    ((C_00403720*)this)->fn_00003720();
    return this;
}
