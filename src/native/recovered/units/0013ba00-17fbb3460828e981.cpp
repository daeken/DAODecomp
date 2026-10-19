class C_53BA00 {
public:
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int fc;
    unsigned int f10;
    unsigned int f14;
    unsigned int f18;
    unsigned int f1c;
    unsigned int f20;
    unsigned int f24;
    unsigned int f28;
    unsigned int f2c;
    unsigned int f30;
};

class C_53C8D0 {
public:
    unsigned char pad0[0x174];
    unsigned char* field174;
    unsigned char fn_0013c8d0() const;
    unsigned char* fn_0013c8e0() const;
    unsigned char* fn_0013c8f0() const;
    unsigned char* fn_0013c900() const;
    unsigned char* fn_0013c910() const;
};

class C_53CBD0 {
public:
    unsigned char* fn_0013cbd0();
};

class C_53DCA0 {
public:
    unsigned char* fn_0013dca0();
};

class C_53DCF0 {
public:
    unsigned char pad0[4];
    unsigned char* field4;
    unsigned char* field8;
    int fn_0013dcf0() const;
};

class C_53DD10 {
public:
    unsigned char* base;
    unsigned char* fn_0013dd10(unsigned int index);
};

class C_53DD20 {
public:
    unsigned char* base;
    unsigned char* fn_0013dd20(unsigned int index);
};

class C_53FD40 {
public:
    unsigned char pad0[4];
    unsigned char* field4;
    unsigned char* field8;
    int fn_0013fd40() const;
};

class C_542630 {
public:
    unsigned char* fn_00142630(unsigned int code);
};

class C_542960 {
public:
    unsigned char pad0[0xee];
    unsigned char fieldEE;
    void fn_00142960(unsigned char v);
};

class C_5429C0 {
public:
    unsigned char pad0[0x2f0];
    int field2F0;
    bool fn_001429c0(int* out) const;
};

class C_542AA0 {
public:
    unsigned char pad0[0x30c];
    unsigned int field30C;
    void fn_00142aa0(unsigned int v);
};

// FUNCTION: DAO 0x53BA00
void __stdcall fn_0013ba00(C_53BA00* p)
{
    p->f0 = 0;
    p->f4 = 0;
    p->f8 = 2;
    p->fc = 0;
    p->f10 = 0;
    p->f14 = 0;
    p->f18 = 0;
    p->f1c = 0xc;
    p->f20 = 4;
    p->f24 = 0xa;
    p->f28 = 0;
    p->f2c = 0;
    p->f30 = 0xffffffff;
}

// FUNCTION: DAO 0x53C8D0
unsigned char C_53C8D0::fn_0013c8d0() const
{
    return field174[0x15c];
}

// FUNCTION: DAO 0x53C8E0
unsigned char* C_53C8D0::fn_0013c8e0() const
{
    return field174 + 0x14c;
}

// FUNCTION: DAO 0x53C8F0
unsigned char* C_53C8D0::fn_0013c8f0() const
{
    return field174 + 0x160;
}

// FUNCTION: DAO 0x53C900
unsigned char* C_53C8D0::fn_0013c900() const
{
    return field174 + 0x1a0;
}

// FUNCTION: DAO 0x53C910
unsigned char* C_53C8D0::fn_0013c910() const
{
    return field174 + 0x1e0;
}

// FUNCTION: DAO 0x53CBD0
unsigned char* C_53CBD0::fn_0013cbd0()
{
    return reinterpret_cast<unsigned char*>(this) + 0x140;
}

// FUNCTION: DAO 0x53DCA0
unsigned char* C_53DCA0::fn_0013dca0()
{
    return reinterpret_cast<unsigned char*>(this) + 0x314;
}

// FUNCTION: DAO 0x53DCF0
int C_53DCF0::fn_0013dcf0() const
{
    if (field4 == 0)
        return 0;
    return (int)(field8 - field4) / 6;
}

// FUNCTION: DAO 0x53DD10
unsigned char* C_53DD10::fn_0013dd10(unsigned int index)
{
    return base + index * 80;
}

// FUNCTION: DAO 0x53DD20
unsigned char* C_53DD20::fn_0013dd20(unsigned int index)
{
    return base + index * 12;
}

// FUNCTION: DAO 0x53FD40
int C_53FD40::fn_0013fd40() const
{
    if (field4 == 0)
        return 0;
    return (int)(field8 - field4) >> 5;
}

// FUNCTION: DAO 0x542630
unsigned char* C_542630::fn_00142630(unsigned int code)
{
    if (code == 0x21)
        return reinterpret_cast<unsigned char*>(this);
    if (code == 0x22)
        return reinterpret_cast<unsigned char*>(this) + 0x2c;
    if (code == 0x23)
        return reinterpret_cast<unsigned char*>(this) + 0x34;
    return 0;
}

// FUNCTION: DAO 0x542960
void C_542960::fn_00142960(unsigned char v)
{
    fieldEE = v;
}

// FUNCTION: DAO 0x5429C0
bool C_5429C0::fn_001429c0(int* out) const
{
    int v = field2F0;
    if (v < 0)
        return false;
    *out = v;
    return true;
}

// FUNCTION: DAO 0x542AA0
void C_542AA0::fn_00142aa0(unsigned int v)
{
    field30C = v;
}
