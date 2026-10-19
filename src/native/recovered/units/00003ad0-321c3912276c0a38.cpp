typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

struct C_000c0d90 { void __thiscall fn_000c0d90(); };
struct C_000c2ab0 { void* __thiscall fn_000c2ab0(void*); };
struct C_00403c70 { void* __thiscall fn_00003c70(); };
struct C_004dffe1 { int locktype; void __thiscall fn_004dffe1(int); void __thiscall fn_004e0002(); };
struct C_004e03c5 { void __thiscall fn_004e03c5(); };
struct C_004e03dd { void __thiscall fn_004e03dd(); };
struct C_004e11f2 { void __thiscall fn_004e11f2(); };

void fn_004136c0(void*);
void* fn_00413660(u32);
void* fn_004e023b();
void* fn_004e006f();

struct C_00403480 { void* __thiscall fn_00003480(void*); };
struct C_00403570 { u32 field_0; u32 refcount; void* __thiscall fn_00003570(); };
struct C_004035c0 { void* field_0; void __thiscall fn_000035c0(); };
struct C_00403720 {
    u32 f00;
    u32 f04;
    u32 f08;
    u32 f0c;
    u32* f10;
    u32* f14;
    u32 f18;
    u32 f1c;
    u32* f20;
    u32* f24;
    u32 f28;
    u32 f2c;
    u32* f30;
    u32* f34;
    void __thiscall fn_00003720();
};
struct C_00403790 {
    void* vtbl;
    u32 base[13];
    void* field_38;
    void __thiscall fn_00003790();
};
struct C_00403850 {
    void** vtbl;
    u8 pad20[0x1c];
    u16** ptr20;
    u8 pad30[0xc];
    int* ptr30;
    u16 __thiscall fn_00003850();
};
struct C_00403ad0 { void* ptr; int offset; int __thiscall fn_00003ad0(C_00403ad0*); };
struct C_00403b10 {
    void* vtbl;
    u32 base[13];
    void* field_38;
    void* __thiscall fn_00003b10();
};

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
    u32 n = refcount;
    if (n > 0u && n < 0xffffffffu) {
        n = n - 1u;
        refcount = n;
    }
    void* result = (refcount == 0u) ? (void*)this : 0;
    lock.fn_004e0002();
    return result;
}

// FUNCTION: DAO 0x004035C0
void __thiscall C_004035c0::fn_000035c0() {
    void* p = field_0;
    if (!p) return;
    C_004dffe1 lock;
    lock.fn_004dffe1(0);
    u32 n = *(u32*)((char*)p + 4);
    if (n > 0u && n < 0xffffffffu) {
        n = n - 1u;
        *(u32*)((char*)p + 4) = n;
    }
    void* result = (*(u32*)((char*)p + 4) == 0u) ? p : 0;
    lock.fn_004e0002();
    if (result) {
        void** vt = *(void***)result;
        typedef void (__thiscall *Dtor)(void*, int);
        ((Dtor)vt[0])(result, 1);
    }
}

// FUNCTION: DAO 0x00403720
void __thiscall C_00403720::fn_00003720() {
    f20 = &f18;
    f24 = &f1c;
    f10 = &f08;
    f30 = &f28;
    f14 = &f0c;
    f34 = &f2c;
    f0c = 0;
    *f24 = 0;
    *f34 = 0;
    *f10 = 0;
    *f20 = 0;
    *f30 = 0;
}

// FUNCTION: DAO 0x00403790
void __thiscall C_00403790::fn_00003790() {
    C_004dffe1 lock;
    void* p = field_38;
    vtbl = (void*)0xade570;
    if (p) {
        void* q = *(void**)p;
        if (q) {
            lock.fn_004dffe1(0);
            u32 n = *(u32*)((char*)q + 4);
            if (n > 0u && n < 0xffffffffu) {
                n = n - 1u;
                *(u32*)((char*)q + 4) = n;
            }
            void* r = (*(u32*)((char*)q + 4) == 0u) ? q : 0;
            lock.fn_004e0002();
            if (r) {
                void** vt = *(void***)r;
                typedef void (__thiscall *Dtor)(void*, int);
                ((Dtor)vt[0])(r, 1);
            }
        }
        fn_004136c0(p);
    }
    ((C_004e03dd*)((char*)this + 4))->fn_004e03dd();
}

// FUNCTION: DAO 0x00403850
u16 __thiscall C_00403850::fn_00003850() {
    typedef u16 (__thiscall *Get16)(void*);
    Get16 get = (Get16)vtbl[4];
    u16 ax = get(this);
    if (ax == 0xffff) return 0xffff;
    int* cnt = ptr30;
    *cnt = *cnt - 1;
    u16** pp = ptr20;
    u16* p = *pp;
    *pp = p + 1;
    return *p;
}

// FUNCTION: DAO 0x00403AD0
int __thiscall C_00403ad0::fn_00003ad0(C_00403ad0* other) {
    if (ptr == 0 || ptr != other->ptr) {
        ((C_004e11f2*)this)->fn_004e11f2();
    }
    int diff = offset - other->offset;
    return diff / 28;
}

// FUNCTION: DAO 0x00403B10
void* __thiscall C_00403b10::fn_00003b10() {
    C_004dffe1 lock;
    vtbl = (void*)0xade570;
    ((C_004e03c5*)((char*)this + 4))->fn_004e03c5();
    void* p = fn_00413660(4u);
    if (p) {
        *(void**)p = fn_004e023b();
        void* q = fn_004e006f();
        lock.fn_004dffe1(0);
        u32 n = *(u32*)((char*)q + 4);
        if (n < 0xffffffffu) {
            n = n + 1u;
            *(u32*)((char*)q + 4) = n;
        }
        lock.fn_004e0002();
    } else {
        p = 0;
    }
    field_38 = p;
    ((C_00403720*)this)->fn_00003720();
    return this;
}
