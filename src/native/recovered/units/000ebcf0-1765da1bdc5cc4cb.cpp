typedef unsigned char u8;

struct H_000c0d90 { void fn_000c0d90(); };
struct H_000c2480 { void* fn_000c2480(void*); };
struct H_000c0db0 { void fn_000c0db0(); };
struct H_00001670 { void fn_00001670(int, const char*); };
struct H_000019d0 { void fn_000019d0(void*); };
struct H_8e1202 { void* fn_004e1202(void*); };
struct H_87b880 { void fn_0047b880(void*); };
struct H_67a910 { void fn_0027a910(void*); };
struct H_880be0 { bool fn_00480be0(void*); };
struct H_67ba40 { void fn_0027ba40(); };
struct H_c2510 { void fn_000c2510(void*); };
struct H_880f80 { void* fn_00480f80(void*, void*); };
struct H_881ee0 { void* fn_00481ee0(void*, void*); };
struct H_c2ab0 { void fn_000c2ab0(); };
struct H_51fe10 { void* fn_0011fe10(void*); };
struct H_8911e0 { void* fn_004911e0(); };
struct H_891690 { void fn_00491690(void*, void*); };
struct H_8e18c1 { void fn_004e18c1(void*); };
struct H_8ec877 { void fn_004ec877(void*, void*, void*, void*, void*, void*, void*); };

extern "C" void* __cdecl fn_002499b0(void);
extern "C" void __cdecl fn_004e11f2(void);
extern "C" void* __cdecl fn_0047cbd0(void*, void*, void*, void*, void*);
extern "C" void __cdecl fn_00480cd0(void);

struct C_000d1cd0 {
    int f0;
    int f4;
    char pad[8];
    void fn_000d1c30(void*);
    C_000d1cd0* fn_000d1cd0(void*);
};

struct C_003d6ff0 {
    int f0;
    int f4;
    int f8;
    void fn_003d5f60(void*, void*, void*, void*, void*, void*, void*);
    C_003d6ff0* fn_003d6ff0(int*);
};

struct C_00426110 {
    int f0;
    int f4;
    int f8;
    void fn_004913e0(void*, void*, void*, void*);
    void fn_00401530(void*, void*, void*, void*, void*);
    void fn_00426110(unsigned int, void*, void*, void*);
};

struct C_0047cc80 {
    int f0;
    int f4;
    int f8;
    void* fn_0047cc80(void*, void*, void*, void*);
};

struct C_0047cec0 {
    int f0;
    int f4;
    int f8;
    void fn_0047cec0(void*, void*);
};

struct C_004819e0 {
    int f0;
    int f4;
    int f8;
    void* fn_00481310(void*, void*, void*, void*);
    void* fn_004819e0(void*, void*);
};

struct C_00481c70 {
    int f0;
    int f4;
    int f8;
    bool fn_00481c70(void*, void*);
};

struct C_00482010 {
    int f0;
    int f4;
    int f8;
    void* fn_00482010(void*, void*);
};

struct C_004919e0 {
    int f0;
    int f4;
    int f8;
    int f10;
    int f14;
    int f18;
    int f1c;
    int f20;
    int f24;
    C_004919e0* fn_004919e0(void*, void*);
};

struct C_0065fee0 {
    int f0;
    int f4;
    int f8;
    void* fn_00201130(void*, void*);
    bool fn_0065fee0(void*, void*);
};

// FUNCTION: DAO 0x004d1cd0
C_000d1cd0* C_000d1cd0::fn_000d1cd0(void* arg) {
    ((H_000c0d90*)((char*)this + 8))->fn_000c0d90();
    char tmp[0x40];
    void* p = ((H_000c2480*)tmp)->fn_000c2480(arg);
    fn_000d1c30(p);
    ((H_000c0db0*)p)->fn_000c0db0();
    return this;
}

// FUNCTION: DAO 0x004ebcf0
int __cdecl fn_000ebcf0(int base, int index) {
    return *(int*)(base + index);
}

// FUNCTION: DAO 0x007d6ff0
C_003d6ff0* C_003d6ff0::fn_003d6ff0(int* arg) {
    void* p = fn_002499b0();
    f4 = (int)p;
    f8 = 0;
    int* edx = *(int**)((char*)arg + 4);
    int edi = *edx;
    int eaxv = *(int*)p;
    fn_003d5f60((void*)this, (void*)eaxv, (void*)arg, (void*)edi, (void*)arg, (void*)edx, (void*)arg);
    return this;
}

