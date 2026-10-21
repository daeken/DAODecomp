extern unsigned char g_006dd904;
extern "C" void __cdecl fn_000136c0(void*);
struct Recovered {
    void fn_004e0f9d();
    void* fn_00001070(unsigned int arg_0);
};
// FUNCTION: DAOrigins.exe 0x00401070
void* Recovered::fn_00001070(unsigned int arg_0) {
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0) = &g_006dd904;
    fn_004e0f9d();
    if ((arg_0 & 1u) != 0u) {
        fn_000136c0(this);
    }

    return this;
}
