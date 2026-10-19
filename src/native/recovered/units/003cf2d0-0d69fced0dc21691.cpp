struct TreeNode {
    TreeNode* field0;
    TreeNode* field4;
    TreeNode* field8;
    unsigned int field_c;
    unsigned short keybuf[8];
    unsigned int key_size;
    unsigned int key_cap;
    unsigned char pad_28[0x41 - 0x28];
    unsigned char flag41;
    unsigned char pad_42[0x65 - 0x42];
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
    TreeNode* fn_003cf2d0();
    TreeNode* fn_003d3670(WKey* key);
    TreeNode* fn_003d3730(WKey* key);
};

// FUNCTION: DAO 0x7CF2D0
TreeNode* Tree::fn_003cf2d0() {
    TreeNode* p = this->field4;
    if (p != 0) {
        return p->field0;
    }
    return 0;
}

// FUNCTION: DAO 0x7D0050
void fn_003d0050(void* dst, unsigned int count, const void* src) {
    if (count <= 0) {
        return;
    }
    unsigned int* d = (unsigned int*)dst;
    const unsigned int* s = (const unsigned int*)src;
    do {
        if (d != 0) {
            d[0] = s[0];
            d[1] = s[1];
            d[2] = s[2];
            d[3] = s[3];
            d[4] = s[4];
            d[5] = s[5];
        }
        --count;
        d += 6;
    } while (count > 0);
}

// FUNCTION: DAO 0x7D3670
TreeNode* Tree::fn_003d3670(WKey* key) {
    TreeNode* header = this->field4;
    TreeNode* node = header->field4;
    if (node->flag65 != 0) {
        return header;
    }
    unsigned int key_len = key->size;
    TreeNode* result = header;
    do {
        const unsigned short* key_data;
        if (key->cap >= 8) {
            key_data = *(const unsigned short**)((unsigned char*)key + 4);
        } else {
            key_data = key->buf;
        }
        unsigned int node_len = node->key_size;
        unsigned int len = node_len;
        if (len > key_len) {
            len = key_len;
        }
        const unsigned short* node_data;
        if (node->key_cap >= 8) {
            node_data = *(const unsigned short**)((unsigned char*)node + 0x10);
        } else {
            node_data = node->keybuf;
        }
        int cmp = 0;
        unsigned int i = len;
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
    return result;
}

// FUNCTION: DAO 0x7D3730
TreeNode* Tree::fn_003d3730(WKey* key) {
    TreeNode* header = this->field4;
    TreeNode* node = header->field4;
    if (node->flag41 != 0) {
        return header;
    }
    unsigned int key_len = key->size;
    TreeNode* result = header;
    do {
        const unsigned short* key_data;
        if (key->cap >= 8) {
            key_data = *(const unsigned short**)((unsigned char*)key + 4);
        } else {
            key_data = key->buf;
        }
        unsigned int node_len = node->key_size;
        unsigned int len = node_len;
        if (len > key_len) {
            len = key_len;
        }
        const unsigned short* node_data;
        if (node->key_cap >= 8) {
            node_data = *(const unsigned short**)((unsigned char*)node + 0x10);
        } else {
            node_data = node->keybuf;
        }
        int cmp = 0;
        unsigned int i = len;
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
    return result;
}

// FUNCTION: DAO 0x7EEF50
void fn_003eef50(const void* begin, const void* end, void* dst) {
    const unsigned int* s = (const unsigned int*)begin;
    const unsigned int* e = (const unsigned int*)end;
    unsigned int* d = (unsigned int*)dst;
    while (s != e) {
        if (d != 0) {
            d[0] = s[0];
            d[1] = s[1];
            d[2] = s[2];
            d[3] = s[3];
            d[4] = s[4];
        }
        s += 5;
        d += 5;
    }
}

struct Class9 {
    unsigned int* field0;
    unsigned int field4;
    int fn_003ef150();
};

// FUNCTION: DAO 0x7EF150
int Class9::fn_003ef150() {
    unsigned int* p = this->field0;
    if (p != 0 && this->field4 > 0x1c &&
        p[0] == 0x20464647 &&
        p[1] == 0x302e3456 &&
        p[3] == 0x564e4f43 &&
        p[4] == 0x312e3056) {
        return 1;
    }
    return 0;
}

struct IntNode {
    IntNode* field0;
    IntNode* field4;
    IntNode* field8;
    unsigned int field_c;
    unsigned char pad_10[0x15 - 0x10];
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
    IterPair result;
    if (candidate == header2 || *key < candidate->field_c) {
        result.first = this;
        result.second = header2;
    } else {
        result.first = this;
        result.second = candidate;
    }
    *out = result;
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
