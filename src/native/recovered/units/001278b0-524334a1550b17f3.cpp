typedef unsigned char u8;
typedef unsigned int u32;

static float U2F(u32 v) {
  float f = (float)(int)v;
  if ((int)v < 0) f += *(float*)0xAE095C;
  return f;
}

struct CAny {
  int __thiscall fn_004621c0();
  void __thiscall fn_004c2480(const void*);
  void __thiscall fn_004c1750(int, const void*);
  void __thiscall fn_004c0db0();
  void __thiscall fn_004d74a0(void*);
  void __thiscall fn_004d7310();
  void* __thiscall fn_004fe680();
  void* __thiscall fn_004fe7f0();
  void* __thiscall fn_00a53690();
  void __thiscall fn_00457690(int);
  void __thiscall fn_004d7340(int);
  void __thiscall fn_004ebb40(int);
  void* __thiscall fn_004bc0f0();
  void __thiscall fn_004bc540();
  void __thiscall fn_004d7c40();
  void __thiscall fn_004d7dc0();
  bool __thiscall fn_004bbe30();
  void __thiscall fn_005d8f00(int);
};

extern void* __cdecl fn_004fe090(void*, void*);
extern void __cdecl fn_004136c0(void*);
extern void __cdecl fn_004e6160();
extern int __cdecl fn_0041e870();
extern void* __cdecl fn_004bbe00();
extern void __cdecl fn_004c4da0(int);
extern void __cdecl fn_008e11f2();

struct C4D7 {
  void fn_000d7ca0();
  void fn_000d7cd0();
  int fn_000d7d40(int);
  void fn_000d7d60();
  void* fn_000d7e40(u32);
  void* fn_000d7e60(void*);
  void* fn_000d7ea0();
  void* fn_000d7f40(u32);
  void* fn_000d7f80(u32);
};

