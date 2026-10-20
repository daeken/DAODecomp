extern unsigned char g_006dd904;
struct Recovered {
    void fn_004e0ef7(unsigned int*);
    void* fn_00001040(unsigned int arg_0);
};
// FUNCTION: DAOrigins.exe 0x00401040
void* Recovered::fn_00001040(unsigned int arg_0) {
    fn_004e0ef7(&arg_0);
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0) = &g_006dd904;
    return this;
}
