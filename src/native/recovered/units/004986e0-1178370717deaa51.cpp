struct C4986E0
{
    unsigned char pad0[0x88];
    int field_88;
    bool fn_004986e0();
};

struct C499700
{
    unsigned char pad0[0xC];
    unsigned int field_C;
    unsigned int field_10;
    void fn_00499700(unsigned int a, unsigned int b);
};

struct C499FE0
{
    unsigned char pad0[0x9C];
    unsigned int field_9C;
    void fn_00499fe0(unsigned int a);
};

struct C499FF0
{
    unsigned char pad0[0x44];
    unsigned int field_44;
    void fn_00499ff0(unsigned int a);
};

struct C49AF90
{
    unsigned char pad0[0x6C];
    unsigned int field_6C;
    void fn_0049af90(unsigned int a);
};

struct C49AFA0
{
    unsigned char pad0[0x70];
    unsigned int field_70;
    void fn_0049afa0(unsigned int a);
};

struct C4A0040
{
    unsigned int f0, f4, f8, fc, f10, f14;
    C4A0040* fn_004a0040();
};

struct C4A0640
{
    unsigned int f0, f4, f8, fc;
    void fn_004a0640(const unsigned int* src, unsigned int);
};

struct C4A0660
{
    unsigned int f0, f4, f8, fc;
    void fn_004a0660(unsigned int* dst, unsigned int);
};

struct C4A0680
{
    unsigned short f0;
    unsigned short f2;
    unsigned int f4;
    unsigned int f8;
    C4A0680* fn_004a0680();
};

struct C4A2D40
{
    unsigned int f0, f4, f8, fc, f10, f14, f18, f1c, f20;
    C4A2D40* fn_004a2d40();
};

struct C4A30B0
{
    unsigned int f0, f4, f8, fc;
    C4A30B0* fn_004a30b0();
};

struct C4A3F90
{
    unsigned int f0;
    unsigned int f4;
    C4A3F90* fn_004a3f90();
};

struct C4A4390
{
    unsigned int f0;
    unsigned int f4;
    unsigned int gap8;
    unsigned int fc;
    C4A4390* fn_004a4390();
};

struct C4A4880
{
    unsigned int f0, f4, f8, fc;
    C4A4880* fn_004a4880();
};

// FUNCTION: DAO 0x8986E0
bool C4986E0::fn_004986e0()
{
    return field_88 != -1;
}

// FUNCTION: DAO 0x899700
void C499700::fn_00499700(unsigned int a, unsigned int b)
{
    field_C = a;
    field_10 = b;
}

// FUNCTION: DAO 0x899830
void __stdcall fn_00499830(unsigned int* dst, const unsigned int* src)
{
    if (dst) {
        *dst = *src;
    }
}

// FUNCTION: DAO 0x899FE0
void C499FE0::fn_00499fe0(unsigned int a)
{
    field_9C = a;
}

// FUNCTION: DAO 0x899FF0
void C499FF0::fn_00499ff0(unsigned int a)
{
    field_44 = a;
}

// FUNCTION: DAO 0x89AF90
void C49AF90::fn_0049af90(unsigned int a)
{
    field_6C = a;
}

// FUNCTION: DAO 0x89AFA0
void C49AFA0::fn_0049afa0(unsigned int a)
{
    field_70 = a;
}

// FUNCTION: DAO 0x8A0040
C4A0040* C4A0040::fn_004a0040()
{
    f0 = 0;
    f4 = 0;
    f8 = 0;
    fc = 0;
    f10 = 0;
    f14 = 0;
    return this;
}

// FUNCTION: DAO 0x8A0640
void C4A0640::fn_004a0640(const unsigned int* src, unsigned int)
{
    f0 = src[0];
    f4 = src[1];
    f8 = src[2];
    fc = src[3];
}

// FUNCTION: DAO 0x8A0660
void C4A0660::fn_004a0660(unsigned int* dst, unsigned int)
{
    dst[0] = f0;
    dst[1] = f4;
    dst[2] = f8;
    dst[3] = fc;
}

// FUNCTION: DAO 0x8A0680
C4A0680* C4A0680::fn_004a0680()
{
    f0 = 0;
    f2 = 0;
    f8 = 0;
    return this;
}

// FUNCTION: DAO 0x8A2D40
C4A2D40* C4A2D40::fn_004a2d40()
{
    f0 = 0;
    f4 = 0;
    f8 = 0;
    fc = 1;
    f10 = 0;
    f14 = 0;
    f18 = 0;
    f1c = 0;
    f20 = 0;
    return this;
}

// FUNCTION: DAO 0x8A30B0
C4A30B0* C4A30B0::fn_004a30b0()
{
    f0 = 0;
    f4 = 0;
    f8 = 0;
    fc = 0;
    return this;
}

// FUNCTION: DAO 0x8A3F90
C4A3F90* C4A3F90::fn_004a3f90()
{
    f4 = 0;
    return this;
}

// FUNCTION: DAO 0x8A4390
C4A4390* C4A4390::fn_004a4390()
{
    f0 = 0;
    f4 = 0;
    fc = 0;
    return this;
}

// FUNCTION: DAO 0x8A4880
C4A4880* C4A4880::fn_004a4880()
{
    f0 = 0x10000;
    f4 = 0x100;
    f8 = 0x800;
    fc = 0;
    return this;
}
