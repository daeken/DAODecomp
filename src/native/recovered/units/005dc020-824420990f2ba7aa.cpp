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

struct Fn005dc020_Header { unsigned int pad0; unsigned int field4; };
class Fn005dc020_Object {
public:
    Fn005dc020_Header* ptr;
    unsigned int field4;
    unsigned int field8;
    unsigned char pad0[0x10];
    int field1c;
    int fn_005dc020();
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

class Fn005dc840_Object {
public:
    unsigned int field0;
    unsigned int field4;
    unsigned int field8;
    unsigned int fieldC;
    unsigned int field10;
    bool fn_005dc840(unsigned int size1, unsigned int size2, unsigned int* out1, unsigned int* out2);
};

class Fn005dca00_Object {
public:
    unsigned char pad0[0x3b0];
    unsigned char table[0x300];
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
        } else if (key >= nodekey) {
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
            int mid = (lo + hi) / 2;
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
    while (lo <= hi) {
        int diff = c->array[lo].key - *keyptr;
        if (diff >= 0)
            break;
        ++lo;
    }
    return lo;
}

// FUNCTION: DAO 0x9DBEF0
Fn005dbef0_Element* Fn005dbef0_Object::fn_005dbef0(unsigned int key) {
    unsigned int n = this->count;
    unsigned int i = 0;
    Fn005dbef0_Element* p = this->data;
    for (; i < n; ++i) {
        if (p[i].key == key)
            return &p[i];
    }
    return 0;
}

// FUNCTION: DAO 0x9DC020
int Fn005dc020_Object::fn_005dc020() {
    if (this->field8 < this->ptr->field4) {
        if (this->field1c != 0)
            return 0;
    }
    return 1;
}

// FUNCTION: DAO 0x9DC060
void Fn005dc060_Object::fn_005dc060(Fn005dc060_Source* src) {
    unsigned int low = src->flags;
    if ((low & 7) != 0) {
        this->flags ^= (unsigned char)((this->flags ^ (low & 7)) & 7);
    }
    if (src->flags & 8) {
        this->flags |= 8;
        this->field0 = src->field0;
    }
    if (src->flags & 0x10) {
        this->flags |= 0x10;
        this->field4 = src->field4;
    }
    if (src->flags & 0x20) {
        this->flags |= 0x20;
        this->field8 = src->field8;
    }
}

// FUNCTION: DAO 0x9DC840
bool Fn005dc840_Object::fn_005dc840(unsigned int size1, unsigned int size2, unsigned int* out1, unsigned int* out2) {
    unsigned int cur8 = this->field8;
    if (cur8 + size1 <= this->field0) {
        if (this->fieldC + size2 <= this->field4) {
            *out1 = cur8;
            *out2 = this->fieldC;
            this->field8 += size1;
            if (size2 > this->field10)
                this->field10 = size2;
            return true;
        }
    }
    this->fieldC += this->field10;
    if (this->fieldC + size2 <= this->field4) {
        *out1 = 0;
        *out2 = this->fieldC;
        this->field8 = size1;
        this->field10 = size2;
        return true;
    }
    return false;
}

// FUNCTION: DAO 0x9DCA00
void Fn005dca00_Object::fn_005dca00(const unsigned char* input, unsigned char* output, unsigned int count) {
    const unsigned char* p = input + 2;
    for (unsigned int i = 4; i < count; ++i) {
        unsigned char b = *p;
        output[0] += this->table[0x200 + b];
        output[1] += this->table[0x100 + b];
        output[2] += this->table[b];
        output[3] += this->table[0x100 + b];
        output[4] += this->table[0x200 + b];
        ++p;
        ++output;
    }
}
