typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct VMInner {
    u8 pad0[8];
    u8* field8;
    u8** fieldC;
};

struct VMReader {
    VMInner* field0;
    u32 fn_0055ddf0(u32 offset);
    u32 fn_0055dee0(u32 offset, u32* out);
    u32 fn_0055e070(u32 offset, u32* out);
    u32 fn_0055e1d0(u32 offset, u32* out);
};

struct CmpObject {
    u8 pad0[0x10];
    u32 field10;
    u8* field14;
    u32 field18;
    int fn_0055eaf0(const CmpObject* other);
};

struct SearchObject {
    u8 pad0[0x10];
    VMInner* field10;
    int field14;
    u32 field18;
    int fn_0055ee90(u16 key);
};

// FUNCTION: DAO 0x0095DDF0
u32 __thiscall VMReader::fn_0055ddf0(u32 offset) {
    u8** pages = field0->fieldC;
    u32 b0 = pages[offset >> 12][offset & 0xfffu];
    u32 o1 = offset + 1u;
    u32 b1 = pages[o1 >> 12][o1 & 0xfffu];
    u32 o2 = offset + 2u;
    u32 b2 = pages[o2 >> 12][o2 & 0xfffu];
    u32 o3 = offset + 3u;
    u32 b3 = pages[o3 >> 12][o3 & 0xfffu];
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
}

// FUNCTION: DAO 0x0095DEE0
u32 __thiscall VMReader::fn_0055dee0(u32 offset, u32* out) {
    u8** pages = field0->fieldC;
    u32 b0 = pages[offset >> 12][offset & 0xfffu];
    u32 code = b0 & 3u;
    u32 value = b0 >> 2;
    switch (code) {
    case 0:
        *out = value;
        return 1u;
    case 1: {
        u32 o1 = offset + 1u;
        u8 b1 = pages[o1 >> 12][o1 & 0xfffu];
        *out = value | ((u32)b1 << 6);
        return 2u;
    }
    case 2: {
        u32 o2 = offset + 2u;
        u32 o1 = offset + 1u;
        u8 b2 = pages[o2 >> 12][o2 & 0xfffu];
        u8 b1 = pages[o1 >> 12][o1 & 0xfffu];
        u32 w = ((u32)b2 << 8) | b1;
        *out = value | (w << 6);
        return 3u;
    }
    default: {
        u32 o3 = offset + 3u;
        u32 o2 = offset + 2u;
        u32 o1 = offset + 1u;
        u8 b3 = pages[o3 >> 12][o3 & 0xfffu];
        u8 b2 = pages[o2 >> 12][o2 & 0xfffu];
        u8 b1 = pages[o1 >> 12][o1 & 0xfffu];
        u32 w = ((u32)b3 << 8) | b2;
        w = (w << 8) | b1;
        *out = value | (w << 6);
        return 4u;
    }
    }
}

// FUNCTION: DAO 0x0095E070
u32 __thiscall VMReader::fn_0055e070(u32 offset, u32* out) {
    u8* p = field0->field8 + offset;
    u32 b0 = p[0];
    u32 code = b0 & 3u;
    u32 value = b0 >> 2;
    switch (code) {
    case 0:
        *out = value;
        return 1u;
    case 1:
        *out = value | ((u32)p[1] << 6);
        return 2u;
    case 2: {
        u32 w = ((u32)p[2] << 8) | p[1];
        *out = value | (w << 6);
        return 3u;
    }
    default: {
        u32 w = ((u32)p[3] << 8) | p[2];
        w = (w << 8) | p[1];
        *out = value | (w << 6);
        return 4u;
    }
    }
}

// FUNCTION: DAO 0x0095E1D0
u32 __thiscall VMReader::fn_0055e1d0(u32 offset, u32* out) {
    u8** pages = field0->fieldC;
    u32 b0 = pages[offset >> 12][offset & 0xfffu];
    if ((b0 & 1u) == 0u) {
        *out = b0 >> 1;
        return 1u;
    }
    u32 o1 = offset + 1u;
    u32 b1 = pages[o1 >> 12][o1 & 0xfffu];
    *out = (b0 >> 1) | (b1 << 7);
    return 2u;
}

// FUNCTION: DAO 0x0095EAF0
int __thiscall CmpObject::fn_0055eaf0(const CmpObject* other) {
    const u8* a = field14 + 0xc;
    const u8* b = other->field14 + 0xc;
    while (*a == *b) {
        if (*a == 0u) {
            if (field10 != other->field10) return 0;
            if (field18 != other->field18) return 0;
            return 1;
        }
        ++a;
        ++b;
    }
    return 0;
}

// FUNCTION: DAO 0x0095EE90
int __thiscall SearchObject::fn_0055ee90(u16 key) {
    int high = field14 - 1;
    int low = 0;
    if (high < 0) return -1;
    u32 off = field18;
    u8* base = field10->field8;
    u32 k = (u32)key;
    while (low <= high) {
        int mid = (low + high) / 2;
        u32 idx = off + (u32)mid * 8u;
        u32 v = (u32)base[idx] | ((u32)base[idx + 1u] << 8);
        if (k == v) return mid;
        if (k >= v) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
