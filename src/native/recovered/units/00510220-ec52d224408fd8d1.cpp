struct C510220 { unsigned int fn_00510220(); };
struct C515440 { void* m0; int fn_00515440(void*, int); int fn_005154a0(void*, int); int fn_00518090(void*, int); };
struct C517FB0 { void* m0; unsigned int m4; void fn_00517fb0(); };
struct C518000 { void* m0; unsigned int m4; int fn_00518000(void*); };

// FUNCTION: DAO 0x00910220
unsigned int C510220::fn_00510220() {
    unsigned int* p = (unsigned int*)this;
    if (p[196]) {
        p = (unsigned int*)p[196];
    } else {
        p = (unsigned int*)((char*)p + 0x30);
    }
    return p[12] - p[11] + p[10];
}

// FUNCTION: DAO 0x00915440
int C515440::fn_00515440(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    int idx = key;
    int* entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    if (*entry == -2) return -1;
    if (entry[1] != key) return -1;
    for (;;) {
        if (entry[1] == key) {
            void* obj = *(void**)(entry + 2);
            void* other = *(void**)arg1;
            if (*(void**)((char*)obj + 0x10) == *(void**)((char*)other + 0x10)) return idx;
        }
        int next = *entry;
        if (next == -1) return -1;
        idx = next;
        entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    }
}

// FUNCTION: DAO 0x009154A0
int C515440::fn_005154a0(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    int idx = key;
    int* entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    if (*entry == -2) return -1;
    if (entry[1] != key) return -1;
    for (;;) {
        if (entry[1] == key) {
            void* obj = *(void**)(entry + 2);
            if (*(void**)((char*)obj + 0x10) == *(void**)arg1) return idx;
        }
        int next = *entry;
        if (next == -1) return -1;
        idx = next;
        entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    }
}

// FUNCTION: DAO 0x00917FB0
void C517FB0::fn_00517fb0() {
    void** p = (void**)m0;
    unsigned int i = m4;
    if (i > *(unsigned int*)((char*)*p + 4)) return;
    m4 = ++i;
    if (i > *(unsigned int*)((char*)*p + 4)) return;
    for (;;) {
        if (*(int*)((char*)*p + i * 16u + 8u) != -2) return;
        m4 = ++i;
        if (i > *(unsigned int*)((char*)*p + 4)) return;
    }
}

// FUNCTION: DAO 0x00918000
int C518000::fn_00518000(void* other) {
    if (m0 != 0 && *(void**)m0 != 0 && m4 <= *(unsigned int*)((char*)*(void**)m0 + 4)) goto compare;
    if (*(void**)other != 0 && *(void**)*(void**)other != 0 && *(unsigned int*)((char*)other + 4) <= *(unsigned int*)((char*)*(void**)*(void**)other + 4)) goto compare;
    return 1;
compare:
    if (m0 != *(void**)other) return 0;
    if (m4 != *(unsigned int*)((char*)other + 4)) return 0;
    return 1;
}

// FUNCTION: DAO 0x00918090
int C515440::fn_00518090(void* arg1, int key) {
    unsigned char* base = *(unsigned char**)this;
    int idx = key;
    int* entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    if (*entry == -2) return -1;
    if (entry[1] != key) return -1;
    for (;;) {
        if (entry[1] == key) {
            char* a = (char*)(*(void**)(entry + 2)) + 0xc;
            char* b = (char*)(*(void**)arg1) + 0xc;
            for (;;) {
                if (*a != *b) break;
                if (*a == 0) return idx;
                ++a;
                ++b;
            }
        }
        int next = *entry;
        if (next == -1) return -1;
        idx = next;
        entry = (int*)(base + 8 + (unsigned int)idx * 12u);
    }
}
