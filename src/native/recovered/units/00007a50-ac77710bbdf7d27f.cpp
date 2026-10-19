typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

extern int __cdecl fn_004DFEF4(void*, int, void*, void*);
extern void __cdecl fn_004E11F2(void);
extern void __cdecl fn_004E1A5A(void*);
extern void __cdecl fn_000136C0(void*);
extern int __cdecl fn_004E1202(const void*, ...);
extern void __cdecl fn_00001A60(void*, const void*);
extern void __cdecl fn_00006D50(void*, void*);
extern void* __cdecl fn_00013660(u32);
extern void* __cdecl fn_004E023B(void);
extern void* __cdecl fn_004E006F(void);
extern void __cdecl fn_004DFFE1(void*, int);
extern void __cdecl fn_004E0002(void*);
extern void __cdecl fn_00018F90(void*);
extern void __cdecl fn_00019D50(void*, void*);
extern void __cdecl fn_00006A20(void*, void*);
extern void __cdecl fn_00002980(void*);
extern void __cdecl fn_00006F60(void*, void*, void*, void*);
extern int __cdecl fn_00007A90(void*);
extern void __cdecl fn_004E0FC0(void*, const void*);
extern void __cdecl fn_00003540(void*);
extern void __cdecl fn_004E013D(void*);
extern void* __cdecl fn_004EB47B(void);
extern void* __cdecl fn_004EB455(void);
extern int __cdecl fn_004E0563(const char*);
extern int __cdecl fn_004EB43F(const char*);
extern void* __cdecl fn_004EB058(void);
extern int* __cdecl fn_004E37B6(void);
extern int (__stdcall *g_ADA0D8)(u32, u32, const char*, int, u16*, int);
extern void* g_C1D1F4;
extern u32 g_C3ECF4;
extern u32 g_C3ECE8;
extern int __cdecl fn_004e0646(u16*, char*, u32, void*, void*);

struct C_Convert {
    char pad0[0x18];
    void* cvt;
    u16 fn_00007840(u8 c);
    char* fn_000078c0(char* first, char* last, u16* dest, u32 cap);
    u8 fn_00007940(int a, u8 b);
    u16* fn_000079c0(u16* first, u16* last, u8 def, char* dest, u32 cap);
};

// FUNCTION: DAO 0x00407840
u16 C_Convert::fn_00007840(u8 c) {
    u16 w = 0;
    u32 st = 0;
    int r = fn_004e0646(&w, (char*)&c, 1, &st, this->cvt);
    if (r < 0) return (u16)0xffff;
    return w;
}

// FUNCTION: DAO 0x004078c0
char* C_Convert::fn_000078c0(char* first, char* last, u16* dest, u32 cap) {
    u32 n = (u32)(last - first);
    if (cap < n) fn_004E11F2();
    char* p = first;
    u16* d = dest;
    while (p != last) {
        u8 c = (u8)*p;
        u16 w = 0;
        u32 st = 0;
        int r = fn_004e0646(&w, (char*)&c, 1, &st, this->cvt);
        if (r < 0) w = (u16)0xffff;
        *d = w;
        ++p;
        ++d;
    }
    return p;
}

// FUNCTION: DAO 0x00407940
u8 C_Convert::fn_00007940(int a, u8 b) {
    u8 local1 = 0;
    u8 local2 = 0;
    int r = fn_004DFEF4(&local2, a, &local1, this->cvt);
    if (r == 1) return local2;
    return b;
}

// FUNCTION: DAO 0x004079c0
u16* C_Convert::fn_000079c0(u16* first, u16* last, u8 def, char* dest, u32 cap) {
    u32 n = (u32)(last - first);
    if (cap < n) fn_004E11F2();
    u16* p = first;
    char* d = dest;
    while (p != last) {
        u16 ch = *p;
        u8 local1 = 0;
        u8 local2 = 0;
        int r = fn_004DFEF4(&local2, (int)ch, &local1, this->cvt);
        u8 out = (r == 1) ? local1 : def;
        *d = (char)out;
        ++p;
        ++d;
    }
    return p;
}

