typedef unsigned int uint32;
typedef unsigned char uint8;

extern "C" {
extern uint8 g_00affd98[];
extern uint8 g_00bf99e0[];
extern uint8 g_00c2be00[];
extern uint8 g_0083293c[];
extern uint8 g_00832a30[];
extern uint8 g_00c327ec[];
}

struct U_001c7df0 { void* meth(); };
struct U_00a58190 { void meth(void*, void*); };
struct U_005e40f0 { void meth(); };
struct U_00a35af0 { void meth(void*, void*); };
struct U_00a35b90 { int meth(void*, void*, void*, void*, void*, void*); };
struct U_0064a740 { void* meth(void*, void*, void*, void*, void*, void*); };
struct U_0064a630 { void* meth(void*, void*, void*, void*, void*, void*); };
struct U_00a59e10 { void meth(); };
struct U_004c0d90 { void meth(); };
struct U_0069baa0 { void meth(); };
struct U_001dee10 { void meth(); };
struct U_0008a970 { void meth(); };
struct U_001de5b0 { void meth(int, void*); };
struct U_001bdcf0 { void meth(); };
struct U_004e2900 { void meth(); };
struct U_0048a900 { void meth(); };
struct U_004c0db0 { void meth(); };

struct C_1c7d60 {
    void* v0;
    void* p;
    int f8;
    C_1c7d60* fn_001c7d60(void*);
};

struct C_1c7d90 {
    void* v0;
    void* p;
    void* f8;
    void fn_001c7d90();
    void* fn_001c7db0();
    bool fn_001c7dd0();
    void* fn_001c7e10();
};

struct C_1c7e50 {
    void* v0;
    void* p;
    void* f8;
    void* fn_001c7e50();
};

struct C_1d4fc0 {
    char pad[0xcc];
    void* fcc;
    char pad2[0x2b8 - 0xd0];
    void* f2b8;
    void* fn_001d4fc0();
};

struct C_1e4880 {
    char pad[0x570];
    void* begin;
    void* end;
    void fn_001e4880(unsigned char);
};

struct C_1e6280 {
    char pad[0x58];
    void* obj58_vt;
    char pad2[0x57c - 0x5c];
    void fn_001e6280();
};

struct C_24ace0 {
    void* fn_0024ace0(void*, void*, void*, void*, void*, void*);
};

struct C_6796e0 {
    void* fn_002796e0();
};

struct C_29bac0 {
    void* v0;
    char pad[0x1c];
    void* f20;
    uint32 f24;
    uint32 f28;
    char pad2[0x1c];
    void* f48;
    void* f4c;
    C_29bac0* fn_0029bac0();
};

// FUNCTION: DAO 0x005C7D60
C_1c7d60* C_1c7d60::fn_001c7d60(void* arg) {
    this->v0 = (void*)g_00affd98;
    this->p = arg;
    if (!arg) {
        this->f8 = 0;
        return this;
    }
    void** vt = *(void***)arg;
    typedef int (__thiscall *VFn44)(void*);
    this->f8 = ((VFn44)vt[0x44 / 4])(arg);
    return this;
}

// FUNCTION: DAO 0x005C7D90
void C_1c7d90::fn_001c7d90() {
    this->v0 = (void*)g_00affd98;
    void* q = this->f8;
    if (q) {
        void** vt = *(void***)q;
        typedef void (__thiscall *VFn0)(void*, int);
        ((VFn0)vt[0])(q, 1);
    }
}

// FUNCTION: DAO 0x005C7DB0
void* C_1c7d90::fn_001c7db0() {
    void* q = this->f8;
    if (!q) return 0;
    void** vt = *(void***)q;
    typedef void* (__thiscall *VFn4)(void*);
    return ((VFn4)vt[1])(q);
}

// FUNCTION: DAO 0x005C7DD0
bool C_1c7d90::fn_001c7dd0() {
    void* q = this->f8;
    if (!q) return false;
    void** vt = *(void***)q;
    typedef bool (__thiscall *VFn8)(void*);
    return ((VFn8)vt[2])(q);
}

// FUNCTION: DAO 0x005C7E10
void* C_1c7d90::fn_001c7e10() {
    void* q = this->f8;
    if (!q) return (void*)g_00bf99e0;
    void** vt = *(void***)q;
    typedef void* (__thiscall *VFn10)(void*);
    void* r = ((VFn10)vt[4])(q);
    return r ? r : (void*)g_00bf99e0;
}

// FUNCTION: DAO 0x005C7E50
void* C_1c7e50::fn_001c7e50() {
    if (!this->p) return (void*)g_00c2be00;
    void* inner = this->p;
    void** vt = *(void***)inner;
    void* arg = ((U_001c7df0*)this)->meth();
    typedef void* (__thiscall *VFn1c)(void*, void*);
    return ((VFn1c)vt[0x1c / 4])(inner, arg);
}

