struct ElemNameId {
    unsigned int pad0[10];
    const char* name;
    unsigned int pad2c;
    unsigned int id;
};

struct InnerNameId {
    unsigned int pad0[24];
    ElemNameId** begin;
    ElemNameId** end;
};

struct C004bcce0 {
    InnerNameId* field0;
    unsigned int fn_004bcce0(const char* name);
};

struct C004bcd70 {
    InnerNameId* field0;
    const char* fn_004bcd70(unsigned int id);
};

struct Out004bcdc0 {
    unsigned int count1;
    unsigned int count2;
    unsigned int size1;
    unsigned int size2;
    unsigned int ptr1;
    unsigned int ptr2;
    unsigned int field18;
    unsigned int field1c;
    unsigned int field20;
    unsigned int ptr24;
    unsigned int ptr28;
};

struct Obj004bcdc0 {
    unsigned int pad0;
    unsigned int pad4;
    unsigned int begin1;
    unsigned int end1;
    unsigned int pad10;
    unsigned int pad14;
    unsigned int begin2;
    unsigned int end2;
    unsigned int pad20;
    unsigned int pad24;
    unsigned int pad28;
    unsigned int begin3;
    unsigned int end3;
    unsigned int pad34;
    unsigned int pad38;
    unsigned int begin4;
    unsigned int end4;
};

struct Elem004bce60 {
    const char* name;
    unsigned int pad0[18];
    unsigned int value;
};

struct Inner004bce60 {
    unsigned int pad0[32];
    Elem004bce60** begin;
    Elem004bce60** end;
};

struct C004bce60 {
    Inner004bce60* field0;
    unsigned int fn_004bce60(const char* name);
};

struct Obj004c1b80 {
    unsigned int pad0;
    unsigned int field4;
    unsigned int pad8;
    unsigned int fieldc;
    unsigned char pad10[0x211 - 0x10];
    unsigned char field211;
};

struct Elem004cdd60 {
    unsigned int pad0[7];
    const char* name;
};

struct C004cdd60 {
    unsigned int pad0[6];
    Elem004cdd60** begin;
    Elem004cdd60** end;
    unsigned int pad20;
    Elem004cdd60* fn_004cdd60(const char* name);
};

struct Elem004cde80 {
    unsigned int pad0[7];
    unsigned char flag;
};

struct C004cde80 {
    unsigned int pad0[7];
    Elem004cde80** begin;
    Elem004cde80** end;
    bool fn_004cde80();
};

// FUNCTION: DAO 0x8BCCE0
unsigned int C004bcce0::fn_004bcce0(const char* name)
{
    InnerNameId* inner = field0;
    if (inner == 0) {
        return 0;
    }
    if (name == 0) {
        return 0;
    }
    unsigned int count = (unsigned int)(inner->end - inner->begin);
    for (unsigned int i = 0; i < count; ++i) {
        ElemNameId* elem = inner->begin[i];
        const char* a = elem->name;
        const char* b = name;
        while (*a && *a == *b) {
            ++a;
            ++b;
        }
        if (*a == *b) {
            return elem->id;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8BCD70
const char* C004bcd70::fn_004bcd70(unsigned int id)
{
    InnerNameId* inner = field0;
    if (inner == 0) {
        return 0;
    }
    if (id == 0) {
        return 0;
    }
    unsigned int count = (unsigned int)(inner->end - inner->begin);
    for (unsigned int i = 0; i < count; ++i) {
        ElemNameId* elem = inner->begin[i];
        if (elem->id == id) {
            return elem->name;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8BCDC0
Out004bcdc0* __stdcall fn_004bcdc0(Out004bcdc0* out, const Obj004bcdc0* obj)
{
    unsigned int diff1 = obj->end1 - obj->begin1;
    out->count1 = diff1 / 12;
    unsigned int diff2 = obj->end2 - obj->begin2;
    out->count2 = diff2 >> 4;
    out->size1 = 0xc;
    out->size2 = 0x10;
    if (out->count1 != 0) {
        out->ptr1 = obj->begin1;
    }
    if (out->count2 != 0) {
        out->ptr2 = obj->begin2;
    }
    unsigned int diff3 = obj->end3 - obj->begin3;
    if ((diff3 & 0xfffffffc) != 0) {
        out->ptr28 = obj->begin3;
        out->field20 = 4;
    } else {
        out->ptr28 = 0;
        out->field20 = 0;
    }
    unsigned int diff4 = obj->end4 - obj->begin4;
    if ((diff4 & 0xfffffffc) != 0) {
        out->ptr24 = obj->begin4;
        out->field1c = 4;
    } else {
        out->ptr24 = 0;
        out->field1c = 0;
    }
    return out;
}

// FUNCTION: DAO 0x8BCE60
unsigned int C004bce60::fn_004bce60(const char* name)
{
    Inner004bce60* inner = field0;
    if (inner == 0) {
        return 0;
    }
    if (name == 0) {
        return 0;
    }
    unsigned int count = (unsigned int)(inner->end - inner->begin);
    for (unsigned int i = 0; i < count; ++i) {
        Elem004bce60* elem = inner->begin[i];
        const char* a = elem->name;
        const char* b = name;
        while (*a && *a == *b) {
            ++a;
            ++b;
        }
        if (*a == *b) {
            return elem->value;
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8C1B80
unsigned int __cdecl fn_004c1b80(Obj004c1b80* obj, unsigned int* out)
{
    *out = 0;
    if (obj == 0) {
        return 0;
    }
    unsigned int result = obj->field4;
    *out = obj->fieldc;
    obj->field211 = 0;
    return result;
}

// FUNCTION: DAO 0x8CDD60
Elem004cdd60* C004cdd60::fn_004cdd60(const char* name)
{
    unsigned int count = (unsigned int)(end - begin);
    for (unsigned int i = 0; i < count; ++i) {
        Elem004cdd60* elem = begin[i];
        const char* s = name;
        if (s != 0) {
            const char* t = elem->name;
            if (t != 0) {
                if (*s == '#') {
                    ++s;
                }
                const char* a = s;
                const char* b = t;
                while (*a && *a == *b) {
                    ++a;
                    ++b;
                }
                if (*a == *b) {
                    return elem;
                }
            }
        }
    }
    return 0;
}

// FUNCTION: DAO 0x8CDE80
bool C004cde80::fn_004cde80()
{
    unsigned int count = (unsigned int)(end - begin);
    if (count == 0) {
        return true;
    }
    for (unsigned int i = 0; i < count; ++i) {
        if (begin[i]->flag == 0) {
            return false;
        }
    }
    return true;
}

// FUNCTION: DAO 0x8DA0F0
int __cdecl fn_004da0f0(const int* a, const int* b)
{
    int x = *a;
    int y = *b;
    return x < y ? x : y;
}
