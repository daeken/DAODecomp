class C_000f2810 {
    char pad[0x3c];
    unsigned int f3c;
    unsigned int f40;
public:
    void __thiscall fn_000f2810(unsigned int, unsigned int);
};

class C_000f6ae0 {
    char pad[0x30];
    unsigned int f30;
    unsigned int f34;
public:
    void __thiscall fn_000f6ae0(unsigned int, unsigned int);
};

class C_000f6b00 {
    char pad[0x30];
    unsigned int f30;
    unsigned int f34;
public:
    void __thiscall fn_000f6b00(unsigned int, unsigned int);
};

class C_0046bee0 {
    char pad0[4];
    unsigned char* begin;
    unsigned char* end;
public:
    unsigned char __thiscall fn_0046bee0();
};

class C_00638ea0 {
    unsigned int* data;
    unsigned int size;
public:
    int __thiscall fn_00638ea0();
};

// FUNCTION: DAO 0x4F2810
void __thiscall C_000f2810::fn_000f2810(unsigned int a, unsigned int b)
{
    if (!a) {
        this->f3c = a;
        this->f40 = 0;
    } else {
        this->f3c = a;
        this->f40 = b;
    }
}

// FUNCTION: DAO 0x4F6AE0
void __thiscall C_000f6ae0::fn_000f6ae0(unsigned int a, unsigned int b)
{
    this->f30 |= a;
    this->f34 |= b;
}

// FUNCTION: DAO 0x4F6B00
void __thiscall C_000f6b00::fn_000f6b00(unsigned int a, unsigned int b)
{
    this->f30 &= ~a;
    this->f34 &= ~b;
}

// FUNCTION: DAO 0x86BEE0
unsigned char __thiscall C_0046bee0::fn_0046bee0()
{
    int n;
    if (this->begin == 0) {
        n = 0;
    } else {
        n = (int)(this->end - this->begin) >> 2;
    }
    return n == 0;
}

// FUNCTION: DAO 0xA38EA0
int __thiscall C_00638ea0::fn_00638ea0()
{
    return (this->data != 0) &&
           (this->size > 0x1c) &&
           (this->data[0] == 0x20464647u) &&
           (this->data[1] == 0x302e3456u);
}
