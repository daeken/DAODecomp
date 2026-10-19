typedef unsigned int u32;
typedef unsigned char u8;
typedef signed int s32;

struct RBNode {
    RBNode* left;
    RBNode* parent;
    RBNode* right;
    u8 pad15[0x15 - 0xC];
    u8 flag15;
};

class Ctx_518510 {
public:
    int fn_00118510();
private:
    u8 pad0[0x34];
    int field34;
};

class Ctx_51d2c0 {
public:
    int fn_0011d2c0();
private:
    u8 pad0[4];
    u32 field4;
    u32 field8;
};

class Ctx_523570 {
public:
    void* fn_00123570();
private:
    u8 pad0[0x58];
};

class RBTree {
public:
    void fn_00123b30(RBNode* x);
private:
    u8 pad0[4];
    RBNode* head;
};

class Ctx_527080 {
public:
    void fn_00127080(u32 a, u32 b);
private:
    u8 pad0[4];
    u32 field4;
    u32 field8;
    u32 fieldC;
};

class Ctx52C {
public:
    void fn_0012c070(u8 flag);
    u8 fn_0012bf90();
    u32 fn_0012c400(u32 idx);
    u32 fn_0012c460(u32 idx);
    u32 fn_0012cc50();
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

// FUNCTION: DAO 0x00518510
int Ctx_518510::fn_00118510() {
    return this->field34 != 0;
}

// FUNCTION: DAO 0x00518550
void fn_00118550(u8* src_begin, u8* src_end, u8* dst) {
    while (src_begin != src_end) {
        *(u32*)(dst + 0) = *(u32*)(src_begin + 0);
        *(u32*)(dst + 8) = *(u32*)(src_begin + 8);
        *(u32*)(dst + 12) = *(u32*)(src_begin + 12);
        src_begin += 16;
        dst += 16;
    }
}

// FUNCTION: DAO 0x005185a0
void fn_001185a0(u8* src_begin, u8* src_end, u8* dst_end) {
    while (src_end != src_begin) {
        src_end -= 16;
        dst_end -= 16;
        *(u32*)(dst_end + 0) = *(u32*)(src_end + 0);
        *(u32*)(dst_end + 8) = *(u32*)(src_end + 8);
        *(u32*)(dst_end + 12) = *(u32*)(src_end + 12);
    }
}

// FUNCTION: DAO 0x00518c60
void fn_00118c60(u8* src_begin, u8* src_end, u8* dst) {
    while (src_begin != src_end) {
        if (dst != 0) {
            *(u32*)(dst + 0) = *(u32*)(src_begin + 0);
            *(u32*)(dst + 8) = *(u32*)(src_begin + 8);
            *(u32*)(dst + 12) = *(u32*)(src_begin + 12);
        }
        src_begin += 16;
        dst += 16;
    }
}

// FUNCTION: DAO 0x00518d90
void fn_00118d90(u8* dst_begin, u8* dst_end, const u8* src) {
    while (dst_begin != dst_end) {
        *(u32*)(dst_begin + 0) = *(const u32*)(src + 0);
        *(u32*)(dst_begin + 8) = *(const u32*)(src + 8);
        *(u32*)(dst_begin + 12) = *(const u32*)(src + 12);
        dst_begin += 16;
    }
}

// FUNCTION: DAO 0x00518dc0
void fn_00118dc0(u8* dst, u32 count, const u8* src) {
    while (count != 0) {
        if (dst != 0) {
            *(u32*)(dst + 0) = *(const u32*)(src + 0);
            *(u32*)(dst + 8) = *(const u32*)(src + 8);
            *(u32*)(dst + 12) = *(const u32*)(src + 12);
        }
        count -= 1;
        dst += 16;
    }
}

// FUNCTION: DAO 0x0051af70
int fn_0011af70(const u8* a, const u8* b, u32 n) {
    while (n >= 4) {
        u32 va = *(const u32*)a;
        u32 vb = *(const u32*)b;
        if (va != vb) {
            break;
        }
        n -= 4;
        a += 4;
        b += 4;
    }
    while (n != 0) {
        u8 ca = *a;
        u8 cb = *b;
        if (ca != cb) {
            return (ca > cb) ? 1 : -1;
        }
        n -= 1;
        a += 1;
        b += 1;
    }
    return 0;
}

// FUNCTION: DAO 0x0051d2c0
int Ctx_51d2c0::fn_0011d2c0() {
    u32 begin = this->field4;
    if (begin == 0) {
        return begin == 0;
    }
    s32 diff = (s32)this->field8 - (s32)begin;
    s32 count = diff / 28;
    return count == 0;
}

// FUNCTION: DAO 0x00523570
void* Ctx_523570::fn_00123570() {
    return (void*)((u8*)this + 0x58);
}

// FUNCTION: DAO 0x00523b30
void RBTree::fn_00123b30(RBNode* x) {
    RBNode* y = x->right;
    x->right = y->left;
    RBNode* yl = y->left;
    if (yl->flag15 == 0) {
        yl->parent = x;
    }
    y->parent = x->parent;
    RBNode* h = this->head;
    if (x == h->parent) {
        h->parent = y;
        y->left = x;
        x->parent = y;
        return;
    }
    RBNode* p = x->parent;
    if (x == p->left) {
        p->left = y;
        y->left = x;
        x->parent = y;
    } else {
        p->right = y;
        y->left = x;
        x->parent = y;
    }
}

// FUNCTION: DAO 0x00527080
void Ctx_527080::fn_00127080(u32 a, u32 b) {
    this->field4 = a;
    this->field8 = b;
    this->fieldC = 0;
}

// FUNCTION: DAO 0x0052bf90
u8 Ctx52C::fn_0012bf90() {
    return (u8)(this->f_214 & 1);
}

// FUNCTION: DAO 0x0052c070
void Ctx52C::fn_0012c070(u8 flag) {
    if (flag != 0) {
        this->flags_1bc &= 0xfbffffff;
    } else {
        this->flags_1bc |= 0x4000000;
    }
}

// FUNCTION: DAO 0x0052c400
u32 Ctx52C::fn_0012c400(u32 idx) {
    if (idx > 4) {
        if (idx == 8) {
            return this->f_730;
        }
        if (idx == 0x100) {
            return this->f_8f0;
        }
        return 0;
    }
    if (idx == 4) {
        return this->f_570;
    }
    if (idx == 1) {
        return this->f_1f0;
    }
    if (idx == 2) {
        return this->f_3b0;
    }
    return 0;
}

// FUNCTION: DAO 0x0052c460
u32 Ctx52C::fn_0012c460(u32 idx) {
    if (idx > 4) {
        if (idx == 8) {
            return this->f_734;
        }
        if (idx == 0x100) {
            return this->f_8f4;
        }
        return 0;
    }
    if (idx == 4) {
        return this->f_574;
    }
    if (idx == 1) {
        return this->f_1f4;
    }
    if (idx == 2) {
        return this->f_3b4;
    }
    return 0;
}

// FUNCTION: DAO 0x0052cc50
u32 Ctx52C::fn_0012cc50() {
    u32 v = this->flags_1bc >> 26;
    return (u32)((u8)(~v) & 1u);
}
