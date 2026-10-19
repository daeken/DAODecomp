// FUNCTION: DAO 0x007A2240
bool __stdcall fn_003a2240(unsigned int a, unsigned int b)
{
    if (a == 0)
        return false;
    return b;
}

// FUNCTION: DAO 0x007A2260
bool __stdcall fn_003a2260(unsigned int a, unsigned int)
{
    return a;
}

// FUNCTION: DAO 0x0084AEF0
bool __cdecl fn_0044aef0(unsigned int code)
{
    if (code == 0 || code == 1 || code == 2 || code == 9)
        return true;
    return false;
}

// FUNCTION: DAO 0x0084B1B0
unsigned int __cdecl fn_0044b1b0(unsigned int value)
{
    unsigned int result = 1;
    unsigned int base = 2;
    if (value > base)
    {
        do
        {
            base += base;
            result += result;
        } while (base < value);
    }
    return result;
}

// FUNCTION: DAO 0x008B6520
char __fastcall fn_004b6520(char value)
{
    char result;
    if (value < 10)
        result = (char)(value + 0x30);
    else
        result = (char)(value + 0x37);
    return result;
}

// FUNCTION: DAO 0x008B65E0
char __fastcall fn_004b65e0(char value)
{
    char result = 0;
    if ((unsigned char)(value - 0x30) <= 9)
        result = (char)(value - 0x30);
    else if ((unsigned char)(value - 0x61) <= 5)
        result = (char)(value - 0x57);
    else if ((unsigned char)(value - 0x41) <= 5)
        result = (char)(value - 0x37);
    return result;
}

// FUNCTION: DAO 0x008F5078
unsigned int __cdecl fn_004f5078(unsigned int, unsigned int high)
{
    if ((high & 0x7ff00000u) == 0x7ff00000u)
        return high;
    return high & 0x7ff00000u;
}
