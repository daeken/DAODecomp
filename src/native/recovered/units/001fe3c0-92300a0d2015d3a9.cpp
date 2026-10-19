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

// FUNCTION: DAO 0x5FE3C0
Node3* fn_001fe3c0(Node3* p) {
    while (p->left->flag == 0)
        p = p->left;
    return p;
}

// FUNCTION: DAO 0x5FE770
Blk16* fn_001fe770(Blk16* first, Blk16* last, Blk16* destEnd) {
    Blk16* result = destEnd - (last - first);
    while (first != last) {
        --last;
        --destEnd;
        *destEnd = *last;
    }
    return result;
}

// FUNCTION: DAO 0x5FFBF0
void C_5ffbf0::fn_001ffbf0(Out6* out, int* key) {
    Node6* upper = this->head;
    Node6* x = upper->parent;
    while (x->flag == 0) {
        if (*key < x->key) {
            upper = x;
            x = x->left;
        } else {
            x = x->right;
        }
    }
    Node6* lower = this->head;
    x = lower->parent;
    while (x->flag == 0) {
        if (x->key >= *key) {
            lower = x;
            x = x->left;
        } else {
            x = x->right;
        }
    }
    out->f4 = lower;
    out->f0 = this;
    out->f8 = this;
    out->fC = upper;
}

// FUNCTION: DAO 0x6175C0
void C_6175c0::fn_002175c0(Out6* out, unsigned int* key) {
    Node10* upper = this->head;
    Node10* x = upper->parent;
    while (x->flag == 0) {
        if (*key < x->key) {
            upper = x;
            x = x->left;
        } else {
            x = x->right;
        }
    }
    Node10* lower = this->head;
    x = lower->parent;
    while (x->flag == 0) {
        if (x->key >= *key) {
            lower = x;
            x = x->left;
        } else {
            x = x->right;
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
    if (begin == 0) {
        count = 0;
    } else {
        count = ((int)(end - begin)) >> 3;
    }
    return count == 0;
}

// FUNCTION: DAO 0x62AAF0
void C_62aaf0::fn_0022aaf0(Out14* out, int* key) {
    Node14* head = this->head;
    Node14* node = head;
    Node14* x = head->parent;
    while (x->flag == 0) {
        if (x->key >= *key) {
            node = x;
            x = x->left;
        } else {
            x = x->right;
        }
    }
    if (node != head && *key >= node->key) {
        out->container = this;
        out->node = node;
    } else {
        out->container = this;
        out->node = head;
    }
}
