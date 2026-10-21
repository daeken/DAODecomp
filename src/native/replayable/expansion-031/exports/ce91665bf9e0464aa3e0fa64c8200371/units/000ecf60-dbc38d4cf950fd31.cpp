struct Recovered {
    unsigned char fn_000ecf60();
};
// FUNCTION: DAOrigins.exe 0x004ecf60
unsigned char Recovered::fn_000ecf60() {
    return *reinterpret_cast<unsigned char*>((reinterpret_cast<unsigned int>(this) + 4u));
}
