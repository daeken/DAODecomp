struct Node19;
class Tree19;
struct Iter19 { Tree19* tree; Node19* node; };
struct PairIter19 { Iter19 first; Iter19 second; };
struct Node19 {
    Node19* left;
    Node19* parent;
    Node19* right;
    unsigned int key;
    unsigned char pad19[0x19 - 0x10];
    unsigned char flag19;
};
class Tree19 {
public:
    unsigned int pad0;
    Node19* head;
    void fn_000f2bb0(PairIter19* out, unsigned int* keyptr);
};

struct Node21;
class Tree21;
struct Iter21 { Tree21* tree; Node21* node; };
struct Node21 {
    Node21* left;
    Node21* parent;
    Node21* right;
    unsigned int key;
    unsigned char pad21[0x21 - 0x10];
    unsigned char flag21;
};
class Tree21 {
public:
    unsigned int pad0;
    Node21* head;
    void fn_000fed40(Iter21* out, unsigned int* keyptr);
};

struct Node2d {
    unsigned int pad0;
    unsigned int pad4;
    Node2d* child;
    unsigned char pad[0x2d - 0x0c];
    unsigned char flag;
};

struct Node31 {
    Node31* child;
    unsigned char pad[0x31 - 0x04];
    unsigned char flag;
};

struct WString18 {
    unsigned int pad0;
    union {
        unsigned short* ptr;
        unsigned short buf[8];
    } data;
    unsigned int length;
    unsigned int capacity;
};

class Obj6AA0 {
public:
    unsigned int pad[8];
    unsigned int field20;
    void fn_000f6aa0(unsigned int v);
};

class Obj9390 { public: void* fn_000f9390(); };
class Obj93A0 { public: unsigned char fn_000f93a0(); };
class ObjFA060 { public: int fn_000fa060(); };
class ObjFE8F0 { public: void* fn_000fe8f0(); };
class ObjFE900 { public: unsigned int fn_000fe900(); };
class ObjFE910 { public: void* fn_000fe910(); };
class ObjFE920 { public: unsigned char fn_000fe920(); };
class ObjFE940 { public: void fn_000fe940(unsigned int v); };

// FUNCTION: DAO 0x4F2B00
void __cdecl fn_000f2b00(unsigned int* first, unsigned int* last, unsigned int* dest)
{
    while (first != last) {
        dest[0] = first[0];
        dest[1] = first[1];
        first += 2;
        dest += 2;
    }
}

// FUNCTION: DAO 0x4F2BB0
void Tree19::fn_000f2bb0(PairIter19* out, unsigned int* keyptr)
{
    Node19* header = this->head;
    Node19* upper = header;
    Node19* cur = header->parent;
    if (cur->flag19 == 0) {
        unsigned int key = *keyptr;
        do {
            if (key < cur->key) {
                upper = cur;
                cur = cur->left;
            } else {
                cur = cur->right;
            }
        } while (cur->flag19 == 0);
    }
    Node19* lower = header;
    cur = header->parent;
    if (cur->flag19 == 0) {
        unsigned int key = *keyptr;
        do {
            if (cur->key >= key) {
                lower = cur;
                cur = cur->left;
            } else {
                cur = cur->right;
            }
        } while (cur->flag19 == 0);
    }
    out->first.tree = this;
    out->first.node = lower;
    out->second.tree = this;
    out->second.node = upper;
}

// FUNCTION: DAO 0x4F6AA0
void Obj6AA0::fn_000f6aa0(unsigned int v)
{
    if (this->field20 == 0) {
        this->field20 = v;
    }
}

// FUNCTION: DAO 0x4F6B20
Node2d* __cdecl fn_000f6b20(Node2d* p)
{
    Node2d* n = p->child;
    while (n->flag == 0) {
        p = n;
        n = p->child;
    }
    return p;
}

// FUNCTION: DAO 0x4F6F40
Node31* __cdecl fn_000f6f40(Node31* p)
{
    Node31* n = p->child;
    while (n->flag == 0) {
        p = n;
        n = p->child;
    }
    return p;
}

// FUNCTION: DAO 0x4F7AA0
bool __cdecl fn_000f7aa0(WString18* s)
{
    for (unsigned int i = 0; i < s->length; ++i) {
        unsigned short c = (s->capacity >= 8) ? s->data.ptr[i] : s->data.buf[i];
        if (!((c >= 0x30 && c <= 0x39) ||
              (c >= 0x61 && c <= 0x7a) ||
              (c >= 0x41 && c <= 0x5a) ||
              c == 0x5f || c == 0x2d ||
              c == 0x28 || c == 0x29 || c == 0x2e)) {
            return false;
        }
    }
    return true;
}

// FUNCTION: DAO 0x4F9390
void* Obj9390::fn_000f9390()
{
    return (void*)((char*)this + 8);
}

// FUNCTION: DAO 0x4F93A0
unsigned char Obj93A0::fn_000f93a0()
{
    return *(unsigned char*)((char*)this + 0x24);
}

// FUNCTION: DAO 0x4FA060
int ObjFA060::fn_000fa060()
{
    unsigned char* begin = *(unsigned char**)((char*)this + 4);
    if (begin == 0) {
        return 0;
    }
    unsigned char* end = *(unsigned char**)((char*)this + 8);
    return (int)((end - begin) / 68);
}

// FUNCTION: DAO 0x4FE8F0
void* ObjFE8F0::fn_000fe8f0()
{
    return (void*)((char*)this + 0x1c);
}

// FUNCTION: DAO 0x4FE900
unsigned int ObjFE900::fn_000fe900()
{
    return *(unsigned int*)((char*)this + 0x70);
}

// FUNCTION: DAO 0x4FE910
void* ObjFE910::fn_000fe910()
{
    return (void*)((char*)this + 0x10c);
}

// FUNCTION: DAO 0x4FE920
unsigned char ObjFE920::fn_000fe920()
{
    return *(unsigned char*)((char*)this + 0x10);
}

// FUNCTION: DAO 0x4FE940
void ObjFE940::fn_000fe940(unsigned int v)
{
    if (v != 0) {
        *(unsigned int*)((char*)this + 0x74) = v;
    }
}

// FUNCTION: DAO 0x4FE950
Node21* __cdecl fn_000fe950(Node21* p)
{
    Node21* n = p->left;
    while (n->flag21 == 0) {
        p = n;
        n = p->left;
    }
    return p;
}

// FUNCTION: DAO 0x4FED40
void Tree21::fn_000fed40(Iter21* out, unsigned int* keyptr)
{
    Node21* header = this->head;
    Node21* prev = header;
    Node21* cur = header->parent;
    if (cur->flag21 == 0) {
        unsigned int key = *keyptr;
        do {
            if (key < cur->key) {
                prev = cur;
                cur = cur->left;
            } else {
                cur = cur->right;
            }
        } while (cur->flag21 == 0);
    }
    Node21* end = this->head;
    if (prev != end && *keyptr >= prev->key) {
        out->tree = this;
        out->node = prev;
    } else {
        out->tree = this;
        out->node = end;
    }
}