// FUNCTION: DAO 0x005D4FC0
void* C_1d4fc0::fn_001d4fc0() {
    if (!this->fcc) return 0;
    void* local = 0;
    void* obj = this->fcc;
    void* arg = this->f2b8;
    ((U_00a58190*)obj)->meth(arg, &local);
    if (!local) return 0;
    void** vt = *(void***)local;
    typedef void* (__thiscall *VFn1c)(void*);
    return ((VFn1c)vt[0x1c / 4])(local);
}

// FUNCTION: DAO 0x005E4880
void C_1e4880::fn_001e4880(unsigned char flag) {
    for (int i = 0; i < 6; ++i) {
        void* elem = 0;
        if (this->begin) {
            uint32 n = (uint32)(((char*)this->end - (char*)this->begin) / 4);
            if ((uint32)i < n) elem = ((void**)this->begin)[i];
            else elem = *(void**)g_00832a30;
        } else {
            elem = *(void**)g_00832a30;
        }
        if (elem) elem = (char*)elem + 0x1c;
        else elem = 0;

        C_1c7d60 obj;
        obj.fn_001c7d60(elem);

        while (((C_1c7d90*)&obj)->fn_001c7dd0()) {
            void* base = *(void**)g_0083293c;
            void* ptr = 0;
            void* vb = *(void**)((char*)base + 0x570);
            if (vb) {
                uint32 n = (uint32)(((char*)(*(void**)((char*)base + 0x574)) - (char*)vb) / 4);
                if ((uint32)i < n) ptr = *(void**)((char*)vb + i * 4);
                else ptr = *(void**)g_00832a30;
            } else {
                ptr = *(void**)g_00832a30;
            }

            ((C_1c7e50*)&obj)->fn_001c7e50();
            void* r1 = 0;
            if (ptr) r1 = ((C_6796e0*)ptr)->fn_002796e0();
            void* r2 = ((C_1c7d90*)&obj)->fn_001c7e10();
            if (r1) {
                void* vtbl = *(void**)r1;
                void* fn = *(void**)((char*)vtbl + 0x3c);
                typedef void* (__thiscall *VFn)(void*, void*);
                ((VFn)fn)(r1, r2);
            }
            ((C_1c7d90*)&obj)->fn_001c7db0();
            if (!((C_1c7d90*)&obj)->fn_001c7dd0()) break;
        }
        ((C_1c7d90*)&obj)->fn_001c7d90();
    }
    if (flag) ((U_005e40f0*)this)->meth();
}

// FUNCTION: DAO 0x005E6280
void C_1e6280::fn_001e6280() {
    ((U_001dee10*)this)->meth();
    void* obj = (void*)((char*)this + 0x58);
    void** vt = *(void***)obj;
    typedef void (__thiscall *VFn54)(void*, int);
    ((VFn54)vt[0x54 / 4])(obj, 0x410);

    unsigned char local[0x80];
    ((U_0008a970*)local)->meth();
    for (int i = 0; i < 6; ++i) {
        ((U_001de5b0*)this)->meth(i, local);
    }
    ((U_001bdcf0*)((char*)this + 0x57c))->meth();
    ((U_004e2900*)local)->meth();
    ((U_0048a900*)(local + 0x1c))->meth();
    ((U_004c0db0*)local)->meth();
}

// FUNCTION: DAO 0x0064ACE0
void* C_24ace0::fn_0024ace0(void* a1, void* a2, void* a3, void* a4, void* a5, void* a6) {
    void* g = *(void**)g_00c327ec;
    void* field = *(void**)((char*)g + 0xd4);
    void* l1 = 0;
    void* l2 = 0;
    ((U_00a35af0*)field)->meth(&l2, &l1);
    int r = ((U_00a35b90*)field)->meth(a1, a2, a3, a4, a5, a6);
    if (r) return 0;
    if (a1) return ((U_0064a740*)this)->meth(a1, a2, a3, a4, a5, a6);
    return ((U_0064a630*)this)->meth(a1, a2, a3, a4, a5, a6);
}

// FUNCTION: DAO 0x006796E0
void* C_6796e0::fn_002796e0() {
    void** vt = *(void***)this;
    typedef void* (__thiscall *VFn0)(void*);
    return ((VFn0)vt[0])(this);
}

// FUNCTION: DAO 0x0069BAC0
C_29bac0* C_29bac0::fn_0029bac0() {
    ((U_00a59e10*)this)->meth();
    this->v0 = (void*)0x00B0F12CUL;
    this->f20 = 0;
    this->f24 = 0xFFFFFFFFUL;
    this->f28 = 0xFFFFFFFFUL;
    ((U_004c0d90*)((char*)this + 0x2c))->meth();
    this->f48 = 0;
    this->f4c = 0;
    ((U_0069baa0*)this)->meth();
    return this;
}
