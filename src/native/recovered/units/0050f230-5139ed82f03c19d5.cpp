struct C50F230 { unsigned short* data; int len; void fn_0050f230(); };
struct C510170 { char pad0[0x310]; void* m310; void* fn_00510170(); unsigned int fn_00510220(); };
struct C515440 { void* m0; int fn_00515440(void*, int); int fn_005154a0(void*, int); int fn_00518090(void*, int); };
struct C515AD0 { char pad0[0x24]; unsigned int m24; void* fn_00515ad0(); };
struct C5171E0 { void* m0; void* m4; void* m8; void fn_005171e0(); };
struct C517250 { char pad0[0x70]; int m70; char pad74[4]; unsigned char m78; int fn_00517250(); };
struct C517DE0 { char pad0[0x10]; unsigned int m10; unsigned int m14; unsigned int m18; unsigned int m1c; unsigned int m20; unsigned int m24; unsigned int m28; unsigned int m2c; unsigned int fn_00517de0(); int fn_00517e00(void*); };
struct C517FB0 { void* m0; unsigned int m4; void fn_00517fb0(); };
struct C518000 { void* m0; unsigned int m4; int fn_00518000(void*); };
struct C518B10 { char pad0[0xb0]; void* m_b0; void* fn_00518b10(unsigned int); };
struct C51DCC0 { char pad0[0x10]; void* m10; void* fn_0051dcc0(unsigned int); };
struct C5601A0 { char pad0[0x20]; void* m20; void* fn_005601a0(); };

// FUNCTION: DAO 0x0090F230
void C50F230::fn_0050f230() {
    int n = len;
    if (n > 0) {
        if (data[n - 1] == 0) {
            --n;
        }
    }
    int i = n - 1;
    if (i >= 0) {
        do {
            unsigned short ch = data[i];
            if (ch == 0x0A || ch == 0x0D) {
                --len;
                data[i] = 0;
                --i;
            } else {
                break;
            }
        } while (i >= 0);
    }
}

// FUNCTION: DAO 0x00910170
void* C510170::fn_00510170() {
    if (m310) return m310;
    return (char*)this + 0x30;
}

// FUNCTION: DAO 0x00910220
unsigned int C510170::fn_00510220() {
    void* base = m310;
    if (!base) base = (char*)this + 0x30;
    unsigned char* p = (unsigned char*)base;
    return *(unsigned int*)(p + 0x30) - *(unsigned int*)(p + 0x2c) + *(unsigned int*)(p + 0x28);
}

// FUNCTION: DAO 0x00915440
int C515440::fn_00515440(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    unsigned char* entry = base + 8 + (unsigned int)key * 12u;
    if (*(int*)(entry + 8) == -2) return -1;
    if (*(int*)(entry + 4) != key) return -1;
    int idx = key;
    for (;;) {
        if (*(int*)(entry + 4) == key) {
            void* obj = *(void**)(entry + 8);
            void* other = *(void**)arg1;
            if (*(void**)((char*)obj + 0x10) == *(void**)((char*)other + 0x10)) return idx;
        }
        int next = *(int*)entry;
        if (next == -1) return -1;
        idx = next;
        entry = base + 8 + (unsigned int)idx * 12u;
    }
}

// FUNCTION: DAO 0x009154A0
int C515440::fn_005154a0(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    unsigned char* entry = base + 8 + (unsigned int)key * 12u;
    if (*(int*)(entry + 8) == -2) return -1;
    if (*(int*)(entry + 4) != key) return -1;
    int idx = key;
    for (;;) {
        if (*(int*)(entry + 4) == key) {
            void* obj = *(void**)(entry + 8);
            if (*(void**)((char*)obj + 0x10) == *(void**)arg1) return idx;
        }
        int next = *(int*)entry;
        if (next == -1) return -1;
        idx = next;
        entry = base + 8 + (unsigned int)idx * 12u;
    }
}

// FUNCTION: DAO 0x00915AD0
void* C515AD0::fn_00515ad0() {
    unsigned int n = m24;
    if ((n - 1) >= 2) return 0;
    return *(void**)((char*)this + 0x18 + n * 4u);
}

// FUNCTION: DAO 0x009171E0
void C5171E0::fn_005171e0() {
    m8 = 0;
    m0 = 0;
    m4 = 0;
}

