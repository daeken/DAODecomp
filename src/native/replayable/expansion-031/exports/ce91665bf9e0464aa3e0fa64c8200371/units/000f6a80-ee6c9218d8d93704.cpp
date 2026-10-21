struct Recovered {
    unsigned int fn_000f6a80();
};
// FUNCTION: DAOrigins.exe 0x004f6a80
unsigned int Recovered::fn_000f6a80() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 36u));
}
