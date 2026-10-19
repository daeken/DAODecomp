struct E6 { char b[6]; };
struct U4 { unsigned int v[4]; };

struct C_587d30 { unsigned int fn_00187d30(); };
struct C_599c90 { void *fn_00199c90(void *key); };
struct C_599f00 { void fn_00199f00(); };

// FUNCTION: DAO 0x587D30
unsigned int C_587d30::fn_00187d30()
{
    unsigned int *p = reinterpret_cast<unsigned int *>(this);
    if (p[0] != 0 && p[1] != 0xFFFFFFFFu)
        return 1;
    return 0;
}

// FUNCTION: DAO 0x58C610
E6 *__cdecl fn_0018c610(E6 *first, E6 *last, E6 *dest)
{
    E6 *destEnd = dest + (last - first);
    char *s = reinterpret_cast<char *>(first);
    char *e = reinterpret_cast<char *>(last);
    char *d = reinterpret_cast<char *>(dest);
    while (s != e) {
        *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<unsigned int *>(s);
        *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<unsigned short *>(s + 4);
        s += 6;
        d += 6;
    }
    return destEnd;
}

// FUNCTION: DAO 0x58C680
void __cdecl fn_0018c680(void *dest, const void *base, unsigned int offset)
{
    *reinterpret_cast<U4 *>(dest) =
        *reinterpret_cast<const U4 *>(reinterpret_cast<const char *>(base) + offset);
}

// FUNCTION: DAO 0x58C6B0
E6 *__cdecl fn_0018c6b0(E6 *first, E6 *last, E6 *destEnd)
{
    E6 *destBegin = destEnd - (last - first);
    char *e = reinterpret_cast<char *>(first);
    char *s = reinterpret_cast<char *>(last);
    char *d = reinterpret_cast<char *>(destEnd);
    while (s != e) {
        s -= 6;
        d -= 6;
        *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<unsigned int *>(s);
        *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<unsigned short *>(s + 4);
    }
    return destBegin;
}

// FUNCTION: DAO 0x58C820
void __cdecl fn_0018c820(E6 *first, E6 *last, E6 *dest)
{
    while (first != last) {
        if (dest != 0) {
            *reinterpret_cast<unsigned int *>(dest) = *reinterpret_cast<unsigned int *>(first);
            *reinterpret_cast<unsigned short *>(reinterpret_cast<char *>(dest) + 4) =
                *reinterpret_cast<unsigned short *>(reinterpret_cast<char *>(first) + 4);
        }
        ++first;
        ++dest;
    }
}

// FUNCTION: DAO 0x58C9A0
void __cdecl fn_0018c9a0(E6 *destFirst, E6 *destLast, const E6 *src)
{
    while (destFirst != destLast) {
        *reinterpret_cast<unsigned int *>(destFirst) = *reinterpret_cast<const unsigned int *>(src);
        *reinterpret_cast<unsigned short *>(reinterpret_cast<char *>(destFirst) + 4) =
            *reinterpret_cast<const unsigned short *>(reinterpret_cast<const char *>(src) + 4);
        ++destFirst;
        ++src;
    }
}

// FUNCTION: DAO 0x58CA50
void __cdecl fn_0018ca50(E6 *dest, unsigned int count, const E6 *src)
{
    while (count > 0) {
        if (dest != 0) {
            *reinterpret_cast<unsigned int *>(dest) = *reinterpret_cast<const unsigned int *>(src);
            *reinterpret_cast<unsigned short *>(reinterpret_cast<char *>(dest) + 4) =
                *reinterpret_cast<const unsigned short *>(reinterpret_cast<const char *>(src) + 4);
        }
        --count;
        ++dest;
    }
}

// FUNCTION: DAO 0x599C90
void *C_599c90::fn_00199c90(void *key)
{
    void *tree = *reinterpret_cast<void **>(reinterpret_cast<char *>(this) + 4);
    void *node = *reinterpret_cast<void **>(reinterpret_cast<char *>(tree) + 4);
    if (*reinterpret_cast<unsigned char *>(reinterpret_cast<char *>(node) + 0x35) != 0)
        return tree;

    unsigned int keyLen = *reinterpret_cast<unsigned int *>(reinterpret_cast<char *>(key) + 0x18);
    unsigned int keyCmpLen = *reinterpret_cast<unsigned int *>(reinterpret_cast<char *>(key) + 0x14);
    char *keyBase = reinterpret_cast<char *>(key) + 4;
    void *result = tree;

    for (;;) {
        const void *keyData;
        if (keyLen >= 8)
            keyData = *reinterpret_cast<void **>(keyBase);
        else
            keyData = keyBase;

        char *n = reinterpret_cast<char *>(node);
        unsigned int nodeLen = *reinterpret_cast<unsigned int *>(n + 0x20);
        unsigned int cmpLen = nodeLen < keyCmpLen ? nodeLen : keyCmpLen;

        const void *nodeData;
        if (*reinterpret_cast<unsigned int *>(n + 0x24) >= 8)
            nodeData = *reinterpret_cast<void **>(n + 0x10);
        else
            nodeData = n + 0x10;

        int cmp = 0;
        const unsigned short *nd = reinterpret_cast<const unsigned short *>(nodeData);
        const unsigned short *kd = reinterpret_cast<const unsigned short *>(keyData);
        unsigned int i = 0;
        for (; i < cmpLen; ++i) {
            unsigned short nc = nd[i];
            unsigned short kc = kd[i];
            if (nc != kc) {
                cmp = (nc < kc) ? -1 : 1;
                break;
            }
        }
        if (i == cmpLen) {
            if (nodeLen < keyCmpLen)
                cmp = -1;
            else if (nodeLen > keyCmpLen)
                cmp = 1;
        }

        if (cmp < 0) {
            node = *reinterpret_cast<void **>(n + 8);
        } else {
            result = node;
            node = *reinterpret_cast<void **>(n);
        }

        if (*reinterpret_cast<unsigned char *>(reinterpret_cast<char *>(node) + 0x35) == 0)
            continue;
        return result;
    }
}

// FUNCTION: DAO 0x599F00
void C_599f00::fn_00199f00()
{
    unsigned int *begin = *reinterpret_cast<unsigned int **>(reinterpret_cast<char *>(this) + 0xc4);
    if (begin != 0) {
        unsigned int *end = *reinterpret_cast<unsigned int **>(reinterpret_cast<char *>(this) + 0xc8);
        if ((end - begin) != 0) {
            --end;
            *reinterpret_cast<unsigned int **>(reinterpret_cast<char *>(this) + 0xc8) = end;
        }
    }
}
