struct C_0044e810 {
    unsigned int pad0;
    unsigned int begin;
    unsigned int end;
    int fn_0044e810();
};

struct C_00453470 {
    void* field0;
    void* field4;
    void* field8;
    void* fieldC;
    void* field10;
    void fn_00453470();
};

// FUNCTION: DAO 0x84B0C0
bool fn_0044b0c0(void* p) {
    unsigned char* b = (unsigned char*)p;
    if ((*(unsigned int*)(b + 0x70) & 0x200000u) != 0) {
        unsigned int v = *(unsigned int*)(b + 0x18);
        if (v > 0)
            return v != 1;
    }
    return false;
}

// FUNCTION: DAO 0x84E810
int C_0044e810::fn_0044e810() {
    unsigned int b = this->begin;
    if (b == 0)
        return 0;
    int diff = (int)(this->end - b);
    return diff / 88;
}

// FUNCTION: DAO 0x852850
void __fastcall fn_00452850(unsigned int list, unsigned int owner) {
    if (list == 0)
        return;
    unsigned int cur = list;
    while (cur != 0) {
        unsigned int next = *(unsigned int*)(cur + 4);
        unsigned int head = *(unsigned int*)(owner + 0x174);
        *(unsigned int*)(cur + 4) = head;
        *(unsigned int*)(owner + 0x174) = cur;
        cur = next;
    }
}

// FUNCTION: DAO 0x8528A0
void fn_004528a0(void* p, unsigned int value) {
    unsigned int* q = (unsigned int*)p;
    if (q[1] == q[0]) {
        q[0] = value;
        q[1] = value;
    } else {
        q[0] = value;
    }
}

// FUNCTION: DAO 0x8528D0
void fn_004528d0(void* p, unsigned int a, unsigned int b) {
    *(unsigned int*)((char*)p + 0x34) = a;
    *(unsigned int*)((char*)p + 0x38) = b;
}

// FUNCTION: DAO 0x8528F0
void fn_004528f0(void* p, unsigned int a) {
    *(unsigned int*)((char*)p + 0x3c) = a;
}

// FUNCTION: DAO 0x852E20
unsigned int fn_00452e20(void* p) {
    return *(unsigned int*)((char*)p + 0x11c);
}

// FUNCTION: DAO 0x852E30
void fn_00452e30(unsigned short* p) {
    unsigned short* src = p;
    while (*src != 0) {
        if (*src == 0x0D)
            break;
        ++src;
    }
    if (*src == 0)
        return;
    unsigned short* dst = src;
    for (;;) {
        unsigned short ch = *src;
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

// FUNCTION: DAO 0x853070
bool __fastcall fn_00453070(const unsigned short* a, const unsigned short* b) {
    for (;;) {
        if (*a != *b)
            return false;
        if (*a == 0)
            return true;
        ++a;
        ++b;
    }
}

// FUNCTION: DAO 0x8530A0
unsigned int __fastcall fn_004530a0(unsigned int, const unsigned short* s) {
    unsigned int h = 0;
    while (*s != 0) {
        h = h * 0xF4243u;
        h ^= (unsigned int)*s;
        ++s;
    }
    return h;
}

// FUNCTION: DAO 0x853400
void __fastcall fn_00453400(unsigned int obj, unsigned int val) {
    unsigned int* p = (unsigned int*)obj;
    *((unsigned char*)p + 4) = 0;
    p[2] = 0;
    p[3] = 0;
    p[0] = 0;
    p[4] = val;
}

// FUNCTION: DAO 0x853420
void __fastcall fn_00453420(const unsigned int* src, unsigned int* dst) {
    unsigned int base = src[0];
    dst[0] = base;
    unsigned int count = src[2];
    dst[1] = base + count * 4;
}

// FUNCTION: DAO 0x853430
void* __fastcall fn_00453430(unsigned int, void** it) {
    unsigned char* cur = (unsigned char*)it[0];
    unsigned char* end = (unsigned char*)it[1];
    while (cur != end) {
        void* v = *(void**)cur;
        cur += 4;
        it[0] = cur;
        if (v != 0)
            return v;
    }
    return 0;
}

// FUNCTION: DAO 0x853450
void __fastcall fn_00453450(unsigned int obj, unsigned int val) {
    unsigned int* p = (unsigned int*)obj;
    p[0] = 0;
    p[1] = 0;
    p[4] = 0;
    p[3] = 0;
    p[2] = 0;
    p[5] = val;
}

// FUNCTION: DAO 0x853470
void C_00453470::fn_00453470() {
    if (this->field4 == 0) {
        this->field4 = this->field0;
    } else {
        void* node = this->field0;
        while (node != 0) {
            void* next = *(void**)node;
            *(void**)node = this->field4;
            this->field4 = node;
            node = next;
        }
    }
    this->field0 = 0;
    this->field10 = 0;
    this->fieldC = 0;
    this->field8 = 0;
}

// FUNCTION: DAO 0x8592F0
int __fastcall fn_004592f0(const char* begin, const char* end, int* status) {
    status[0] = 0xb;
    if ((unsigned int)(end - begin) != 3)
        return 1;
    unsigned int upper = 0;
    char c = begin[0];
    if (c == 'X') {
        upper = 1;
    } else if (c != 'x') {
        return 1;
    }
    c = begin[1];
    if (c == 'M') {
        upper = 1;
    } else if (c != 'm') {
        return 1;
    }
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