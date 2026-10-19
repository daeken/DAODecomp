struct Block20 {
    unsigned int v0;
    unsigned int v1;
    unsigned int v2;
    unsigned int v3;
    unsigned int v4;
};

class C_00143f80 {
public:
    unsigned int pad0;
    unsigned char* begin;
    unsigned char* end;
    bool fn_00143f80() const;
};

class C_00147910 {
public:
    unsigned char pad[0x180];
    unsigned int* field180;
    unsigned int* field184;
    bool fn_00147910() const;
};

class C_001500c0 {
public:
    unsigned char pad[0x510];
    unsigned int field510;
    unsigned int fn_001500c0() const;
};

// FUNCTION: DAO 0x543F80
bool C_00143f80::fn_00143f80() const {
    if (begin == 0) {
        bool result = (begin == 0);
        return result;
    }
    int count = (int)((end - begin) / 72);
    bool result = (count == 0);
    return result;
}

// FUNCTION: DAO 0x544270
bool __stdcall fn_00144270(unsigned char* base, unsigned int count, unsigned int stride, unsigned int offset) {
    bool result = false;
    unsigned int i = 0;
    if (count <= 0) {
        return result;
    }
    unsigned char* p = base + offset * 8;
    unsigned int step = stride * 8;
    do {
        if (*(unsigned int*)p != 0) {
            result = true;
            break;
        }
        ++i;
        p += step;
    } while (i < count);
    return result;
}

// FUNCTION: DAO 0x5468C0
void __cdecl fn_001468c0(void* dest, unsigned int count, const void* src) {
    if (count <= 0) {
        return;
    }
    const Block20* s = (const Block20*)src;
    unsigned char* d = (unsigned char*)dest;
    do {
        if (d) {
            *(Block20*)d = *s;
        }
        --count;
        d += 20;
    } while (count > 0);
}

// FUNCTION: DAO 0x547910
bool C_00147910::fn_00147910() const {
    unsigned int count = 0;
    if (field180 != 0) {
        count = (unsigned int)(field184 - field180);
        return count > 0;
    }
    return count > 0;
}

// FUNCTION: DAO 0x5500C0
unsigned int C_001500c0::fn_001500c0() const {
    unsigned int result = 0;
    switch (field510) {
    case 0:
        result = 0x20;
        break;
    case 1:
        result = 0x44;
        break;
    }
    return result;
}
