typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct C_00403c70 {
    u32 field0;
    u32 field4;
    u32 field8;
    void* fn_00003c70();
};

struct C_00451780 {
    u32 field0;
    C_00451780* fn_00051780();
};

struct E_004b9100 {
    u8 pad[0xd4];
    u32 key;
};

struct C_004b9100 {
    u8 pad[0x4c0];
    E_004b9100* slots[4];
    E_004b9100* fn_000b9100(u32 key);
};

struct C_004c05b0 {
    u32 field0;
    union Data_004c05b0 {
        u16 inline_buf[8];
        u16* heap_ptr;
    } data;
    u32 length;
    u32 capacity;
    int fn_000c05b0(const u16* set, u32 start, u32 count) const;
    C_004c05b0* fn_000c0d90();
};

struct S_000c4e10 {
    void* field0;
    void* field4;
};

struct C_000df4e0 {
    u32 field0;
    C_000df4e0* fn_000df4e0();
};

struct C_001389f0 {
    u32 field0;
    u32 field4;
    u8 field8;
    C_001389f0* fn_001389f0();
};

struct E_001dd7b0 { u8 data[12]; };
struct C_001dd7b0 {
    u32 field0;
    E_001dd7b0* begin;
    E_001dd7b0* end;
    int fn_001dd7b0() const;
};

struct E_001de880 { u8 data[16]; };
struct C_001de880 {
    u32 field0;
    E_001de880* begin;
    E_001de880* end;
    int fn_001de880() const;
};

struct C_00438210 {
    u8 pad[0xc];
    u8 field_c;
    u8 fn_00438210() const;
};

struct E_004714c0 { u8 data[28]; };
struct C_004714c0 {
    u32 field0;
    E_004714c0* begin;
    E_004714c0* end;
    int fn_004714c0() const;
};

struct C_00533d70 {
    u32 field0;
    u32 field4;
    u32 field8;
    u32 field_c;
    C_00533d70* fn_00533d70(const C_00533d70* other);
};

// FUNCTION: DAO 0x00403C70
void* C_00403c70::fn_00003c70() {
    return reinterpret_cast<void*>(reinterpret_cast<u8*>(this) + 0xc);
}

// FUNCTION: DAO 0x00413800
int fn_00138000(const u16* lhs, const u16* rhs, u32 count) {
    if (count != 0) {
        do {
            u16 a = *lhs;
            u16 b = *rhs;
            if (a != b) {
                return (a < b) ? -1 : 1;
            }
            ++lhs;
            ++rhs;
            --count;
        } while (count != 0);
    }
    return 0;
}

// FUNCTION: DAO 0x00451780
C_00451780* C_00451780::fn_00051780() {
    field0 = 0;
    return this;
}

// FUNCTION: DAO 0x004B9100
E_004b9100* C_004b9100::fn_000b9100(u32 key) {
    for (u32 i = 0; i < 4; ++i) {
        E_004b9100* p = slots[i];
        if (p != 0 && p->key == key) {
            return slots[i];
        }
    }
    return 0;
}

// FUNCTION: DAO 0x004C05B0
int C_004c05b0::fn_000c05b0(const u16* set, u32 start, u32 count) const {
    if (count == 0) {
        return -1;
    }
    if (start >= length) {
        return -1;
    }
    const u16* base = (capacity < 8) ? data.inline_buf : data.heap_ptr;
    const u16* end = base + length;
    const u16* cur = base + start;
    while (cur < end) {
        u16 ch = *cur;
        const u16* p = set;
        u32 n = count;
        do {
            if (*p == ch) {
                return static_cast<int>(cur - base);
            }
            ++p;
        } while (--n != 0);
        ++cur;
    }
    return -1;
}

// FUNCTION: DAO 0x004C0D90
C_004c05b0* C_004c05b0::fn_000c0d90() {
    capacity = 7;
    length = 0;
    data.inline_buf[0] = 0;
    return this;
}

// FUNCTION: DAO 0x004C4E10
void* __stdcall fn_000c4e10(S_000c4e10* p) {
    return p->field4;
}

// FUNCTION: DAO 0x004DF4E0
C_000df4e0* C_000df4e0::fn_000df4e0() {
    field0 = 0x33cf;
    return this;
}

// FUNCTION: DAO 0x005389F0
C_001389f0* C_001389f0::fn_001389f0() {
    field0 = 0;
    field4 = 0;
    field8 = 0;
    return this;
}

// FUNCTION: DAO 0x005DD7B0
int C_001dd7b0::fn_001dd7b0() const {
    if (begin == 0) {
        return 0;
    }
    return static_cast<int>(end - begin);
}

// FUNCTION: DAO 0x005DE880
int C_001de880::fn_001de880() const {
    if (begin == 0) {
        return 0;
    }
    return static_cast<int>(end - begin);
}

// FUNCTION: DAO 0x00838210
u8 C_00438210::fn_00438210() const {
    return field_c;
}

// FUNCTION: DAO 0x008714C0
int C_004714c0::fn_004714c0() const {
    if (begin == 0) {
        return 0;
    }
    return static_cast<int>(end - begin);
}

// FUNCTION: DAO 0x008EAB50
u32 __cdecl fn_004eab50(const char* str) {
    const char* p = str;
    while ((reinterpret_cast<u32>(p) & 3) != 0) {
        if (*p == 0) {
            return static_cast<u32>(p - str);
        }
        ++p;
    }
    for (;;) {
        u32 v = *reinterpret_cast<const u32*>(p);
        u32 haszero = ((v + 0x7efefeffU) ^ (~v)) & 0x81010100U;
        if (haszero == 0) {
            p += 4;
            continue;
        }
        if ((v & 0xffU) == 0) {
            return static_cast<u32>(p - str);
        }
        if ((v & 0xff00U) == 0) {
            return static_cast<u32>((p + 1) - str);
        }
        if ((v & 0xff0000U) == 0) {
            return static_cast<u32>((p + 2) - str);
        }
        if ((v & 0xff000000U) == 0) {
            return static_cast<u32>((p + 3) - str);
        }
        p += 4;
    }
}

// FUNCTION: DAO 0x00933D70
C_00533d70* C_00533d70::fn_00533d70(const C_00533d70* other) {
    field0 = other->field0;
    field4 = other->field4;
    field8 = other->field8;
    field_c = other->field_c;
    return this;
}
