class C_0012cf20 {
public:
    unsigned char pad0[8];
    unsigned char flags8;
    unsigned char fn_0012cf20();
};
// FUNCTION: DAO 0x0052CF20
unsigned char C_0012cf20::fn_0012cf20() {
    return (unsigned char)(flags8 & 1u);
}

class C_0012cf30 {
public:
    unsigned char pad0[8];
    unsigned char flags8;
    unsigned char fn_0012cf30();
};
// FUNCTION: DAO 0x0052CF30
unsigned char C_0012cf30::fn_0012cf30() {
    return (unsigned char)((flags8 >> 1) & 1u);
}

class C_0012cf40 {
public:
    unsigned char pad0[8];
    unsigned int flags8;
    void fn_0012cf40(unsigned char enable);
};
// FUNCTION: DAO 0x0052CF40
void C_0012cf40::fn_0012cf40(unsigned char enable) {
    if (enable != 0)
        flags8 |= 2u;
    else
        flags8 &= 0xFFFFFFFDu;
}

class C_001320b0 {
public:
    unsigned char pad0[0x3C];
    int* begin;
    int* end;
    int fn_001320b0();
};
// FUNCTION: DAO 0x005320B0
int C_001320b0::fn_001320b0() {
    if (begin == 0)
        return 0;
    return (reinterpret_cast<int>(end) - reinterpret_cast<int>(begin)) >> 2;
}

class C_00133030 {
public:
    void* fn_00133030();
};
// FUNCTION: DAO 0x00533030
void* C_00133030::fn_00133030() {
    return (void*)((unsigned char*)this + 0x80);
}

class C_00137c60 {
public:
    unsigned char pad0[0xC0];
    unsigned int value_c0;
    unsigned char value_c4;
    void fn_00137c60(unsigned int value, unsigned char byteValue, unsigned char setByte);
};
// FUNCTION: DAO 0x00537C60
void C_00137c60::fn_00137c60(unsigned int value, unsigned char byteValue, unsigned char setByte) {
    value_c0 = value;
    if (setByte == 1)
        value_c4 = byteValue;
}

class C_00137d60 {
public:
    unsigned char pad0[0xCC];
    unsigned int value_cc;
    unsigned int fn_00137d60(unsigned int unused);
};
// FUNCTION: DAO 0x00537D60
unsigned int C_00137d60::fn_00137d60(unsigned int unused) {
    (void)unused;
    return value_cc;
}

class C_00137d70 {
public:
    void* fn_00137d70();
};
// FUNCTION: DAO 0x00537D70
void* C_00137d70::fn_00137d70() {
    return (void*)((unsigned char*)this + 0x90);
}

class C_00137f00 {
public:
    unsigned char pad0[0xD8];
    unsigned int value_d8;
    unsigned int value_dc;
    unsigned int value_e0;
    unsigned int fn_00137f00(unsigned int index);
};
// FUNCTION: DAO 0x00537F00
unsigned int C_00137f00::fn_00137f00(unsigned int index) {
    if (index == 0)
        return value_d8;
    if (index == 1)
        return value_dc;
    if (index == 2)
        return value_e0;
    return 0;
}

class C_00137f40 {
public:
    unsigned char pad0[0x10];
    unsigned char value_10;
    unsigned char value_11;
    unsigned char fn_00137f40();
};
// FUNCTION: DAO 0x00537F40
unsigned char C_00137f40::fn_00137f40() {
    return (unsigned char)((value_10 != 0) || (value_11 != 0));
}

class C_00137f60 {
public:
    unsigned char pad0[0x11];
    unsigned char value_11;
    void fn_00137f60();
};
// FUNCTION: DAO 0x00537F60
void C_00137f60::fn_00137f60() {
    value_11 = 0;
}

class C_00137f70 {
public:
    unsigned char pad0[0x68];
    unsigned int value_68;
    void fn_00137f70(unsigned int value);
};
// FUNCTION: DAO 0x00537F70
void C_00137f70::fn_00137f70(unsigned int value) {
    value_68 = value;
}

class C_00137f80 {
public:
    unsigned char pad0[0x64];
    unsigned int value_64;
    void fn_00137f80(unsigned int value);
};
// FUNCTION: DAO 0x00537F80
void C_00137f80::fn_00137f80(unsigned int value) {
    value_64 = value;
}

class C_001380b0 {
public:
    void fn_001380b0(void** outPtr, unsigned int* outSize);
};
// FUNCTION: DAO 0x005380B0
void C_001380b0::fn_001380b0(void** outPtr, unsigned int* outSize) {
    *outPtr = (void*)((unsigned char*)this + 0x24);
    *outSize = 0x10;
}

class C_001380d0 {
public:
    unsigned int base;
    unsigned int fn_001380d0(unsigned int index);
};
// FUNCTION: DAO 0x005380D0
unsigned int C_001380d0::fn_001380d0(unsigned int index) {
    return base + index * 320u;
}

// FUNCTION: DAO 0x0053AFD0
int fn_0013afd0(int* p) {
    if (p == 0)
        return 0;
    int count = 0;
    while (*p != -1) {
        p += 6;
        ++count;
    }
    return count + 1;
}
