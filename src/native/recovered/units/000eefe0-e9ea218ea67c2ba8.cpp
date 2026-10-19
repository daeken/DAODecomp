class DAO_Object {
public:
    int fn_000eef80(const unsigned char*, unsigned int, unsigned char*, unsigned int*, unsigned int);
    int fn_000eefe0(unsigned char*, unsigned int, unsigned int*, unsigned int);
    char fn_000f25b0();
    unsigned int fn_000f2830(unsigned int, unsigned int);
};

// FUNCTION: DAO 0x4E99E0
unsigned int __cdecl fn_000e99e0(unsigned int* p) {
    unsigned int v = *p;
    unsigned int r = (v << 16) | (v & 0x0000FF00u);
    r = (r << 8) | ((unsigned int)((unsigned char)(v >> 16)) << 8) | (unsigned int)((unsigned char)(v >> 24));
    *p = r;
    return v >> 24;
}

// FUNCTION: DAO 0x4E9A10
unsigned short* __cdecl fn_000e9a10(unsigned short* p) {
    unsigned char* b = reinterpret_cast<unsigned char*>(p);
    unsigned short r;
    *((unsigned char*)&r + 0) = b[1];
    *((unsigned char*)&r + 1) = b[0];
    *p = r;
    return p;
}

// FUNCTION: DAO 0x4EEF80
int __thiscall DAO_Object::fn_000eef80(const unsigned char* src, unsigned int len, unsigned char* dst, unsigned int* outLen, unsigned int) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    unsigned int i = 0;
    if (len > 0) {
        unsigned int count = len;
        unsigned char* d = dst;
        const unsigned char* s = src;
        do {
            *d = (unsigned char)(*s ^ base[4 + i]);
            ++i;
            if (i > *reinterpret_cast<unsigned int*>(base + 0x104)) {
                i = 0;
            }
            ++d;
            ++s;
        } while (--count != 0);
    }
    *outLen = len;
    return 1;
}

// FUNCTION: DAO 0x4EEFE0
int __thiscall DAO_Object::fn_000eefe0(unsigned char* buf, unsigned int len, unsigned int* outLen, unsigned int) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    unsigned int i = 0;
    unsigned int j = 0;
    if (len > 0) {
        do {
            buf[j] = (unsigned char)(buf[j] ^ base[4 + i]);
            ++i;
            if (i > *reinterpret_cast<unsigned int*>(base + 0x104)) {
                i = 0;
            }
            ++j;
        } while (j < len);
    }
    *outLen = len;
    return 1;
}

// FUNCTION: DAO 0x4F1E60
unsigned int* __stdcall fn_000f1e60(const unsigned char* src, unsigned int* dst) {
    unsigned char n;
    *dst = 0;
    n = 4;
    do {
        *dst = (*dst << 8) | *src;
        ++src;
        --n;
    } while (n != 0);
    dst[1] = 0;
    n = 4;
    do {
        dst[1] = (dst[1] << 8) | *src;
        ++src;
        --n;
    } while (n != 0);
    return dst;
}

// FUNCTION: DAO 0x4F25B0
char __thiscall DAO_Object::fn_000f25b0() {
    return *reinterpret_cast<unsigned int*>(this) == 6;
}

// FUNCTION: DAO 0x4F2830
unsigned int __thiscall DAO_Object::fn_000f2830(unsigned int a, unsigned int b) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    if (a != 0) {
        *reinterpret_cast<unsigned int*>(base + 0x44) = a;
        *reinterpret_cast<unsigned int*>(base + 0x48) = b;
        return b;
    }
    *reinterpret_cast<unsigned int*>(base + 0x44) = 0;
    *reinterpret_cast<unsigned int*>(base + 0x48) = 0;
    return 0;
}

// FUNCTION: DAO 0x8E29F0
char* __cdecl fn_004e29f0(char* dest, const char* src, unsigned int count) {
    char* start = dest;
    unsigned int words;
    unsigned int rem;
    if (count == 0) {
        return start;
    }
    if (((unsigned int)src & 3) != 0) {
        do {
            char c = *src;
            ++src;
            *dest = c;
            ++dest;
            if (--count == 0) {
                return start;
            }
            if (c == 0) {
                goto zero_align;
            }
        } while (((unsigned int)src & 3) != 0);
    }
    words = count >> 2;
    rem = count & 3;
    while (words != 0) {
        unsigned int v = *reinterpret_cast<const unsigned int*>(src);
        unsigned int t = v + 0x7efefeffu;
        unsigned int z = (v ^ 0xffffffffu) ^ t;
        if ((z & 0x81010100u) != 0) {
            if ((v & 0xffu) == 0) {
                *reinterpret_cast<unsigned int*>(dest) = 0;
            } else if ((v & 0xff00u) == 0) {
                *reinterpret_cast<unsigned int*>(dest) = v & 0xffu;
            } else if ((v & 0xff0000u) == 0) {
                *reinterpret_cast<unsigned int*>(dest) = v & 0xffffu;
            } else {
                *reinterpret_cast<unsigned int*>(dest) = v;
            }
            dest += 4;
            src += 4;
            --words;
            goto zero_words;
        }
        *reinterpret_cast<unsigned int*>(dest) = v;
        dest += 4;
        src += 4;
        --words;
    }
    while (rem != 0) {
        char c = *src;
        ++src;
        *dest = c;
        ++dest;
        if (c == 0) {
            --rem;
            goto zero_tail;
        }
        --rem;
    }
    return start;

zero_align:
    while (((unsigned int)dest & 3) != 0) {
        *dest = 0;
        ++dest;
        if (--count == 0) {
            return start;
        }
    }
    words = count >> 2;
    rem = count & 3;
    {
        volatile unsigned int* vd = reinterpret_cast<volatile unsigned int*>(dest);
        while (words != 0) {
            *vd = 0;
            ++vd;
            --words;
        }
        dest = (char*)vd;
    }
    {
        volatile unsigned char* vc = reinterpret_cast<volatile unsigned char*>(dest);
        while (rem != 0) {
            *vc = 0;
            ++vc;
            --rem;
        }
    }
    return start;

zero_words:
    {
        volatile unsigned int* vd = reinterpret_cast<volatile unsigned int*>(dest);
        while (words != 0) {
            *vd = 0;
            ++vd;
            --words;
        }
        dest = (char*)vd;
    }
    {
        volatile unsigned char* vc = reinterpret_cast<volatile unsigned char*>(dest);
        while (rem != 0) {
            *vc = 0;
            ++vc;
            --rem;
        }
    }
    return start;

zero_tail:
    {
        volatile unsigned char* vc = reinterpret_cast<volatile unsigned char*>(dest);
        while (rem != 0) {
            *vc = 0;
            ++vc;
            --rem;
        }
    }
    return start;
}
