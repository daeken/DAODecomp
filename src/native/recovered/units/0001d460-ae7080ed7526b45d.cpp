typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned short u16;
typedef signed short s16;
typedef signed char s8;

struct Obj18210 {
    u32 pad0[2];
    u32 f8;
    unsigned char fn_00018210() const;
};

struct Obj186a0 {
    void* f0;
    void* fn_000186a0();
};

struct GThread {
    u32 pad0[7];
    int f1c;
    unsigned char fn_00018780();
};

struct Obj1d460 {
    u32 pad0[8];
    void* f20;
    u32 pad24;
    void* f28;
    bool fn_0001d460() const;
};

struct Obj1d480 {
    u32 pad0[2];
    void* f8;
    u32 padc;
    void* f10;
    bool fn_0001d480() const;
};

struct Key {
    u32 pad0;
    u8 b4;
    u8 b5;
    u16 w6;
    u8 b8;
    u8 b9;
    u8 b10;
    u8 pad11;
    unsigned char fn_0001dc70(const Key* other) const;
    unsigned char fn_0001dce0(const Key* other) const;
};

// FUNCTION: DAO 0x418210
unsigned char Obj18210::fn_00018210() const {
    return !f8;
}

// FUNCTION: DAO 0x4186a0
void* Obj186a0::fn_000186a0() {
    if (f0 != 0) return *(void**)f0;
}

// FUNCTION: DAO 0x418780
unsigned char GThread::fn_00018780() {
    unsigned char r = 0;
    if (f1c > 0) r = 1;
    return r;
}

// FUNCTION: DAO 0x419730
unsigned int* __fastcall fn_00019730(unsigned int* src, unsigned int* dst) {
    unsigned int* p = src;
    *dst = *p;
    return p + 1;
}

// FUNCTION: DAO 0x41d460
bool Obj1d460::fn_0001d460() const {
    return f20 != 0 || f28 != 0;
}

// FUNCTION: DAO 0x41d480
bool Obj1d480::fn_0001d480() const {
    return f8 != 0 || f10 != 0;
}

// FUNCTION: DAO 0x41d960
unsigned char __cdecl fn_0001d960(const Key* a, const Key* b) {
    if ((s16)a->w6 > (s16)b->w6) return 1;
    if ((s16)a->w6 < (s16)b->w6) return 0;
    if ((s8)a->b4 > (s8)b->b4) return 1;
    if ((s8)a->b4 < (s8)b->b4) return 0;
    if ((s8)a->b5 > (s8)b->b5) return 1;
    return 0;
}

// FUNCTION: DAO 0x41dc70
unsigned char Key::fn_0001dc70(const Key* other) const {
    if ((s16)w6 < (s16)other->w6) return 1;
    if ((s16)w6 > (s16)other->w6) return 0;
    if ((s8)b4 < (s8)other->b4) return 1;
    if ((s8)b4 > (s8)other->b4) return 0;
    if ((s8)b5 < (s8)other->b5) return 1;
    if ((s8)b5 > (s8)other->b5) return 0;
    if ((s8)b8 < (s8)other->b8) return 1;
    if ((s8)b8 > (s8)other->b8) return 0;
    if ((s8)b9 < (s8)other->b9) return 1;
    if ((s8)b9 > (s8)other->b9) return 0;
    if ((s8)b10 < (s8)other->b10) return 1;
    return 0;
}

// FUNCTION: DAO 0x41dce0
unsigned char Key::fn_0001dce0(const Key* other) const {
    return (unsigned char)(w6 == other->w6 && b4 == other->b4 && b5 == other->b5 && b8 == other->b8 && b9 == other->b9 && b10 == other->b10 ? 1 : 0);
}
