inline unsigned int& U32(void* p, unsigned int off){ return *reinterpret_cast<unsigned int*>(reinterpret_cast<unsigned char*>(p)+off); }
inline int& I32(void* p, unsigned int off){ return *reinterpret_cast<int*>(reinterpret_cast<unsigned char*>(p)+off); }
inline void*& PTR(void* p, unsigned int off){ return *reinterpret_cast<void**>(reinterpret_cast<unsigned char*>(p)+off); }
extern void __cdecl fn_004e11f2(...);
extern void __cdecl fn_000c0db0(...);
extern void __cdecl fn_00006880(...);
extern void __cdecl fn_000136c0(...);
extern void __cdecl fn_000e7d30(...);
extern void __cdecl fn_000dfb50(...);
extern void __cdecl fn_0028f180(...);
extern void __cdecl fn_004779c0(...);
extern void __cdecl fn_0044c9f0(...);
extern void __cdecl fn_000e04d0(...);
extern void __cdecl fn_00003990(...);
extern void __cdecl fn_000e13e0(...);
extern void __cdecl fn_000e4a50(...);
extern void __cdecl fn_00641f80(...);
extern void __cdecl fn_001389f0(...);
extern void __cdecl fn_000df670(...);
struct C_00491200 { void __thiscall fn_00491200(void* result, const int* key); };
struct C_000df9d0 { void* __thiscall fn_000df9d0(int key); };
struct C_000dfae0 { void __thiscall fn_000dfae0(); };
struct C_000e0050 { void __thiscall fn_000e0050(void* out, const int* key); };
struct C_000e07b0 { void __thiscall fn_000e07b0(void* arg); };
struct C_000e1bc0 { void* __thiscall fn_000e1bc0(int flags); };
struct C_001671e0 { void* __thiscall fn_001671e0(); };
struct C_001caa60 { int __thiscall fn_001caa60(const int* key); };
struct C_00297bf0 { void __thiscall fn_00297bf0(); };
// FUNCTION: DAO 0x4DF9D0
void* __thiscall C_000df9d0::fn_000df9d0(int key) {
    if (U32(this,0xc) == 0) return reinterpret_cast<unsigned char*>(this)+0x2c;
    unsigned char local[8];
    reinterpret_cast<C_00491200*>(this)->fn_00491200(local, &key);
    void* edi = PTR(local,0);
    void* ebx = PTR(this,8);
    void* eax = reinterpret_cast<unsigned char*>(this)+4;
    if (edi != 0 && edi != eax) fn_004e11f2();
    void* ebp = PTR(local,4);
    if (ebp == ebx) return reinterpret_cast<unsigned char*>(this)+0x2c;
    if (edi == 0) fn_004e11f2();
    if (ebp != PTR(edi,4)) fn_004e11f2();
    return reinterpret_cast<unsigned char*>(ebp)+0xc;
}
// FUNCTION: DAO 0x4DFAE0
void __thiscall C_000dfae0::fn_000dfae0() {
    fn_000c0db0(reinterpret_cast<unsigned char*>(this)+0xc);
    fn_00006880(this);
    void* p = PTR(this,4);
    fn_000136c0(p);
    PTR(this,4) = 0;
}
// FUNCTION: DAO 0x4E0050
void __thiscall C_000e0050::fn_000e0050(void* out, const int* key) {
    unsigned int a = U32(this,0xc) >> 2;
    unsigned int b = U32(this,0x24);
    if (b > a) return;
    void* vec = PTR(this,0x14);
    void* header = reinterpret_cast<unsigned char*>(this)+4;
    fn_000e7d30(this, header, key);
    fn_000dfb50(this, 0);
    fn_0028f180(this, key);
    *(void**)out = 0;
    *((void**)out+1) = 0;
    *((unsigned char*)out+8) = 0;
    (void)vec;
}
// FUNCTION: DAO 0x4E07B0
void __thiscall C_000e07b0::fn_000e07b0(void* arg) {
    unsigned char local1[16];
    unsigned char local2[16];
    fn_004779c0(this, local1, arg);
    fn_0044c9f0(this, arg, local1, local2);
    fn_000e04d0(this, local2, arg, arg);
}
// FUNCTION: DAO 0x4E1BC0
void* __thiscall C_000e1bc0::fn_000e1bc0(int flags) {
    U32(this,0) = 0xaf1048;
    fn_00003990();
    fn_000e13e0(this);
    if (flags & 1) fn_000136c0(this);
    return this;
}
// FUNCTION: DAO 0x4E4C90
void __cdecl fn_000e4c90() { fn_000e4a50(); }
// FUNCTION: DAO 0x5671E0
void* __thiscall C_001671e0::fn_001671e0() {
    if (U32(this,8) == 0) return PTR(this,0xc);
    void* p = PTR(this,4);
    void* edi = PTR(p,0);
    if (edi != p) fn_004e11f2();
    void* eax = PTR(PTR(this,4),0);
    edi = PTR(edi,8);
    unsigned char local[8];
    fn_00641f80(this, local, this, eax);
    return edi;
}
// FUNCTION: DAO 0x5CAA60
int __thiscall C_001caa60::fn_001caa60(const int* key) {
    if (U32(this,0xc) == 0) return 0;
    unsigned char local[8];
    reinterpret_cast<C_00491200*>(this)->fn_00491200(local, key);
    void* eax = PTR(local,0);
    void* esi = reinterpret_cast<unsigned char*>(this)+4;
    if (eax != 0 && eax != esi) fn_004e11f2();
    if (PTR(local,4) == PTR(this,8)) return 0;
    return 1;
}
// FUNCTION: DAO 0x697BF0
void __thiscall C_00297bf0::fn_00297bf0() {
    unsigned char local[12];
    fn_001389f0(local);
    fn_000df670(this, local);
}
// FUNCTION: DAO 0x891200
void __thiscall C_00491200::fn_00491200(void* result, const int* key) {
    unsigned int mask = U32(this,0x20);
    unsigned int h = mask & (unsigned int)*key;
    unsigned int cnt = U32(this,0x24);
    if (h >= cnt) {
        unsigned int half = mask >> 1;
        int adj = -1 - (int)half;
        h = (unsigned int)((int)h + adj);
    }
    void* vec = PTR(this,0x14);
    void* node = 0;
    if (vec != 0) node = PTR(vec, h*8+4);
    void* header = reinterpret_cast<unsigned char*>(this)+4;
    void* end = PTR(header,4);
    if (node == 0) node = end;
    while (node != end) {
        int nk = I32(node,8);
        if (nk < *key) {
            node = PTR(node,0);
        } else {
            end = node;
            node = PTR(node,0);
        }
        if (node == 0) break;
    }
    PTR(result,0) = node;
    PTR(result,4) = header;
}
