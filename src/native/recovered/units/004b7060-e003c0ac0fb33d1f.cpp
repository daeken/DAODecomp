struct C4A4B30 {
    unsigned char pad0[0x40];
    unsigned int f40;
    bool fn_004a4b30();
};

struct C4A8520 {
    unsigned int f00;
    unsigned int f04;
    unsigned int f08;
    unsigned int f0C;
    unsigned int f10;
    unsigned int pad14;
    unsigned int f18;
    unsigned int f1C;
    unsigned int f20;
    unsigned int pad24;
    unsigned int f28;
    unsigned int f2C;
    unsigned int f30;
    unsigned int f34;
    unsigned int f38;
    unsigned int pad3C;
    unsigned int f40;
    unsigned int f44;
    void fn_004a8520();
};

struct C4A8870 {
    unsigned int f00;
    unsigned int f04;
    unsigned int f08;
    unsigned int pad0C;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int pad1C;
    unsigned int f20;
    unsigned int f24;
    void fn_004a8870();
};

struct C4AB3F0 {
    unsigned int f00;
    unsigned int f04;
    unsigned int f08;
    unsigned int f0C;
    unsigned int pad10;
    unsigned int f14;
    unsigned int f18;
    unsigned int f1C;
    unsigned int pad20;
    unsigned int f24;
    unsigned int f28;
    unsigned int f2C;
    unsigned int pad30;
    unsigned int f34;
    unsigned int f38;
    unsigned int f3C;
    unsigned int pad40;
    unsigned int f44;
    unsigned int f48;
    unsigned int f4C;
    unsigned int pad50;
    unsigned int f54;
    unsigned int f58;
    unsigned int f5C;
    unsigned int pad60;
    unsigned int f64;
    unsigned int f68;
    void fn_004ab3f0();
};

struct C4AC290 {
    unsigned int f00;
    unsigned int f04;
    unsigned int f08;
    unsigned int f0C;
    unsigned int f10;
    unsigned int pad14;
    unsigned int f18;
    unsigned int f1C;
    unsigned int f20;
    unsigned int pad24;
    unsigned int f28;
    unsigned int f2C;
    unsigned int f30;
    unsigned int f34;
    unsigned int pad38;
    unsigned int f3C;
    unsigned int f40;
    unsigned int f44;
    unsigned int pad48;
    unsigned int f4C;
    void fn_004ac290();
};

struct C4AD860 {
    unsigned int f00;
    unsigned int f04;
    unsigned int f08;
    unsigned int f0C;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int pad1C;
    unsigned int f20;
    void fn_004ad860();
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

struct C4B7060 {
    unsigned char pad0[0x18];
    int count18;
    unsigned int arr1C[32];
    void fn_004b7060(unsigned int v);
};

struct C4BSetters {
    unsigned char pad0[0x2b8];
    unsigned int f2B8;
    unsigned int f2BC;
    unsigned char pad2C0[8];
    unsigned int f2C8;
    unsigned int f2CC;
    unsigned int f2D0;
    void fn_004b7150(unsigned int v);
    void fn_004b7160(unsigned int v);
    void fn_004b7170(unsigned int v);
    void fn_004b7180(unsigned int v);
    void fn_004b7190(unsigned int v);
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
bool C4A4B30::fn_004a4b30() {
    return f40 != 0;
}

// FUNCTION: DAO 0x8A8520
void C4A8520::fn_004a8520() {
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
}

// FUNCTION: DAO 0x8A8870
void C4A8870::fn_004a8870() {
    f00 = 0;
    f04 = 0;
    f08 = 0;
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f20 = 0;
    f24 = 0;
}

// FUNCTION: DAO 0x8AB3F0
void C4AB3F0::fn_004ab3f0() {
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
}

// FUNCTION: DAO 0x8AC290
void C4AC290::fn_004ac290() {
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
}

// FUNCTION: DAO 0x8AD860
void C4AD860::fn_004ad860() {
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f00 = 0;
    f04 = 0;
    f08 = 0;
    f0C = 0;
    f20 = 0;
}

// FUNCTION: DAO 0x8B68F0
bool C4B68F0::fn_004b68f0() {
    unsigned int n = c2D0;
    if (n == 0) return false;
    --n;
    c2D0 = n;
    f8 = a1D0[n];
    return true;
}

// FUNCTION: DAO 0x8B6920
int C4B6920::fn_004b6920(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8, int a9, int a10) {
    int args[11];
    args[0] = a0;
    args[1] = a1;
    args[2] = a2;
    args[3] = a3;
    args[4] = a4;
    args[5] = a5;
    args[6] = a6;
    args[7] = a7;
    args[8] = a8;
    args[9] = a9;
    args[10] = a10;
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

// FUNCTION: DAO 0x8B7060
void C4B7060::fn_004b7060(unsigned int v) {
    if (count18 < 0x20) {
        arr1C[count18] = v;
        ++count18;
    }
}

// FUNCTION: DAO 0x8B7150
void C4BSetters::fn_004b7150(unsigned int v) {
    f2B8 = v;
}

// FUNCTION: DAO 0x8B7160
void C4BSetters::fn_004b7160(unsigned int v) {
    f2BC = v;
}

// FUNCTION: DAO 0x8B7170
void C4BSetters::fn_004b7170(unsigned int v) {
    f2C8 = v;
}

// FUNCTION: DAO 0x8B7180
void C4BSetters::fn_004b7180(unsigned int v) {
    f2D0 = v;
}

// FUNCTION: DAO 0x8B7190
void C4BSetters::fn_004b7190(unsigned int v) {
    f2CC = v;
}

// FUNCTION: DAO 0x8B7500
Entry4B7500* __cdecl fn_004b7500(Container4B7500* obj, const char* name, int* outIndex) {
    if (name == 0) return 0;
    unsigned int count = (unsigned int)(obj->end - obj->begin);
    if (count == 0) return 0;
    for (unsigned int i = 0; i < count; ++i) {
        Entry4B7500* e = obj->begin[i];
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
    unsigned int count = (unsigned int)(obj->end - obj->begin);
    if (count == 0) return 0;
    for (unsigned int i = 0; i < count; ++i) {
        Entry4B75A0* e = obj->begin[i];
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
