struct Recovered {
    unsigned char fn_000f6a70();
};
// FUNCTION: DAOrigins.exe 0x004f6a70
unsigned char Recovered::fn_000f6a70() {
    return *reinterpret_cast<unsigned char*>((reinterpret_cast<unsigned int>(this) + 56u));
}
