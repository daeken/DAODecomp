struct Recovered {
    unsigned int fn_0001f050();
};
// FUNCTION: DAOrigins.exe 0x0041f050
unsigned int Recovered::fn_0001f050() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 16u));
}
