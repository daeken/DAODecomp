struct Recovered {
    unsigned int fn_000fe900();
};
// FUNCTION: DAOrigins.exe 0x004fe900
unsigned int Recovered::fn_000fe900() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 112u));
}
