struct TreeNode {
    TreeNode* field0;
    TreeNode* field4;
    TreeNode* field8;
    unsigned char pad0[0x10 - 12];
    unsigned short keybuf[8];
    unsigned int key_size;
    unsigned int key_cap;
    unsigned char pad1[0x41 - 0x28];
    unsigned char flag41;
    unsigned char pad2[0x65 - 0x42];
    unsigned char flag65;
};

struct WKey {
    unsigned char pad[4];
    unsigned short buf[8];
    unsigned int size;
    unsigned int cap;
};

struct Tree {
    unsigned int pad0;
    TreeNode* field4;
    void fn_003cebd0(TreeNode* p);
    TreeNode* fn_003cf2d0();
    TreeNode* fn_003d3670(WKey* key);
    TreeNode* fn_003d3730(WKey* key);
};

// FUNCTION: DAO 0x7CEBD0
void Tree::fn_003cebd0(TreeNode* p) {
    TreeNode* eax = p->field8;
    TreeNode* esi = eax->field0;
    p->field8 = esi;
    esi = eax->field0;
    if (esi->flag41 == 0) {
        esi->field4 = p;
    }
    esi = p->field4;
    eax->field4 = esi;
    TreeNode* ecx = this->field4;
    if (p == ecx->field4) {
        ecx->field4 = eax;
        eax->field0 = p;
        p->field4 = eax;
        return;
    }
    ecx = p->field4;
    if (p == ecx->field0) {
        ecx->field0 = eax;
        eax->field0 = p;
        p->field4 = eax;
        return;
    }
    ecx->field8 = eax;
    eax->field0 = p;
    p->field4 = eax;
}

// FUNCTION: DAO 0x7CF2D0
TreeNode* Tree::fn_003cf2d0() {
    TreeNode* eax = this->field4;
    if (eax == 0) {
        return 0;
    }
    return eax->field0;
}

// FUNCTION: DAO 0x7D0050
void fn_003d0050(void* dst, unsigned int count, const void* src) {
    if (count == 0) {
        return;
    }
    unsigned char* d = (unsigned char*)dst;
    const unsigned char* s = (const unsigned char*)src;
    do {
        if (d) {
            unsigned int* di = (unsigned int*)d;
            const unsigned int* si = (const unsigned int*)s;
            di[0] = si[0];
            di[1] = si[1];
            di[2] = si[2];
            di[3] = si[3];
            di[4] = si[4];
            di[5] = si[5];
        }
        --count;
        d += 0x18;
    } while (count != 0);
}

// FUNCTION: DAO 0x7D3670
TreeNode* Tree::fn_003d3670(WKey* key) {
    TreeNode* sentinel = this->field4;
    TreeNode* node = sentinel->field4;
    TreeNode* result = sentinel;
    if (node->flag65 == 0) {
        unsigned int key_len = key->size;
        unsigned int key_cap = key->cap;
        const unsigned short* key_base;
        if (key_cap >= 8) {
            key_base = *(const unsigned short**)((unsigned char*)key + 4);
        } else {
            key_base = key->buf;
        }
        do {
            unsigned int node_len = node->key_size;
            unsigned int min_len = node_len < key_len ? node_len : key_len;
            const unsigned short* node_data;
            if (node->key_cap >= 8) {
                node_data = *(const unsigned short**)((unsigned char*)node + 0x10);
            } else {
                node_data = node->keybuf;
            }
            const unsigned short* key_data = key_base;
            int cmp = 0;
            unsigned int i = min_len;
            while (i != 0) {
                unsigned short a = *node_data;
                unsigned short b = *key_data;
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                ++node_data;
                ++key_data;
                --i;
            }
            if (cmp == 0) {
                if (node_len < key_len) {
                    cmp = -1;
                } else if (node_len > key_len) {
                    cmp = 1;
                }
            }
            if (cmp < 0) {
                node = node->field8;
            } else {
                result = node;
                node = node->field0;
            }
        } while (node->flag65 == 0);
    }
    return result;
}

// FUNCTION: DAO 0x7D3730
TreeNode* Tree::fn_003d3730(WKey* key) {
    TreeNode* sentinel = this->field4;
    TreeNode* node = sentinel->field4;
    TreeNode* result = sentinel;
    if (node->flag41 == 0) {
        unsigned int key_len = key->size;
        unsigned int key_cap = key->cap;
        const unsigned short* key_base;
        if (key_cap >= 8) {
            key_base = *(const unsigned short**)((unsigned char*)key + 4);
        } else {
            key_base = key->buf;
        }
        do {
            unsigned int node_len = node->key_size;
            unsigned int min_len = node_len < key_len ? node_len : key_len;
            const unsigned short* node_data;
            if (node->key_cap >= 8) {
                node_data = *(const unsigned short**)((unsigned char*)node + 0x10);
            } else {
                node_data = node->keybuf;
            }
            const unsigned short* key_data = key_base;
            int cmp = 0;
            unsigned int i = min_len;
            while (i != 0) {
                unsigned short a = *node_data;
                unsigned short b = *key_data;
                if (a != b) {
                    cmp = (a < b) ? -1 : 1;
                    break;
                }
                ++node_data;
                ++key_data;
                --i;
            }
            if (cmp == 0) {
                if (node_len < key_len) {
                    cmp = -1;
                } else if (node_len > key_len) {
                    cmp = 1;
                }
            }
            if (cmp < 0) {
                node = node->field8;
            } else {
                result = node;
                node = node->field0;
            }
        } while (node->flag41 == 0);
    }
    return result;
}

