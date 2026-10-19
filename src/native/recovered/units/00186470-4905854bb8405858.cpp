struct C_586470 { void fn_00186470(unsigned char); };
struct C_586480 { void fn_00186480(unsigned char); };
struct C_587250 { void fn_00187250(unsigned int); };
struct C_587c20 { unsigned int fn_00187c20(); };
struct C_587d30 { unsigned int fn_00187d30(); };
struct C_599c90 { void *fn_00199c90(const void *); };
struct C_599f00 { void fn_00199f00(); };
struct C_5b4df0 { int fn_001b4df0(); };
struct C_5b6230 { void fn_001b6230(); };

// FUNCTION: DAO 0x586470
void C_586470::fn_00186470(unsigned char value)
{
    *reinterpret_cast<unsigned char *>(reinterpret_cast<char *>(this) + 0x51) = value;
}

// FUNCTION: DAO 0x586480
void C_586480::fn_00186480(unsigned char value)
{
    *reinterpret_cast<unsigned char *>(reinterpret_cast<char *>(this) + 0x50) = value;
}

// FUNCTION: DAO 0x587250
void C_587250::fn_00187250(unsigned int value)
{
    *reinterpret_cast<unsigned int *>(reinterpret_cast<char *>(this) + 0x34) = value;
}

// FUNCTION: DAO 0x587C20
unsigned int C_587c20::fn_00187c20()
{
    unsigned int *p = reinterpret_cast<unsigned int *>(this);
    unsigned int old = p[4];
    p[4] = 0;
    p[6] = 0;
    return old;
}

// FUNCTION: DAO 0x587D30
unsigned int C_587d30::fn_00187d30()
{
    unsigned int *p = reinterpret_cast<unsigned int *>(this);
    if (p[0] == 0)
        return 0;
    if (p[1] == 0xFFFFFFFFu)
        return 0;
    return 1;
}

// FUNCTION: DAO 0x58C600
unsigned short __cdecl fn_0018c600(const void *base, unsigned int index)
{
    return *reinterpret_cast<const unsigned short *>(reinterpret_cast<const char *>(base) + index);
}

// FUNCTION: DAO 0x58C610
void __cdecl fn_0018c610(void *first, void *last, void *dest)
{
    unsigned char *s = reinterpret_cast<unsigned char *>(first);
    unsigned char *e = reinterpret_cast<unsigned char *>(last);
    unsigned char *d = reinterpret_cast<unsigned char *>(dest);
    while (s != e) {
        *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<unsigned int *>(s);
        *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<unsigned short *>(s + 4);
        s += 6;
        d += 6;
    }
}

// FUNCTION: DAO 0x58C680
void __cdecl fn_0018c680(void *dest, const void *base, unsigned int offset)
{
    const unsigned char *s = reinterpret_cast<const unsigned char *>(base) + offset;
    unsigned int *d = reinterpret_cast<unsigned int *>(dest);
    d[0] = *reinterpret_cast<const unsigned int *>(s);
    d[1] = *reinterpret_cast<const unsigned int *>(s + 4);
    d[2] = *reinterpret_cast<const unsigned int *>(s + 8);
    d[3] = *reinterpret_cast<const unsigned int *>(s + 12);
}

// FUNCTION: DAO 0x58C6B0
void __cdecl fn_0018c6b0(void *first, void *last, void *destEnd)
{
    unsigned char *begin = reinterpret_cast<unsigned char *>(first);
    unsigned char *s = reinterpret_cast<unsigned char *>(last);
    unsigned char *d = reinterpret_cast<unsigned char *>(destEnd);
    while (s != begin) {
        s -= 6;
        d -= 6;
        *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<unsigned int *>(s);
        *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<unsigned short *>(s + 4);
    }
}