// FUNCTION: DAO 0x004d7540
void __cdecl fn_000d7540(void* obj, u32 a, u32 b) {
  *(float*)0xC2C044 = U2F(a);
  *(float*)0xC2C040 = U2F(b);
  u8* o = (u8*)obj;
  void** vt = *(void***)o;
  typedef void* (__thiscall *Fn6a)(void*, int,int,int,int,int,int);
  void* r = ((Fn6a)vt[0x54/4])(obj, 0, 0, 1, 3, 0x60, 0);
  *(void**)0xC2C03C = r;
  u8 buf[0x100];
  ((CAny*)(buf + 0x1C))->fn_00457690(0);
  ((CAny*)(buf + 0x1C))->fn_004d7340(1);
  typedef void* (__thiscall *Fn6b)(void*, void*, int, int, int, void*, int);
  void* r2 = ((Fn6b)vt[0x64/4])(obj, buf + 0x2C, 4, 1, 0, buf + 0x48, 0);
  *(void**)0xC2C038 = r2;
  ((CAny*)(buf + 0x2C))->fn_004c2480((const void*)0xAF0F4C);
  void* s = fn_004fe090(buf + 0x14, buf + 0x28);
  void* r3 = ((CAny*)s)->fn_004fe680();
  ((CAny*)0xC2C070)->fn_004d74a0(r3);
  ((CAny*)(buf + 0x10))->fn_004d7310();
  ((CAny*)(buf + 0x28))->fn_004c0db0();
  ((CAny*)(buf + 0x2C))->fn_004c2480((const void*)0xAF0F30);
  s = fn_004fe090(buf + 0x14, buf + 0x28);
  r3 = ((CAny*)s)->fn_004fe680();
  ((CAny*)0xC2C078)->fn_004d74a0(r3);
  ((CAny*)(buf + 0x10))->fn_004d7310();
  ((CAny*)(buf + 0x28))->fn_004c0db0();
  ((CAny*)(buf + 0x2C))->fn_004c2480((const void*)0xAF0F1C);
  s = fn_004fe090(buf + 0x14, buf + 0x28);
  r3 = ((CAny*)s)->fn_004fe7f0();
  ((CAny*)0xC2C080)->fn_004d74a0(r3);
  ((CAny*)(buf + 0x10))->fn_004d7310();
  ((CAny*)(buf + 0x28))->fn_004c0db0();
  int x = ((CAny*)0xC2C070)->fn_004621c0();
  void* edi = ((CAny*)x)->fn_00a53690();
  typedef void* (__thiscall *Fn2)(void*, void*, void*);
  typedef void* (__thiscall *Fn1)(void*, void*);
  ((CAny*)(buf + 0x30))->fn_004c1750(9, (const void*)0xAF0F10);
  void* rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C060 = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(10, (const void*)0xAF0F04);
  rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C064 = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(10, (const void*)0xAF0EF8);
  rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C068 = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(8, (const void*)0xAF0EEC);
  rr = ((Fn2)vt[0x118/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C06C = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  x = ((CAny*)0xC2C078)->fn_004621c0();
  edi = ((CAny*)x)->fn_00a53690();
  ((CAny*)(buf + 0x30))->fn_004c1750(6, (const void*)0xAF0EE4);
  rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C04C = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(7, (const void*)0xAF0EDC);
  rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C050 = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(7, (const void*)0xAF0ED4);
  rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C054 = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(6, (const void*)0xAF0ECC);
  rr = ((Fn2)vt[0x114/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C058 = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(5, (const void*)0xAF0EC4);
  rr = ((Fn2)vt[0x118/4])(obj, edi, buf + 0x28);
  *(void**)0xC2C05C = rr;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
  ((CAny*)(buf + 0x30))->fn_004c1750(0xB, (const void*)0xAF0EB8);
  x = ((CAny*)0xC2C080)->fn_004621c0();
  void* e2 = ((CAny*)x)->fn_00a53690();
  void* rlast = ((Fn1)vt[0x118/4])(obj, e2);
  *(void**)0xC2C048 = rlast;
  if (*(u32*)(buf + 0x40) >= 0x10) fn_004136c0(*(void**)(buf + 0x2C));
}

// FUNCTION: DAO 0x004d7ca0
void __thiscall C4D7::fn_000d7ca0() {
  u8* p = (u8*)this;
  void* edi = p + 0x1C;
  do {
    ((CAny*)this)->fn_004d7c40();
  } while (((CAny*)edi)->fn_004621c0() >= 0);
  p[0x19] = 1;
  p[0x18] = 1;
}

// FUNCTION: DAO 0x004d7cd0
void __thiscall C4D7::fn_000d7cd0() {
  u8* p = (u8*)this;
  void* edi = p + 0x1C;
  do {
    ((CAny*)this)->fn_004d7c40();
  } while (((CAny*)edi)->fn_004621c0() >= 0);
  if (p[0x18] == 0) {
    do {
      fn_004e6160();
    } while (p[0x18] == 0);
  }
  int t0 = fn_0041e870();
  void* q = p + 0x20;
  if (((CAny*)q)->fn_004621c0() <= 0) return;
  for (;;) {
    int t1 = fn_0041e870();
    if ((u32)(t1 - t0) > 1000) return;
    fn_004e6160();
    if (((CAny*)q)->fn_004621c0() <= 0) return;
  }
}

// FUNCTION: DAO 0x004d7d40
int __thiscall C4D7::fn_000d7d40(int arg) {
  ((CAny*)this)->fn_004d7c40();
  u8* p = (u8*)this;
  if (p[0x19] != 0) p[0x18] = 1;
  (void)arg;
  return 3;
}

// FUNCTION: DAO 0x004d7d60
void __thiscall C4D7::fn_000d7d60() {
  if (((CAny*)fn_004bbe00())->fn_004bbe30()) return;
  u8* p = (u8*)this;
  u8* begin = *(u8**)(p + 0x28);
  u8* end = *(u8**)(p + 0x2C);
  int cnt = 0;
  if (begin) cnt = (int)((end - begin) >> 2);
  ((CAny*)(p + 0x1C))->fn_004ebb40(begin ? cnt - 1 : 0);
  ((CAny*)(p + 0x20))->fn_004ebb40(cnt);
}

// FUNCTION: DAO 0x004d7e40
void* __thiscall C4D7::fn_000d7e40(u32 flags) {
  ((CAny*)this)->fn_004d7dc0();
  if (flags & 1) fn_004136c0(this);
  return this;
}

// FUNCTION: DAO 0x004d7e60
void* __thiscall C4D7::fn_000d7e60(void* arg) {
  u8* p = (u8*)this;
  if (((CAny*)(p + 0x1C))->fn_004621c0() < 0) {
    u8* q = (u8*)arg + 0x24;
    void* r = ((CAny*)q)->fn_004bc0f0();
    if (*(void**)r == this) {
      ((CAny*)q)->fn_004bc540();
      p[0x19] = 1;
    }
  }
  return this;
}

// FUNCTION: DAO 0x004d7ea0
void* __thiscall C4D7::fn_000d7ea0() {
  u8* p = (u8*)this;
  fn_004c4da0(0);
  *(void**)p = (void*)0xAF0F70;
  *(void**)(p + 0x1C) = 0;
  *(void**)(p + 0x20) = 0;
  ((CAny*)(p + 0x24))->fn_005d8f00(0);
  ((CAny*)(p + 0x1C))->fn_004ebb40(-1);
  p[0x19] = 1;
  p[0x18] = 1;
  return this;
}

// FUNCTION: DAO 0x004d7f40
void* __thiscall C4D7::fn_000d7f40(u32 idx) {
  u8* p = (u8*)this;
  u8* begin = *(u8**)(p + 4);
  if (begin) {
    u8* end = *(u8**)(p + 8);
    u32 n = (u32)((end - begin) >> 4);
    if (idx < n) return begin + (idx << 4);
  }
  return (void*)0xC2C0A4;
}

// FUNCTION: DAO 0x004d7f80
void* __thiscall C4D7::fn_000d7f80(u32 idx) {
  u8* p = (u8*)this;
  u8* begin = *(u8**)(p + 4);
  if (begin) {
    u8* end = *(u8**)(p + 8);
    u32 n = (u32)((end - begin) >> 2);
    if (idx < n) return begin + (idx << 2);
  }
  return (void*)0xC2C0A0;
}

// FUNCTION: DAO 0x004d7fb0
void __cdecl fn_000d7fb0(void* dest, void* src) {
  if (!dest) return;
  *(void**)dest = *(void**)src;
  void* p = *(void**)((u8*)src + 4);
  if (p) {
    void** vt = *(void***)p;
    typedef void* (__thiscall *Fn)(void*);
    void* r = ((Fn)vt[1])(p);
    *(void**)((u8*)dest + 4) = r;
  } else {
    *(void**)((u8*)dest + 4) = 0;
  }
}

// FUNCTION: DAO 0x005278b0
unsigned int __cdecl fn_001278b0() {
  unsigned int p = *(unsigned int*)0xC31650;
  return *(unsigned int*)(p + 0xB4);
}
