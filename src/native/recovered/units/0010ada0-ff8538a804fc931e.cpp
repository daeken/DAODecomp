typedef unsigned int u32;

extern "C" int __cdecl fn_004e687b(const wchar_t*, const wchar_t*);
extern "C" void* __cdecl fn_00413660(u32);
extern "C" void __cdecl fn_004136c0(void*);
extern void* g_00C31250;
extern void* g_00C310E0;
extern void* g_00C31140;

struct C_004C2480 { const wchar_t* fn_004c2480(const wchar_t*); };
struct C_004C0DB0 { void fn_004c0db0(); };
struct C_00455850 { void fn_00455850(void*); };
struct C_0081CDD0 { void fn_0081cdd0(void*); };
struct C_00507650 { void* fn_00507650(); };
struct C_005076C0 { void fn_005076c0(void*); };
struct C_00507260 { void fn_00507260(void*); };
struct C_00506F00 { void fn_00506f00(); };
struct C_00505F20 { void* fn_00505f20(); };
struct C_00503980 { void fn_00503980(void*); };
struct C_00503990 { void fn_00503990(void*); };
struct C_005062F0 { void fn_005062f0(void*); };
struct C_00503D80 { void fn_00503d80(void*); };
struct C_00504D80 { void fn_00504d80(void*); };
struct C_00504DA0 { void fn_00504da0(void*); };
struct C_005064B0 { void* fn_005064b0(); };
struct C_00505D40 { void fn_00505d40(void*); };
struct C_00504EB0 { void fn_00504eb0(void*); };
struct C_00505E50 { void fn_00505e50(); };
struct C_004C2AB0 { void fn_004c2ab0(); };

struct C_00C31250 {
    virtual void* v0();
    virtual void* v1();
    virtual void* v2();
    virtual void* v3();
    virtual void* v4();
    virtual void* v5();
};

struct C_0050A720 {
    void fn_0010a720(const wchar_t**);
    void fn_0050c500(const wchar_t*);
    void fn_00509da0(const wchar_t*);
    void fn_00509dc0(const wchar_t*);
    void fn_00509870(const wchar_t*);
    void fn_00509610(const wchar_t*);
};

struct C_0050A8C0 {
    void fn_0010a8c0(const wchar_t**);
    void fn_00509f80(const wchar_t*);
    void fn_00509fa0(const wchar_t*);
    void fn_005093a0(const wchar_t*);
    void fn_00509f60(const wchar_t*);
    void fn_00509f70(const wchar_t*);
    void fn_00509610(const wchar_t*);
};

struct C_0050AB90 {
    void fn_0010ab90();
};

struct C_0050AC50 : public C_0050AB90 {
    void* fn_0010ac50(unsigned int);
};

struct C_0050AD10 {
    void* fn_0010ad10(unsigned int);
    void fn_005096e0();
};

struct C_0050AD30 {
    void* fn_0010ad30(unsigned int);
    void fn_00509800();
};

struct C_0050AD50 {
    void* fn_0010ad50(unsigned int);
    void fn_0050a1f0();
};

struct C_0050ADA0 {
    void fn_0010ada0(const void*);
};

struct C_0050AE10 {
    void fn_0010ae10();
};

struct C_0050AF10 {
    void fn_0010af10();
};

struct C_0050B0C0 {
    void fn_0010b0c0();
};

struct C_0050C500 {
    void fn_0010c500();
};

// FUNCTION: DAO 0x0050a720
void C_0050A720::fn_0010a720(const wchar_t** pairs)
{
    unsigned char temp[64];
    for (u32 i = 0; pairs[i] != 0; i += 2) {
        const wchar_t* name = pairs[i];
        const wchar_t* value = pairs[i + 1];
        bool handled = false;
        if (fn_004e687b(name, (const wchar_t*)0x00aeda08) == 0 ||
            fn_004e687b(name, (const wchar_t*)0x00b2be58) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509610(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af10f4) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_0050c500(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c3c) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509da0(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c24) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509dc0(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c08) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509870(s);
            handled = true;
        }
        if (handled)
            reinterpret_cast<C_004C0DB0*>(temp)->fn_004c0db0();
    }
}

