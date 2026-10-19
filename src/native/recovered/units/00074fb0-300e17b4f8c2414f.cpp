class C_00074fb0 {
    char pad0[4];
    unsigned char* begin;
    unsigned char* end;
public:
    int fn_00074fb0();
};
class C_00079930 {
    char pad0[4];
    unsigned char* begin;
    unsigned char* end;
public:
    int fn_00079930();
};
class C_000a54f0 {
    char pad[0x21];
    unsigned char b;
public:
    void fn_000a54f0(unsigned int);
};
class C_000bff90 {
    char pad[0xe4];
    unsigned char b;
public:
    unsigned char fn_000bff90();
};
class C_000f2810 {
    char pad[0x3c];
    unsigned int f3c;
    unsigned int f40;
public:
    void fn_000f2810(unsigned int, unsigned int);
};
class C_000f6a60 {
    char pad[0x30];
    unsigned __int64 v;
public:
    unsigned __int64 fn_000f6a60();
};
class C_000f6a80 {
    char pad[0x24];
    unsigned int f;
public:
    unsigned int fn_000f6a80();
};
class C_000f6a90 {
    char pad[0x3c];
    unsigned int f;
public:
    unsigned int fn_000f6a90();
};
class C_000f6ae0 {
    char pad[0x30];
    unsigned __int64 v;
public:
    void fn_000f6ae0(unsigned int, unsigned int);
};
class C_000f6b00 {
    char pad[0x30];
    unsigned __int64 v;
public:
    void fn_000f6b00(unsigned int, unsigned int);
};
class C_00103950 {
    char pad[0x54];
public:
    char* fn_00103950();
};
class C_0013af00 {
    unsigned int f0;
    unsigned int f4;
    unsigned int f8;
    unsigned int f12;
    unsigned int f16;
    unsigned int f20;
public:
    C_0013af00* fn_0013af00();
};
class C_0013cc40 {
    char pad[0xc];
    unsigned int f;
public:
    unsigned int fn_0013cc40();
};
class C_0027d390 {
    char pad0[4];
    unsigned char* begin;
    unsigned char* end;
public:
    int fn_0027d390();
};
class C_0046bee0 {
    char pad0[4];
    unsigned char* begin;
    unsigned char* end;
public:
    unsigned char fn_0046bee0();
};
class C_00638ea0 {
    unsigned int* data;
    unsigned int size;
public:
    int fn_00638ea0();
};

// FUNCTION: DAO 0x474FB0
int C_00074fb0::fn_00074fb0()
{
    if (this->begin == 0) { return 0; }
    int diff = (int)(this->end - this->begin);
    return diff / 676;
}

// FUNCTION: DAO 0x479930
int C_00079930::fn_00079930()
{
    if (this->begin == 0) { return 0; }
    int diff = (int)(this->end - this->begin);
    return diff / 464;
}

// FUNCTION: DAO 0x4A54F0
void C_000a54f0::fn_000a54f0(unsigned int)
{
    this->b = 0;
}

// FUNCTION: DAO 0x4BFF90
unsigned char C_000bff90::fn_000bff90()
{
    return this->b;
}

// FUNCTION: DAO 0x4F2810
void C_000f2810::fn_000f2810(unsigned int a, unsigned int b)
{
    if (a == 0) {
        this->f3c = a;
        this->f40 = 0;
    } else {
        this->f3c = a;
        this->f40 = b;
    }
}

// FUNCTION: DAO 0x4F6A60
unsigned __int64 C_000f6a60::fn_000f6a60()
{
    return this->v;
}

// FUNCTION: DAO 0x4F6A80
unsigned int C_000f6a80::fn_000f6a80()
{
    return this->f;
}

// FUNCTION: DAO 0x4F6A90
unsigned int C_000f6a90::fn_000f6a90()
{
    return this->f;
}

// FUNCTION: DAO 0x4F6AE0
void C_000f6ae0::fn_000f6ae0(unsigned int lo, unsigned int hi)
{
    this->v |= ((unsigned __int64)lo | ((unsigned __int64)hi << 32));
}

// FUNCTION: DAO 0x4F6B00
void C_000f6b00::fn_000f6b00(unsigned int lo, unsigned int hi)
{
    this->v &= ~((unsigned __int64)lo | ((unsigned __int64)hi << 32));
}

// FUNCTION: DAO 0x503950
char* C_00103950::fn_00103950()
{
    return (char*)this + 0x54;
}

// FUNCTION: DAO 0x53AF00
C_0013af00* C_0013af00::fn_0013af00()
{
    this->f0 = 0;
    this->f4 = 0;
    this->f8 = 0xFFFFFFFFu;
    this->f12 = 0xFFFFFFFFu;
    this->f16 = 0;
    this->f20 = 0;
    return this;
}

// FUNCTION: DAO 0x53CC40
unsigned int C_0013cc40::fn_0013cc40()
{
    return this->f;
}

// FUNCTION: DAO 0x67D390
int C_0027d390::fn_0027d390()
{
    if (this->begin == 0) { return 0; }
    return (int)(this->end - this->begin) >> 2;
}

// FUNCTION: DAO 0x86BEE0
unsigned char C_0046bee0::fn_0046bee0()
{
    int n;
    if (this->begin == 0) {
        n = 0;
    } else {
        n = (int)(this->end - this->begin) >> 2;
    }
    return (unsigned char)(n == 0);
}

// FUNCTION: DAO 0xA38EA0
int C_00638ea0::fn_00638ea0()
{
    if (this->data == 0) { return 0; }
    if (this->size <= 0x1c) { return 0; }
    if (this->data[0] != 0x20464647u) { return 0; }
    if (this->data[1] != 0x302e3456u) { return 0; }
    return 1;
}
