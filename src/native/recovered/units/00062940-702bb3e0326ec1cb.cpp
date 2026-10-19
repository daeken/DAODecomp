typedef unsigned int u32;
typedef unsigned char u8;

struct CUnresolved {
    void fn_005d2480(void** a, void** b);
    void fn_004a62e0(u32 index);
    void fn_0049d170(void* p);
    int fn_004621c0();
};

struct C4628a0 { void fn_000628a0(int value, u8 flag); };
struct C462920 { void fn_00062920(); };
struct C462970 { void fn_00062970(); };
struct C4629c0 { void fn_000629c0(void* p, u8 flag); };
struct C4629e0 { void* fn_000629e0(void* other); };
struct C462a10 { void* fn_00062a10(void* other); };
struct C462cc0 { void* fn_00062cc0(void* p); };
struct C462ce0 { void* fn_00062ce0(void* p); };

extern "C" void __cdecl fn_004136c0(void*);
extern "C" bool __cdecl fn_00461eb0(void* a, void* b);

// FUNCTION: DAO 0x004628a0
void C4628a0::fn_000628a0(int value, u8 flag) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    void* begin = 0;
    void* end = 0;
    CUnresolved* sub = reinterpret_cast<CUnresolved*>(self + 4);
    sub->fn_005d2480(&begin, &end);
    if ((u32)begin < (u32)end) {
        unsigned char* p = reinterpret_cast<unsigned char*>(begin);
        unsigned char* e = reinterpret_cast<unsigned char*>(end);
        while (*reinterpret_cast<u32*>(p) != (u32)value) {
            p += 4;
            if ((u32)p >= (u32)e) { p = 0; break; }
        }
        if (p != 0) {
            u32 index = (u32)((p - reinterpret_cast<unsigned char*>(begin)) >> 2);
            sub->fn_004a62e0(index);
        }
    }
    u32* ref = reinterpret_cast<u32*>(self + 0x14);
    if (*ref != 0) {
        if (flag == 0) {
            --(*ref);
        }
        if (*ref == 0) {
            typedef void (__thiscall *VFn)(void*, int);
            void* vtable = *reinterpret_cast<void**>(self);
            VFn fn = *reinterpret_cast<VFn*>(vtable);
            fn(self, 1);
        }
    }
}

// FUNCTION: DAO 0x00462920
void C462920::fn_00062920() {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    void* p = *reinterpret_cast<void**>(self);
    if (p != 0) {
        u8 flag = *reinterpret_cast<u8*>(self + 4);
        reinterpret_cast<C4628a0*>(p)->fn_000628a0((int)(u32)self, flag);
        *reinterpret_cast<void**>(self) = 0;
    }
}

// FUNCTION: DAO 0x00462940
void __stdcall fn_00062940(void* first, void* last) {
    unsigned char* p = reinterpret_cast<unsigned char*>(first);
    unsigned char* e = reinterpret_cast<unsigned char*>(last);
    while (p != e) {
        reinterpret_cast<C462920*>(p)->fn_00062920();
        p += 8;
    }
}

// FUNCTION: DAO 0x00462970
void C462970::fn_00062970() {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    void* first = *reinterpret_cast<void**>(self + 4);
    if (first != 0) {
        unsigned char* p = reinterpret_cast<unsigned char*>(first);
        unsigned char* e = *reinterpret_cast<unsigned char**>(self + 8);
        while (p != e) {
            reinterpret_cast<C462920*>(p)->fn_00062920();
            p += 8;
        }
        fn_004136c0(first);
    }
    *reinterpret_cast<void**>(self + 4) = 0;
    *reinterpret_cast<void**>(self + 8) = 0;
    *reinterpret_cast<void**>(self + 0xc) = 0;
}

// FUNCTION: DAO 0x004629c0
void C4629c0::fn_000629c0(void* p, u8 flag) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    CUnresolved* sub = reinterpret_cast<CUnresolved*>(self + 4);
    sub->fn_0049d170(&p);
    if (flag == 0) {
        ++(*reinterpret_cast<u32*>(self + 0x14));
    }
}

// FUNCTION: DAO 0x004629e0
void* C4629e0::fn_000629e0(void* other) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    unsigned char* o = reinterpret_cast<unsigned char*>(other);
    if (self != o) {
        *reinterpret_cast<u8*>(self + 4) = *reinterpret_cast<u8*>(o + 4);
        void* p = *reinterpret_cast<void**>(o);
        *reinterpret_cast<void**>(self) = p;
        if (p != 0) {
            reinterpret_cast<C4629c0*>(p)->fn_000629c0(self, *reinterpret_cast<u8*>(self + 4));
        }
    }
    return self;
}

