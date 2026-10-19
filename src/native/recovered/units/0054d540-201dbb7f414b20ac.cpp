struct Pair0054e080 {
    unsigned int key;
    unsigned int value;
};

class C546c10 {
public:
    unsigned int pad0;
    unsigned char* data;
    void fn_00546c10(int* a, int* b, int* c);
};

class C54d540 {
public:
    unsigned int pad0[12];
    unsigned int f30;
    unsigned int f34;
    unsigned int f38;
    unsigned int f3c;
    unsigned int f40;
    unsigned int f44;
    unsigned int f48;
    unsigned int f4c;
    unsigned int f50;
    void fn_0054d540();
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
    void fn_0054e510();
};

class C54f0f0 {
public:
    unsigned char pad[0x7d0];
    unsigned int f7d0;
    unsigned int f7d4;
    unsigned int pad2[8];
    unsigned int f7f8;
    void fn_0054f0f0();
};

class C54f160 {
public:
    unsigned int f00, f04, f08;
    void fn_0054f160(unsigned int* arg);
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
    if ((t & 1) != 0 || (t & 6) == 2) {
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
        unsigned int base = (unsigned int)(p + 2);
        base &= 0xFFFFFFFEu;
        unsigned short* q = (unsigned short*)base;
        unsigned int v;
        v = (unsigned int)q[0];
        *a = (int)v;
        v = (unsigned int)q[1];
        q = (unsigned short*)((unsigned char*)q + 2);
        *b = (int)v;
        v = (unsigned int)q[1];
        *c = (int)v;
    } else {
        unsigned int base = (unsigned int)(p + 4);
        base &= 0xFFFFFFFCu;
        unsigned int* q = (unsigned int*)base;
        unsigned int v;
        v = q[0];
        *a = (int)v;
        v = q[1];
        q = (unsigned int*)((unsigned char*)q + 4);
        *b = (int)v;
        v = q[1];
        *c = (int)v;
    }
}

// FUNCTION: DAO 0x0094D540
void C54d540::fn_0054d540() {
    if (f3c == 0 && f48 == 0) {
        return;
    }
    if (f3c != 0) {
        if (f34 == 0) {
            *(unsigned int*)f44 = f30;
            f30 = f3c;
        } else {
            *(unsigned int*)f44 = *(unsigned int*)f34;
            *(unsigned int*)f34 = f3c;
        }
        f34 = f44;
        f40 = 0;
        f44 = 0;
        f3c = 0;
    }
    if (f48 != 0) {
        if (f34 == 0) {
            *(unsigned int*)f50 = f30;
            f30 = f48;
            f34 = f50;
        } else {
            *(unsigned int*)f50 = *(unsigned int*)f34;
            *(unsigned int*)f34 = f48;
            f34 = f50;
        }
        f4c = 0;
        f50 = 0;
        f48 = 0;
    }
}

// FUNCTION: DAO 0x0094E080
unsigned int C54e080::fn_0054e080(unsigned int key) {
    unsigned int count = f1c;
    unsigned int i = 0;
    if (count == 0) {
        return 0;
    }
    Pair0054e080* p = (Pair0054e080*)f18;
    do {
        if (p[i].key == key) {
            return p[i].value;
        }
        ++i;
    } while (i < count);
    return 0;
}

// FUNCTION: DAO 0x0094E510
void C54e510::fn_0054e510() {
    unsigned int* p = (unsigned int*)this;
    unsigned int z = 0;
    p[1] = z;
    p[2] = z;
    p[0] = z;
    p[4] = z;
    p[5] = z;
    p[3] = z;
    p[7] = z;
    p[8] = z;
    p[6] = z;
    p[10] = z;
    p[11] = z;
    p[9] = z;
    p[13] = z;
    p[14] = z;
    p[12] = z;
    p[16] = z;
    p[17] = z;
    p[15] = z;
    p[19] = z;
    p[20] = z;
    p[18] = z;
    p[21] = 1;
    p[22] = z;
    p[25] = 1;
    p[23] = 1;
    p[24] = z;
}

// FUNCTION: DAO 0x0094F0F0
void C54f0f0::fn_0054f0f0() {
    unsigned int* p = (unsigned int*)this;
    unsigned int z = 0;
    p[500] = z;
    p[501] = z;
    p[510] = z;
}

// FUNCTION: DAO 0x0094F160
void C54f160::fn_0054f160(unsigned int* arg) {
    unsigned int* p = (unsigned int*)this;
    unsigned int* a = arg;
    p[0] = a[0];
    unsigned int v = a[1];
    p[1] = v;
    ++(*(unsigned int*)(v + 0xc));
    p[2] = a[2];
}

// FUNCTION: DAO 0x00952020
int C552020::fn_00552020(unsigned int* nodePtr, int index) {
    unsigned int base = f0;
    unsigned int esi = (unsigned int)index;
    unsigned int edi = base;
    unsigned int ecx = base + 8 + 12 * esi;
    unsigned int eax = esi;
    if (*(unsigned int*)ecx == 0xFFFFFFFEu) {
        return -1;
    }
    unsigned int edx = *(unsigned int*)(ecx + 4);
    unsigned int ebx = *(unsigned int*)(edi + 4);
    edx = *(unsigned int*)(edx + 0x10);
    edx &= ebx;
    if (edx != esi) {
        return -1;
    }
    for (;;) {
        edx = *(unsigned int*)(ecx + 4);
        unsigned int ebp = *(unsigned int*)(edx + 0x10);
        ebp &= ebx;
        if (ebp == esi) {
            if (edx == *nodePtr) {
                break;
            }
        }
        unsigned int next = *(unsigned int*)ecx;
        if (next == 0xFFFFFFFFu) {
            eax = 0xFFFFFFFFu;
            break;
        }
        eax = next;
        ecx = base + 8 + 12 * next;
    }
    return (int)eax;
}

// FUNCTION: DAO 0x009520E0
int C5520e0::fn_005520e0(unsigned int* nodePtr, int index) {
    unsigned int base = f0;
    unsigned int esi = (unsigned int)index;
    unsigned int edi = base;
    unsigned int ecx = base + 8 + 28 * esi;
    unsigned int eax = esi;
    if (*(unsigned int*)ecx == 0xFFFFFFFEu) {
        return -1;
    }
    unsigned int edx = *(unsigned int*)(ecx + 4);
    unsigned int ebx = *(unsigned int*)(edi + 4);
    edx = *(unsigned int*)(edx + 0x10);
    edx &= ebx;
    if (edx != esi) {
        return -1;
    }
    for (;;) {
        edx = *(unsigned int*)(ecx + 4);
        unsigned int ebp = *(unsigned int*)(edx + 0x10);
        ebp &= ebx;
        if (ebp == esi) {
            if (edx == *nodePtr) {
                break;
            }
        }
        unsigned int next = *(unsigned int*)ecx;
        if (next == 0xFFFFFFFFu) {
            eax = 0xFFFFFFFFu;
            break;
        }
        eax = next;
        ecx = base + 8 + 28 * next;
    }
    return (int)eax;
}
