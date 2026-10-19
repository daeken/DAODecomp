class C546c10 {
public:
    unsigned int pad0;
    unsigned char* data;
    void fn_00546c10(int* a, int* b, int* c);
};

struct Pair0054e080 {
    unsigned int key;
    unsigned int value;
};

class C54e080 {
public:
    unsigned int pad0[6];
    unsigned int f18;
    unsigned int f1c;
    unsigned int fn_0054e080(unsigned int key);
};

class C54e510 {
public:
    unsigned int f00, f04, f08, f0c, f10, f14, f18, f1c, f20, f24, f28, f2c;
    unsigned int f30, f34, f38, f3c, f40, f44, f48, f4c, f50, f54, f58, f5c, f60, f64;
    C54e510* fn_0054e510();
};

class C54f0f0 {
public:
    unsigned char pad[0x7d0];
    unsigned int f7d0;
    unsigned int f7d4;
    unsigned int pad2[8];
    unsigned int f7f8;
    C54f0f0* fn_0054f0f0();
};

class C54f160 {
public:
    unsigned int f00, f04, f08;
    C54f160* fn_0054f160(unsigned int* arg);
};

class C552020 {
public:
    unsigned int f0;
    int fn_00552020(unsigned int* nodePtr, int index);
};

class C5520e0 {
public:
    unsigned int f0;
    int fn_005520e0(unsigned int* nodePtr, int index);
};

// FUNCTION: DAO 0x00946C10
void C546c10::fn_00546c10(int* a, int* b, int* c) {
    unsigned char* p = data;
    unsigned char t = *p;
    if (((t & 1) != 0) || ((t & 6) == 2)) {
        unsigned char v;
        v = p[1];
        p += 1;
        *a = (int)v;
        v = p[1];
        p += 1;
        *b = (int)v;
        v = p[1];
        *c = (int)v;
        return;
    }
    if ((t & 7) == 0) {
        return;
    }
    if ((t & 6) == 4) {
        unsigned short* q = (unsigned short*)(((unsigned int)p + 2) & 0xFFFFFFFEu);
        unsigned short v;
        *a = (int)q[0];
        v = q[1];
        q = (unsigned short*)((unsigned char*)q + 2);
        *b = (int)v;
        *c = (int)q[1];
    } else {
        unsigned int* q = (unsigned int*)(((unsigned int)p + 4) & 0xFFFFFFFCu);
        unsigned int v;
        *a = (int)q[0];
        v = q[1];
        q = (unsigned int*)((unsigned char*)q + 4);
        *b = (int)v;
        *c = (int)q[1];
    }
}

// FUNCTION: DAO 0x0094E080
unsigned int C54e080::fn_0054e080(unsigned int key) {
    unsigned int count = f1c;
    if (count == 0) {
        return 0;
    }
    Pair0054e080* base = (Pair0054e080*)f18;
    unsigned int i = 0;
    do {
        if (base[i].key == key) {
            return base[i].value;
        }
        ++i;
    } while (i < count);
    return 0;
}

// FUNCTION: DAO 0x0094E510
C54e510* C54e510::fn_0054e510() {
    C54e510* p = this;
    unsigned int z = 0;
    p->f04 = z;
    p->f08 = z;
    p->f00 = z;
    p->f10 = z;
    p->f14 = z;
    p->f0c = z;
    p->f1c = z;
    p->f20 = z;
    p->f18 = z;
    p->f28 = z;
    p->f2c = z;
    p->f24 = z;
    p->f34 = z;
    p->f38 = z;
    p->f30 = z;
    p->f40 = z;
    p->f44 = z;
    p->f3c = z;
    p->f4c = z;
    p->f50 = z;
    p->f48 = z;
    p->f54 = 1;
    p->f58 = z;
    p->f64 = 1;
    p->f5c = 1;
    p->f60 = z;
    return p;
}

// FUNCTION: DAO 0x0094F0F0
C54f0f0* C54f0f0::fn_0054f0f0() {
    C54f0f0* p = this;
    unsigned int z = 0;
    p->f7d0 = z;
    p->f7d4 = z;
    p->f7f8 = z;
    return p;
}

// FUNCTION: DAO 0x0094F160
C54f160* C54f160::fn_0054f160(unsigned int* arg) {
    C54f160* p = this;
    p->f00 = arg[0];
    p->f04 = arg[1];
    ++(*(unsigned int*)(p->f04 + 0xc));
    p->f08 = arg[2];
    return p;
}

// FUNCTION: DAO 0x00952020
int C552020::fn_00552020(unsigned int* nodePtr, int index) {
    unsigned int* base = (unsigned int*)f0;
    unsigned int idx = (unsigned int)index;
    unsigned int* node = base + 2 + idx * 3;
    unsigned int result = idx;
    if (node[0] == 0xFFFFFFFEu) {
        return -1;
    }
    unsigned int mask = base[1];
    unsigned int v = node[1];
    if (((*(unsigned int*)(v + 0x10)) & mask) != idx) {
        return -1;
    }
    for (;;) {
        v = node[1];
        if (((*(unsigned int*)(v + 0x10)) & mask) == idx) {
            if (v == *nodePtr) {
                break;
            }
        }
        unsigned int next = node[0];
        if (next == 0xFFFFFFFFu) {
            return -1;
        }
        result = next;
        node = base + 2 + next * 3;
    }
    return (int)result;
}

// FUNCTION: DAO 0x009520E0
int C5520e0::fn_005520e0(unsigned int* nodePtr, int index) {
    unsigned int* base = (unsigned int*)f0;
    unsigned int idx = (unsigned int)index;
    unsigned int* node = base + 2 + idx * 7;
    unsigned int result = idx;
    if (node[0] == 0xFFFFFFFEu) {
        return -1;
    }
    unsigned int mask = base[1];
    unsigned int v = node[1];
    if (((*(unsigned int*)(v + 0x10)) & mask) != idx) {
        return -1;
    }
    for (;;) {
        v = node[1];
        if (((*(unsigned int*)(v + 0x10)) & mask) == idx) {
            if (v == *nodePtr) {
                break;
            }
        }
        unsigned int next = node[0];
        if (next == 0xFFFFFFFFu) {
            return -1;
        }
        result = next;
        node = base + 2 + next * 7;
    }
    return (int)result;
}
