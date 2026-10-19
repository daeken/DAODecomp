struct C510220 { char pad0[0x310]; void* m310; unsigned int fn_00510220(); };
struct C515440 { void* m0; int fn_00515440(void*, int); int fn_005154a0(void*, int); int fn_00518090(void*, int); };
struct C515AD0 { char pad0[0x24]; unsigned int m24; void* fn_00515ad0(); };
struct C5171E0 { void* m0; void* m4; void* m8; C5171E0* fn_005171e0(); };
struct C517E00 { char pad0[0x10]; unsigned int m10; unsigned int m14; unsigned int m18; unsigned int m1c; unsigned int m20; unsigned int m24; unsigned int m28; unsigned int m2c; int fn_00517e00(void*); };
struct C517FB0 { void* m0; unsigned int m4; void fn_00517fb0(); };
struct C518000 { void* m0; unsigned int m4; int fn_00518000(void*); };
struct C518B10 { char pad0[0xb0]; void* m_b0; void* fn_00518b10(unsigned int); };
struct C51DCC0 { char pad0[0x10]; void* m10; void* fn_0051dcc0(unsigned int); };

// FUNCTION: DAO 0x00910220
unsigned int C510220::fn_00510220() {
    char* self = (char*)this;
    char* base = (char*)*(void**)(self + 0x310);
    if (base == 0) base = self + 0x30;
    return *(unsigned int*)(base + 0x30) - *(unsigned int*)(base + 0x2c) + *(unsigned int*)(base + 0x28);
}

// FUNCTION: DAO 0x00915440
int C515440::fn_00515440(void* arg1, int key) {
    int idx = key;
    unsigned char* base = *(unsigned char**)this;
    unsigned char* entry = base + 8 + (unsigned int)idx * 12u;
    if (*(int*)(entry + 8) == -2) return -1;
    if (*(int*)(entry + 4) != key) return -1;
    void** pother = (void**)arg1;
    for (;;) {
        if (*(int*)(entry + 4) == key) {
            void* obj = *(void**)(entry + 8);
            void* other = *pother;
            if (*(void**)((char*)obj + 0x10) == *(void**)((char*)other + 0x10))
                return idx;
        }
        int next = *(int*)entry;
        if (next == -1) return -1;
        idx = next;
        entry = base + 8 + (unsigned int)idx * 12u;
    }
}

// FUNCTION: DAO 0x009154A0
int C515440::fn_005154a0(void* arg1, int key) {
    int idx = key;
    unsigned char* base = *(unsigned char**)this;
    unsigned char* entry = base + 8 + (unsigned int)idx * 12u;
    if (*(int*)(entry + 8) == -2) return -1;
    if (*(int*)(entry + 4) != key) return -1;
    void** pother = (void**)arg1;
    for (;;) {
        if (*(int*)(entry + 4) == key) {
            void* obj = *(void**)(entry + 8);
            if (*(void**)((char*)obj + 0x10) == *pother)
                return idx;
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
    if ((n - 1) < 2)
        return *(void**)((char*)this + 0x18 + n * 4u);
    return 0;
}

// FUNCTION: DAO 0x009171E0
C5171E0* C5171E0::fn_005171e0() {
    m8 = 0;
    m0 = 0;
    m4 = 0;
    return this;
}

// FUNCTION: DAO 0x00917E00
int C517E00::fn_00517e00(void* other) {
    unsigned int* p = (unsigned int*)other;
    if (m10 == p[4] && m14 == p[5] && m18 == p[6] && m1c == p[7] &&
        m20 == p[8] && m24 == p[9] && m28 == p[10] && m2c == p[11])
        return 1;
    return 0;
}

// FUNCTION: DAO 0x00917FB0
void C517FB0::fn_00517fb0() {
    void** holder = (void**)m0;
    unsigned int i = m4;
    unsigned char* block = (unsigned char*)*holder;
    unsigned int cap = *(unsigned int*)(block + 4);
    if (i > cap) return;
    ++i;
    m4 = i;
    block = (unsigned char*)*holder;
    cap = *(unsigned int*)(block + 4);
    if (i > cap) return;
    for (;;) {
        if (*(int*)(block + i * 16u + 8u) != -2) return;
        ++i;
        m4 = i;
        block = (unsigned char*)*holder;
        cap = *(unsigned int*)(block + 4);
        if (i > cap) return;
    }
}

// FUNCTION: DAO 0x00918000
int C518000::fn_00518000(void* other) {
    void* self = m0;
    void* arg = other;
    if (self != 0) {
        void* p = *(void**)self;
        if (p != 0) {
            if (m4 <= *(unsigned int*)((char*)p + 4))
                goto compare;
        }
    }
    {
        void* op = *(void**)arg;
        if (op != 0) {
            void* opp = *(void**)op;
            if (opp != 0) {
                if (*(unsigned int*)((char*)arg + 4) <= *(unsigned int*)((char*)opp + 4))
                    goto compare;
            }
        }
    }
    return 1;
compare:
    if (self != *(void**)arg) return 0;
    if (m4 != *(unsigned int*)((char*)arg + 4)) return 0;
    return 1;
}

// FUNCTION: DAO 0x00918090
int C515440::fn_00518090(void* arg1, int key) {
    int idx = key;
    unsigned char* base = *(unsigned char**)this;
    unsigned char* entry = base + 8 + (unsigned int)idx * 12u;
    if (*(int*)(entry + 8) == -2) return -1;
    if (*(int*)(entry + 4) != key) return -1;
    void** pother = (void**)arg1;
    for (;;) {
        if (*(int*)(entry + 4) == key) {
            char* a = (char*)(*(void**)(entry + 8)) + 0xc;
            char* b = (char*)(*pother) + 0xc;
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
    do {
        if (*(unsigned int*)p == key)
            return *(void**)((char*)p + 4);
        p = *(void**)((char*)p + 0xc);
    } while (p != 0);
    return 0;
}

// FUNCTION: DAO 0x0091DCC0
void* C51DCC0::fn_0051dcc0(unsigned int flags) {
    void* result = 0;
    if (!(flags & 0x80)) {
        void* p = *(void**)((char*)m10 + 0x18);
        if (p != 0) {
            if (*(unsigned char*)((char*)p + 0x14) == 0)
                result = p;
        }
    }
    return result;
}
