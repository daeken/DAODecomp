typedef unsigned int uint32;

struct DAOObject;
struct Key { uint32 id; uint32 pad; char name[1]; };
struct Node {
    void* field0;
    char* name4;
    char* name8;
    unsigned char pad0c[4];
    DAOObject* owner10;
    Key* key14;
    unsigned char pad18[8];
    Node* field20;
    Node* field24;
    Node* field28;
};

class DAOObject {
public:
    unsigned char pad0[0x10];
    DAOObject* field10;
    void* field14;
    void* field18;
    void* field1c;
    void* field20;
    void* field24;
    void* field28;
    void* field2c;
    Node* fn_004cddf0(const char* name);
    Node* fn_004ce6a0(const char* name);
    Node* fn_004ce740(const char* name);
    Node* fn_004ce7e0(const char* name);
    void fn_004d5f50(Node* node);
    Node* fn_004d6220(Key** key);
};

// FUNCTION: DAO 0x8CDDF0
Node* DAOObject::fn_004cddf0(const char* name) {
    int count = (Node**)field24 - (Node**)field20;
    unsigned int i = 0;
    if (count == 0) return 0;
    Node** p = (Node**)field20;
    while (i < (unsigned int)((Node**)field24 - (Node**)field20)) {
        Node* node = *p;
        const char* s = name;
        if (s != 0 && node->name4 != 0) {
            if (*s == '#') ++s;
            const char* t = node->name4;
            while (*s == *t) {
                if (*s == 0) return node;
                ++s;
                ++t;
            }
        }
        ++p;
        ++i;
    }
    return 0;
}

// FUNCTION: DAO 0x8CE6A0
Node* DAOObject::fn_004ce6a0(const char* name) {
    if (name == 0) return 0;
    int count = (Node**)field1c - (Node**)field18;
    unsigned int i = 0;
    if (count == 0) return 0;
    Node** p = (Node**)field18;
    while (i < (unsigned int)((Node**)field1c - (Node**)field18)) {
        Node* node = *p;
        const char* s = name;
        if (*s == '#') ++s;
        const char* t = node->name8;
        if (t != 0) {
            while (*s == *t) {
                if (*s == 0) return node;
                ++s;
                ++t;
            }
        }
        ++p;
        ++i;
    }
    return 0;
}

// FUNCTION: DAO 0x8CE740
Node* DAOObject::fn_004ce740(const char* name) {
    if (name == 0) return 0;
    int count = (Node**)field2c - (Node**)field28;
    unsigned int i = 0;
    if (count == 0) return 0;
    Node** p = (Node**)field28;
    while (i < (unsigned int)((Node**)field2c - (Node**)field28)) {
        Node* node = *p;
        const char* s = name;
        const char* t = node->name8;
        if (t != 0) {
            if (*s == '#') ++s;
            while (*s == *t) {
                if (*s == 0) return node;
                ++s;
                ++t;
            }
        }
        ++p;
        ++i;
    }
    return 0;
}

// FUNCTION: DAO 0x8CE7E0
Node* DAOObject::fn_004ce7e0(const char* name) {
    int count = (Node**)field1c - (Node**)field18;
    unsigned int i = 0;
    if (count == 0) return 0;
    Node** p = (Node**)field18;
    while (i < (unsigned int)((Node**)field1c - (Node**)field18)) {
        Node* node = *p;
        const char* s = name;
        if (s != 0 && node->name4 != 0) {
            if (*s == '#') ++s;
            const char* t = node->name4;
            while (*s == *t) {
                if (*s == 0) return node;
                ++s;
                ++t;
            }
        }
        ++p;
        ++i;
    }
    return 0;
}

// FUNCTION: DAO 0x8D5F50
void DAOObject::fn_004d5f50(Node* node) {
    node->owner10 = this;
    node->field24 = (Node*)field1c;
    node->field28 = 0;
    Node* tail = (Node*)field1c;
    if (tail != 0) {
        tail->field28 = node;
        field1c = (void*)node;
    } else {
        field18 = (void*)node;
        field1c = (void*)node;
    }
}

// FUNCTION: DAO 0x8D6220
Node* DAOObject::fn_004d6220(Key** key) {
    Node* node = (Node*)field20;
    Node* result = 0;
    if (node != (Node*)this) {
        Key* k = *key;
        unsigned int id = k->id;
        for (;;) {
            Key* nk = node->key14;
            if (nk->id == id) {
                const char* a = (const char*)nk + 8;
                const char* b = (const char*)k + 8;
                while (*a == *b) {
                    if (*a == 0) {
                        result = node;
                        break;
                    }
                    ++a;
                    ++b;
                }
                if (result != 0) break;
            }
            node = node->field20;
            if (node == (Node*)this) break;
        }
    }
    return result;
}
