extern "C" void * __cdecl memcpy(void *, const void *, unsigned int);
#pragma intrinsic(memcpy)
static __forceinline unsigned int read_word(unsigned int address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }
static __forceinline void write_word(unsigned int address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }
// Observed access-slot view; actual field types, sizes and object extent remain unknown.
struct ReceiverAccessView {
    unsigned char unknown_0000[4];
    unsigned char access_0004[4];
    unsigned char unknown_0008[12];
    unsigned char access_0014[4];
    unsigned char access_0018[4];
};
typedef char checked_receiver_access_view[(sizeof(ReceiverAccessView) == 28u) ? 1 : -1];
enum ReceiverAccessOffsets {
    receiver_access_0004 = 4u,
    receiver_access_0014 = 20u,
    receiver_access_0018 = 24u,
};
extern "C" void __cdecl fn_004e0e8b(unsigned int, unsigned int, unsigned int, unsigned int);
extern "C" void __cdecl fn_004dfd4b();
// VC8 compile-time offsetof idiom; no header or runtime null dereference.
#define DAO_ACCESS_OFFSETOF(type, member) ((unsigned int)&(((type *)0)->member))
// Packed access-carrier hypothesis; field widths are observations, object extent/type remain unknown.
#pragma pack(push, 1)
struct Recovered {
    unsigned char unknown_0000[4];
    unsigned int field_0004;
    unsigned char unknown_0008[12];
    unsigned int field_0014;
    unsigned int field_0018;
    void * fn_00001210(unsigned int arg_0, unsigned int arg_1);
};
#pragma pack(pop)
typedef char checked_field_0004[(DAO_ACCESS_OFFSETOF(Recovered, field_0004) == 4u) ? 1 : -1];
typedef char checked_field_0014[(DAO_ACCESS_OFFSETOF(Recovered, field_0014) == 20u) ? 1 : -1];
typedef char checked_field_0018[(DAO_ACCESS_OFFSETOF(Recovered, field_0018) == 24u) ? 1 : -1];
// FUNCTION: DAOrigins.exe 0x00401210
void * Recovered::fn_00001210(unsigned int arg_0, unsigned int arg_1) {
    unsigned int r_1 = reinterpret_cast<unsigned int>(this);
    bool f_0;
    bool f_6;
    unsigned int push_40125d;
    unsigned int push_401266;
    unsigned int push_401269;
    unsigned int push_40126c;
    unsigned int r_0;
    unsigned int r_2;
    unsigned int r_3;
    unsigned int r_5;
    unsigned int r_6;
    unsigned int r_7;
    unsigned int slot_value_0004;
    unsigned __int64 t_401218_0;
    unsigned int t_401218_1;
    unsigned int t_401232_0;
    unsigned __int64 t_40127a_0;
    unsigned int t_40127a_1;
    r_3 = arg_0;
    r_6 = r_1;
    t_401218_0 = static_cast<unsigned __int64>(static_cast<unsigned int>((static_cast<unsigned __int64>(r_6) + static_cast<unsigned __int64>(receiver_access_0014))));
    t_401218_1 = this->field_0014;
    f_0 = (t_401218_1 < r_3);
    if (!((f_0 == 0u))) {
        fn_004dfd4b();
    }
    r_0 = this->field_0014;
    r_7 = arg_1;
    r_0 = (r_0 - r_3);
    f_0 = (r_0 < r_7);
    if (!((f_0 == 0u))) {
        r_7 = r_0;
    }
    t_401232_0 = (r_7 & r_7);
    f_0 = 0u;
    f_6 = (t_401232_0 == 0u);
    if ((t_401232_0 > 0u)) {
        r_1 = this->field_0018;
        f_0 = (r_1 < 16u);
        r_5 = static_cast<unsigned int>(static_cast<unsigned __int64>(static_cast<unsigned int>((static_cast<unsigned __int64>(r_6) + 4ULL))));
        if (!(f_0)) {
            r_2 = this->field_0004;
            slot_value_0004 = r_2;
        } else {
            slot_value_0004 = r_5;
        }
        f_0 = (r_1 < 16u);
        if (!(f_0)) {
            r_2 = this->field_0004;
        } else {
            r_2 = r_5;
        }
        r_0 = (r_0 - r_7);
        push_40125d = r_0;
        r_0 = slot_value_0004;
        r_0 = (r_0 + r_3);
        r_0 = (r_0 + r_7);
        push_401266 = r_0;
        r_1 = (r_1 - r_3);
        push_401269 = r_1;
        r_2 = (r_2 + r_3);
        push_40126c = r_2;
        fn_004e0e8b(push_40126c, push_401269, push_401266, push_40125d);
        r_0 = this->field_0014;
        r_0 = (r_0 - r_7);
        t_40127a_0 = static_cast<unsigned __int64>(static_cast<unsigned int>((static_cast<unsigned __int64>(r_6) + static_cast<unsigned __int64>(receiver_access_0018))));
        t_40127a_1 = this->field_0018;
        f_0 = (t_40127a_1 < 16u);
        this->field_0014 = r_0;
        if (!(f_0)) {
            r_5 = this->field_0004;
        }
        *reinterpret_cast<unsigned char *>(static_cast<unsigned int>(static_cast<unsigned __int64>(static_cast<unsigned int>((static_cast<unsigned __int64>(r_0) + static_cast<unsigned __int64>(r_5)))))) = static_cast<unsigned char>(0u);
    }
    r_0 = r_6;
    return this;
}
