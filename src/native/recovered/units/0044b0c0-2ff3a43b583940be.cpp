// FUNCTION: DAO 0x84B0C0
unsigned char __cdecl fn_0044b0c0(void* p) {
    unsigned int* w = (unsigned int*)p;
    if ((w[28] & 0x200000u) != 0) {
        unsigned int v = w[6];
        if (v > 0)
            return (unsigned char)(v != 1);
    }
    return 0;
}

// FUNCTION: DAO 0x852850
void __fastcall fn_00452850(unsigned int owner, unsigned int list) {
    unsigned int cur = list;
    if (cur == 0)
        return;
    unsigned int head = *(unsigned int*)(owner + 0x174);
    for (;;) {
        unsigned int next = *(unsigned int*)(cur + 4);
        *(unsigned int*)(cur + 4) = head;
        *(unsigned int*)(owner + 0x174) = cur;
        if (next == 0)
            break;
        cur = next;
    }
}

// FUNCTION: DAO 0x852E30
void __cdecl fn_00452e30(unsigned short* p) {
    unsigned short* src = p;
    unsigned short ch;
    for (;;) {
        ch = *src;
        if (ch == 0)
            return;
        if (ch == 0x0D)
            break;
        ++src;
    }
    unsigned short* dst = src;
    for (;;) {
        ch = *src;
        if (ch == 0x0D) {
            *dst = 0x0A;
            ++dst;
            ++src;
            if (*src == 0x0A)
                ++src;
        } else {
            *dst = ch;
            ++dst;
            ++src;
        }
        if (*src == 0) {
            *dst = 0;
            return;
        }
    }
}

// FUNCTION: DAO 0x853400
void __cdecl fn_00453400(unsigned int obj, unsigned int val) {
    unsigned int* p = (unsigned int*)obj;
    *((unsigned char*)p + 4) = 0;
    p[2] = 0;
    p[3] = 0;
    p[0] = 0;
    p[4] = val;
}

// FUNCTION: DAO 0x853430
void* __fastcall fn_00453430(unsigned int, void** it) {
    if (it[0] == it[1])
        return 0;
    for (;;) {
        unsigned char* cur = (unsigned char*)it[0];
        void* v = *(void**)cur;
        cur += 4;
        it[0] = cur;
        if (v != 0)
            return v;
        if (it[0] == it[1])
            return 0;
    }
}

// FUNCTION: DAO 0x853450
void __cdecl fn_00453450(unsigned int obj, unsigned int val) {
    unsigned int* p = (unsigned int*)obj;
    p[0] = 0;
    p[1] = 0;
    p[4] = 0;
    p[3] = 0;
    p[2] = 0;
    p[5] = val;
}

// FUNCTION: DAO 0x8592F0
int __fastcall fn_004592f0(const char* begin, const char* end, int* status) {
    unsigned int upper = 0;
    status[0] = 0xb;
    if ((unsigned int)(end - begin) != 3)
        return 1;
    char c = begin[0];
    if (c == 'X')
        upper = 1;
    else if (c != 'x')
        return 1;
    c = begin[1];
    if (c == 'M')
        upper = 1;
    else if (c != 'm')
        return 1;
    c = begin[2];
    if (c == 'L')
        return 0;
    if (c != 'l')
        return 1;
    if (upper == 0) {
        status[0] = 0xc;
        return 1;
    }
    return 0;
}