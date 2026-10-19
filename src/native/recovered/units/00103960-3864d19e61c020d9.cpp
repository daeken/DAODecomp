struct C_00103960 { unsigned char pad_0x00[0xe0]; unsigned char field_0xe0; unsigned char* __thiscall fn_00103960(); };
struct C_00103970 { unsigned char pad_0x00[0x64]; unsigned char field_0x64; unsigned char __thiscall fn_00103970(); };
struct Block16_103c00 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; };
struct C_00106e30 { unsigned char pad_0x00[0x20]; bool field_0x20; bool __thiscall fn_00106e30(); };
struct C_00107260 { unsigned char pad_0x00[0x14]; unsigned int field_0x14; void __thiscall fn_00107260(unsigned int value); };
struct C_00107270 { unsigned char pad_0x00[0x18]; bool field_0x18; bool __thiscall fn_00107270(); };
struct C_0010f120 { unsigned char pad_0x00[0x10]; unsigned short field_0x10; unsigned short __thiscall fn_0010f120(); };
struct C_0010fc90 { unsigned char pad_0x00[0x30]; unsigned char field_0x30; unsigned char* __thiscall fn_0010fc90(); };
struct C_00110900 { unsigned char pad_0x00[0x2c]; int field_0x2c; };
struct Node_110d20 { unsigned char pad_0x00[8]; Node_110d20* next; unsigned char pad_0x0c[5]; unsigned char flag_0x11; };
struct C_001184d0 { unsigned char pad_0x00[0x38]; unsigned int field_0x38; bool __thiscall fn_001184d0(); };
struct C_00467ed0 { unsigned int field_0x00; unsigned int field_0x04; unsigned char field_0x08; void __thiscall fn_00467ed0(const C_00467ed0* src); };

// FUNCTION: DAO 0x503960
unsigned char* __thiscall C_00103960::fn_00103960() {
    return &this->field_0xe0;
}

// FUNCTION: DAO 0x503970
unsigned char __thiscall C_00103970::fn_00103970() {
    return this->field_0x64;
}

// FUNCTION: DAO 0x503c00
Block16_103c00* __cdecl fn_00103c00(Block16_103c00* first, Block16_103c00* last, Block16_103c00* dest) {
    Block16_103c00* result = dest + (last - first);
    while (first != last) {
        *dest = *first;
        ++dest;
        ++first;
    }
    return result;
}

// FUNCTION: DAO 0x506e30
bool __thiscall C_00106e30::fn_00106e30() {
    return this->field_0x20;
}

// FUNCTION: DAO 0x507260
void __thiscall C_00107260::fn_00107260(unsigned int value) {
    if (this->field_0x14 == 0) {
        this->field_0x14 = value;
    }
}

// FUNCTION: DAO 0x507270
bool __thiscall C_00107270::fn_00107270() {
    return this->field_0x18;
}

// FUNCTION: DAO 0x50f120
unsigned short __thiscall C_0010f120::fn_0010f120() {
    return this->field_0x10;
}

// FUNCTION: DAO 0x50f210
void __stdcall fn_0010f210(unsigned int* a, unsigned int* b) {
    *a = 0;
    *b = 0;
    *a += 0x28;
}

// FUNCTION: DAO 0x50f850
void __stdcall fn_0010f850(unsigned int* a, unsigned int* b) {
    *a = 0;
    *b = 0;
    *a += 0x24;
}

// FUNCTION: DAO 0x50fc90
unsigned char* __thiscall C_0010fc90::fn_0010fc90() {
    return &this->field_0x30;
}

// FUNCTION: DAO 0x510900
int __stdcall fn_00110900(C_00110900* a, C_00110900* b) {
    return a->field_0x2c < b->field_0x2c;
}

// FUNCTION: DAO 0x510d20
Node_110d20* __cdecl fn_00110d20(Node_110d20* p) {
    Node_110d20* eax = p;
    Node_110d20* ecx = eax->next;
    if (ecx->flag_0x11 != 0) {
        return eax;
    }
    do {
        eax = ecx;
        ecx = eax->next;
    } while (ecx->flag_0x11 == 0);
    return eax;
}

// FUNCTION: DAO 0x5115d0
unsigned short* __cdecl fn_001115d0(unsigned short* first, unsigned short* last, unsigned short* dest) {
    unsigned short* result = dest + (last - first);
    while (first != last) {
        *dest = *first;
        ++dest;
        ++first;
    }
    return result;
}

// FUNCTION: DAO 0x511700
unsigned short* __cdecl fn_00111700(unsigned short* first, unsigned short* last, unsigned short* dest) {
    while (first != last) {
        if (dest != 0) {
            *dest = *first;
        }
        ++first;
        ++dest;
    }
    return dest;
}

// FUNCTION: DAO 0x5184d0
bool __thiscall C_001184d0::fn_001184d0() {
    return this->field_0x38 == 2;
}

// FUNCTION: DAO 0x867ed0
void __thiscall C_00467ed0::fn_00467ed0(const C_00467ed0* src) {
    this->field_0x00 |= src->field_0x00;
    this->field_0x04 |= src->field_0x04;
    this->field_0x08 |= src->field_0x08;
}
