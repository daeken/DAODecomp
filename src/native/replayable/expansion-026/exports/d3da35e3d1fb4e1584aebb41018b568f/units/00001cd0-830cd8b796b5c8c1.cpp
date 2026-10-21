extern unsigned char g_006ddce0;
struct Recovered {

    void fn_00001cd0();
};
// FUNCTION: DAOrigins.exe 0x00401cd0
void Recovered::fn_00001cd0() {
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0) = &g_006ddce0;
}