// FUNCTION: DAO 0x0050a8c0
void C_0050A8C0::fn_0010a8c0(const wchar_t** pairs)
{
    unsigned char temp[64];
    for (u32 i = 0; pairs[i] != 0; i += 2) {
        const wchar_t* name = pairs[i];
        const wchar_t* value = pairs[i + 1];
        bool handled = false;
        if (fn_004e687b(name, (const wchar_t*)0x00aeda08) == 0 ||
            fn_004e687b(name, (const wchar_t*)0x00b2be58) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509610(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c3c) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509f80(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c24) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509fa0(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c74) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_005093a0(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c60) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509f60(s);
            handled = true;
        } else if (fn_004e687b(name, (const wchar_t*)0x00af4c48) == 0) {
            const wchar_t* s = reinterpret_cast<C_004C2480*>(temp)->fn_004c2480(value);
            this->fn_00509f70(s);
            handled = true;
        }
        if (handled)
            reinterpret_cast<C_004C0DB0*>(temp)->fn_004c0db0();
    }
}

// FUNCTION: DAO 0x0050ab90
void C_0050AB90::fn_0010ab90()
{
    *reinterpret_cast<void**>(this) = (void*)0x00af4cac;
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0xb8)->fn_004c0db0();
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0x9c)->fn_004c0db0();
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0x7c)->fn_004c0db0();
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0x60)->fn_004c0db0();
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0x40)->fn_004c0db0();
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0x24)->fn_004c0db0();
    reinterpret_cast<C_004C0DB0*>(reinterpret_cast<char*>(this) + 0x08)->fn_004c0db0();
    *reinterpret_cast<void**>(this) = (void*)0x00af4520;
}

// FUNCTION: DAO 0x0050ac50
void* C_0050AC50::fn_0010ac50(unsigned int flags)
{
    this->fn_0010ab90();
    if (flags & 1)
        fn_004136c0(this);
    return this;
}

// FUNCTION: DAO 0x0050ad10
void* C_0050AD10::fn_0010ad10(unsigned int flags)
{
    this->fn_005096e0();
    if (flags & 1)
        fn_004136c0(this);
    return this;
}

// FUNCTION: DAO 0x0050ad30
void* C_0050AD30::fn_0010ad30(unsigned int flags)
{
    this->fn_00509800();
    if (flags & 1)
        fn_004136c0(this);
    return this;
}

// FUNCTION: DAO 0x0050ad50
void* C_0050AD50::fn_0010ad50(unsigned int flags)
{
    this->fn_0050a1f0();
    if (flags & 1)
        fn_004136c0(this);
    return this;
}

// FUNCTION: DAO 0x0050ada0
void C_0050ADA0::fn_0010ada0(const void* arg)
{
    u32 len = *reinterpret_cast<const u32*>(reinterpret_cast<const char*>(arg) + 0x18);
    const wchar_t* s;
    if (len >= 8)
        s = *reinterpret_cast<const wchar_t* const*>(reinterpret_cast<const char*>(arg) + 4);
    else
        s = reinterpret_cast<const wchar_t*>(reinterpret_cast<const char*>(arg) + 4);

    u32* flags = reinterpret_cast<u32*>(reinterpret_cast<char*>(this) + 8);
    if (*flags & 2)
        return;
    if (fn_004e687b(s, (const wchar_t*)0x00af4cec) == 0) {
        *flags |= 4;
        return;
    }
    if (fn_004e687b(s, (const wchar_t*)0x00af4cdc) == 0) {
        *flags |= 8;
        return;
    }
    if (fn_004e687b(s, (const wchar_t*)0x00af4cd4) == 0) {
        *flags |= 0x10;
        return;
    }
}

