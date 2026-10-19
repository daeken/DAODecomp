struct Node3 {
    Node3* left;
    unsigned char pad[0x0d];
    unsigned char flag;
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

struct C_5fe380 {
    int pad0;
    char* begin;
    char* end;
    int fn_001fe380();
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

struct C_5ffbf0 {
    char pad0[4];
    Node6* head;
    void fn_001ffbf0(Out6* out, int* key);
};

struct C_606c60 {
    unsigned char pad0[0x1f4];
    void* field;
    void fn_00206c60(void* p);
};

struct C_616fe0 {
    int val;
    unsigned char fn_00216fe0();
};

struct Node9 {
    Node9* left;
    Node9* parent;
    Node9* right;
    unsigned char pad[0x15];
    unsigned char flag;
};

struct C_617270 {
    char pad0[4];
    Node9* head;
    void fn_00217270(Node9* x);
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

struct C_62a040 {
    char pad0[8];
    int offset;
    void fn_0022a040(char* base, char* src);
};

struct C_62a150 {
    char pad0[4];
    char* begin;
    char* end;
    bool fn_0022a150();
};

struct S13 {
    char pad0[8];
    unsigned int offset;
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

struct C_62eca0 {
    char* fn_0022eca0();
};

struct C_62ecb0 {
    char* fn_0022ecb0();
};

struct Blk16 {
    unsigned int w0;
    unsigned int w1;
    unsigned int w2;
    unsigned int w3;
};

// FUNCTION: DAO 0x5FE380
int C_5fe380::fn_001fe380() {
    if (!begin) return 0;
    return (int)(end - begin) / 44;
}

// FUNCTION: DAO 0x5FE3A0
int C_5fe3a0::fn_001fe3a0() {
    if (!begin) return 0;
    return (int)(end - begin) / 36;
}

// FUNCTION: DAO 0x5FE3C0
Node3* fn_001fe3c0(Node3* p) {
    Node3* x = p->left;
    if (x->flag != 0) return p;
    do {
        p = x;
        x = p->left;
    } while (x->flag == 0);
    return p;
}

// FUNCTION: DAO 0x5FE770
void fn_001fe770(Blk16* first, Blk16* last, Blk16* destEnd) {
    while (first != last) {
        --last;
        --destEnd;
        *destEnd = *last;
    }
}

// FUNCTION: DAO 0x5FEAD0
int C_5fead0::fn_001fead0() {
    if (!begin) return 0;
    return (int)(end - begin) / 36;
}

// FUNCTION: DAO 0x5FFBF0
void C_5ffbf0::fn_001ffbf0(Out6* out, int* key) {
    Node6* head = this->head;
    Node6* upper = head;
    Node6* y = head->parent;
    if (y->flag == 0) {
        int k = *key;
        do {
            if (k < y->key) {
                upper = y;
                y = y->left;
            } else {
                y = y->right;
            }
        } while (y->flag == 0);
    }
    Node6* lower = head;
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
    out->f4 = lower;
    out->f0 = this;
    out->f8 = this;
    out->fC = upper;
}

// FUNCTION: DAO 0x606C60
void C_606c60::fn_00206c60(void* p) {
    field = p;
}

// FUNCTION: DAO 0x616FE0
unsigned char C_616fe0::fn_00216fe0() {
    return val != -1;
}

// FUNCTION: DAO 0x617270
void C_617270::fn_00217270(Node9* x) {
    Node9* y = x->right;
    x->right = y->left;
    if (y->left->flag == 0) {
        y->left->parent = x;
    }
    y->parent = x->parent;
    Node9* head = this->head;
    if (x == head->parent) {
        head->parent = y;
        y->left = x;
        x->parent = y;
        return;
    }
    Node9* p = x->parent;
    if (x == p->left) {
        p->left = y;
        y->left = x;
        x->parent = y;
        return;
    }
    p->right = y;
    y->left = x;
    x->parent = y;
}

// FUNCTION: DAO 0x6175C0
void C_6175c0::fn_002175c0(Out6* out, unsigned int* key) {
    Node10* head = this->head;
    Node10* upper = head;
    Node10* y = head->parent;
    if (y->flag == 0) {
        unsigned int k = *key;
        do {
            if (k >= y->key) {
                y = y->right;
            } else {
                upper = y;
                y = y->left;
            }
        } while (y->flag == 0);
    }
    Node10* lower = head;
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
    out->f4 = lower;
    out->f0 = this;
    out->f8 = this;
    out->fC = upper;
}

// FUNCTION: DAO 0x62A040
void C_62a040::fn_0022a040(char* base, char* src) {
    base[offset] = *src;
}

// FUNCTION: DAO 0x62A150
bool C_62a150::fn_0022a150() {
    if (!begin) return true;
    return ((int)(end - begin) / 8) == 0;
}

// FUNCTION: DAO 0x62A1A0
char fn_0022a1a0(S13* s, unsigned int idx) {
    return *(char*)(s->offset + idx);
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
    if (node != head && *key >= node->key) {
        out->container = this;
        out->node = node;
    } else {
        out->container = this;
        out->node = head;
    }
}

// FUNCTION: DAO 0x62ECA0
char* C_62eca0::fn_0022eca0() {
    return (char*)this + 0x454;
}

// FUNCTION: DAO 0x62ECB0
char* C_62ecb0::fn_0022ecb0() {
    return (char*)this + 0x470;
}