// FUNCTION: DAO 0x00826110
void C_00426110::fn_00426110(unsigned int index, void* a2, void* a3, void* a4) {
    (void)a3;
    (void)a4;
    unsigned int count = 0;
    if (f4 != 0) count = (unsigned int)((f8 - f4) / 12);
    if (count < index) {
        unsigned int cnt2 = 0;
        if (f4 != 0) cnt2 = (unsigned int)((f8 - f4) / 12);
        if ((unsigned int)f4 > (unsigned int)f8) fn_004e11f2();
        fn_004913e0((void*)this, (void*)f8, (void*)(index - cnt2), a2);
        return;
    }
    unsigned int cnt = 0;
    if (f4 != 0) cnt = (unsigned int)((f8 - f4) / 12);
    if (index < cnt) {
        if ((unsigned int)f4 > (unsigned int)f8) fn_004e11f2();
        char* dest = (char*)f4 + index * 12;
        if (dest > (char*)f8) fn_004e11f2();
        if (dest < (char*)f4) fn_004e11f2();
        char local[16];
        fn_00401530((void*)this, dest, (void*)this, (void*)this, local);
    }
}

// FUNCTION: DAO 0x0087cc80
void* C_0047cc80::fn_0047cc80(void* a1, void* a2, void* a3, void* a4) {
    (void)a3;
    if (f8 >= 0x0AAAAAA9) {
        char tmp[0x40];
        ((H_00001670*)tmp)->fn_00001670(0x13, (const char*)0x00AE0204);
        ((H_000019d0*)tmp)->fn_000019d0(tmp);
        ((H_8e1202*)tmp)->fn_004e1202(tmp);
    }
    void* p = fn_0047cbd0((void*)f4, a1, (void*)f4, a2, 0);
    if (p == 0) return 0;
    ((H_87b880*)this)->fn_0047b880(p);
    ((H_67a910*)this)->fn_0027a910(p);
    if (f4 == 0) {
        f4 = (int)p;
        f8 = 1;
    } else {
        f8 += 1;
    }
    *(void**)a4 = p;
    return a4;
}

// FUNCTION: DAO 0x0087cec0
void C_0047cec0::fn_0047cec0(void* a1, void* a2) {
    if (((H_880be0*)a1)->fn_00480be0((char*)this + 0xc)) {
        char local[16];
        void* r = ((C_0047cc80*)this)->fn_0047cc80(a1, (void*)0, (void*)1, local);
        (void)r;
    } else {
        char tmp[8];
        ((H_67ba40*)tmp)->fn_0027ba40();
    }
}

// FUNCTION: DAO 0x008819e0
void* C_004819e0::fn_004819e0(void* result, void* key) {
    char local[16];
    void* p = fn_00481310(local, key, (void*)0, (void*)1);
    (void)p;
    if (*(int*)this == 0) fn_00480cd0();
    *(void**)result = key;
    return result;
}

// FUNCTION: DAO 0x00881c70
bool C_00481c70::fn_00481c70(void* a1, void* a2) {
    char temp[0x28];
    ((H_c2510*)temp)->fn_000c2510(a1);
    void* node = ((C_004819e0*)this)->fn_004819e0(temp, a2);
    bool r = *(u8*)((char*)node + 8);
    ((H_000c0db0*)temp)->fn_000c0db0();
    return r;
}

// FUNCTION: DAO 0x00882010
void* C_00482010::fn_00482010(void* a1, void* a2) {
    void* p = 0;
    if (this == 0) fn_004e11f2();
    ((H_880f80*)this)->fn_00480f80(&p, a2);
    if (p != 0 && p != this) fn_004e11f2();
    void* q = ((H_881ee0*)this)->fn_00481ee0(a1, a2);
    ((H_c2ab0*)q)->fn_000c2ab0();
    void* r = ((H_51fe10*)((char*)this + 0x2c))->fn_0011fe10(a2);
    *(void**)r = *(void**)a1;
    return r;
}

// FUNCTION: DAO 0x008919e0
C_004919e0* C_004919e0::fn_004919e0(void* a1, void* a2) {
    (void)a1;
    (void)a2;
    f0 = 0;
    f4 = 0;
    f8 = 0;
    f14 = 0;
    f10 = (int)((H_8911e0*)((char*)this + 4))->fn_004911e0();
    int local = 0;
    ((H_891690*)((char*)this + 0x10))->fn_00491690((void*)9, &local);
    f20 = 1;
    f24 = 1;
    return this;
}

// FUNCTION: DAO 0x008ecad8
int __cdecl fn_004ecad8(int a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8) {
    char local[0x10];
    ((H_8e18c1*)local)->fn_004e18c1((void*)a1);
    ((H_8ec877*)local)->fn_004ec877((void*)a2, (void*)a3, (void*)a4, (void*)a5, (void*)a6, (void*)a7, (void*)a8);
    if (local[0xc]) {
        int* p = *(int**)(local + 8);
        p[0x1c] &= ~2;
    }
    return 0;
}

// FUNCTION: DAO 0x00a5fee0
bool C_0065fee0::fn_0065fee0(void* a1, void* a2) {
    char temp[0x28];
    void* local = 0;
    ((H_c2510*)temp)->fn_000c2510(a1);
    void* p = fn_00201130(temp, &local);
    bool r = *(u8*)((char*)p + 8);
    ((H_000c0db0*)temp)->fn_000c0db0();
    return r;
}
