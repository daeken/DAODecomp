struct C00666b40 {
    unsigned char pad0[0x224];
    unsigned int* arr[5];
    unsigned int __thiscall fn_00666b40(unsigned int index);
};

// FUNCTION: DAO 0x00A66B40
unsigned int __thiscall C00666b40::fn_00666b40(unsigned int index) {
    unsigned int delta = index - 3;
    if (delta > 1) {
        return 0;
    }
    unsigned int* p = arr[delta + 3];
    if (p == 0) {
        return 0;
    }
    return p[1];
}

struct C00667ab0 {
    void* field_0;
    unsigned int __thiscall fn_00667ab0();
};

// FUNCTION: DAO 0x00A67AB0
unsigned int __thiscall C00667ab0::fn_00667ab0() {
    unsigned int v = *(unsigned int*)((unsigned char*)field_0 + 0x150);
    return v == 0xFFFFFFFFu ? 3u : v;
}

struct C00668ff0 {
    const unsigned short* field_0;
    const unsigned short* field_4;
    bool __thiscall fn_00668ff0(C00668ff0* other);
};

// FUNCTION: DAO 0x00A68FF0
bool __thiscall C00668ff0::fn_00668ff0(C00668ff0* other) {
    const unsigned short* a = field_0;
    const unsigned short* b = other->field_0;
    while (*a != 0 && *a == *b) {
        ++a;
        ++b;
    }
    if (*a < *b) {
        return true;
    }
    if (*a > *b) {
        return false;
    }
    a = field_4;
    b = other->field_4;
    while (*a != 0 && *a == *b) {
        ++a;
        ++b;
    }
    return *a < *b;
}

// FUNCTION: DAO 0x00A690E0
void* __cdecl fn_006690e0(void** arg) {
    void* node = *arg;
    if (((unsigned char*)node)[0x19] != 0) {
        return arg;
    }
    do {
        arg = (void**)node;
        node = *arg;
    } while (((unsigned char*)node)[0x19] == 0);
    return arg;
}

// FUNCTION: DAO 0x00A6BC10
unsigned int* __cdecl fn_0066bc10(unsigned int* first, unsigned int* last, unsigned int* dest) {
    unsigned int* q = dest;
    unsigned int* result = q + (last - first);
    unsigned int* p = first;
    if (p != last) {
        do {
            *q = *p;
            ++q;
            ++p;
        } while (p != last);
    }
    return result;
}

// FUNCTION: DAO 0x00A6E4E0
unsigned int __cdecl fn_0066e4e0(const char* str, const char* control) {
    unsigned int bits[8] = { 0 };
    const unsigned char* c = (const unsigned char*)control;
    while (*c != 0) {
        unsigned int v = *c;
        bits[v >> 5] |= 1u << (v & 31);
        ++c;
    }
    const unsigned char* p = (const unsigned char*)str;
    unsigned int n = 0xFFFFFFFFu;
    for (;;) {
        ++n;
        unsigned char ch = *p;
        if (ch == 0) {
            break;
        }
        ++p;
        if ((bits[ch >> 5] & (1u << (ch & 31))) == 0) {
            break;
        }
    }
    return n;
}
