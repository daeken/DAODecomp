extern "C" unsigned g_00831128;
extern "C" void* fn_004e24a0(void*, const void*, unsigned);

struct BaseOps {
    void fn_0010fa20(void*);
    void fn_0010f810(void*);
};

struct Fn00415870 {
    void fn_00415870();
};

struct Fn000D37E0 {
    void fn_000d37e0(void*);
};

struct Fn0010FA80 {
    void* fn_0010fa80(void*, void*);
};

struct Fn0010FB30 {
    void fn_0010fb30(void*, const void*, unsigned);
};

struct Fn0010FBB0 {
    void fn_0010fbb0();
};

struct Fn0010FBC0 {
    void fn_0010fbc0(void*, void*);
};

struct Fn0010FBE0 {
    void* fn_0010fbe0(void*, void*);
};

struct Fn0010FCB0 {
    void fn_0010fcb0(void*, void*, void*);
};

struct Fn0010FD00 {
    void fn_0010fd00();
};

struct Fn0010FD10 {
    void* fn_0010fd10(void*, void*);
};

struct Fn0010FDD0 {
    void fn_0010fdd0();
};

struct Fn0010FDE0 {
    void* fn_0010fde0(void*, void*);
};

struct Fn0010FEA0 {
    void fn_0010fea0();
};

struct Fn0010FEB0 {
    void fn_0010feb0(void*, void*);
};

// FUNCTION: DAO 0x50fa80
void* __thiscall Fn0010FA80::fn_0010fa80(void* arg1, void* arg2)
{
    reinterpret_cast<BaseOps*>(this)->fn_0010fa20(arg2);
    *reinterpret_cast<void**>(this) = (void*)0xaf50e8u;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x28) = 0;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x2c) = 0;
    reinterpret_cast<BaseOps*>(this)->fn_0010f810(arg1);
    return this;
}

// FUNCTION: DAO 0x50fb30
void __thiscall Fn0010FB30::fn_0010fb30(void* desc, const void* src, unsigned count)
{
    if (*reinterpret_cast<int*>(reinterpret_cast<char*>(desc) + 8) != 0) {
        unsigned limit = static_cast<unsigned>(*reinterpret_cast<unsigned short*>(reinterpret_cast<char*>(desc) + 0x14)) << 4;
        unsigned n = (count < limit) ? count : limit;
        unsigned dst = *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x10);
        dst += static_cast<unsigned>(*reinterpret_cast<unsigned short*>(reinterpret_cast<char*>(desc) + 0x10)) << 4;
        dst += g_00831128;
        fn_004e24a0((void*)dst, src, n);
    }
    if (*reinterpret_cast<int*>(reinterpret_cast<char*>(desc) + 0xc) != 0) {
        unsigned limit = static_cast<unsigned>(*reinterpret_cast<unsigned short*>(reinterpret_cast<char*>(desc) + 0x1a)) << 4;
        unsigned n = (count < limit) ? count : limit;
        unsigned dst = *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x10);
        dst += static_cast<unsigned>(*reinterpret_cast<unsigned short*>(reinterpret_cast<char*>(desc) + 0x16)) << 4;
        dst += g_00831128;
        fn_004e24a0((void*)dst, src, n);
    }
}

// FUNCTION: DAO 0x50fbb0
void __thiscall Fn0010FBB0::fn_0010fbb0()
{
    *reinterpret_cast<void**>(this) = (void*)0xaf50e8u;
    reinterpret_cast<Fn00415870*>(this)->fn_00415870();
}

// FUNCTION: DAO 0x50fbc0
void __thiscall Fn0010FBC0::fn_0010fbc0(void* arg1, void* arg2)
{
    reinterpret_cast<Fn0010FB30*>(this)->fn_0010fb30(arg1, arg2, 4u);
}

// FUNCTION: DAO 0x50fbe0
void* __thiscall Fn0010FBE0::fn_0010fbe0(void* arg1, void* arg2)
{
    reinterpret_cast<BaseOps*>(this)->fn_0010fa20(arg2);
    *reinterpret_cast<void**>(this) = (void*)0xaf5118u;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x70) = 0;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x74) = 0;
    reinterpret_cast<BaseOps*>(this)->fn_0010f810(arg1);
    return this;
}

// FUNCTION: DAO 0x50fcb0
void __thiscall Fn0010FCB0::fn_0010fcb0(void* arg1, void* arg2, void* arg3)
{
    unsigned char local[0x40];
    if (*reinterpret_cast<unsigned char*>(reinterpret_cast<char*>(this) + 0x1c) != 0) {
        reinterpret_cast<Fn000D37E0*>(arg1)->fn_000d37e0(local);
        reinterpret_cast<Fn0010FB30*>(arg3)->fn_0010fb30(this, local, 0x40u);
    } else {
        reinterpret_cast<Fn0010FB30*>(arg3)->fn_0010fb30(this, arg1, 0x40u);
    }
}

// FUNCTION: DAO 0x50fd00
void __thiscall Fn0010FD00::fn_0010fd00()
{
    *reinterpret_cast<void**>(this) = (void*)0xaf5118u;
    reinterpret_cast<Fn00415870*>(this)->fn_00415870();
}

// FUNCTION: DAO 0x50fd10
void* __thiscall Fn0010FD10::fn_0010fd10(void* arg1, void* arg2)
{
    reinterpret_cast<BaseOps*>(this)->fn_0010fa20(arg2);
    *reinterpret_cast<void**>(this) = (void*)0xaf5148u;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x30) = 0.0f;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x34) = 0.0f;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x38) = 0.0f;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x3c) = 1.0f;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x40) = 0;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x44) = 0;
    reinterpret_cast<BaseOps*>(this)->fn_0010f810(arg1);
    return this;
}

// FUNCTION: DAO 0x50fdd0
void __thiscall Fn0010FDD0::fn_0010fdd0()
{
    *reinterpret_cast<void**>(this) = (void*)0xaf5148u;
    reinterpret_cast<Fn00415870*>(this)->fn_00415870();
}

// FUNCTION: DAO 0x50fde0
void* __thiscall Fn0010FDE0::fn_0010fde0(void* arg1, void* arg2)
{
    reinterpret_cast<BaseOps*>(this)->fn_0010fa20(arg2);
    *reinterpret_cast<void**>(this) = (void*)0xaf5178u;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x24) = 0.0f;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x28) = 0.0f;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x2c) = 0.0f;
    *reinterpret_cast<float*>(reinterpret_cast<char*>(this) + 0x30) = 0.0f;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x34) = 0;
    *reinterpret_cast<unsigned*>(reinterpret_cast<char*>(this) + 0x38) = 0;
    reinterpret_cast<BaseOps*>(this)->fn_0010f810(arg1);
    return this;
}

// FUNCTION: DAO 0x50fea0
void __thiscall Fn0010FEA0::fn_0010fea0()
{
    *reinterpret_cast<void**>(this) = (void*)0xaf5178u;
    reinterpret_cast<Fn00415870*>(this)->fn_00415870();
}

// FUNCTION: DAO 0x50feb0
void __thiscall Fn0010FEB0::fn_0010feb0(void* arg1, void* arg2)
{
    reinterpret_cast<Fn0010FB30*>(this)->fn_0010fb30(arg1, arg2, 0x10u);
}
