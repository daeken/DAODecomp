struct Recovered {
    unsigned int fn_0001f060();
};
// FUNCTION: DAOrigins.exe 0x0041f060
unsigned int Recovered::fn_0001f060() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 20u));
}
