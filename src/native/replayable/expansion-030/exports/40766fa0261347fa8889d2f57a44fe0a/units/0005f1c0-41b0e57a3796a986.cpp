struct Recovered {
    unsigned char fn_0005f1c0();
};
// FUNCTION: DAOrigins.exe 0x0045f1c0
unsigned char Recovered::fn_0005f1c0() {
    return *reinterpret_cast<unsigned char*>((reinterpret_cast<unsigned int>(this) + 40u));
}
