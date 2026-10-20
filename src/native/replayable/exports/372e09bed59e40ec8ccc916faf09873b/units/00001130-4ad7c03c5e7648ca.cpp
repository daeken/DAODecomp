extern "C" void __cdecl fn_000136c0(void*);
struct Recovered {
    void fn_00001030();
    void* fn_00001130(unsigned int arg_0);
};
// FUNCTION: DAOrigins.exe 0x00401130
void* Recovered::fn_00001130(unsigned int arg_0) {
    fn_00001030();
    if ((arg_0 & 1u) != 0u) {
        fn_000136c0(this);
    }

    return this;
}
