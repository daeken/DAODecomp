struct Block20 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; unsigned int v4; };
struct Block16 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; };

class C_00142b70 { public: unsigned int pad0; unsigned char* begin; unsigned char* end; unsigned int fn_00142b70() const; };
class C_00143f80 { public: unsigned int pad0; unsigned char* begin; unsigned char* end; bool fn_00143f80() const; };
class C_00146850 { public: unsigned int pad0; unsigned char* begin; unsigned char* end; unsigned int fn_00146850() const; };
class C_00146870 { public: unsigned int pad0; unsigned char* begin; unsigned char* end; unsigned int fn_00146870() const; };
class C_00142ea0 { public: unsigned char pad[0x30]; Block16 field30; void fn_00142ea0(const Block16* src); };
class C_00143d70 { public: unsigned char pad[0x274]; void* field274; void fn_00143d70(void* p); };
class C_00147910 { public: unsigned char pad[0x180]; unsigned int* field180; unsigned int* field184; bool fn_00147910() const; };
class C_0014f650 { public: void* fn_0014f650(); };
class C_0014f750 { public: unsigned char pad[0x28]; void* field28; void fn_0014f750(void* p); };
class C_0014f890 { public: void* fn_0014f890(); };
class C_001500c0 { public: unsigned char pad[0x510]; unsigned int field510; unsigned int fn_001500c0() const; };
class C_001502b0 { public: unsigned char* base; void* fn_001502b0(unsigned int index) const; };
class C_001502c0 { public: unsigned char* base; void* fn_001502c0(unsigned int index) const; };

// FUNCTION: DAO 0x542B70
unsigned int C_00142b70::fn_00142b70() const {
    if (!begin) return 0;
    return (unsigned int)((end - begin) / 52);
}

// FUNCTION: DAO 0x542BF0
void __cdecl fn_00142bf0(void* dest, void* end, const void* src) {
    unsigned char* d = (unsigned char*)dest;
    unsigned char* e = (unsigned char*)end;
    const Block20* s = (const Block20*)src;
    if (d == e) return;
    do {
        *(Block20*)d = *s;
        d += 20;
    } while (d != e);
}

// FUNCTION: DAO 0x542EA0
void C_00142ea0::fn_00142ea0(const Block16* src) {
    if (&field30 != src) {
        field30 = *src;
    }
}

// FUNCTION: DAO 0x543D70
void C_00143d70::fn_00143d70(void* p) {
    if (field274 && p) {
        *(void**)((unsigned char*)field274 + 0x14) = p;
    }
}

// FUNCTION: DAO 0x543F80
bool C_00143f80::fn_00143f80() const {
    if (!begin) return true;
    return ((end - begin) / 72) == 0;
}

// FUNCTION: DAO 0x544270
bool __stdcall fn_00144270(unsigned char* base, unsigned int count, unsigned int stride, unsigned int offset) {
    unsigned int i = 0;
    unsigned char* p;
    unsigned int step;
    if (count == 0) return false;
    p = base + offset * 8;
    step = stride * 8;
    do {
        if (*(unsigned int*)p != 0) return true;
        ++i;
        p += step;
    } while (i < count);
    return false;
}

// FUNCTION: DAO 0x546850
unsigned int C_00146850::fn_00146850() const {
    if (!begin) return 0;
    return (unsigned int)((end - begin) / 48);
}

// FUNCTION: DAO 0x546870
unsigned int C_00146870::fn_00146870() const {
    if (!begin) return 0;
    return (unsigned int)((end - begin) / 20);
}

// FUNCTION: DAO 0x5468C0
void __cdecl fn_001468c0(void* dest, unsigned int count, const void* src) {
    unsigned char* d = (unsigned char*)dest;
    const Block20* s = (const Block20*)src;
    if (count == 0) return;
    do {
        if (d) {
            *(Block20*)d = *s;
        }
        --count;
        d += 20;
    } while (count != 0);
}

// FUNCTION: DAO 0x547910
bool C_00147910::fn_00147910() const {
    if (!field180) return false;
    return (((int)((unsigned char*)field184 - (unsigned char*)field180)) >> 2) != 0;
}

// FUNCTION: DAO 0x54F650
void* C_0014f650::fn_0014f650() {
    return (void*)((unsigned char*)this - 4);
}

// FUNCTION: DAO 0x54F750
void C_0014f750::fn_0014f750(void* p) {
    field28 = p;
}

// FUNCTION: DAO 0x54F890
void* C_0014f890::fn_0014f890() {
    return (void*)((unsigned char*)this + 0x5c);
}

// FUNCTION: DAO 0x5500C0
unsigned int C_001500c0::fn_001500c0() const {
    unsigned int v = field510;
    if (v == 0) return 0x20;
    if (v == 1) return 0x44;
    return 0;
}

// FUNCTION: DAO 0x5502B0
void* C_001502b0::fn_001502b0(unsigned int index) const {
    return (void*)(base + (index << 7));
}

// FUNCTION: DAO 0x5502C0
void* C_001502c0::fn_001502c0(unsigned int index) const {
    return (void*)(base + (index * 9) * 16);
}
