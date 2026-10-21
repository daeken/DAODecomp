extern "C" void * __cdecl memcpy(void *, const void *, unsigned int);
#pragma intrinsic(memcpy)
typedef unsigned int guest_address;
static __forceinline unsigned int read_word(guest_address address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }
static __forceinline void write_word(guest_address address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }
static __forceinline void write_byte(void *base, unsigned int offset, unsigned char value) { guest_address address = reinterpret_cast<guest_address>(base) + offset; *reinterpret_cast<unsigned char *>(address) = value; }
extern "C" void __cdecl fn_004e0e10(unsigned int, unsigned int, unsigned int, unsigned int);
extern "C" void __cdecl fn_000136c0(unsigned int);
struct Recovered { void fn_000011c0(unsigned char arg_0, unsigned int arg_1); };
// FUNCTION: DAOrigins.exe 0x004011c0
void Recovered::fn_000011c0(unsigned char arg_0, unsigned int arg_1) {
    if (!(arg_0 == 0u)) {
        unsigned int word_4011cf = read_word((reinterpret_cast<guest_address>(this) + 24u));
        if (!(word_4011cf < 16u)) {
            unsigned int word_4011db = read_word((reinterpret_cast<guest_address>(this) + 4u));
            if ((arg_1 > 0u)) {
                fn_004e0e10((reinterpret_cast<guest_address>(this) + 4u), 16u, word_4011db, arg_1);
            }
            fn_000136c0(word_4011db);
        }
    }
    write_word((reinterpret_cast<guest_address>(this) + 20u), arg_1);
    write_word((reinterpret_cast<guest_address>(this) + 24u), 15u);
    write_byte(this, ((0u + arg_1) + 4u), 0u);
}
