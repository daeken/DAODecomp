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

class C54db90 {
public:
    unsigned char pad[0x7d0];
    unsigned int f7d0;
    unsigned int f7d4;
    unsigned int* fn_0054db90();
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
    int fn_00552020(int index, unsigned int* nodePtr);
};

class C5520e0 {
public:
    unsigned int f0;
    int fn_005520e0(int index, unsigned int* nodePtr);
};

class C55de70 {
public:
    unsigned int f0;
    int fn_0055de70(unsigned int offset, int* out);
};

// FUNCTION: DAO 0x00946C10
void C546c10::fn_00546c10(int* a, int* b, int* c) {
    unsigned char* p = data;
    unsigned char t = *p;
    if ((t & 1) != 0 || (t & 6) == 2) {
        *a = (int)p[1];
        *b = (int)p[2];
        *c = (int)p[3];
        return;
    }
    if ((t & 7) == 0) {
        return;
    }
    if ((t & 6) == 4) {
        unsigned int base = (unsigned int)(p + 2);
        base &= 0xFFFFFFFEu;
        unsigned short* q = (unsigned short*)base;
        *a = (int)q[0];
        *b = (int)q[1];
        *c = (int)q[2];
    } else {
        unsigned int base = (unsigned int)(p + 4);
        base &= 0xFFFFFFFCu;
        unsigned int* q = (unsigned int*)base;
        *a = (int)q[0];
        *b = (int)q[1];
        *c = (int)q[2];
    }
}

// FUNCTION: DAO 0x0094D540
void C54d540::fn_0054d540() {
    unsigned int eax = f3c;
    unsigned int edx = 0;
    unsigned int esi;
    if (eax != edx) goto L552;
    if (f48 == edx) return;
L552:
    if (eax == edx) goto L58c;
    eax = f34;
    if (eax != edx) goto L56e;
    eax = f44;
    esi = f30;
    *(unsigned int*)eax = esi;
    eax = f3c;
    f30 = eax;
    goto L57d;
L56e:
    esi = f44;
    eax = *(unsigned int*)eax;
    *(unsigned int*)esi = eax;
    eax = f34;
    esi = f3c;
    *(unsigned int*)eax = esi;
L57d:
    eax = f44;
    f34 = eax;
    f40 = edx;
    f44 = edx;
    f3c = edx;
L58c:
    if (f48 == edx) return;
    eax = f34;
    if (eax != edx) goto L5b7;
    eax = f50;
    esi = f30;
    *(unsigned int*)eax = esi;
    eax = f48;
    f30 = eax;
    eax = f50;
    f34 = eax;
    f4c = edx;
    f50 = edx;
    f48 = edx;
    return;
L5b7:
    eax = *(unsigned int*)eax;
    esi = f50;
    *(unsigned int*)esi = eax;
    eax = f34;
    esi = f48;
    *(unsigned int*)eax = esi;
    eax = f50;
    f34 = eax;
    f4c = edx;
    f50 = edx;
    f48 = edx;
}

// FUNCTION: DAO 0x0094DB90
unsigned int* C54db90::fn_0054db90() {
    if (f7d4 == 100) {
        f7d0 += 1;
        unsigned int eax = f7d0;
        f7d4 = 0x63;
        if (eax == 100) f7d0 = 0;
    }
    unsigned int edx = f7d4;
    unsigned int eax = f7d0 + edx;
    if (eax >= 100) eax -= 100;
    edx += 1;
    f7d4 = edx;
    unsigned int off = eax * 5 * 4;
    return (unsigned int*)((unsigned char*)this + off);
}

// FUNCTION: DAO 0x0094E080
unsigned int C54e080::fn_0054e080(unsigned int key) {
    unsigned int count = f1c;
    if (count == 0) return 0;
    unsigned int* p = (unsigned int*)f18;
    unsigned int i = 0;
    while (i < count) {
        if (p[0] == key) return p[1];
        i += 1;
        p += 2;
    }
    return 0;
}

