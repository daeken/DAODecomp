typedef unsigned int u32;
typedef unsigned char u8;
typedef signed int s32;

class Ctx_51d2c0 {
public:
    bool fn_0011d2c0();
private:
    u8 pad0[4];
    u32 field4;
    u32 field8;
};

class Ctx52C {
public:
    u8 fn_0012bf90();
    u32 fn_0012c400(int idx);
    u32 fn_0012c460(int idx);
    u8 fn_0012cc50();
private:
    u8 pad_000[0x1bc];
    u32 flags_1bc;
    u8 pad_1c0[0x1f0 - 0x1c0];
    u32 f_1f0;
    u32 f_1f4;
    u8 pad_1f8[0x214 - 0x1f8];
    u8 f_214;
    u8 pad_215[0x3b0 - 0x215];
    u32 f_3b0;
    u32 f_3b4;
    u8 pad_3b8[0x570 - 0x3b8];
    u32 f_570;
    u32 f_574;
    u8 pad_578[0x730 - 0x578];
    u32 f_730;
    u32 f_734;
    u8 pad_738[0x8f0 - 0x738];
    u32 f_8f0;
    u32 f_8f4;
};

// FUNCTION: DAO 0x00518550
void fn_00118550(u8* src_begin, u8* src_end, u8* dst) {
    u32* s0 = (u32*)src_begin;
    u32* s8 = (u32*)(src_begin + 8);
    u32* d0 = (u32*)dst;
    u32* d8 = (u32*)(dst + 8);
    u32* end = (u32*)src_end;
    while (s0 != end) {
        d0[0] = s0[0];
        d8[0] = s8[0];
        d8[1] = s8[1];
        s0 += 4;
        d0 += 4;
        s8 += 4;
        d8 += 4;
    }
}

// FUNCTION: DAO 0x005185a0
void fn_001185a0(u8* src_begin, u8* src_end, u8* dst_end) {
    u32* begin = (u32*)src_begin;
    u32* s0 = (u32*)src_end;
    u32* s8 = (u32*)(src_end + 8);
    u32* d0 = (u32*)dst_end;
    u32* d8 = (u32*)(dst_end + 8);
    while (s0 != begin) {
        s0 -= 4;
        s8 -= 4;
        d0 -= 4;
        d8 -= 4;
        d0[0] = s0[0];
        d8[0] = s8[0];
        d8[1] = s8[1];
    }
}

// FUNCTION: DAO 0x00518c60
void fn_00118c60(u8* src_begin, u8* src_end, u8* dst) {
    u32* s0 = (u32*)src_begin;
    u32* s8 = (u32*)(src_begin + 8);
    u32* d0 = (u32*)dst;
    u32* d8 = (u32*)(dst + 8);
    u32* end = (u32*)src_end;
    while (s0 != end) {
        if (d0 != 0) {
            d0[0] = s0[0];
            d8[0] = s8[0];
            d8[1] = s8[1];
        }
        s0 += 4;
        d0 += 4;
        s8 += 4;
        d8 += 4;
    }
}

// FUNCTION: DAO 0x00518dc0
void fn_00118dc0(u8* dst, u32 count, const u8* src) {
    if (count == 0) {
        return;
    }
    u32* d0 = (u32*)dst;
    u32* d8 = (u32*)(dst + 8);
    const u32* s = (const u32*)src;
    do {
        if (d0 != 0) {
            d0[0] = s[0];
            d8[0] = s[2];
            d8[1] = s[3];
        }
        --count;
        d0 += 4;
        d8 += 4;
    } while (count != 0);
}

// FUNCTION: DAO 0x0051af70
int fn_0011af70(const u8* b, const u8* a, u32 n) {
    while (n >= 4) {
        u32 vb = *(const u32*)b;
        u32 va = *(const u32*)a;
        if (vb != va) {
            break;
        }
        n -= 4;
        b += 4;
        a += 4;
    }
    if (n == 0) {
        return 0;
    }
    {
        u32 cb = (u32)*b;
        u32 ca = (u32)*a;
        int d = (int)cb - (int)ca;
        if (d != 0) {
            return d > 0 ? 1 : -1;
        }
        --n;
        ++b;
        ++a;
    }
    if (n == 0) {
        return 0;
    }
    {
        u32 cb = (u32)*b;
        u32 ca = (u32)*a;
        int d = (int)cb - (int)ca;
        if (d != 0) {
            return d > 0 ? 1 : -1;
        }
        --n;
        ++b;
        ++a;
    }
    if (n == 0) {
        return 0;
    }
    {
        u32 cb = (u32)*b;
        u32 ca = (u32)*a;
        int d = (int)cb - (int)ca;
        if (d != 0) {
            return d > 0 ? 1 : -1;
        }
        --n;
        ++b;
        ++a;
    }
    if (n == 0) {
        return 0;
    }
    {
        u32 cb = (u32)*b;
        u32 ca = (u32)*a;
        int d = (int)cb - (int)ca;
        if (d != 0) {
            return d > 0 ? 1 : -1;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x0051d2c0
bool Ctx_51d2c0::fn_0011d2c0() {
    u32 begin = this->field4;
    if (begin != 0) {
        s32 diff = (s32)this->field8 - (s32)begin;
        s32 count = diff / 28;
        return count == 0;
    }
    return !begin;
}

// FUNCTION: DAO 0x0052bf90
u8 Ctx52C::fn_0012bf90() {
    u8 r = this->f_214;
    r &= 1;
    return r;
}

// FUNCTION: DAO 0x0052c400
u32 Ctx52C::fn_0012c400(int idx) {
    switch (idx) {
    case 1:
        return this->f_1f0;
    case 2:
        return this->f_3b0;
    case 4:
        return this->f_570;
    case 8:
        return this->f_730;
    case 0x100:
        return this->f_8f0;
    default:
        return 0;
    }
}

// FUNCTION: DAO 0x0052c460
u32 Ctx52C::fn_0012c460(int idx) {
    switch (idx) {
    case 1:
        return this->f_1f4;
    case 2:
        return this->f_3b4;
    case 4:
        return this->f_574;
    case 8:
        return this->f_734;
    case 0x100:
        return this->f_8f4;
    default:
        return 0;
    }
}

// FUNCTION: DAO 0x0052cc50
u8 Ctx52C::fn_0012cc50() {
    u32 v = this->flags_1bc >> 26;
    u8 r = (u8)v;
    r = (u8)~r;
    r &= 1;
    return r;
}
