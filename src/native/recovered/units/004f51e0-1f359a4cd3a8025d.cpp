struct PMD {
    int mdisp;
    int pdisp;
    int vdisp;
};

class C_Object24 {
public:
    unsigned char pad24[0x24];
    unsigned char *ptr24;
    unsigned char *fn_0050b240();
    void fn_00517c60();
};

class C_0050ef60 {
public:
    unsigned int value0;
    void fn_0050ef60(unsigned int v, unsigned char flag);
};

// FUNCTION: DAO 0x008E6EC0
extern "C" char * __cdecl fn_004e6ec0(char *dest, char *src, unsigned int count) {
    if (count == 0) {
        return dest;
    }
    char *d = dest;
    while (*d != '\0') {
        ++d;
    }
    while (count != 0 && *src != '\0') {
        *d++ = *src++;
        --count;
    }
    *d = '\0';
    return dest;
}

// FUNCTION: DAO 0x008E9C42
extern "C" int __cdecl fn_004e9c42(void *p, PMD *pmd) {
    int offset = 0;
    if (pmd->pdisp >= 0) {
        int vbtable = *reinterpret_cast<int *>(reinterpret_cast<char *>(p) + pmd->pdisp);
        offset = pmd->pdisp + *reinterpret_cast<int *>(reinterpret_cast<char *>(vbtable) + pmd->vdisp);
    }
    return pmd->mdisp + offset;
}

// FUNCTION: DAO 0x008EA140
extern "C" void __cdecl fn_004ea140(unsigned char *a, unsigned char *b, unsigned int n) {
    if (a == b || n == 0) {
        return;
    }
    do {
        unsigned char bl = *b;
        unsigned char dl = *a;
        *a = bl;
        --n;
        *b = dl;
        ++a;
        ++b;
    } while (n != 0);
}

// FUNCTION: DAO 0x008EA9F8
extern "C" int __cdecl fn_004ea9f8(const unsigned char *s1, const unsigned char *s2) {
    for (;;) {
        unsigned int a = *s1++;
        if ((unsigned int)(a - 0x41) <= 0x19) {
            a += 0x20;
        }
        unsigned int b = *s2++;
        if ((unsigned int)(b - 0x41) <= 0x19) {
            b += 0x20;
        }
        if (a == 0) {
            return (int)(a - b);
        }
        if (a != b) {
            return (int)(a - b);
        }
    }
}

// FUNCTION: DAO 0x008ECF75
extern "C" char * __cdecl fn_004ecf75(char *p, PMD *pmd) {
    int offset = 0;
    if (pmd->pdisp >= 0) {
        int vbtable = *reinterpret_cast<int *>(p + pmd->pdisp);
        offset = pmd->pdisp + *reinterpret_cast<int *>(reinterpret_cast<char *>(vbtable) + pmd->vdisp);
    }
    return p + pmd->mdisp + offset;
}

// FUNCTION: DAO 0x008F51E0
extern "C" int __cdecl fn_004f51e0(unsigned char *pImageBase) {
    if (*reinterpret_cast<unsigned short *>(pImageBase) != 0x5a4d) {
        return 0;
    }
    unsigned char *nt = pImageBase + *reinterpret_cast<unsigned int *>(pImageBase + 0x3c);
    if (*reinterpret_cast<unsigned int *>(nt) != 0x4550) {
        return 0;
    }
    return (*reinterpret_cast<unsigned short *>(nt + 0x18) == 0x10b) ? 1 : 0;
}

// FUNCTION: DAO 0x008F5210
extern "C" unsigned char * __cdecl fn_004f5210(unsigned char *pImageBase, unsigned int rva) {
    unsigned char *nt = pImageBase + *reinterpret_cast<unsigned int *>(pImageBase + 0x3c);
    unsigned int sizeOpt = *reinterpret_cast<unsigned short *>(nt + 0x14);
    unsigned int numSections = *reinterpret_cast<unsigned short *>(nt + 6);
    unsigned char *sec = nt + 0x18 + sizeOpt;
    for (unsigned int i = 0; i < numSections; ++i, sec += 0x28) {
        unsigned int va = *reinterpret_cast<unsigned int *>(sec + 0xc);
        if (rva >= va) {
            unsigned int vsize = *reinterpret_cast<unsigned int *>(sec + 8);
            if (rva < va + vsize) {
                return sec;
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x009013E7
extern "C" unsigned int __cdecl fn_005013e7(const char *s) {
    unsigned int result = 0;
    unsigned char c;
    while ((c = *reinterpret_cast<const unsigned char *>(s++)) != 0) {
        unsigned char al = (unsigned char)(c - 0x61);
        if (al <= 5) {
            c = (unsigned char)(c + 0xd9);
        } else {
            al = (unsigned char)(c - 0x41);
            if (al <= 5) {
                c = (unsigned char)(c + 0xf9);
            }
        }
        int val = (signed char)c;
        result = (result << 4) + (unsigned int)(val - 0x30);
    }
    return result;
}

// FUNCTION: DAO 0x00901419
extern "C" unsigned int __cdecl fn_00501419(const char *s) {
    unsigned int count = 0;
    for (;;) {
        unsigned char c = *reinterpret_cast<const unsigned char *>(s++);
        if (c >= 0x41 && c <= 0x5a) {
            ++count;
            continue;
        }
        unsigned char t = (unsigned char)(c - 0x61);
        if (t <= 0x19) {
            ++count;
            continue;
        }
        break;
    }
    return count;
}

// FUNCTION: DAO 0x0090855E
extern "C" unsigned int __cdecl fn_0050855e(const char *s, unsigned int maxCount) {
    unsigned int n = 0;
    if (maxCount == 0) {
        return 0;
    }
    while (n < maxCount && s[n] != '\0') {
        ++n;
    }
    return n;
}

// FUNCTION: DAO 0x0090B240
unsigned char *C_Object24::fn_0050b240() {
    return ptr24 + 12;
}

// FUNCTION: DAO 0x0090EF60
void C_0050ef60::fn_0050ef60(unsigned int v, unsigned char flag) {
    value0 = v;
    if (flag != 0) {
        v |= 0x80000000u;
        value0 = v;
    }
}

// FUNCTION: DAO 0x0090F0D0
extern "C" unsigned int __stdcall fn_0050f0d0(const unsigned char *data, unsigned int len, unsigned int seed) {
    while (len != 0) {
        unsigned int b = data[len - 1];
        --len;
        seed = b ^ ((seed << 5) + seed);
    }
    return seed;
}

// FUNCTION: DAO 0x00917C60
void C_Object24::fn_00517c60() {
    ptr24[0x38] = 1;
}
