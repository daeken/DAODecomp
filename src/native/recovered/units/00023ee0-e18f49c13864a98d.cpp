typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

void* __stdcall fn_00636a90(void*, void*);

struct C23EE0 { void fn_00023ee0(u32); };
struct C347B50 { void fn_00347b50(u8); };
struct C347B70 { void fn_00347b70(u32); };
struct C347D10 { void fn_00347d10(u8, u16); };
struct C347D50 { void fn_00347d50(u8, u8); };
struct C347D90 { void fn_00347d90(u8, u8); };
struct C347DD0 { void fn_00347dd0(u8, u32); };
struct C347E10 { void fn_00347e10(u8, u32); };
struct C636E40 {
    void* fn_00636a10(void*, void*);
    int fn_00636e40(u32*, void*, void*);
    u8 fn_00636e90(void*, void*, u32*, u8);
    u32 fn_00637050(void*, void*, u32*, u32);
};

// FUNCTION: DAO 0x00423EE0
void C23EE0::fn_00023ee0(u32 v) {
    *(u32*)((u8*)this + 0x10) = v;
}

// FUNCTION: DAO 0x00747B50
void C347B50::fn_00347b50(u8 v) {
    u8 dl = (u8)(v - 1);
    if (dl <= 2) {
        *(u8*)((u8*)this + 0x50) = v;
    } else {
        *(u8*)((u8*)this + 0x50) = 1;
    }
}

// FUNCTION: DAO 0x00747B70
void C347B70::fn_00347b70(u32 v) {
    *(u32*)((u8*)this + 0x20) = v;
}

// FUNCTION: DAO 0x00747D10
void C347D10::fn_00347d10(u8 idx, u16 val) {
    if (idx < 7) {
        *(u16*)((u8*)this + 0x12a + idx * 2) = val;
    }
}

// FUNCTION: DAO 0x00747D50
void C347D50::fn_00347d50(u8 idx, u8 val) {
    if (idx < 7) {
        *(u8*)((u8*)this + 0x138 + idx) = val;
    }
}

// FUNCTION: DAO 0x00747D90
void C347D90::fn_00347d90(u8 idx, u8 val) {
    if (idx < 7) {
        *(u8*)((u8*)this + 0x13f + idx) = val;
    }
}

// FUNCTION: DAO 0x00747DD0
void C347DD0::fn_00347dd0(u8 idx, u32 val) {
    if (idx < 7) {
        *(u32*)((u8*)this + 0x148 + idx * 4) = val;
    }
}

// FUNCTION: DAO 0x00747E10
void C347E10::fn_00347e10(u8 idx, u32 val) {
    if (idx < 7) {
        *(u32*)((u8*)this + 0x164 + idx * 4) = val;
    }
}

// FUNCTION: DAO 0x007480D0
unsigned char __cdecl fn_003480d0(unsigned int code) {
    switch (code) {
    case 0: return 3;
    case 1: return 4;
    case 2: return 0;
    case 3: return 5;
    case 4: return 2;
    case 5: return 1;
    case 6: return 6;
    case 7: return 0xFF;
    case 8: return 0xFF;
    default: return 0xFF;
    }
}

// FUNCTION: DAO 0x00A36E40
int C636E40::fn_00636e40(u32* out, void* key2, void* key3) {
    if (!out || !key2 || !key3) {
        return 0;
    }
    void* r1 = fn_00636a90(key2, key3);
    void* res = fn_00636a10(key2, r1);
    if (res && *(u32*)res == 0xE) {
        *out = *(u32*)((u8*)res + 8);
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00A36E90
u8 C636E40::fn_00636e90(void* key1, void* key2, u32* out, u8 def) {
    if (!key1 || !key2) {
        *out = 0;
        return def;
    }
    void* r1 = fn_00636a90(key1, key2);
    void* res = fn_00636a10(key1, r1);
    if (res && *(u32*)res == 0) {
        *out = 1;
        return *((u8*)res + 8);
    }
    *out = 0;
    return def;
}

// FUNCTION: DAO 0x00A37050
u32 C636E40::fn_00637050(void* key1, void* key2, u32* out, u32 def) {
    if (!key1 || !key2) {
        *out = 0;
        return def;
    }
    void* r1 = fn_00636a90(key1, key2);
    void* res = fn_00636a10(key1, r1);
    if (res && *(u32*)res == 5) {
        *out = 1;
        return *(u32*)((u8*)res + 8);
    }
    *out = 0;
    return def;
}
