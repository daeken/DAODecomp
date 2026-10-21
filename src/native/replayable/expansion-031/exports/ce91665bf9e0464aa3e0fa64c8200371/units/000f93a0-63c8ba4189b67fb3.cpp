struct Recovered {
    unsigned char fn_000f93a0();
};
// FUNCTION: DAOrigins.exe 0x004f93a0
unsigned char Recovered::fn_000f93a0() {
    return *reinterpret_cast<unsigned char*>((reinterpret_cast<unsigned int>(this) + 36u));
}
