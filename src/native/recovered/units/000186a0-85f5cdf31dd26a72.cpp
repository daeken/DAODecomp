typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned short u16;
typedef signed short s16;
typedef signed char s8;

struct Obj18210 {
    u32 pad0[2];
    u32 f8;
    signed char fn_00018210() const;
};

struct Obj186a0 {
    void* f0;
    void* fn_000186a0();
};

struct GThread {
    u32 pad0[7];
    int f1c;
    signed char fn_00018780();
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
signed char Obj18210::fn_00018210() const {
    unsigned int v = f8;
    unsigned char b = (v == 0);
    return (signed char)b;
}

// FUNCTION: DAO 0x4186a0
void* Obj186a0::fn_000186a0() {
    void* p = f0;
    if (p == 0) return 0;
    return *(void**)p;
}

// FUNCTION: DAO 0x418780
signed char GThread::fn_00018780() {
    int v = f1c;
    unsigned char b = (v > 0);
    return (signed char)b;
}

// FUNCTION: DAO 0x419730
unsigned int* __fastcall fn_00019730(unsigned int* src, unsigned int* dst) {
    unsigned int v = *src;
    *dst = v;
    return src + 1;
}

// FUNCTION: DAO 0x41d960
unsigned char __cdecl fn_0001d960(const Key* a, const Key* b) {
    if ((s16)a->w6 > (s16)b->w6) return 1;
    if ((s16)a->w6 == (s16)b->w6) {
        if ((s8)a->b4 > (s8)b->b4) return 1;
        if ((s8)a->b4 == (s8)b->b4) {
            if ((s8)a->b5 > (s8)b->b5) return 1;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x41dc70
unsigned char Key::fn_0001dc70(const Key* other) const {
    if ((s16)w6 < (s16)other->w6) return 1;
    if ((s16)w6 == (s16)other->w6) {
        if ((s8)b4 < (s8)other->b4) return 1;
        if ((s8)b4 == (s8)other->b4) {
            if ((s8)b5 < (s8)other->b5) return 1;
            if ((s8)b5 == (s8)other->b5) {
                if ((s8)b8 < (s8)other->b8) return 1;
                if ((s8)b8 == (s8)other->b8) {
                    if ((s8)b9 < (s8)other->b9) return 1;
                    if ((s8)b9 == (s8)other->b9) {
                        return (unsigned char)((s8)b10 < (s8)other->b10);
                    }
                }
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x41dce0
unsigned char Key::fn_0001dce0(const Key* other) const {
    if (w6 == other->w6 &&
        b4 == other->b4 &&
        b5 == other->b5 &&
        b8 == other->b8 &&
        b9 == other->b9 &&
        b10 == other->b10)
        return 1;
    return 0;
}
