struct String092140 {
    union {
        unsigned short buf[8];
        unsigned short* ptr;
    } bx;
    unsigned int size;
    unsigned int cap;
};

struct ArgKey092140 {
    unsigned int field_0;
    String092140 key;
};

struct Node092140 {
    Node092140* field_0;
    Node092140* field_4;
    Node092140* field_8;
    unsigned int field_C;
    String092140 key;
    unsigned char pad_28[0x45 - 0x28];
    unsigned char isnil;
};

struct C092140 {
    unsigned int field_0;
    Node092140* field_4;
    Node092140* fn_00092140(const ArgKey092140& key);
};

struct C097560 {
    unsigned char pad_0[0x134];
    unsigned int field_134;
    unsigned char fn_00097560(unsigned int mask);
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
    unsigned char fn_00098d90();
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
    NodeB54E0* fn_000b54e0(const char* key);
};

extern "C" int __cdecl strcmp(const char*, const char*);
#pragma intrinsic(strcmp)

// FUNCTION: DAO 0x492140
Node092140* C092140::fn_00092140(const ArgKey092140& key) {
    Node092140* result = field_4;
    Node092140* node = result->field_4;
    if (!node->isnil) {
        unsigned int keylen = key.key.size;
        unsigned int keycap = key.key.cap;
        do {
            const unsigned short* keydata = (keycap < 8) ? key.key.bx.buf : key.key.bx.ptr;
            unsigned int nodelen = node->key.size;
            unsigned int minlen = (nodelen < keylen) ? nodelen : keylen;
            const unsigned short* nodedata = (node->key.cap < 8) ? node->key.bx.buf : node->key.bx.ptr;
            unsigned int i = 0;
            while (i < minlen && nodedata[i] == keydata[i])
                ++i;
            int cmp;
            if (i < minlen)
                cmp = (nodedata[i] < keydata[i]) ? -1 : 1;
            else if (nodelen < keylen)
                cmp = -1;
            else if (nodelen > keylen)
                cmp = 1;
            else
                cmp = 0;
            if (cmp < 0) {
                node = node->field_8;
            } else {
                result = node;
                node = node->field_0;
            }
        } while (!node->isnil);
    }
    return result;
}

// FUNCTION: DAO 0x497560
unsigned char C097560::fn_00097560(unsigned int mask) {
    return (field_134 & mask) != 0;
}

// FUNCTION: DAO 0x498D90
unsigned char C098D90::fn_00098d90() {
    return field_4C != 0 && field_134 != -1 && field_138 != -1 && field_13C != -1 && field_144 != -1;
}

// FUNCTION: DAO 0x4B54E0
NodeB54E0* C0B54E0::fn_000b54e0(const char* key) {
    NodeB54E0* node = field_18;
    while (node) {
        if (strcmp(node->field_20 + 8, key) == 0)
            return node;
        node = node->field_28;
    }
    return 0;
}