// FUNCTION: DAO 0x00917250
int C517250::fn_00517250() {
    int v = 1;
    if (m70 <= v) m78 = (unsigned char)v;
    return v;
}

// FUNCTION: DAO 0x00917DE0
unsigned int C517DE0::fn_00517de0() {
    unsigned int v = m2c;
    v ^= m28;
    v ^= m24;
    v ^= m20;
    v ^= m1c;
    v ^= m18;
    v ^= m14;
    v ^= m10;
    return (v >> 7) ^ v;
}

// FUNCTION: DAO 0x00917E00
int C517DE0::fn_00517e00(void* other) {
    unsigned char* p = (unsigned char*)other;
    if (m10 != *(unsigned int*)(p + 0x10)) return 0;
    if (m14 != *(unsigned int*)(p + 0x14)) return 0;
    if (m18 != *(unsigned int*)(p + 0x18)) return 0;
    if (m1c != *(unsigned int*)(p + 0x1c)) return 0;
    if (m20 != *(unsigned int*)(p + 0x20)) return 0;
    if (m24 != *(unsigned int*)(p + 0x24)) return 0;
    if (m28 != *(unsigned int*)(p + 0x28)) return 0;
    if (m2c != *(unsigned int*)(p + 0x2c)) return 0;
    return 1;
}

// FUNCTION: DAO 0x00917FB0
void C517FB0::fn_00517fb0() {
    unsigned char* block = *(unsigned char**)m0;
    unsigned int cap = *(unsigned int*)(block + 4);
    unsigned int i = m4;
    if (i > cap) return;
    ++i;
    m4 = i;
    if (i > cap) return;
    do {
        if (*(int*)(block + i * 16u + 8u) != -2) return;
        ++i;
        m4 = i;
    } while (i <= cap);
}

// FUNCTION: DAO 0x00918000
int C518000::fn_00518000(void* other) {
    void* eax = m0;
    if (eax != 0 && *(void**)eax != 0) {
        void* edx = *(void**)eax;
        if (m4 <= *(unsigned int*)((char*)edx + 4)) goto L_compare;
    }
    {
        void* edx = *(void**)other;
        if (edx != 0 && *(void**)edx != 0) {
            void* edx2 = *(void**)edx;
            if (*(unsigned int*)((char*)other + 4) <= *(unsigned int*)((char*)edx2 + 4)) goto L_compare;
        }
    }
    return 1;
L_compare:
    if (eax != *(void**)other) return 0;
    if (m4 != *(unsigned int*)((char*)other + 4)) return 0;
    return 1;
}

// FUNCTION: DAO 0x00918090
int C515440::fn_00518090(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    unsigned char* entry = base + 8 + (unsigned int)key * 12u;
    if (*(int*)(entry + 8) == -2) return -1;
    if (*(int*)(entry + 4) != key) return -1;
    int idx = key;
    for (;;) {
        if (*(int*)(entry + 4) == key) {
            char* a = (char*)(*(void**)(entry + 8)) + 0xc;
            char* b = (char*)(*(void**)arg1) + 0xc;
            for (;;) {
                if (*a != *b) break;
                if (*a == 0) return idx;
                ++a;
                ++b;
            }
        }
        int next = *(int*)entry;
        if (next == -1) return -1;
        idx = next;
        entry = base + 8 + (unsigned int)idx * 12u;
    }
}

// FUNCTION: DAO 0x00918B10
void* C518B10::fn_00518b10(unsigned int key) {
    void* p = m_b0;
    if (!p) return 0;
    for (;;) {
        if (*(unsigned int*)p == key) return *(void**)((char*)p + 4);
        p = *(void**)((char*)p + 0xc);
        if (!p) return 0;
    }
}

// FUNCTION: DAO 0x0091DCC0
void* C51DCC0::fn_0051dcc0(unsigned int flags) {
    if (flags & 0x80) return 0;
    void* p = *(void**)((char*)m10 + 0x18);
    if (!p) return 0;
    if (*(unsigned char*)((char*)p + 0x14) != 0) return 0;
    return p;
}

// FUNCTION: DAO 0x009601A0
void* C5601A0::fn_005601a0() {
    return m20;
}
