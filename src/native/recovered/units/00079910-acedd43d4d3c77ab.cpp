struct C079910 {
    unsigned int field_0;
    unsigned char* field_4;
    unsigned char* field_8;
    int fn_00079910();
};

struct C091A90 {
    unsigned int field_0;
    unsigned char* field_4;
    unsigned char* field_8;
    int fn_00091a90();
};

struct ArgKey092140 {
    unsigned int field_0;
    union {
        unsigned short buf[8];
        unsigned short* ptr;
    } bx;
    unsigned int size;
    unsigned int cap;
};

struct Node092140 {
    Node092140* field_0;
    Node092140* field_4;
    Node092140* field_8;
    unsigned int field_C;
    union {
        unsigned short buf[8];
        unsigned short* ptr;
    } key;
    unsigned int size;
    unsigned int cap;
    unsigned char pad_28[0x45 - 0x28];
    unsigned char isnil;
};

struct C092140 {
    unsigned int pad_0;
    Node092140* header;
    Node092140* fn_00092140(const ArgKey092140& key);
};

struct C097560 {
    unsigned char pad_0[0x134];
    unsigned int field_134;
    bool fn_00097560(unsigned int mask);
};

struct C097B60 {
    unsigned char pad_0[0x70];
    unsigned char* fn_00097b60();
};

struct C097B70 {
    unsigned int field_0;
    unsigned char* field_4;
    unsigned char* field_8;
    int fn_00097b70();
};

struct C098D90 {
    unsigned char pad_0[0x4c];
    unsigned int field_4C;
    unsigned char pad_50[0x134 - 0x50];
    int field_134;
    int field_138;
    int field_13C;
    unsigned char pad_140[0x144 - 0x140];
    int field_144;
    bool fn_00098d90();
};

struct C0A49B0 {
    unsigned int field_0;
    unsigned char* field_4;
    unsigned int field_8;
    unsigned int field_C;
    C0A49B0* fn_000a49b0();
    unsigned int fn_000a49e0();
    unsigned char fn_000a49f0();
    unsigned int fn_000a4a30(unsigned int value);
    unsigned int fn_000a4a50(unsigned char value);
};

struct C0A52B0 {
    unsigned char pad_0[0x21];
    unsigned char field_21;
    unsigned char pad_22[0x158 - 0x22];
    unsigned char field_158;
    unsigned char pad_159[0x15f - 0x159];
    unsigned char field_15f;
    unsigned char pad_160[0x162 - 0x160];
    unsigned char field_162;
    void fn_000a52b0();
    bool fn_000a52d0();
    bool fn_000a52e0();
};

struct NodeB54E0 {
    unsigned char pad_0[0x20];
    char* field_20;
    unsigned char pad_24[4];
    NodeB54E0* field_28;
};

struct C0B54E0 {
    unsigned char pad_0[0x18];
    NodeB54E0* field_18;
    void* fn_000b54e0(const char* key);
};

// FUNCTION: DAO 0x479910
int C079910::fn_00079910() {
    unsigned char* begin = field_4;
    if (!begin) return 0;
    int diff = (int)(field_8 - begin);
    return diff / 36;
}

// FUNCTION: DAO 0x491A90
int C091A90::fn_00091a90() {
    unsigned char* begin = field_4;
    if (!begin) return 0;
    int diff = (int)(field_8 - begin);
    return diff / 104;
}

// FUNCTION: DAO 0x492140
Node092140* C092140::fn_00092140(const ArgKey092140& key) {
    Node092140* result = this->header;
    Node092140* node = this->header->field_4;
    const unsigned short* keydata = (key.cap < 8) ? key.bx.buf : key.bx.ptr;
    unsigned int keylen = key.size;
    while (!node->isnil) {
        unsigned int nodelen = node->size;
        const unsigned short* nodedata = (node->cap < 8) ? node->key.buf : node->key.ptr;
        unsigned int minlen = nodelen < keylen ? nodelen : keylen;
        unsigned int i = 0;
        while (i < minlen) {
            if (nodedata[i] != keydata[i]) break;
            ++i;
        }
        int cmp;
        if (i < minlen) {
            cmp = (nodedata[i] < keydata[i]) ? -1 : 1;
        } else {
            if (nodelen < keylen) cmp = -1;
            else if (nodelen > keylen) cmp = 1;
            else cmp = 0;
        }
        if (cmp < 0) {
            node = node->field_8;
        } else {
            result = node;
            node = node->field_0;
        }
    }
    return result;
}

// FUNCTION: DAO 0x497560
bool C097560::fn_00097560(unsigned int mask) {
    return (field_134 & mask) != 0;
}

// FUNCTION: DAO 0x497B60
unsigned char* C097B60::fn_00097b60() {
    return (unsigned char*)this + 0x70;
}

// FUNCTION: DAO 0x497B70
int C097B70::fn_00097b70() {
    unsigned char* begin = field_4;
    if (!begin) return 0;
    int diff = (int)(field_8 - begin);
    return diff / 372;
}

// FUNCTION: DAO 0x498D90
bool C098D90::fn_00098d90() {
    if (field_4C == 0) return false;
    if (field_134 == -1) return false;
    if (field_138 == -1) return false;
    if (field_13C == -1) return false;
    if (field_144 == -1) return false;
    return true;
}

// FUNCTION: DAO 0x4A49B0
C0A49B0* C0A49B0::fn_000a49b0() {
    field_0 = 0;
    field_8 = 0;
    field_C = 0;
    field_4 = 0;
    return this;
}

// FUNCTION: DAO 0x4A49E0
unsigned int C0A49B0::fn_000a49e0() {
    unsigned int result = *(unsigned int*)field_4;
    field_C += 4;
    field_4 += 4;
    return result;
}

// FUNCTION: DAO 0x4A49F0
unsigned char C0A49B0::fn_000a49f0() {
    unsigned char result = *field_4;
    field_C += 1;
    ++field_4;
    return result;
}

// FUNCTION: DAO 0x4A4A30
unsigned int C0A49B0::fn_000a4a30(unsigned int value) {
    *(unsigned int*)field_4 = value;
    field_4 += 4;
    field_C += 4;
    return 4;
}

// FUNCTION: DAO 0x4A4A50
unsigned int C0A49B0::fn_000a4a50(unsigned char value) {
    *field_4 = value;
    ++field_4;
    field_C += 1;
    return 1;
}

// FUNCTION: DAO 0x4A52B0
void C0A52B0::fn_000a52b0() {
    field_158 = 1;
    field_15f = 0;
}

// FUNCTION: DAO 0x4A52D0
bool C0A52B0::fn_000a52d0() {
    return field_162 == 0;
}

// FUNCTION: DAO 0x4A52E0
bool C0A52B0::fn_000a52e0() {
    return field_21 == 0;
}

// FUNCTION: DAO 0x4B54E0
void* C0B54E0::fn_000b54e0(const char* key) {
    NodeB54E0* node = field_18;
    while (node) {
        const char* s = node->field_20 + 8;
        const char* k = key;
        while (*s == *k) {
            if (*s == 0) return node;
            ++s;
            ++k;
        }
        node = node->field_28;
    }
    return 0;
}
