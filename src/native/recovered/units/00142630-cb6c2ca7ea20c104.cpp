class C_542630 {
public:
    unsigned char* fn_00142630(unsigned int code);
};

// FUNCTION: DAO 0x542630
unsigned char* C_542630::fn_00142630(unsigned int code)
{
    unsigned char* result = 0;
    switch (code)
    {
    case 0x21:
        result = reinterpret_cast<unsigned char*>(this);
        break;
    case 0x22:
        result = reinterpret_cast<unsigned char*>(this) + 0x2c;
        break;
    case 0x23:
        result = reinterpret_cast<unsigned char*>(this) + 0x34;
        break;
    }
    return result;
}
