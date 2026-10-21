struct Recovered {
    unsigned int fn_000f6a90();
};
// FUNCTION: DAOrigins.exe 0x004f6a90
unsigned int Recovered::fn_000f6a90() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 60u));
}
