extern "C" void * __cdecl memcpy(void *, const void *, unsigned int);
#pragma intrinsic(memcpy)
typedef unsigned int guest_address;
static __forceinline unsigned int read_word(guest_address address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }
static __forceinline void write_word(guest_address address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }
// FUNCTION: DAOrigins.exe 0x00401180
extern "C" void __cdecl fn_00001180(volatile unsigned int arg_0, unsigned int arg_1, volatile unsigned int arg_2) {
    unsigned int remaining = arg_1;
    if (remaining > 0u) {
        guest_address source = arg_2;
        guest_address destination = arg_0;
        do {
        if (destination != 0u) {
            unsigned int word_0 = read_word(source + 0u);
            write_word(destination + 0u, word_0);
            unsigned int word_1 = read_word(source + 4u);
            write_word(destination + 4u, word_1);
            unsigned int word_2 = read_word(source + 8u);
            write_word(destination + 8u, word_2);
        }
        --remaining;
        destination += 12u;
        } while (remaining > 0u);
    }
}