// FUNCTION: DAO 0x00462a10
void* C462a10::fn_00062a10(void* other) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    unsigned char* o = reinterpret_cast<unsigned char*>(other);
    if (self != o) {
        void* old = *reinterpret_cast<void**>(self);
        if (old != 0) {
            reinterpret_cast<C4628a0*>(old)->fn_000628a0((int)(u32)self, *reinterpret_cast<u8*>(self + 4));
        }
        *reinterpret_cast<u8*>(self + 4) = *reinterpret_cast<u8*>(o + 4);
        void* p = *reinterpret_cast<void**>(o);
        *reinterpret_cast<void**>(self) = p;
        if (p != 0) {
            reinterpret_cast<C4629c0*>(p)->fn_000629c0(self, *reinterpret_cast<u8*>(self + 4));
        }
    }
    return self;
}

// FUNCTION: DAO 0x00462a50
void __cdecl fn_00062a50(void* a, void* b) {
    unsigned char local[8] = {0};
    reinterpret_cast<C4629e0*>(local)->fn_000629e0(a);
    reinterpret_cast<C462a10*>(a)->fn_00062a10(b);
    reinterpret_cast<C462a10*>(b)->fn_00062a10(local);
    reinterpret_cast<C462920*>(local)->fn_00062920();
}

// FUNCTION: DAO 0x00462ad0
void __cdecl fn_00062ad0(void* base, int count, int index, void* comp) {
    unsigned char* basep = reinterpret_cast<unsigned char*>(base);
    int esi = (count - 1) / 2;
    if (index < count) {
        int key = reinterpret_cast<CUnresolved*>(comp)->fn_004621c0();
        unsigned char* item = basep + (u32)esi * 8;
        int itemVal = reinterpret_cast<CUnresolved*>(item)->fn_004621c0();
        bool less = fn_00461eb0((void*)(u32)key, (void*)(u32)itemVal);
        if (less) {
            unsigned char* hole = basep + (u32)index * 8;
            reinterpret_cast<C462a10*>(hole)->fn_00062a10(item);
            while (index < count) {
                int parent = (index - 1) / 2;
                if (index >= count) break;
                reinterpret_cast<C462a10*>(basep + (u32)index * 8)->fn_00062a10(basep + (u32)count * 8);
                index = parent;
            }
        }
    }
    unsigned char temp[8] = {0};
    reinterpret_cast<C462920*>(temp)->fn_00062920();
}

// FUNCTION: DAO 0x00462ba0
void __cdecl fn_00062ba0(void* first, void* middle, void* last) {
    unsigned char* firstp = reinterpret_cast<unsigned char*>(first);
    unsigned char* middlep = reinterpret_cast<unsigned char*>(middle);
    unsigned char* lastp = reinterpret_cast<unsigned char*>(last);
    int n = (int)((lastp - firstp) / 8);
    int m = (int)((middlep - firstp) / 8);
    if (m > 0 && m < n) {
        unsigned char temp[8] = {0};
        reinterpret_cast<C4629e0*>(temp)->fn_000629e0(firstp + (u32)m * 8);
        int i = m;
        while (i < n) {
            reinterpret_cast<C462a10*>(firstp + (u32)i * 8)->fn_00062a10(firstp + (u32)(i - m) * 8);
            i += m;
            if (i >= n) i -= n;
        }
        reinterpret_cast<C462920*>(temp)->fn_00062920();
    }
}

// FUNCTION: DAO 0x00462cc0
void* C462cc0::fn_00062cc0(void* p) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    *reinterpret_cast<void**>(self) = p;
    *reinterpret_cast<u8*>(self + 4) = 0;
    if (p != 0) {
        reinterpret_cast<C4629c0*>(p)->fn_000629c0(self, 0);
    }
    return self;
}

// FUNCTION: DAO 0x00462ce0
void* C462ce0::fn_00062ce0(void* p) {
    unsigned char* self = reinterpret_cast<unsigned char*>(this);
    void* old = *reinterpret_cast<void**>(self);
    if (old != 0) {
        reinterpret_cast<C4628a0*>(old)->fn_000628a0((int)(u32)self, *reinterpret_cast<u8*>(self + 4));
    }
    *reinterpret_cast<void**>(self) = p;
    *reinterpret_cast<u8*>(self + 4) = 0;
    if (p != 0) {
        reinterpret_cast<C4629c0*>(p)->fn_000629c0(self, 0);
    }
    return self;
}
