struct C515440 {
    void* m0;
    int fn_00515440(void* arg1, int key);
    int fn_005154a0(void* arg1, int key);
    int fn_00518090(void* arg1, int key);
};

struct C517FB0 {
    void* m0;
    unsigned int m4;
    void fn_00517fb0();
};

struct C518000 {
    void* m0;
    unsigned int m4;
    bool fn_00518000(void* other);
};

// FUNCTION: DAO 0x00915440
int C515440::fn_00515440(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    int idx = key;
    int* entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    if (entry[0] != -2 && entry[1] == key) {
        for (;;) {
            if (entry[1] == key) {
                void* obj = (void*)entry[2];
                void* other = *(void**)arg1;
                if (*(void**)((char*)obj + 0x10) == *(void**)((char*)other + 0x10)) return idx;
            }
            int next = entry[0];
            if (next == -1) return -1;
            idx = next;
            entry = (int*)(base + 8 + (unsigned int)idx * 12u);
        }
    }
    return -1;
}

// FUNCTION: DAO 0x009154A0
int C515440::fn_005154a0(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    int idx = key;
    int* entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    if (entry[0] != -2 && entry[1] == key) {
        for (;;) {
            if (entry[1] == key) {
                void* obj = (void*)entry[2];
                if (*(void**)((char*)obj + 0x10) == *(void**)arg1) return idx;
            }
            int next = entry[0];
            if (next == -1) return -1;
            idx = next;
            entry = (int*)(base + 8 + (unsigned int)idx * 12u);
        }
    }
    return -1;
}

// FUNCTION: DAO 0x00917FB0
void C517FB0::fn_00517fb0() {
    unsigned int i = m4;
    unsigned int* block = *(unsigned int**)m0;
    if (i > block[1]) return;
    m4 = ++i;
    block = *(unsigned int**)m0;
    if (i > block[1]) return;
    do {
        if (*(int*)((char*)*(unsigned int**)m0 + i * 16u + 8u) != -2) return;
        m4 = ++i;
    } while (i <= (*(unsigned int**)m0)[1]);
}

// FUNCTION: DAO 0x00918000
bool C518000::fn_00518000(void* other) {
    if (m0 != 0 && *(void**)m0 != 0 && m4 <= *(unsigned int*)((char*)*(void**)m0 + 4)) goto L_compare;
    if (*(void**)other != 0 && *(void**)*(void**)other != 0 && *(unsigned int*)((char*)other + 4) <= *(unsigned int*)((char*)*(void**)*(void**)other + 4)) goto L_compare;
    return true;
L_compare:
    if (m0 != *(void**)other) return false;
    if (m4 != *(unsigned int*)((char*)other + 4)) return false;
    return true;
}

// FUNCTION: DAO 0x00918090
int C515440::fn_00518090(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    int idx = key;
    int* entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    if (entry[0] != -2 && entry[1] == key) {
        for (;;) {
            if (entry[1] == key) {
                char* a = (char*)(void*)entry[2] + 0xc;
                char* b = (char*)*(void**)arg1 + 0xc;
                while (*a == *b) {
                    if (*a == 0) return idx;
                    ++a;
                    ++b;
                }
            }
            int next = entry[0];
            if (next == -1) return -1;
            idx = next;
            entry = (int*)(base + 8 + (unsigned int)idx * 12u);
        }
    }
    return -1;
}