struct Class6 {
    unsigned char pad[0x4ac];
    unsigned int field4ac;
    void fn_003e4720(unsigned int v);
};

// FUNCTION: DAO 0x7E4720
void Class6::fn_003e4720(unsigned int v) {
    this->field4ac = v;
}

struct Class7 {
    unsigned char pad[0x444];
    unsigned int field444;
    void fn_003e6850();
};

// FUNCTION: DAO 0x7E6850
void Class7::fn_003e6850() {
    this->field444 = 2;
}

// FUNCTION: DAO 0x7EEF50
void fn_003eef50(const void* begin, const void* end, void* dst) {
    const unsigned char* s = (const unsigned char*)begin;
    const unsigned char* e = (const unsigned char*)end;
    unsigned char* d = (unsigned char*)dst;
    if (s == e) {
        return;
    }
    do {
        if (d) {
            unsigned int* di = (unsigned int*)d;
            const unsigned int* si = (const unsigned int*)s;
            di[0] = si[0];
            di[1] = si[1];
            di[2] = si[2];
            di[3] = si[3];
            di[4] = si[4];
        }
        s += 0x14;
        d += 0x14;
    } while (s != e);
}

struct Class9 {
    unsigned int* field0;
    unsigned int field4;
    int fn_003ef150();
};

// FUNCTION: DAO 0x7EF150
int Class9::fn_003ef150() {
    unsigned int* p = this->field0;
    if (p == 0) {
        return 0;
    }
    if (this->field4 <= 0x1c) {
        return 0;
    }
    if (p[0] != 0x20464647) {
        return 0;
    }
    if (p[1] != 0x302e3456) {
        return 0;
    }
    if (p[3] != 0x564e4f43) {
        return 0;
    }
    if (p[4] != 0x312e3056) {
        return 0;
    }
    return 1;
}

struct IntNode {
    IntNode* field0;
    IntNode* field4;
    IntNode* field8;
    unsigned int field_c;
    unsigned char pad[0x15 - 0x10];
    unsigned char flag15;
};

struct TreeInt;
struct IterPair {
    TreeInt* first;
    IntNode* second;
};

struct TreeInt {
    unsigned int pad0;
    IntNode* field4;
    void fn_003f4f60(IterPair* out, const unsigned int* key);
};

// FUNCTION: DAO 0x7F4F60
void TreeInt::fn_003f4f60(IterPair* out, const unsigned int* key) {
    IntNode* header = this->field4;
    IntNode* node = header->field4;
    IntNode* candidate = header;
    if (node->flag15 == 0) {
        do {
            if (node->field_c < *key) {
                node = node->field8;
            } else {
                candidate = node;
                node = node->field0;
            }
        } while (node->flag15 == 0);
    }
    IntNode* header2 = this->field4;
    if (candidate == header2) {
        out->first = this;
        out->second = header2;
    } else {
        if (*key < candidate->field_c) {
            out->first = this;
            out->second = header2;
        } else {
            out->first = this;
            out->second = candidate;
        }
    }
}

// FUNCTION: DAO 0x7F6AF0
void fn_003f6af0(void* begin, void* end, const void* src) {
    unsigned char* p = (unsigned char*)begin;
    unsigned char* e = (unsigned char*)end;
    const unsigned char* s = (const unsigned char*)src;
    if (p == e) {
        return;
    }
    do {
        *(unsigned int*)(p + 4) = *(const unsigned int*)(s + 4);
        *(unsigned int*)(p + 8) = *(const unsigned int*)(s + 8);
        *(unsigned int*)(p + 0xc) = *(const unsigned int*)(s + 0xc);
        p += 0x10;
    } while (p != e);
}

// FUNCTION: DAO 0x7F8350
IntNode* fn_003f8350(IntNode* n) {
    IntNode* eax = n;
    IntNode* ecx = eax->field0;
    if (ecx->flag15 != 0) {
        return eax;
    }
    do {
        eax = ecx;
        ecx = eax->field0;
    } while (ecx->flag15 == 0);
    return eax;
}
