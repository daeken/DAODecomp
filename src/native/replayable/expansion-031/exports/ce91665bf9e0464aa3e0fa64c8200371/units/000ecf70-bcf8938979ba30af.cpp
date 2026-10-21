struct Recovered {
    unsigned int fn_000ecf70();
};
// FUNCTION: DAOrigins.exe 0x004ecf70
unsigned int Recovered::fn_000ecf70() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 44u));
}