struct C_407A50 {
    void* vt;
    char pad[0xc];
    void* p10;
    u32 f14;
    void* fn_00007a50(u32 flags);
};

// FUNCTION: DAO 0x00407a50
void* C_407A50::fn_00007a50(u32 flags) {
    this->vt = (void*)0xADED7C;
    if (this->f14 != 0) fn_004E1A5A(this->p10);
    this->vt = (void*)0xADE540;
    if ((flags & 1) != 0) fn_000136C0(this);
    return this;
}

struct C_407B00 {
    char pad[8];
    u32 mask8;
    u32 flagsC;
    void fn_00007b00(u32 a, u8 b);
};

// FUNCTION: DAO 0x00407b00
void C_407B00::fn_00007b00(u32 a, u8 b) {
    u32 m = a & 0x17;
    this->mask8 = m;
    u32 f = this->flagsC & m;
    if (f == 0) return;
    if (b != 0) fn_004E1202((const void*)0, 0, 0);
    if ((f & 4) != 0) {
        char b1[0x40];
        fn_00001A60(b1, (const void*)0xADEDEC);
        fn_00006D50(b1, b1);
        fn_004E1202((const void*)0xB93ADC, b1, 0);
    }
    if ((f & 2) != 0) {
        char b2[0x40];
        fn_00001A60(b2, (const void*)0xADEDD4);
        fn_00006D50(b2, b2);
        fn_004E1202((const void*)0xB93ADC, b2, 0);
    }
    {
        char b3[0x40];
        fn_00001A60(b3, (const void*)0xADEDBC);
        fn_00006D50(b3, b3);
        fn_004E1202((const void*)0xB93ADC, b3, 0);
    }
}

struct C_407C50 {
    char pad[0xc];
    u32 f0c;
    u32 f10;
    u32 f14;
    void* f18;
    void* f1c;
    void* f20;
    void* f24;
    void fn_00007c50();
};

// FUNCTION: DAO 0x00407c50
void C_407C50::fn_00007c50() {
    this->f24 = 0;
    this->f0c = 0;
    this->f10 = 0x201;
    this->f14 = 6;
    this->f18 = 0;
    this->f1c = 0;
    this->f20 = 0;
    ((C_407B00*)this)->fn_00007b00(0, 0);
    void* p = fn_00013660(4);
    if (p != 0) {
        *(void**)p = fn_004E023B();
        void* q = fn_004E006F();
        u32 dummy = 0;
        fn_004DFFE1(&dummy, 0);
        if (q != 0) {
            u32* counter = (u32*)((char*)q + 4);
            if (*counter < 0xffffffffu) ++(*counter);
        }
        fn_004E0002(&dummy);
        this->f24 = p;
    }
}

struct C_407CD0 {
    void* vt;
    char pad[0xc];
    void* p10;
    void fn_00007cd0(void* arg);
    void fn_00007d90(void* arg);
};

// FUNCTION: DAO 0x00407cd0
void C_407CD0::fn_00007cd0(void* arg) {
    fn_00018F90(this);
    this->vt = (void*)0xADE2F8;
    fn_00019D50(&this->p10, arg);
    this->vt = (void*)0xADEE08;
}

// FUNCTION: DAO 0x00407d90
void C_407CD0::fn_00007d90(void* arg) {
    fn_00018F90(this);
    this->vt = (void*)0xADE2F8;
    void* p = 0;
    if (arg != 0) p = (void*)((char*)arg + 0x10);
    fn_00019D50(&this->p10, p);
    this->vt = (void*)0xADEE08;
}

struct Node {
    Node* next;
    Node* prev;
    Node* extra;
};

struct C_408040 {
    void* pad0;
    Node* head4;
    void fn_00008040(void** out, Node* a, Node* b, Node* c, Node* d);
};

