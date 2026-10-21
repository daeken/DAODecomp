struct Recovered {
    unsigned int fn_000621c0();
};
// FUNCTION: DAOrigins.exe 0x004621c0
unsigned int Recovered::fn_000621c0() {
    return *reinterpret_cast<unsigned int*>((reinterpret_cast<unsigned int>(this) + 0u));
}
