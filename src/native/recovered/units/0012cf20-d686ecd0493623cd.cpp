class C_0012cf20 {
public:
    unsigned char pad0[8];
    unsigned char flag0 : 1;
    unsigned char fn_0012cf20();
};

class C_0012cf30 {
public:
    unsigned char pad0[8];
    unsigned char flag0 : 1;
    unsigned char flag1 : 1;
    unsigned char fn_0012cf30();
};

// FUNCTION: DAO 0x0052CF20
unsigned char C_0012cf20::fn_0012cf20() {
    return flag0;
}

// FUNCTION: DAO 0x0052CF30
unsigned char C_0012cf30::fn_0012cf30() {
    return flag1;
}