// FUNCTION: DAO 0x0050ae10
void C_0050AE10::fn_0010ae10()
{
    void* mem = fn_00413660(0x20);
    void* obj = 0;
    if (mem)
        obj = reinterpret_cast<C_00507650*>(mem)->fn_00507650();
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x38) = obj;
    reinterpret_cast<C_00455850*>(obj)->fn_00455850(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 8));
    reinterpret_cast<C_0081CDD0*>(obj)->fn_0081cdd0(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x34));

    void** begin = *reinterpret_cast<void***>(reinterpret_cast<char*>(this) + 0x28);
    void** end = *reinterpret_cast<void***>(reinterpret_cast<char*>(this) + 0x2c);
    u32 count = begin ? (u32)(end - begin) : 0;
    for (u32 i = 0; i < count; ++i) {
        void* globalObj = g_00C31250;
        void* ret = reinterpret_cast<C_00C31250*>(globalObj)->v5();
        reinterpret_cast<C_005076C0*>(obj)->fn_005076c0(ret);
    }

    void* p = *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x3c);
    if (p) {
        void* ret = reinterpret_cast<C_00C31250*>(p)->v5();
        reinterpret_cast<C_00507260*>(obj)->fn_00507260(ret);
        reinterpret_cast<C_00506F00*>(ret)->fn_00506f00();
    }
}

// FUNCTION: DAO 0x0050af10
void C_0050AF10::fn_0010af10()
{
    void* mem = fn_00413660(0x114);
    void* obj = 0;
    if (mem)
        obj = reinterpret_cast<C_00505F20*>(mem)->fn_00505f20();
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0xe8) = obj;
    reinterpret_cast<C_00455850*>(obj)->fn_00455850(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 8));
    reinterpret_cast<C_00503980*>(obj)->fn_00503980(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x24));
    reinterpret_cast<C_00503990*>(obj)->fn_00503990(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x40));
    reinterpret_cast<C_005062F0*>(obj)->fn_005062f0(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x5c));
    reinterpret_cast<C_00503D80*>(obj)->fn_00503d80(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0xb4));

    void** begin1 = *reinterpret_cast<void***>(reinterpret_cast<char*>(this) + 0x98);
    void** end1 = *reinterpret_cast<void***>(reinterpret_cast<char*>(this) + 0x9c);
    u32 count1 = begin1 ? (u32)(end1 - begin1) : 0;
    for (u32 i = 0; i < count1; ++i)
        reinterpret_cast<C_00504D80*>(obj)->fn_00504d80(g_00C310E0);

    void** begin2 = *reinterpret_cast<void***>(reinterpret_cast<char*>(this) + 0xa8);
    void** end2 = *reinterpret_cast<void***>(reinterpret_cast<char*>(this) + 0xac);
    u32 count2 = begin2 ? (u32)(end2 - begin2) : 0;
    for (u32 i = 0; i < count2; ++i) {
        void* elem;
        if (begin2 && i < count2)
            elem = begin2[i];
        else
            elem = g_00C31140;
        if (elem && *reinterpret_cast<u32*>(reinterpret_cast<char*>(elem) + 0x20) != 0)
            reinterpret_cast<C_00504DA0*>(obj)->fn_00504da0(g_00C31140);
    }

    reinterpret_cast<C_00C31250*>(obj)->v4();
}

// FUNCTION: DAO 0x0050b0c0
void C_0050B0C0::fn_0010b0c0()
{
    void* mem = fn_00413660(0x128);
    void* obj = 0;
    if (mem)
        obj = reinterpret_cast<C_005064B0*>(mem)->fn_005064b0();
    reinterpret_cast<C_00455850*>(obj)->fn_00455850(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 8));
    reinterpret_cast<C_00505D40*>(obj)->fn_00505d40(*reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0x78));

    unsigned char* begin = *reinterpret_cast<unsigned char**>(reinterpret_cast<char*>(this) + 0xc8);
    unsigned char* end = *reinterpret_cast<unsigned char**>(reinterpret_cast<char*>(this) + 0xcc);
    u32 count = 0;
    if (begin)
        count = (u32)((end - begin) / 0x1c);
    if (begin == 0 || count == 0) {
        reinterpret_cast<C_00505E50*>(obj)->fn_00505e50();
    } else {
        for (u32 i = 0; i < count; ++i) {
            void* elem = begin + i * 0x1c;
            reinterpret_cast<C_00504EB0*>(obj)->fn_00504eb0(elem);
        }
    }
    reinterpret_cast<C_00C31250*>(obj)->v2();
    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + 0xe8) = obj;
}

// FUNCTION: DAO 0x0050c500
void C_0050C500::fn_0010c500()
{
    reinterpret_cast<C_004C2AB0*>(reinterpret_cast<char*>(this) + 8)->fn_004c2ab0();
}
