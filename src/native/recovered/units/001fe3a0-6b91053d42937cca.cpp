struct Node3 {
    Node3* left;
    unsigned char pad[0x0d];
    unsigned char flag;
};

struct Blk16 {
    unsigned int w0;
    unsigned int w1;
    unsigned int w2;
    unsigned int w3;
};

struct C_5fe3a0 {
    int pad0;
    char* begin;
    char* end;
    int fn_001fe3a0();
};

struct C_5fead0 {
    unsigned char pad0[0xb8];
    char* begin;
    char* end;
    int fn_001fead0();
};

struct Node6 {
    Node6* left;
    Node6* parent;
    Node6* right;
    int key;
    unsigned char pad[1];
    unsigned char flag;
};

struct Out6 {
    void* f0;
    void* f4;
    void* f8;
    void* fC;
};

struct C_5ffbf0 {
    char pad0[4];
    Node6* head;
    void fn_001ffbf0(Out6* out, int* key);
};

struct C_616fe0 {
    int val;
    int fn_00216fe0();
};

struct Node10 {
    Node10* left;
    Node10* parent;
    Node10* right;
    unsigned int key;
    unsigned char pad[0x11];
    unsigned char flag;
};

struct C_6175c0 {
    char pad0[4];
    Node10* head;
    void fn_002175c0(Out6* out, unsigned int* key);
};

struct C_62a150 {
    char pad0[4];
    char* begin;
    char* end;
    bool fn_0022a150();
};

struct Node14 {
    Node14* left;
    Node14* parent;
    Node14* right;
    int key;
    unsigned char pad[5];
    unsigned char flag;
};

struct Out14 {
    void* container;
    void* node;
};

struct C_62aaf0 {
    char pad0[4];
    Node14* head;
    void fn_0022aaf0(Out14* out, int* key);
};

// FUNCTION: DAO 0x5FE3A0
int C_5fe3a0::fn_001fe3a0() {
    if (!begin) return 0;
    return (int)(end - begin) / 72;
}

// FUNCTION: DAO 0x5FE3C0
Node3* fn_001fe3c0(Node3* p) {
    Node3* x = p->left;
    if (x->flag != 0) return p;
    do {
        Node3* next = x->left;
        p = x;
        x = next;
    } while (x->flag == 0);
    return p;
}

// FUNCTION: DAO 0x5FE770
Blk16* fn_001fe770(Blk16* first, Blk16* last, Blk16* destEnd) {
    int count = (int)(last - first) * 16;
    Blk16* result = (Blk16*)((char*)destEnd - count);
    int delta = (int)((char*)destEnd - (char*)last);
    char* src = (char*)last;
    while (src != (char*)first) {
        src -= 16;
        *(Blk16*)((char*)src + delta) = *(Blk16*)src;
    }
    return result;
}

// FUNCTION: DAO 0x5FEAD0
int C_5fead0::fn_001fead0() {
    if (!begin) return 0;
    return (int)(end - begin) / 72;
}

// FUNCTION: DAO 0x5FFBF0
void C_5ffbf0::fn_001ffbf0(Out6* out, int* key) {
    Node6* head = this->head;
    Node6* upper = head;
    {
        Node6* x = head->parent;
        if (x->flag == 0) {
            int k = *key;
            do {
                if (k < x->key) {
                    upper = x;
                    x = x->left;
                } else {
                    x = x->right;
                }
            } while (x->flag == 0);
        }
    }
    Node6* lower = head;
    {
        Node6* x = head->parent;
        if (x->flag == 0) {
            int k = *key;
            do {
                if (x->key >= k) {
                    lower = x;
                    x = x->left;
                } else {
                    x = x->right;
                }
            } while (x->flag == 0);
        }
    }
    out->f4 = lower;
    out->f0 = this;
    out->f8 = this;
    out->fC = upper;
}

// FUNCTION: DAO 0x616FE0
int C_616fe0::fn_00216fe0() {
    return val != -1;
}

// FUNCTION: DAO 0x6175C0
void C_6175c0::fn_002175c0(Out6* out, unsigned int* key) {
    Node10* head = this->head;
    Node10* upper = head;
    {
        Node10* x = head->parent;
        if (x->flag == 0) {
            unsigned int k = *key;
            do {
                if (k >= x->key) {
                    x = x->right;
                } else {
                    upper = x;
                    x = x->left;
                }
            } while (x->flag == 0);
        }
    }
    Node10* lower = head;
    {
        Node10* x = head->parent;
        if (x->flag == 0) {
            unsigned int k = *key;
            do {
                if (x->key >= k) {
                    lower = x;
                    x = x->left;
                } else {
                    x = x->right;
                }
            } while (x->flag == 0);
        }
    }
    out->f4 = lower;
    out->f0 = this;
    out->f8 = this;
    out->fC = upper;
}

// FUNCTION: DAO 0x62A150
bool C_62a150::fn_0022a150() {
    int count;
    if (begin) count = ((int)(end - begin)) >> 3;
    else count = 0;
    return count == 0;
}

// FUNCTION: DAO 0x62AAF0
void C_62aaf0::fn_0022aaf0(Out14* out, int* key) {
    Node14* head = this->head;
    Node14* node = head;
    Node14* x = head->parent;
    if (x->flag == 0) {
        int k = *key;
        do {
            if (x->key >= k) {
                node = x;
                x = x->left;
            } else {
                x = x->right;
            }
        } while (x->flag == 0);
    }
    Out14 a;
    Out14 b;
    a.container = this;
    a.node = node;
    b.container = this;
    b.node = head;
    Out14* p = (node != head && *key >= node->key) ? &a : &b;
    *out = *p;
}
