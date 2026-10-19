struct DAO_Node {
    DAO_Node* field0;
    DAO_Node* field4;
    DAO_Node* field8;
    unsigned char pad0C[0x0D];
    unsigned char field19;
};

class DAO_Object {
public:
    void fn_000e9bf0(unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int);
    int fn_000ebb60();
    int fn_000eef80(const unsigned char*, unsigned int, unsigned char*, unsigned int*, unsigned int);
    int fn_000eefe0(unsigned char*, unsigned int, unsigned int*, unsigned int);
    DAO_Object* fn_000ef090(unsigned int, unsigned int);
    void* fn_000f2530(void**, unsigned int*);
    bool fn_000f25b0();
    bool fn_000f2800();
    unsigned int fn_000f2830(unsigned int, unsigned int);
    DAO_Node* fn_000f2850(DAO_Node*);
    unsigned char fn_000f6a70();
};

// FUNCTION: DAO 0x4E99E0
unsigned int __cdecl fn_000e99e0(unsigned int* p) {
    unsigned int x = *p;
    *p = (x << 24) | ((x & 0x0000FF00u) << 8) | ((x & 0x00FF0000u) >> 8) | (x >> 24);
    return x >> 24;
}

// FUNCTION: DAO 0x4E9A10
unsigned short* __cdecl fn_000e9a10(unsigned short* p) {
    unsigned short v = *p;
    *p = (unsigned short)((v >> 8) | (v << 8));
    return p;
}

// FUNCTION: DAO 0x4E9BF0
void __thiscall DAO_Object::fn_000e9bf0(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(base + 0x18) = a1;
    *reinterpret_cast<unsigned int*>(base + 0x38) = a4;
    *reinterpret_cast<unsigned int*>(base + 0x3C) = a5;
    *reinterpret_cast<unsigned int*>(base + 0x40) = a6;
    *reinterpret_cast<unsigned int*>(base + 0x44) = a3;
    *reinterpret_cast<unsigned int*>(base + 4) = a2;
}

// FUNCTION: DAO 0x4EBB60
int __thiscall DAO_Object::fn_000ebb60() {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(base + 0x40) = 0;
    *reinterpret_cast<unsigned int*>(base + 0x44) = 0;
    *(base + 0x48) = 0;
    return 0;
}

// FUNCTION: DAO 0x4EBD40
char __cdecl fn_000ebd40(char* p, int index) {
    return p[index];
}

// FUNCTION: DAO 0x4EEF80
int __thiscall DAO_Object::fn_000eef80(const unsigned char* src, unsigned int len, unsigned char* dst, unsigned int* outLen, unsigned int) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    unsigned int i = 0;
    unsigned int j = 0;
    unsigned int count = len;
    if (count != 0) {
        do {
            dst[j] = (unsigned char)(src[j] ^ base[4 + i]);
            ++j;
            ++i;
            if (i > *reinterpret_cast<unsigned int*>(base + 0x104)) {
                i = 0;
            }
        } while (--count != 0);
    }
    *outLen = len;
    return 1;
}

// FUNCTION: DAO 0x4EEFE0
int __thiscall DAO_Object::fn_000eefe0(unsigned char* buf, unsigned int len, unsigned int* outLen, unsigned int) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    unsigned int i = 0;
    unsigned int j = 0;
    if (len != 0) {
        unsigned int count = len;
        do {
            buf[j] = (unsigned char)(buf[j] ^ base[4 + i]);
            ++i;
            if (i > *reinterpret_cast<unsigned int*>(base + 0x104)) {
                i = 0;
            }
            ++j;
        } while (--count != 0);
    }
    *outLen = len;
    return 1;
}

// FUNCTION: DAO 0x4EF090
DAO_Object* __thiscall DAO_Object::fn_000ef090(unsigned int a, unsigned int b) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<unsigned int*>(base) = a;
    *reinterpret_cast<unsigned int*>(base + 4) = b;
    return this;
}

// FUNCTION: DAO 0x4F1E60
unsigned int* __stdcall fn_000f1e60(const unsigned char* src, unsigned int* dst) {
    dst[0] = ((unsigned int)src[0] << 24) | ((unsigned int)src[1] << 16) | ((unsigned int)src[2] << 8) | (unsigned int)src[3];
    dst[1] = ((unsigned int)src[4] << 24) | ((unsigned int)src[5] << 16) | ((unsigned int)src[6] << 8) | (unsigned int)src[7];
    return dst;
}

// FUNCTION: DAO 0x4F2530
void* __thiscall DAO_Object::fn_000f2530(void** outPtr, unsigned int* outSize) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    *outPtr = base + 0x14;
    *outSize = 0x18;
    return outPtr;
}

// FUNCTION: DAO 0x4F25B0
bool __thiscall DAO_Object::fn_000f25b0() {
    return *reinterpret_cast<unsigned int*>(this) == 6;
}

// FUNCTION: DAO 0x4F2800
bool __thiscall DAO_Object::fn_000f2800() {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    return *reinterpret_cast<unsigned int*>(base + 4) != 0;
}

// FUNCTION: DAO 0x4F2830
unsigned int __thiscall DAO_Object::fn_000f2830(unsigned int a, unsigned int b) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    if (a == 0) {
        *reinterpret_cast<unsigned int*>(base + 0x44) = 0;
        *reinterpret_cast<unsigned int*>(base + 0x48) = 0;
        return 0;
    }
    *reinterpret_cast<unsigned int*>(base + 0x44) = a;
    *reinterpret_cast<unsigned int*>(base + 0x48) = b;
    return b;
}

// FUNCTION: DAO 0x4F2850
DAO_Node* __thiscall DAO_Object::fn_000f2850(DAO_Node* z) {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    DAO_Node* y = z->field8;
    z->field8 = y->field0;
    DAO_Node* x = y->field0;
    if (x->field19 == 0) {
        x->field4 = z;
    }
    y->field4 = z->field4;
    DAO_Node* root = *reinterpret_cast<DAO_Node**>(base + 4);
    if (z == root->field4) {
        root->field4 = y;
        y->field0 = z;
        z->field4 = y;
        return y;
    }
    DAO_Node* parent = z->field4;
    if (z == parent->field0) {
        parent->field0 = y;
        y->field0 = z;
        z->field4 = y;
        return y;
    }
    parent->field8 = y;
    y->field0 = z;
    z->field4 = y;
    return y;
}

// FUNCTION: DAO 0x4F6A70
unsigned char __thiscall DAO_Object::fn_000f6a70() {
    unsigned char* base = reinterpret_cast<unsigned char*>(this);
    return *(base + 0x38);
}

// FUNCTION: DAO 0x8E29F0
char* __cdecl fn_004e29f0(char* dest, char* src, unsigned int count) {
    char* start = dest;
    if (count != 0) {
        while (count != 0) {
            char c = *src++;
            *dest++ = c;
            --count;
            if (c == 0) {
                break;
            }
        }
        if (count != 0) {
            volatile char* d = dest;
            do {
                *d++ = 0;
                --count;
            } while (count != 0);
        }
    }
    return start;
}
