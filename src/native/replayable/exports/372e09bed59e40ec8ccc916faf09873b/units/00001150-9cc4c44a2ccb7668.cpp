struct ByteCarrier_5 { unsigned char value; };
extern "C" unsigned int __cdecl fn_0027bc10(unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, ByteCarrier_5);
// FUNCTION: DAOrigins.exe 0x00401150
extern "C" unsigned int __cdecl fn_00001150(unsigned int arg_0, volatile unsigned int arg_1, unsigned int arg_2) {
    ByteCarrier_5 local_5;
    local_5.value = 0u;
    return fn_0027bc10(arg_0, arg_1, arg_2, arg_1, arg_1, local_5);
}
