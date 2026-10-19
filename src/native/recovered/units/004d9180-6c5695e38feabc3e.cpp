typedef unsigned int size_t;

// FUNCTION: DAO 0x8D7980
void __fastcall fn_004d7980(char* p) {
    if (!p) return;
    unsigned char c = (unsigned char)*p;
    if (!c) return;
    for (;;) {
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == ',') {
            c = (unsigned char)*++p;
            if (!c) return;
        } else {
            return;
        }
    }
}

// FUNCTION: DAO 0x8D7DA0
int __cdecl fn_004d7da0(const char* s, int flags_in) {
    unsigned int flags = (unsigned int)flags_in;
    unsigned char c;
    do {
        c = (unsigned char)*s++;
    } while (c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == ',');
    if (c == '-') {
        flags |= 2u;
        c = (unsigned char)*s++;
    } else if (c == '+') {
        c = (unsigned char)*s++;
    }
    unsigned int val = 0u;
    for (;;) {
        if (c < '0' || c > '9') break;
        flags |= 8u;
        unsigned int d = (unsigned int)(c - '0');
        if (val > 0x19999999u || (val == 0x19999999u && d > 5u)) {
            flags |= 4u;
            break;
        }
        val = val * 10u + d;
        c = (unsigned char)*s++;
    }
    if (!(flags & 8u)) return 0;
    if (flags & 4u) {
        if (flags & 1u) val = 0xFFFFFFFFu;
        else val = (flags & 2u) ? 0x80000000u : 0x7FFFFFFFu;
    } else {
        if (!(flags & 1u)) {
            if (flags & 2u) {
                if (val > 0x80000000u) val = 0x80000000u;
            } else {
                if (val > 0x7FFFFFFFu) val = 0x7FFFFFFFu;
            }
        }
    }
    if (flags & 2u) val = (unsigned int)(-(int)val);
    return (int)val;
}

// FUNCTION: DAO 0x8D9180
int __cdecl fn_004d9180(const int* p, int v) {
    return p[0] == v || p[1] == v || p[2] == v;
}

// FUNCTION: DAO 0x8DA060
void __cdecl fn_004da060(int* a, int* b) {
    int t = *a;
    *a = *b;
    *b = t;
}

// FUNCTION: DAO 0x8E1BB0
void* __cdecl fn_004e1bb0(void* buf, int val, size_t n) {
    unsigned char* p = (unsigned char*)buf;
    unsigned char v = (unsigned char)val;
    while (n) {
        if (*p == v) return p;
        ++p;
        --n;
    }
    return 0;
}

// FUNCTION: DAO 0x8E1C60
size_t __cdecl fn_004e1c60(const char* str, const char* control) {
    unsigned int bits[8] = {0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u};
    const unsigned char* c = (const unsigned char*)control;
    while (*c) {
        unsigned char ch = *c++;
        bits[ch >> 5] |= (1u << (ch & 31));
    }
    const unsigned char* s = (const unsigned char*)str;
    size_t n = 0;
    for (;;) {
        unsigned char ch = *s;
        if (!ch) break;
        if (bits[ch >> 5] & (1u << (ch & 31))) break;
        ++s;
        ++n;
    }
    return n;
}

// FUNCTION: DAO 0x8E5480
char* __cdecl fn_004e5480(char* str, char* control) {
    unsigned int bits[8] = {0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u};
    unsigned char* c = (unsigned char*)control;
    while (*c) {
        unsigned char ch = *c++;
        bits[ch >> 5] |= (1u << (ch & 31));
    }
    unsigned char* s = (unsigned char*)str;
    for (;;) {
        unsigned char ch = *s;
        if (!ch) return 0;
        if (bits[ch >> 5] & (1u << (ch & 31))) return (char*)s;
        ++s;
    }
}

// FUNCTION: DAO 0x8E690C
wchar_t* __cdecl fn_004e690c(wchar_t* str, wchar_t ch) {
    wchar_t* p = str;
    for (;;) {
        wchar_t c = *p;
        if (c == ch) return p;
        if (!c) return 0;
        ++p;
    }
}

// FUNCTION: DAO 0x8E7B56
int __cdecl fn_004e7b56(const wchar_t* s1, const wchar_t* s2, size_t n) {
    if (n == 0) return 0;
    for (;;) {
        if (--n == 0) break;
        wchar_t c1 = *s1;
        if (!c1) break;
        if (c1 != *s2) break;
        ++s1;
        ++s2;
    }
    return (int)(unsigned int)*s1 - (int)(unsigned int)*s2;
}

struct C_fn_004e9bb7 {
    int fn_004e9bb7();
};

// FUNCTION: DAO 0x8E9BB7
int C_fn_004e9bb7::fn_004e9bb7() {
    unsigned int self = (unsigned int)(void*)this;
    unsigned int* p = *(unsigned int**)this;
    unsigned int* q = *(unsigned int**)((char*)p - 4);
    unsigned int ret = self - *(unsigned int*)((char*)q + 4);
    unsigned int* r = *(unsigned int**)((char*)q + 8);
    if (r) {
        unsigned int* s = (unsigned int*)(self - (unsigned int)r);
        ret -= *s;
    }
    return (int)ret;
}
