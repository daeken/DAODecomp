struct DAO_Object {
    unsigned char data[0x100];
    void __thiscall fn_000593f0(unsigned int* value);
    unsigned char* __thiscall fn_00065f20();
};

// FUNCTION: DAO 0x0044F990
const char* __fastcall fn_0004f990(const char* tag, const char* attr) {
    if (!tag) return 0;
    if (*tag != '<') return 0;
    const char* p = tag;
    while (*p && (unsigned char)*p > 0x20) ++p;
    for (;;) {
        while (*p && (unsigned char)*p <= 0x20) ++p;
        const char* q = p;
        const char* a = attr;
        while (*a && *q == *a) { ++q; ++a; }
        if (*a == 0) {
            while (*q && (unsigned char)*q <= 0x20) ++q;
            if (*q == '=') {
                ++q;
                while (*q && (unsigned char)*q <= 0x20) ++q;
                return q;
            }
            p = q;
        }
        while (*p && *p != '>' && *p != '=') ++p;
        if (*p != '=') return 0;
        ++p;
        while (*p && (unsigned char)*p <= 0x20) ++p;
        if (*p == 0x22 || *p == 0x27) {
            char quote = *p++;
            while (*p && *p != quote) ++p;
            if (*p == quote) ++p;
        } else {
            while (*p && (unsigned char)*p <= 0x20) ++p;
        }
    }
}

// FUNCTION: DAO 0x004500A0
int __cdecl fn_000500a0(const char* s, int def) {
    if (!s || *s != '<') return def;
    const char* p = s + 1;
    while (*p && *p != '>') ++p;
    if (*p != '>') return def;
    if (p != s && p[-1] == '/') return def;
    ++p;
    while (*p && (unsigned char)*p <= 0x20) ++p;
    int sign = 1;
    if (*p == '+') {
        ++p;
    } else if (*p == '-') {
        sign = -1;
        ++p;
    }
    unsigned int value = 0;
    while (*p >= '0' && *p <= '9') {
        value = value * 10u + (unsigned int)(*p - '0');
        ++p;
    }
    return (int)(value * (unsigned int)sign);
}

// FUNCTION: DAO 0x00451030
void __fastcall fn_00051030(int count, unsigned short* src2, unsigned short* dst, unsigned short* src1) {
    unsigned int carry = 0;
    while (count > 0) {
        --src1;
        --src2;
        --dst;
        unsigned int sum = (unsigned int)*src1 + (unsigned int)*src2 + carry;
        *dst = (unsigned short)sum;
        carry = sum >> 16;
        --count;
    }
}

// FUNCTION: DAO 0x00455B90
void __cdecl fn_00055b90(void** arr, int hole, int top, void* value) {
    int parent = (hole - 1) / 2;
    if (top >= hole) {
        arr[hole] = value;
        return;
    }
    for (;;) {
        void* p = arr[parent];
        if (*(unsigned int*)((unsigned char*)p + 0x80) > *(unsigned int*)((unsigned char*)value + 0x80)) break;
        arr[hole] = p;
        hole = parent;
        parent = (parent - 1) / 2;
        if (top >= hole) break;
    }
    arr[hole] = value;
}

// FUNCTION: DAO 0x00456160
void __cdecl fn_00056160(void** a, void** b, void** c) {
    void* t;
    if (*(unsigned int*)((unsigned char*)*b + 0x80) <= *(unsigned int*)((unsigned char*)*a + 0x80)) {
        t = *a; *a = *b; *b = t;
    }
    if (*(unsigned int*)((unsigned char*)*c + 0x80) <= *(unsigned int*)((unsigned char*)*b + 0x80)) {
        t = *b; *b = *c; *c = t;
    }
    if (*(unsigned int*)((unsigned char*)*b + 0x80) <= *(unsigned int*)((unsigned char*)*a + 0x80)) {
        t = *a; *a = *b; *b = t;
    }
}

// FUNCTION: DAO 0x004563C0
void __cdecl fn_000563c0(void* dst, unsigned int count, const void* src) {
    if (count == 0) return;
    unsigned int d = (unsigned int)dst;
    const unsigned int* s = (const unsigned int*)src;
    do {
        if (d) {
            unsigned int* out = (unsigned int*)d;
            out[0] = s[0];
            out[1] = s[1];
            out[2] = s[2];
            out[3] = s[3];
        }
        d += 16;
        --count;
    } while (count != 0);
}

// FUNCTION: DAO 0x004593F0
void __thiscall DAO_Object::fn_000593f0(unsigned int* value) {
    *reinterpret_cast<unsigned int*>(reinterpret_cast<unsigned char*>(this) + 0x48) = *value;
}

// FUNCTION: DAO 0x00465F20
unsigned char* __thiscall DAO_Object::fn_00065f20() {
    return reinterpret_cast<unsigned char*>(this) + 0xf0;
}
