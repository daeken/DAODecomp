extern unsigned char g_006dd8f0;
struct Recovered {
    void fn_000be090();
    void* fn_00001000();
};
// FUNCTION: DAOrigins.exe 0x00401000
void* Recovered::fn_00001000() {
    fn_000be090();
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0) = &g_006dd8f0;
    *reinterpret_cast<unsigned char*>(reinterpret_cast<char*>(this) + 104) = 1u;
    return this;
}
