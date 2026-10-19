class C_000f2810 {
    char pad[0x3c];
    unsigned int f3c;
    unsigned int f40;
public:
    void __thiscall fn_000f2810(unsigned int, unsigned int);
};

class C_0046bee0 {
    char pad0[4];
    unsigned int* begin;
    unsigned int* end;
public:
    bool __thiscall fn_0046bee0();
};

// FUNCTION: DAO 0x4F2810
void __thiscall C_000f2810::fn_000f2810(unsigned int a, unsigned int b)
{
    if (a == 0) {
        this->f3c = a;
        this->f40 = 0;
    } else {
        this->f3c = a;
        this->f40 = b;
    }
}

// FUNCTION: DAO 0x86BEE0
bool __thiscall C_0046bee0::fn_0046bee0()
{
    unsigned int n;
    if (this->begin == 0) {
        n = 0;
    } else {
        n = (unsigned int)(this->end - this->begin);
    }
    return n == 0;
}
