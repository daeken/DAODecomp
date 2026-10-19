struct Fn005dabb0_Node { unsigned char pad[0x18]; int key; };
struct Fn005dabb0_Entry { unsigned int unknown0; Fn005dabb0_Node* node; };
class Fn005dabb0_Object {
public:
    Fn005dabb0_Entry* data;
    unsigned int count;
    unsigned int fn_005dabb0(int key);
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

struct Fn005dbfd0_Element { unsigned char pad0[0x24]; unsigned char flags; unsigned char pad1[3]; };
class Fn005dbfd0_Object {
public:
    Fn005dbfd0_Element* data;
    unsigned int count;
    unsigned char pad0[0x11];
    unsigned char flag19;
    bool fn_005dbfd0();
};

struct Fn005dc020_Header { unsigned char pad[4]; unsigned int field4; };
class Fn005dc020_Object {
public:
    Fn005dc020_Header* ptr;
    unsigned int field4;
    unsigned int field8;
    unsigned int pad0[4];
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

struct Fn005dc280_Data {
    unsigned int f0;
    unsigned int f1;
    unsigned int f2;
    unsigned int f3;
    unsigned int f4;
    unsigned int f5;
    unsigned int f6;
    unsigned int f7;
    unsigned int f8;
    unsigned char b;
};
class Fn005dc280_Object {
public:
    unsigned char pad[0xc];
    Fn005dc280_Data data;
    void fn_005dc280(Fn005dc280_Data* out);
};

class Fn005dc6d0_Object {
public:
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    unsigned int f14;
    unsigned char b18;
    unsigned char b19;
    Fn005dc6d0_Object* fn_005dc6d0();
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
    unsigned char table3[0x100];
    unsigned char table2[0x100];
    unsigned char table1[0x100];
    void fn_005dca00(const unsigned char* input, unsigned char* output, unsigned int count);
};

class Fn0060db80_Object {
public:
    unsigned char pad0[4];
    unsigned short value;
    unsigned short fn_0060db80();
};

// FUNCTION: DAO 0x9DABB0
unsigned int Fn005dabb0_Object::fn_005dabb0(int key) {
    unsigned int n = this->count;
    if (n == 0) return 0;
    Fn005dabb0_Entry* data = this->data;
    unsigned int lo = n >> 1;
    unsigned int step = n >> 1;
    for (;;) {
        step >>= 1;
        if (step < 1) step = 1;
        int nodekey = data[lo].node->key;
        if (key > nodekey) {
            if (lo == n - 1) return n;
            lo += step;
        } else if (key == nodekey) {
            while (lo != 0 && data[lo - 1].node->key >= key) {
                --lo;
            }
            return lo;
        } else {
            if (lo == 0) return lo;
            if (key > data[lo - 1].node->key) return lo;
            lo -= step;
        }
    }
}

// FUNCTION: DAO 0x9DBE70
int fn_005dbe70(Fn005dbe70_Container* c, int count, int* keyptr) {
    int lo = 0;
    int hi = count - 1;
    if (hi > 0) {
        for (;;) {
            if (hi == -1) break;
            int mid = (hi + lo) >> 1;
            int diff = c->array[mid].key - *keyptr;
            if (diff == 0) return mid;
            if (diff >= 0) hi = mid - 1;
            else lo = mid + 1;
            if (!(lo < hi)) break;
        }
    }
    if (lo > hi) return lo;
    while (lo <= hi) {
        int diff = c->array[lo].key - *keyptr;
        if (diff >= 0) break;
        ++lo;
    }
    return lo;
}

// FUNCTION: DAO 0x9DBEF0
Fn005dbef0_Element* Fn005dbef0_Object::fn_005dbef0(unsigned int key) {
    unsigned int n = this->count;
    if (n == 0) return 0;
    Fn005dbef0_Element* p = this->data;
    for (unsigned int i = 0; i < n; ++i) {
        if (p[i].key == key) return &p[i];
    }
    return 0;
}

// FUNCTION: DAO 0x9DBFD0
bool Fn005dbfd0_Object::fn_005dbfd0() {
    if (this->flag19 == 0) {
        this->flag19 = 0xFF;
        unsigned int n = this->count;
        for (unsigned int i = 0; i < n; ++i) {
            if ((this->data[i].flags & 7) != 0) {
                this->flag19 = 1;
                break;
            }
        }
    }
    return this->flag19 == 1;
}

// FUNCTION: DAO 0x9DC020
int Fn005dc020_Object::fn_005dc020() {
    if (this->field8 >= this->ptr->field4) return 1;
    if (this->field1c == 0) return 1;
    return 0;
}

// FUNCTION: DAO 0x9DC060
void Fn005dc060_Object::fn_005dc060(Fn005dc060_Source* src) {
    unsigned char s = src->flags;
    if ((s & 7) != 0) {
        this->flags ^= (unsigned char)((this->flags ^ s) & 7);
    }
    if (s & 8) {
        this->flags |= 8;
        this->field0 = src->field0;
    }
    if (s & 0x10) {
        this->flags |= 0x10;
        this->field4 = src->field4;
    }
    if (s & 0x20) {
        this->flags |= 0x20;
        this->field8 = src->field8;
    }
}

// FUNCTION: DAO 0x9DC280
void Fn005dc280_Object::fn_005dc280(Fn005dc280_Data* out) {
    out->f0 = this->data.f0;
    out->f1 = this->data.f1;
    out->f2 = this->data.f2;
    out->f3 = this->data.f3;
    out->f4 = this->data.f4;
    out->f5 = this->data.f5;
    out->f6 = this->data.f6;
    out->f7 = this->data.f7;
    out->f8 = this->data.f8;
    out->b = this->data.b;
}

// FUNCTION: DAO 0x9DC6D0
Fn005dc6d0_Object* Fn005dc6d0_Object::fn_005dc6d0() {
    this->f0 = 0;
    this->f4 = 0;
    this->f8 = 0;
    this->fc = 0;
    this->f10 = 0;
    this->f14 = 0;
    this->b18 = 0;
    this->b19 = 0;
    return this;
}

// FUNCTION: DAO 0x9DC840
bool Fn005dc840_Object::fn_005dc840(unsigned int size1, unsigned int size2, unsigned int* out1, unsigned int* out2) {
    unsigned int cur8 = this->field8;
    if (cur8 + size1 <= this->field0) {
        if (this->fieldC + size2 <= this->field4) {
            *out1 = cur8;
            *out2 = this->fieldC;
            this->field8 += size1;
            if (size2 > this->field10) this->field10 = size2;
            return true;
        }
    }
    this->fieldC += this->field10;
    if (this->fieldC + size2 > this->field4) return false;
    *out1 = 0;
    *out2 = this->fieldC;
    this->field8 = size1;
    this->field10 = size2;
    return true;
}

// FUNCTION: DAO 0x9DCA00
void Fn005dca00_Object::fn_005dca00(const unsigned char* input, unsigned char* output, unsigned int count) {
    if (count <= 4) return;
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

// FUNCTION: DAO 0x9FC0D0
int fn_005fc0d0(int a, int b) {
    return (a + b - 1) / b;
}

// FUNCTION: DAO 0xA0DB80
unsigned short Fn0060db80_Object::fn_0060db80() {
    return this->value;
}