// FUNCTION: DAO 0x0094E510
void C54e510::fn_0054e510() {
    f04 = 0;
    f08 = 0;
    f00 = 0;
    f10 = 0;
    f14 = 0;
    f0c = 0;
    f1c = 0;
    f20 = 0;
    f18 = 0;
    f28 = 0;
    f2c = 0;
    f24 = 0;
    f34 = 0;
    f38 = 0;
    f30 = 0;
    f40 = 0;
    f44 = 0;
    f3c = 0;
    f4c = 0;
    f50 = 0;
    f48 = 0;
    f54 = 1;
    f58 = 0;
    f64 = 1;
    f5c = 1;
    f60 = 0;
}

// FUNCTION: DAO 0x0094F0F0
void C54f0f0::fn_0054f0f0() {
    f7d0 = 0;
    f7d4 = 0;
    f7f8 = 0;
}

// FUNCTION: DAO 0x0094F160
void C54f160::fn_0054f160(unsigned int* arg) {
    unsigned int a0 = arg[0];
    unsigned int a1 = arg[1];
    f00 = a0;
    f04 = a1;
    ++(*(unsigned int*)(a1 + 0xc));
    f08 = arg[2];
}

// FUNCTION: DAO 0x00952020
int C552020::fn_00552020(int index, unsigned int* nodePtr) {
    unsigned int base = f0;
    unsigned int esi = (unsigned int)index;
    unsigned int edi = base;
    unsigned int ecx = base + 8 + 12 * esi;
    unsigned int eax = esi;
    if (*(unsigned int*)ecx == 0xFFFFFFFEu) return -1;
    unsigned int edx = *(unsigned int*)(ecx + 4);
    unsigned int ebx = *(unsigned int*)(edi + 4);
    edx = *(unsigned int*)(edx + 0x10);
    edx &= ebx;
    if (edx != esi) return -1;
    for (;;) {
        edx = *(unsigned int*)(ecx + 4);
        unsigned int ebp = *(unsigned int*)(edx + 0x10);
        ebp &= ebx;
        if (ebp == esi) {
            if (edx == *nodePtr) break;
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
int C5520e0::fn_005520e0(int index, unsigned int* nodePtr) {
    unsigned int base = f0;
    unsigned int esi = (unsigned int)index;
    unsigned int edi = base;
    unsigned int ecx = base + 8 + 28 * esi;
    unsigned int eax = esi;
    if (*(unsigned int*)ecx == 0xFFFFFFFEu) return -1;
    unsigned int edx = *(unsigned int*)(ecx + 4);
    unsigned int ebx = *(unsigned int*)(edi + 4);
    edx = *(unsigned int*)(edx + 0x10);
    edx &= ebx;
    if (edx != esi) return -1;
    for (;;) {
        edx = *(unsigned int*)(ecx + 4);
        unsigned int ebp = *(unsigned int*)(edx + 0x10);
        ebp &= ebx;
        if (ebp == esi) {
            if (edx == *nodePtr) break;
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

// FUNCTION: DAO 0x0095DE70
int C55de70::fn_0055de70(unsigned int offset, int* out) {
    unsigned int pagesAddr = *(unsigned int*)(f0 + 0xc);
    unsigned int* pages = (unsigned int*)pagesAddr;
    unsigned int page = pages[offset >> 12];
    unsigned char* p = (unsigned char*)page;
    int eax = (int)(signed char)p[offset & 0xfff];
    if ((eax & 1) == 0) {
        *out = eax >> 1;
        return 1;
    }
    unsigned int off2 = offset + 1;
    unsigned int page2 = pages[off2 >> 12];
    unsigned char* p2 = (unsigned char*)page2;
    int ecx = (int)(signed char)p2[off2 & 0xfff];
    unsigned int uecx = (unsigned int)ecx;
    unsigned int uval = (uecx << 7) | ((unsigned int)(eax >> 1) & 0x7fu);
    *out = (int)uval;
    return 2;
}
