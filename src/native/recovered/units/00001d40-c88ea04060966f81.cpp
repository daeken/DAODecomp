// FUNCTION: DAO 0x401d40
class GMutex {
public:
    void __thiscall fn_00018220(bool param_1, bool param_2);
    void __thiscall fn_00001d40();
};

void __thiscall GMutex::fn_00001d40()
{
    fn_00018220(true, false);
}

class C_001d4500 {
public:
    void __thiscall fn_001d4500();
};

extern "C" C_001d4500* g_00c327ec;

// FUNCTION: DAO 0x402070
extern "C" bool fn_00002070(void)
{
    g_00c327ec->fn_001d4500();
    return true;
}
