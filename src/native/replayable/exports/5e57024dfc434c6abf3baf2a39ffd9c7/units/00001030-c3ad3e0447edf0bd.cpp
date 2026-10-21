extern unsigned char g_006dd8f0;
struct Recovered {
    void fn_000be560();
    void fn_00001030();
};
// FUNCTION: DAOrigins.exe 0x00401030
void Recovered::fn_00001030() {
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0) = &g_006dd8f0;
    fn_000be560();
}
