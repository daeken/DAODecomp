typedef unsigned int u32;
typedef unsigned char u8;
typedef signed char s8;
typedef unsigned short u16;
typedef signed short s16;

struct GEvent {
    void* fn_00017280();
};

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
    bool fn_00018780();
};

struct Node1b {
    void* f0;
    void* f4;
};

struct List1b {
    u32 pad0[2];
    Node1b* f8;
    void fn_0001b1b0(Node1b* n);
};

struct Obj1caf0 {
    u32 a;
    u32 b;
    u32 c;
    void* fn_0001caf0();
};

struct Obj1cc90 {
    u8 b0;
    u8 pad1[0x3f];
    u8 b40;
    u8 pad41[0x0f];
    u32 d50;
    u32 d54;
    u32 d58;
    u32 d5c;
    u32 d60;
    u32 d64;
    void* fn_0001cc90();
};

struct Obj1ccf0 {
    void* f0;
    u32 f4;
    void* fn_0001ccf0(void* p);
};

struct Obj1d460 {
    u32 pad0[8];
    void* f20;
    void* f28;
    bool fn_0001d460() const;
};

struct Obj1d480 {
    u32 pad0[2];
    void* f8;
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
    void* fn_0001d9a0(const Key* src);
    void* fn_0001dc30(const Key* src);
    bool fn_0001dc70(const Key* other) const;
    bool fn_0001dce0(const Key* other) const;
};

// FUNCTION: DAO 0x417280
void* GEvent::fn_00017280() {
    return this ? (void*)((char*)this + 0x14) : 0;
}

// FUNCTION: DAO 0x418210
unsigned char Obj18210::fn_00018210() const {
    return (unsigned char)(f8 == 0);
}

// FUNCTION: DAO 0x4186a0
void* Obj186a0::fn_000186a0() {
    void* p = f0;
    return p ? *(void**)p : 0;
}

// FUNCTION: DAO 0x418780
bool GThread::fn_00018780() {
    return f1c > 0;
}

// FUNCTION: DAO 0x419730
unsigned int* __fastcall fn_00019730(unsigned int* src, unsigned int* dst) {
    *dst = *src;
    return src + 1;
}

// FUNCTION: DAO 0x41b1b0
void List1b::fn_0001b1b0(Node1b* n) {
    n->f0 = 0;
    n->f4 = f8;
    f8 = n;
}

// FUNCTION: DAO 0x41caf0
void* Obj1caf0::fn_0001caf0() {
    a = 0;
    b = 0;
    c = 0;
    return this;
}

// FUNCTION: DAO 0x41cc90
void* Obj1cc90::fn_0001cc90() {
    d50 = 0;
    d54 = 0;
    b0 = 0;
    b40 = 0;
    d60 = 0;
    d64 = 0;
    d58 = 0;
    d5c = 0;
    return this;
}

// FUNCTION: DAO 0x41ccf0
void* Obj1ccf0::fn_0001ccf0(void* p) {
    f0 = p;
    f4 = 0;
    return this;
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
bool fn_0001d960(const Key* a, const Key* b) {
    if ((s16)a->w6 > (s16)b->w6) return true;
    if ((s16)a->w6 != (s16)b->w6) return false;
    if ((s8)a->b4 > (s8)b->b4) return true;
    if (a->b4 != b->b4) return false;
    if ((s8)a->b5 > (s8)b->b5) return true;
    return false;
}

// FUNCTION: DAO 0x41d9a0
void* Key::fn_0001d9a0(const Key* src) {
    b5 = src->b5;
    b4 = src->b4;
    w6 = src->w6;
    return this;
}

// FUNCTION: DAO 0x41dc30
void* Key::fn_0001dc30(const Key* src) {
    b4 = src->b4;
    b5 = src->b5;
    w6 = src->w6;
    b8 = src->b8;
    b9 = src->b9;
    b10 = src->b10;
    return this;
}

// FUNCTION: DAO 0x41dc70
bool Key::fn_0001dc70(const Key* other) const {
    if ((s16)w6 < (s16)other->w6) return true;
    if ((s16)w6 != (s16)other->w6) return false;
    if ((s8)b4 < (s8)other->b4) return true;
    if (b4 != other->b4) return false;
    if ((s8)b5 < (s8)other->b5) return true;
    if (b5 != other->b5) return false;
    if ((s8)b8 < (s8)other->b8) return true;
    if (b8 != other->b8) return false;
    if ((s8)b9 < (s8)other->b9) return true;
    if (b9 != other->b9) return false;
    return (s8)b10 < (s8)other->b10;
}

// FUNCTION: DAO 0x41dce0
bool Key::fn_0001dce0(const Key* other) const {
    return w6 == other->w6 && b4 == other->b4 && b5 == other->b5 && b8 == other->b8 && b9 == other->b9 && b10 == other->b10;
}