// FUNCTION: DAO 0x58C820
void __cdecl fn_0018c820(void *first, void *last, void *dest)
{
    unsigned char *s = reinterpret_cast<unsigned char *>(first);
    unsigned char *e = reinterpret_cast<unsigned char *>(last);
    unsigned char *d = reinterpret_cast<unsigned char *>(dest);
    while (s != e) {
        if (d != 0) {
            *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<unsigned int *>(s);
            *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<unsigned short *>(s + 4);
        }
        s += 6;
        d += 6;
    }
}

// FUNCTION: DAO 0x58C9A0
void __cdecl fn_0018c9a0(void *destFirst, void *destLast, const void *src)
{
    unsigned char *d = reinterpret_cast<unsigned char *>(destFirst);
    unsigned char *e = reinterpret_cast<unsigned char *>(destLast);
    const unsigned char *s = reinterpret_cast<const unsigned char *>(src);
    while (d != e) {
        *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<const unsigned int *>(s);
        *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<const unsigned short *>(s + 4);
        d += 6;
        s += 6;
    }
}

// FUNCTION: DAO 0x58CA50
void __cdecl fn_0018ca50(void *dest, unsigned int count, const void *src)
{
    unsigned char *d = reinterpret_cast<unsigned char *>(dest);
    const unsigned char *s = reinterpret_cast<const unsigned char *>(src);
    while (count > 0) {
        if (d != 0) {
            *reinterpret_cast<unsigned int *>(d) = *reinterpret_cast<const unsigned int *>(s);
            *reinterpret_cast<unsigned short *>(d + 4) = *reinterpret_cast<const unsigned short *>(s + 4);
        }
        --count;
        d += 6;
    }
}

// FUNCTION: DAO 0x599C90
void *C_599c90::fn_00199c90(const void *key)
{
    void *tree = *reinterpret_cast<void * const *>(reinterpret_cast<char *>(this) + 4);
    void *node = *reinterpret_cast<void * const *>(reinterpret_cast<char *>(tree) + 4);
    if (*reinterpret_cast<unsigned char *>(reinterpret_cast<char *>(node) + 0x35) != 0)
        return tree;

    char *k = reinterpret_cast<char *>(const_cast<void *>(key));
    unsigned int keyPtrLen = *reinterpret_cast<unsigned int *>(k + 0x18);
    unsigned int keyCmpLen = *reinterpret_cast<unsigned int *>(k + 0x14);
    void *result = tree;

    for (;;) {
        const void *keyData;
        if (keyPtrLen >= 8)
            keyData = *reinterpret_cast<void **>(k + 4);
        else
            keyData = k + 4;

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
        for (unsigned int i = 0; i < cmpLen; ++i) {
            unsigned short nc = nd[i];
            unsigned short kc = kd[i];
            if (nc != kc) {
                cmp = (nc < kc) ? -1 : 1;
                break;
            }
        }
        if (cmp == 0) {
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
    char *begin = *reinterpret_cast<char **>(reinterpret_cast<char *>(this) + 0xc4);
    if (begin != 0) {
        char *end = *reinterpret_cast<char **>(reinterpret_cast<char *>(this) + 0xc8);
        int diff = static_cast<int>(end - begin);
        if ((diff >> 2) != 0) {
            end -= 4;
            *reinterpret_cast<char **>(reinterpret_cast<char *>(this) + 0xc8) = end;
        }
    }
}

// FUNCTION: DAO 0x5B4DF0
int C_5b4df0::fn_001b4df0()
{
    unsigned int begin = *reinterpret_cast<unsigned int *>(reinterpret_cast<char *>(this) + 4);
    if (begin == 0)
        return 0;
    unsigned int end = *reinterpret_cast<unsigned int *>(reinterpret_cast<char *>(this) + 8);
    int diff = static_cast<int>(end) - static_cast<int>(begin);
    return diff / 56;
}

// FUNCTION: DAO 0x5B6230
void C_5b6230::fn_001b6230()
{
    *reinterpret_cast<unsigned char *>(reinterpret_cast<char *>(this) + 0x44) = 1;
}
