struct C4A4B30 {
    unsigned char pad0[0x40];
    unsigned int f40;
    unsigned char fn_004a4b30();
};

struct C4A8520 {
    unsigned int f00, f04, f08, f0C, f10, pad14, f18, f1C, f20, pad24, f28, f2C, f30, f34, f38, pad3C, f40, f44;
    C4A8520* fn_004a8520();
};

struct C4A8870 {
    unsigned int f00, f04, f08, pad0C, f10, f14, f18, pad1C, f20, f24;
    C4A8870* fn_004a8870();
};

struct C4AB3F0 {
    unsigned int f00, f04, f08, f0C, pad10, f14, f18, f1C, pad20, f24, f28, f2C, pad30, f34, f38, f3C, pad40, f44, f48, f4C, pad50, f54, f58, f5C, pad60, f64, f68;
    C4AB3F0* fn_004ab3f0();
};

struct C4AC290 {
    unsigned int f00, f04, f08, f0C, f10, pad14, f18, f1C, f20, pad24, f28, f2C, f30, f34, pad38, f3C, f40, f44, pad48, f4C;
    C4AC290* fn_004ac290();
};

struct C4AD860 {
    unsigned int f00, f04, f08, f0C, f10, f14, f18, pad1C, f20;
    C4AD860* fn_004ad860();
};

struct C4B68F0 {
    unsigned char pad0[8];
    unsigned int f8;
    unsigned char padC[0x1d0 - 0xC];
    unsigned int a1D0[64];
    unsigned int c2D0;
    bool fn_004b68f0();
};

struct Entry4B6920 {
    unsigned char pad0[0x18];
    int f18;
    int f1C;
};

struct C4B6920 {
    unsigned char pad0[8];
    unsigned int f8;
    unsigned char padC[4];
    Entry4B6920* arr[0x6c];
    int fn_004b6920(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8, int a9, int a10);
};

struct Entry4B7500 {
    const char* name;
};

struct Container4B7500 {
    unsigned char pad0[0x90];
    Entry4B7500** begin;
    Entry4B7500** end;
};

struct Entry4B75A0 {
    const char* name;
};

struct Container4B75A0 {
    unsigned char pad0[0x30];
    Entry4B75A0** begin;
    Entry4B75A0** end;
};

// FUNCTION: DAO 0x8A4B30
unsigned char C4A4B30::fn_004a4b30() {
    return f40 != 0;
}

// FUNCTION: DAO 0x8A8520
C4A8520* C4A8520::fn_004a8520() {
    f08 = 0;
    f0C = 0;
    f10 = 0;
    f18 = 0;
    f1C = 0;
    f20 = 0;
    f30 = 0;
    f34 = 0;
    f38 = 0;
    f00 = 0;
    f04 = 0;
    f28 = 0;
    f2C = 0;
    f40 = 0;
    f44 = 0;
    return this;
}

// FUNCTION: DAO 0x8A8870
C4A8870* C4A8870::fn_004a8870() {
    f00 = 0;
    f04 = 0;
    f08 = 0;
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f20 = 0;
    f24 = 0;
    return this;
}

// FUNCTION: DAO 0x8AB3F0
C4AB3F0* C4AB3F0::fn_004ab3f0() {
    f04 = 0;
    f08 = 0;
    f0C = 0;
    f14 = 0;
    f18 = 0;
    f1C = 0;
    f24 = 0;
    f28 = 0;
    f2C = 0;
    f34 = 0;
    f38 = 0;
    f3C = 0;
    f44 = 0;
    f48 = 0;
    f4C = 0;
    f54 = 0;
    f58 = 0;
    f5C = 0;
    f00 = 0;
    f64 = 0;
    f68 = 0;
    return this;
}

// FUNCTION: DAO 0x8AC290
C4AC290* C4AC290::fn_004ac290() {
    f08 = 0;
    f0C = 0;
    f10 = 0;
    f18 = 0;
    f1C = 0;
    f20 = 0;
    f2C = 0;
    f30 = 0;
    f34 = 0;
    f3C = 0;
    f40 = 0;
    f44 = 0;
    f00 = 0;
    f04 = 0;
    f28 = 0;
    f4C = 0;
    return this;
}

// FUNCTION: DAO 0x8AD860
C4AD860* C4AD860::fn_004ad860() {
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f00 = 0;
    f04 = 0;
    f08 = 0;
    f0C = 0;
    f20 = 0;
    return this;
}

// FUNCTION: DAO 0x8B68F0
bool C4B68F0::fn_004b68f0() {
    bool result = false;
    unsigned int n = c2D0;
    if (n != 0) {
        unsigned int i = n - 1;
        c2D0 = i;
        f8 = a1D0[i];
        result = true;
    }
    return result;
}

// FUNCTION: DAO 0x8B6920
int C4B6920::fn_004b6920(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8, int a9, int a10) {
    int args[11] = { a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 };
    int best = 0xf423f;
    int idx = -1;
    for (int i = 0; i < 11; ++i) {
        int v = args[i];
        if (v < 0) continue;
        if (v >= 0x6c) continue;
        Entry4B6920* e = arr[v];
        if (e == 0) continue;
        if (e->f18 != (int)f8) continue;
        int y = e->f1C;
        if (y >= best) continue;
        best = y;
        idx = v;
    }
    return idx;
}

// FUNCTION: DAO 0x8B7500
Entry4B7500* __cdecl fn_004b7500(Container4B7500* obj, const char* name, int* outIndex) {
    if (name == 0) return 0;
    Entry4B7500** begin = obj->begin;
    Entry4B7500** end = obj->end;
    unsigned int count = (unsigned int)(end - begin);
    if (count == 0) return 0;
    for (unsigned int i = 0; i < count; ++i) {
        Entry4B7500* e = begin[i];
        const char* s1 = e->name;
        if (s1 == 0) continue;
        const char* s2 = name;
        bool equal = false;
        for (;;) {
            unsigned char c = (unsigned char)*s1;
            if (c != (unsigned char)*s2) break;
            if (c == 0) { equal = true; break; }
            c = (unsigned char)s1[1];
            if (c != (unsigned char)s2[1]) break;
            if (c == 0) { equal = true; break; }
            s1 += 2;
            s2 += 2;
        }
        if (equal) {
            *outIndex = (int)i;
            return e;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8B75A0
Entry4B75A0* __cdecl fn_004b75a0(Container4B75A0* obj, const char* name) {
    Entry4B75A0** begin = obj->begin;
    Entry4B75A0** end = obj->end;
    unsigned int count = (unsigned int)(end - begin);
    if (count == 0) return 0;
    for (unsigned int i = 0; i < count; ++i) {
        Entry4B75A0* e = begin[i];
        const char* s1 = e->name;
        if (s1 == 0) continue;
        const char* s2 = name;
        bool equal = false;
        for (;;) {
            unsigned char c = (unsigned char)*s1;
            if (c != (unsigned char)*s2) break;
            if (c == 0) { equal = true; break; }
            c = (unsigned char)s1[1];
            if (c != (unsigned char)s2[1]) break;
            if (c == 0) { equal = true; break; }
            s1 += 2;
            s2 += 2;
        }
        if (equal) return e;
    }
    return 0;
}
