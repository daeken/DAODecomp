struct C930c20 {
    unsigned char* f0;
    unsigned int f4;
    void fn_00530c20();
};

struct C984e60 {
    unsigned char pad0[0x20];
    unsigned int field20;
    unsigned char pad24[6];
    unsigned short field2a;
    void fn_00584e60(unsigned char value);
};

struct C986b60 {
    unsigned char pad0[0x14];
    unsigned int* array;
    int count;
    unsigned int fn_00586b60();
};

struct C9a0280 {
    unsigned char pad0[0x28];
    unsigned char field28;
    unsigned char pad29;
    unsigned short field2a;
    void fn_005a0280(unsigned char value);
};

struct C9a02a0 {
    unsigned char pad0[0x28];
    unsigned char field28;
    unsigned char pad29;
    unsigned short field2a;
    void fn_005a02a0(unsigned char value);
};

struct C9a0300 {
    unsigned char pad0[0x10];
    unsigned int* field10;
    void fn_005a0300(unsigned int index, unsigned int value);
};

// FUNCTION: DAO 0x0090e7b0
unsigned int __stdcall fn_0050e7b0(unsigned char **pp) {
    unsigned char *p = *pp;
    unsigned int c = *p;
    if (c == 0) {
        return 0;
    }
    ++p;
    *pp = p;
    if (c < 0x80) {
        return c;
    }
    if ((c & 0xE0) == 0xC0) {
        unsigned char b1 = *p;
        unsigned int v = (c & 0x1F) << 6;
        if (b1 == 0) return 0;
        if ((b1 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b1 & 0x3F);
        ++p;
        *pp = p;
        if (v < 0x80) return 0xFFFD;
        return v;
    }
    if ((c & 0xF0) == 0xE0) {
        unsigned char b1 = *p;
        unsigned int v = (c & 0x0F) << 12;
        if (b1 == 0) return 0;
        if ((b1 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b1 & 0x3F) << 6;
        ++p;
        *pp = p;
        unsigned char b2 = *p;
        if (b2 == 0) return 0;
        if ((b2 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b2 & 0x3F);
        ++p;
        *pp = p;
        if (v < 0x800) return 0xFFFD;
        if (v >= 0xD800 && v <= 0xDFFF) return 0xFFFD;
        if (v == 0xFFFE || v == 0xFFFF) return 0xFFFD;
        return v;
    }
    if ((c & 0xF8) == 0xF0) {
        unsigned char b1 = *p;
        unsigned int v = (c & 0x07) << 18;
        if (b1 == 0) return 0;
        if ((b1 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b1 & 0x3F) << 12;
        ++p;
        *pp = p;
        unsigned char b2 = *p;
        if (b2 == 0) return 0;
        if ((b2 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b2 & 0x3F) << 6;
        ++p;
        *pp = p;
        unsigned char b3 = *p;
        if (b3 == 0) return 0;
        if ((b3 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b3 & 0x3F);
        ++p;
        *pp = p;
        if (v < 0x10000) return 0xFFFD;
        return v;
    }
    if ((c & 0xFC) == 0xF8) {
        unsigned char b1 = *p;
        unsigned int v = (c & 0x03) << 24;
        if (b1 == 0) return 0;
        if ((b1 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b1 & 0x3F) << 18;
        ++p;
        *pp = p;
        unsigned char b2 = *p;
        if (b2 == 0) return 0;
        if ((b2 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b2 & 0x3F) << 12;
        ++p;
        *pp = p;
        unsigned char b3 = *p;
        if (b3 == 0) return 0;
        if ((b3 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b3 & 0x3F) << 6;
        ++p;
        *pp = p;
        unsigned char b4 = *p;
        if (b4 == 0) return 0;
        if ((b4 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b4 & 0x3F);
        ++p;
        *pp = p;
        if (v < 0x200000) return 0xFFFD;
        return v;
    }
    if ((c & 0xFE) == 0xFC) {
        unsigned char b1 = *p;
        unsigned int v = (c & 0x01) << 30;
        if (b1 == 0) return 0;
        if ((b1 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b1 & 0x3F) << 24;
        ++p;
        *pp = p;
        unsigned char b2 = *p;
        if (b2 == 0) return 0;
        if ((b2 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b2 & 0x3F) << 18;
        ++p;
        *pp = p;
        unsigned char b3 = *p;
        if (b3 == 0) return 0;
        if ((b3 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b3 & 0x3F) << 12;
        ++p;
        *pp = p;
        unsigned char b4 = *p;
        if (b4 == 0) return 0;
        if ((b4 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b4 & 0x3F) << 6;
        ++p;
        *pp = p;
        unsigned char b5 = *p;
        if (b5 == 0) return 0;
        if ((b5 & 0xC0) != 0x80) return 0xFFFD;
        v |= (unsigned int)(b5 & 0x3F);
        ++p;
        *pp = p;
        if (v < 0x4000000) return 0xFFFD;
        return v;
    }
    return 0xFFFD;
}

// FUNCTION: DAO 0x00930c20
void C930c20::fn_00530c20() {
    *reinterpret_cast<unsigned int*>(f0 + 0xa4) = f4;
}

// FUNCTION: DAO 0x00984e60
void C984e60::fn_00584e60(unsigned char value) {
    unsigned int v = field20;
    field2a |= 0x400;
    field20 = (v & 0x00FFFFFFu) | ((unsigned int)value << 24);
}

// FUNCTION: DAO 0x00986b60
unsigned int C986b60::fn_00586b60() {
    unsigned int uidx = (unsigned int)count - 1u;
    int idx = (int)uidx;
    if (idx < 0 || idx >= count) return 0;
    return array[idx];
}

// FUNCTION: DAO 0x00990c10
unsigned int fn_00590c10(unsigned int x) {
    return (x + x * 4) * 4;
}

// FUNCTION: DAO 0x009a0280
void C9a0280::fn_005a0280(unsigned char value) {
    if (value != 0) {
        field28 |= 4;
    } else {
        field28 &= 0xfb;
    }
    field2a |= 0x40;
}

// FUNCTION: DAO 0x009a02a0
void C9a02a0::fn_005a02a0(unsigned char value) {
    if (value != 0) {
        field28 |= 8;
    } else {
        field28 &= 0xf7;
    }
    field2a |= 0x80;
}

// FUNCTION: DAO 0x009a0300
void C9a0300::fn_005a0300(unsigned int index, unsigned int value) {
    unsigned int* p = field10;
    if (p == 0) return;
    if (index >= p[0]) return;
    p[index + 1] = value;
}
