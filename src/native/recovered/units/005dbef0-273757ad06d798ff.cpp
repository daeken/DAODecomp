struct Fn005dabb0_Node { unsigned char pad[0x18]; int key; };
struct Fn005dabb0_Entry { unsigned int unknown; Fn005dabb0_Node* node; };
class Fn005dabb0_Object {
public:
    Fn005dabb0_Entry* data;
    int count;
    int fn_005dabb0(int key);
};

struct Fn005dbe70_Element { int pad[5]; int key; int pad2[4]; };
struct Fn005dbe70_Container { Fn005dbe70_Element* array; };

struct Fn005dbef0_Element { int pad[5]; int key; int pad2[4]; };
class Fn005dbef0_Object {
public:
    Fn005dbef0_Element* data;
    unsigned int count;
    Fn005dbef0_Element* fn_005dbef0(unsigned int key);
};

struct Fn005dc060_Source {
    unsigned int field0;
    unsigned int field4;
    unsigned int field8;
    unsigned char flags;
    unsigned char pad[3];
};
class Fn005dc060_Object {
public:
    unsigned int field0;
    unsigned int field4;
    unsigned int field8;
    unsigned char flags;
    unsigned char pad[3];
    void fn_005dc060(Fn005dc060_Source* src);
};

class Fn005dca00_Object {
public:
    unsigned char pad0[0x3b0];
    unsigned char table3[0x100];
    unsigned char table2[0x100];
    unsigned char table1[0x100];
    void fn_005dca00(const unsigned char* input, unsigned char* output, unsigned int count);
};

// FUNCTION: DAO 0x9DABB0
int Fn005dabb0_Object::fn_005dabb0(int key) {
    int n = this->count;
    if (n == 0)
        return 0;
    Fn005dabb0_Entry* data = this->data;
    int step = n >> 1;
    int idx = step;
    for (;;) {
        step >>= 1;
        if (step < 1)
            step = 1;
        int nodekey = data[idx].node->key;
        if (key > nodekey) {
            if (idx == n - 1)
                return n;
            idx += step;
        } else if (key == nodekey) {
            if (idx == 0)
                return idx;
            while (data[idx - 1].node->key >= key) {
                --idx;
                if (idx == 0)
                    return idx;
            }
            return idx;
        } else {
            if (idx == 0)
                return idx;
            if (key > data[idx - 1].node->key)
                return idx;
            idx -= step;
        }
    }
}

// FUNCTION: DAO 0x9DBE70
int __cdecl fn_005dbe70(Fn005dbe70_Container* c, int count, int* keyptr) {
    int lo = 0;
    int hi = count - 1;
    if (hi > 0) {
        for (;;) {
            if (hi == -1)
                break;
            int mid = (hi + lo) / 2;
            int diff = c->array[mid].key - *keyptr;
            if (diff == 0)
                return mid;
            if (diff >= 0)
                hi = mid - 1;
            else
                lo = mid + 1;
            if (lo >= hi)
                break;
        }
    }
    if (lo > hi)
        return lo;
    int k = *keyptr;
    Fn005dbe70_Element* p = c->array + lo;
    while (lo <= hi) {
        if (p->key - k >= 0)
            break;
        ++lo;
        p = (Fn005dbe70_Element*)((char*)p + 0x28);
    }
    return lo;
}

// FUNCTION: DAO 0x9DBEF0
Fn005dbef0_Element* Fn005dbef0_Object::fn_005dbef0(unsigned int key) {
    unsigned int n = this->count;
    unsigned int i = 0;
    if (i < n) {
        Fn005dbef0_Element* p = this->data;
        int* k = &p[0].key;
        do {
            if (*k == (int)key)
                return &p[i];
            ++i;
            k = (int*)((char*)k + 0x28);
        } while (i < n);
    }
    return 0;
}

// FUNCTION: DAO 0x9DC060
void Fn005dc060_Object::fn_005dc060(Fn005dc060_Source* src) {
    unsigned int s = src->flags;
    if ((s & 7) != 0) {
        unsigned char d = (unsigned char)(this->flags ^ (s & 7));
        d = (unsigned char)(d & 7);
        this->flags ^= d;
    }
    if (src->flags & 8) {
        unsigned int v = src->field0;
        this->flags |= 8;
        this->field0 = v;
    }
    if (src->flags & 0x10) {
        unsigned int v = src->field4;
        this->flags |= 0x10;
        this->field4 = v;
    }
    if (src->flags & 0x20) {
        unsigned int v = src->field8;
        this->flags |= 0x20;
        this->field8 = v;
    }
}

// FUNCTION: DAO 0x9DCA00
void Fn005dca00_Object::fn_005dca00(const unsigned char* input, unsigned char* output, unsigned int count) {
    if (count <= 4)
        return;
    const unsigned char* p = input + 2;
    for (unsigned int i = 4; i < count; ++i) {
        unsigned char b = *p;
        output[0] = (unsigned char)(output[0] + this->table1[b]);
        output[1] = (unsigned char)(output[1] + this->table2[b]);
        output[2] = (unsigned char)(output[2] + this->table3[b]);
        output[3] = (unsigned char)(output[3] + this->table2[b]);
        output[4] = (unsigned char)(output[4] + this->table1[b]);
        ++p;
        ++output;
    }
}
