class C_0012cf20 {
public:
    unsigned char pad0[8];
    unsigned char flags8;
    bool fn_0012cf20();
};

class C_0012cf30 {
public:
    unsigned char pad0[8];
    unsigned char flags8;
    bool fn_0012cf30();
};

class C_00137f00 {
public:
    unsigned char pad0[0xD8];
    unsigned int value_d8;
    unsigned int value_dc;
    unsigned int value_e0;
    unsigned int fn_00137f00(unsigned int index);
};

// FUNCTION: DAO 0x0052CF20
bool C_0012cf20::fn_0012cf20() {
    return (flags8 & 1u) != 0;
}

// FUNCTION: DAO 0x0052CF30
bool C_0012cf30::fn_0012cf30() {
    return ((flags8 >> 1) & 1u) != 0;
}

// FUNCTION: DAO 0x00537F00
unsigned int C_00137f00::fn_00137f00(unsigned int index) {
    switch (index) {
    case 0:
        return value_d8;
    case 1:
        return value_dc;
    case 2:
        return value_e0;
    default:
        return 0;
    }
}
