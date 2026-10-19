struct Elem1 {
    unsigned char pad_00[0x28];
    unsigned int value_28;
    unsigned char pad_2C[0x4C];
    unsigned int key_78;
};
struct Obj1 {
    unsigned char pad_00[0x40];
    Elem1** begin_40;
    Elem1** end_44;
};
struct Holder1 {
    Obj1* p_00;
    unsigned int fn_004bc7e0(unsigned int key);
};

struct Elem2 {
    unsigned int value_00;
    unsigned char pad_04[0x2C];
    unsigned int key_30;
};
struct Obj2 {
    unsigned char pad_00[0x50];
    Elem2** begin_50;
    Elem2** end_54;
};
struct Holder2 {
    Obj2* p_00;
    unsigned int fn_004bc8c0(unsigned int key);
};

struct Elem3 {
    const char* name_00;
    unsigned char pad_04[0x1C];
    unsigned int value_20;
};
struct Obj3 {
    unsigned char pad_00[0x1D0];
    Elem3** begin_1D0;
    Elem3** end_1D4;
};
struct Holder3 {
    unsigned int pad_00;
    Obj3* p_04;
    unsigned int fn_004bc910(const char* key);
};

struct Elem4 {
    const char* name_00;
    unsigned char pad_04[0x9C];
    unsigned int value_A0;
};
struct Obj4 {
    unsigned char pad_00[0x1E0];
    Elem4** begin_1E0;
    Elem4** end_1E4;
};
struct Holder4 {
    unsigned int pad_00;
    Obj4* p_04;
    unsigned int fn_004bc9b0(const char* key);
};

struct Elem5 {
    unsigned char pad_00[0x28];
    const char* name_28;
    unsigned char pad_2C[0x2C];
    unsigned int value_58;
};
struct Obj5 {
    unsigned char pad_00[0x70];
    Elem5** begin_70;
    Elem5** end_74;
};
struct Holder5 {
    Obj5* p_00;
    unsigned int fn_004bca50(const char* key);
};

struct Elem6 {
    const char* name_00;
    unsigned char pad_04[0x1C];
    unsigned int value_20;
};
struct Obj6 {
    unsigned char pad_00[0x170];
    Elem6** begin_170;
    Elem6** end_174;
};
struct Holder6 {
    unsigned int pad_00;
    Obj6* p_04;
    unsigned int fn_004bcae0(const char* key);
};

struct Sub7 {
    unsigned char pad_00[0x14];
    unsigned int* f14;
    unsigned int* f18;
};
struct Holder7 {
    unsigned char pad_00[0x20];
    Sub7* p20;
    Sub7* fn_004d6090();
};

// FUNCTION: DAO 0x008BC7E0
unsigned int Holder1::fn_004bc7e0(unsigned int key)
{
    unsigned int result = 0;
    Obj1* obj = p_00;
    if (obj != 0 && key != 0) {
        Elem1** p = obj->begin_40;
        for (unsigned int i = 0; i < (unsigned int)(obj->end_44 - obj->begin_40); ++i) {
            Elem1* e = *p;
            if (e->key_78 == key) {
                result = e->value_28;
                break;
            }
            ++p;
        }
    }
    return result;
}

// FUNCTION: DAO 0x008BC8C0
unsigned int Holder2::fn_004bc8c0(unsigned int key)
{
    unsigned int result = 0;
    Obj2* obj = p_00;
    if (obj != 0 && key != 0) {
        Elem2** p = obj->begin_50;
        for (unsigned int i = 0; i < (unsigned int)(obj->end_54 - obj->begin_50); ++i) {
            Elem2* e = *p;
            if (e->key_30 == key) {
                result = e->value_00;
                break;
            }
            ++p;
        }
    }
    return result;
}

// FUNCTION: DAO 0x008BC910
unsigned int Holder3::fn_004bc910(const char* key)
{
    unsigned int result = 0;
    Obj3* obj = p_04;
    if (obj != 0 && key != 0) {
        Elem3** p = obj->begin_1D0;
        for (unsigned int i = 0; i < (unsigned int)(obj->end_1D4 - obj->begin_1D0); ++i) {
            Elem3* e = *p;
            const char* s = e->name_00;
            const char* t = key;
            while (*s == *t && *s != 0) {
                ++s;
                ++t;
            }
            if (*s == *t) return e->value_20;
            ++p;
        }
    }
    return result;
}

// FUNCTION: DAO 0x008BC9B0
unsigned int Holder4::fn_004bc9b0(const char* key)
{
    unsigned int result = 0;
    Obj4* obj = p_04;
    if (obj != 0 && key != 0) {
        Elem4** p = obj->begin_1E0;
        for (unsigned int i = 0; i < (unsigned int)(obj->end_1E4 - obj->begin_1E0); ++i) {
            Elem4* e = *p;
            const char* s = e->name_00;
            const char* t = key;
            while (*s == *t && *s != 0) {
                ++s;
                ++t;
            }
            if (*s == *t) return e->value_A0;
            ++p;
        }
    }
    return result;
}

// FUNCTION: DAO 0x008BCA50
unsigned int Holder5::fn_004bca50(const char* key)
{
    unsigned int result = 0;
    Obj5* obj = p_00;
    if (obj != 0 && key != 0) {
        Elem5** p = obj->begin_70;
        for (unsigned int i = 0; i < (unsigned int)(obj->end_74 - obj->begin_70); ++i) {
            Elem5* e = *p;
            const char* s = e->name_28;
            const char* t = key;
            while (*s == *t && *s != 0) {
                ++s;
                ++t;
            }
            if (*s == *t) return e->value_58;
            ++p;
        }
    }
    return result;
}

// FUNCTION: DAO 0x008BCAE0
unsigned int Holder6::fn_004bcae0(const char* key)
{
    unsigned int result = 0;
    Obj6* obj = p_04;
    if (obj != 0 && key != 0) {
        Elem6** p = obj->begin_170;
        for (unsigned int i = 0; i < (unsigned int)(obj->end_174 - obj->begin_170); ++i) {
            Elem6* e = *p;
            const char* s = e->name_00;
            const char* t = key;
            while (*s == *t && *s != 0) {
                ++s;
                ++t;
            }
            if (*s == *t) return e->value_20;
            ++p;
        }
    }
    return result;
}

// FUNCTION: DAO 0x008D6090
Sub7* Holder7::fn_004d6090()
{
    Sub7* p = p20;
    if (*(p->f18) == 0) {
        if (*(p->f14) == 0) {
            return 0;
        }
    }
    return p;
}
