extern "C" void * __cdecl memcpy(void *, const void *, unsigned int);
#pragma intrinsic(memcpy)
typedef unsigned int guest_address;
static __forceinline unsigned int read_word(guest_address address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }
static __forceinline void write_word(guest_address address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }
static __forceinline void write_byte(void *base, unsigned int offset, unsigned char value) { guest_address address = reinterpret_cast<guest_address>(base) + offset; *reinterpret_cast<unsigned char *>(address) = value; }
extern "C" void __cdecl fn_000136c0(unsigned int);
struct Recovered { void fn_000013f0(); };
// FUNCTION: DAOrigins.exe 0x004013f0
void Recovered::fn_000013f0() {
    unsigned int word_4013f3 = read_word((reinterpret_cast<guest_address>(this) + 24u));
    if (!(word_4013f3 < 16u)) {
        unsigned int word_4013f9 = read_word((reinterpret_cast<guest_address>(this) + 4u));
        fn_000136c0(word_4013f9);
    }
    write_word((reinterpret_cast<guest_address>(this) + 24u), 15u);
    write_word((reinterpret_cast<guest_address>(this) + 20u), 0u);
    write_byte(this, 4u, 0u);
}
