typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct VMReader {
    void* field0;
    unsigned int fn_0055ddf0(unsigned int offset);
    unsigned int fn_0055dee0(unsigned int offset, unsigned int* out);
    unsigned int fn_0055e070(unsigned int offset, unsigned int* out);
    unsigned int fn_0055e1d0(unsigned int offset, unsigned int* out);
};

struct CmpObject {
    u8 pad0[0x10];
    u32 field10;
    void* field14;
    u32 field18;
    int fn_0055eaf0(const CmpObject* other);
};

struct SearchObject {
    u8 pad0[0x10];
    void* field10;
    int field14;
    u32 field18;
    int fn_0055ee90(u16 key);
};

struct Flags8C {
    u8 pad0[0x8c];
    u16 field8c;
    void fn_00564d90(u8 flag);
};

struct Bytes38 {
    u8 pad0[0x38];
    u8 field38;
    u8 field39;
    void fn_00565b00();
};

struct Field18 {
    u8 pad0[0x18];
    u32 field18;
    u32 fn_0056bdf0();
};

struct Field6A {
    u8 pad0[0x6a];
    u8 field6a;
    void fn_0057b310();
};

// FUNCTION: DAO 0x0095DDF0
unsigned int VMReader::fn_0055ddf0(unsigned int offset) {
    unsigned char** pages = *reinterpret_cast<unsigned char***>(reinterpret_cast<unsigned char*>(field0) + 0xc);
    unsigned int o0 = offset;
    unsigned int o1 = offset + 1u;
    unsigned int o2 = offset + 2u;
    unsigned int o3 = offset + 3u;
    unsigned int b0 = pages[o0 >> 12][o0 & 0xfffu];
    unsigned int b1 = pages[o1 >> 12][o1 & 0xfffu];
    unsigned int b2 = pages[o2 >> 12][o2 & 0xfffu];
    unsigned int b3 = pages[o3 >> 12][o3 & 0xfffu];
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
}

// FUNCTION: DAO 0x0095DEE0
unsigned int VMReader::fn_0055dee0(unsigned int offset, unsigned int* out) {
    unsigned char** pages = *reinterpret_cast<unsigned char***>(reinterpret_cast<unsigned char*>(field0) + 0xc);
    unsigned int b0 = pages[offset >> 12][offset & 0xfffu];
    unsigned int code = b0 & 3u;
    unsigned int value = b0 >> 2;
    if (code == 0u) { *out = value; return 1u; }
    unsigned int o1 = offset + 1u;
    unsigned int b1 = pages[o1 >> 12][o1 & 0xfffu];
    if (code == 1u) { *out = value | (b1 << 6); return 2u; }
    unsigned int o2 = offset + 2u;
    unsigned int b2 = pages[o2 >> 12][o2 & 0xfffu];
    if (code == 2u) { *out = value | (b1 << 6) | (b2 << 14); return 3u; }
    unsigned int o3 = offset + 3u;
    unsigned int b3 = pages[o3 >> 12][o3 & 0xfffu];
    *out = value | (b1 << 6) | (b2 << 14) | (b3 << 22);
    return 4u;
}

// FUNCTION: DAO 0x0095E070
unsigned int VMReader::fn_0055e070(unsigned int offset, unsigned int* out) {
    unsigned char* base = *reinterpret_cast<unsigned char**>(reinterpret_cast<unsigned char*>(field0) + 8);
    unsigned char* p = base + offset;
    unsigned int b0 = p[0];
    unsigned int code = b0 & 3u;
    unsigned int value = b0 >> 2;
    if (code == 0u) { *out = value; return 1u; }
    if (code == 1u) { *out = value | ((unsigned int)p[1] << 6); return 2u; }
    if (code == 2u) { *out = value | ((unsigned int)p[1] << 6) | ((unsigned int)p[2] << 14); return 3u; }
    *out = value | ((unsigned int)p[1] << 6) | ((unsigned int)p[2] << 14) | ((unsigned int)p[3] << 22);
    return 4u;
}

// FUNCTION: DAO 0x0095E1D0
unsigned int VMReader::fn_0055e1d0(unsigned int offset, unsigned int* out) {
    unsigned char** pages = *reinterpret_cast<unsigned char***>(reinterpret_cast<unsigned char*>(field0) + 0xc);
    unsigned int b0 = pages[offset >> 12][offset & 0xfffu];
    unsigned int value = b0 >> 1;
    if ((b0 & 1u) == 0u) { *out = value; return 1u; }
    unsigned int o1 = offset + 1u;
    unsigned int b1 = pages[o1 >> 12][o1 & 0xfffu];
    *out = value | (b1 << 7);
    return 2u;
}

// FUNCTION: DAO 0x0095EAF0
int CmpObject::fn_0055eaf0(const CmpObject* other) {
    const unsigned char* a = reinterpret_cast<const unsigned char*>(field14) + 0xc;
    const unsigned char* b = reinterpret_cast<const unsigned char*>(other->field14) + 0xc;
    while (*a == *b) {
        if (*a == 0u) {
            if (field10 == other->field10 && field18 == other->field18) return 1;
            return 0;
        }
        ++a;
        ++b;
    }
    return 0;
}

// FUNCTION: DAO 0x0095EE90
int SearchObject::fn_0055ee90(u16 key) {
    int high = field14 - 1;
    int low = 0;
    if (high < 0) return -1;
    unsigned char* base = *reinterpret_cast<unsigned char**>(reinterpret_cast<unsigned char*>(field10) + 8);
    unsigned char* entries = base + field18;
    for (;;) {
        int mid = (low + high) / 2;
        unsigned int value = entries[mid * 8] | ((unsigned int)entries[mid * 8 + 1] << 8);
        if ((unsigned int)key == value) return mid;
        if ((unsigned int)key >= value) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
        if (low > high) return -1;
    }
}

// FUNCTION: DAO 0x00964D90
void Flags8C::fn_00564d90(u8 flag) {
    if (flag != 0u) {
        field8c = (u16)(field8c | 0x180u);
    } else {
        field8c = (u16)((field8c & 0xff7fu) | 0x100u);
    }
}

// FUNCTION: DAO 0x00965B00
void Bytes38::fn_00565b00() {
    field39 = 0u;
    field38 = 0u;
}

// FUNCTION: DAO 0x0096BDF0
unsigned int Field18::fn_0056bdf0() {
    return field18;
}

// FUNCTION: DAO 0x0097B310
void Field6A::fn_0057b310() {
    field6a = (u8)(field6a & 0xf3u);
}