// FUNCTION: DAO 0x00408040
void C_408040::fn_00008040(void** out, Node* a, Node* b, Node* c, Node* d) {
    Node* sentinel = this->head4;
    Node* first = sentinel->next;
    if (a != 0) {
        if (a != (Node*)this) fn_004E11F2();
    }
    if (b != first) {
        if (a != 0) {
            if (a != c) fn_004E11F2();
        }
        if (b != d) {
            u32 local = 0;
            fn_00002980(&local);
            fn_00006F60(this, &local, a, b);
        }
        out[0] = a;
        out[1] = b;
        return;
    }
    if (c != 0) {
        if (c != (Node*)this) fn_004E11F2();
    }
    if (d != sentinel) {
        if (a != 0) {
            if (a != c) fn_004E11F2();
        }
        if (b != d) {
            u32 local = 0;
            fn_00002980(&local);
            fn_00006F60(this, &local, a, b);
        }
        out[0] = a;
        out[1] = b;
        return;
    }
    fn_00006A20(this, sentinel->prev);
    sentinel->prev = sentinel;
    *(u32*)((char*)this + 8) = 0;
    sentinel->next = sentinel;
    sentinel->extra = sentinel;
    out[0] = (void*)this;
    out[1] = sentinel->next;
}

// FUNCTION: DAO 0x00408110
void* __cdecl fn_00008110(void* param) {
    u32 dummy1 = 0;
    u32 dummy2 = 0;
    if (g_C3ECF4 == 0) {
        fn_004DFFE1(&dummy1, 0);
        if (g_C3ECF4 == 0) {
            g_C3ECE8 = g_C3ECE8 + 1;
            g_C3ECF4 = g_C3ECE8;
        }
        fn_004E0002(&dummy2);
    }
    void* result = 0;
    if (param != 0) {
        void* eax = *(void**)param;
        u32 idx = g_C3ECF4;
        if (eax != 0) {
            if (idx < *(u32*)((char*)eax + 0xc)) {
                result = *(void**)(*(char**)((char*)eax + 8) + idx * 4);
            } else {
                result = g_C1D1F4;
            }
        } else {
            result = g_C1D1F4;
        }
    }
    if (result == 0) {
        u32 local = 0;
        int r = fn_00007A90(&local);
        if (r == -1) {
            char buf[0x40];
            fn_004E0FC0(buf, (const void*)0xADEE14);
            fn_004E1202((const void*)0xB93BBC, buf, 0);
        }
        result = (void*)local;
    }
    g_C1D1F4 = result;
    fn_00003540(result);
    fn_004E013D(result);
    return result;
}

// FUNCTION: DAO 0x008E0646
int __cdecl fn_004e0646(u16* out, char* in, u32 count, void* state, void* cvt) {
    if (in == 0 || count == 0) return 0;
    if (*in == 0) {
        if (out != 0) *out = 0;
        return 0;
    }
    void* c = cvt;
    if (c == 0) {
        void* a = fn_004EB47B();
        void* b = (a != 0) ? *(void**)((char*)a + 8) : 0;
        void* d = fn_004EB455();
        c = (d != 0) ? d : b;
    }
    int len = fn_004E0563(in);
    if (state != 0 && *(u32*)state != 0) {
        int r = fn_004EB43F(in);
        if (r > 1) {
            int conv = g_ADA0D8(*(u32*)c, 9, in, r, out, 1);
            if (conv != 0) {
                *(u32*)state = 0;
                return 0;
            }
        }
    }
    if (c == 0) {
        fn_004EB058();
        if (out != 0) *out = (u16)(u8)*in;
        return 1;
    }
    int r0 = g_ADA0D8(*(u32*)c, 9, in, len, out, 1);
    if (r0 != 0) return 1;
    int r1 = fn_004EB43F(in);
    if (r1 > 1) {
        int conv = g_ADA0D8(*(u32*)c, 9, in, r1, out, 1);
        if (conv != 0) return 1;
    }
    int* perr = fn_004E37B6();
    if (perr != 0) *perr = 0x2a;
    return -1;
}
