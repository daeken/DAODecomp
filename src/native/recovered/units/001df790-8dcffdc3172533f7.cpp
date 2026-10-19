struct Pair { void* first; void* second; };
struct C000C4E40 { void* vptr; void* cont; void __thiscall fn_000c4e40(); };
struct C001DF790 { void* vptr; void* begin; void* end; void* cap; void __thiscall fn_001df790(); };
struct C00368F20 { void* vptr; void* begin; void* end; void* cap; void __thiscall fn_00368f20(); };
struct C001DFB00 { void* vptr; void* begin; void* end; void* cap; void __thiscall fn_001dfb00(void*, void*, void*, void*, void*); };
struct C001E0A40 { void* vptr; void* begin; void* end; void* cap; Pair __thiscall fn_001e0a40(void*, void*, void*); };
struct C001E1280 { void* vptr; void* begin; void* end; void* cap; Pair __thiscall fn_001e1280(void*, void*, void*); };

void __cdecl fn_001de000(void*, void*, void*, void*);
void __cdecl fn_001de080(void*, int, unsigned, void*, void*, void*);
void* __cdecl fn_001df980(void*, void*, void*);
void __fastcall fn_000e96e0(void*, int, void*);
void __fastcall fn_0006c760(void*, int);
void __cdecl fn_000136c0(void*);
void __fastcall fn_004af570(void*, int, void*);
void __fastcall fn_0048d190(void*, int, void*);
void __cdecl fn_004e11f2();
void __fastcall fn_001e0290(void*, int, void*, void*, int, void*);
void __fastcall fn_001e0af0(void*, int, void*, void*, int, void*);
void __cdecl fn_004ea784(void*, int);
extern unsigned int g_00c3eee0;

typedef bool (__cdecl *Pred)(void*, void*);

// FUNCTION: DAO 0x4C4E40
void __thiscall C000C4E40::fn_000c4e40() {
  this->vptr = (void*)0xaddccc;
  if (this->cont) {
    void** c = (void**)this->cont;
    void* p = c[1];
    void* e = c[2];
    unsigned n = (unsigned)(((char*)e - (char*)p) >> 2);
    for (unsigned i = 0; i < n; ++i) {
      void* item = ((void**)p)[i];
      fn_000e96e0(item, 0, this);
    }
    fn_0006c760(this->cont, 0);
    fn_000136c0(this->cont);
    this->cont = 0;
  }
  this->vptr = (void*)0xaddcb8;
}

// FUNCTION: DAO 0x5DE960
void __cdecl fn_001de960(void* first, void* unused, void* last, void* pred) {
  int n = (int)(((char*)last - (char*)first) >> 3);
  if (n > 0x28) {
    void* mid = (char*)first + (((unsigned)(n + 1) / 2) * 8);
    fn_001de000(first, mid, last, pred);
    fn_001de000(first, mid, (char*)last - 8, pred);
    fn_001de000(mid, (char*)mid + 8, last, pred);
    fn_001de000(first, first, last, pred);
  } else {
    fn_001de000(first, unused, last, pred);
  }
}

// FUNCTION: DAO 0x5DF180
void __cdecl fn_001df180(void* first, unsigned count, void* arg) {
  while (count) {
    if (first) fn_004af570(first, 0, arg);
    --count;
    first = (char*)first + 0x10;
  }
}

// FUNCTION: DAO 0x5DF1B0
void __cdecl fn_001df1b0(void* first, unsigned count, void* arg) {
  while (count) {
    if (first) fn_0048d190(first, 0, arg);
    --count;
    first = (char*)first + 0x28;
  }
}

// FUNCTION: DAO 0x5DF2B0
void __cdecl fn_001df2b0(void* unused, void* first, void* last, Pred pred) {
  unsigned n = (unsigned)(((char*)last - (char*)first) >> 3);
  if (n < 2) return;
  void* mid = (char*)first + (n / 2) * 8;
  fn_001de960(first, mid, (char*)last - 8, pred);
  fn_001de000(first, mid, last, pred);
}

// FUNCTION: DAO 0x5DF790
void __thiscall C001DF790::fn_001df790() {
  if (this->begin) {
    void* p = this->begin;
    void* e = this->end;
    while (p != e) {
      void** vtbl = *(void***)p;
      ((void (__thiscall*)(void*, int))vtbl[1])(p, 0);
      p = (char*)p + 0x28;
    }
    fn_000136c0(this->begin);
  }
  this->begin = 0;
  this->end = 0;
  this->cap = 0;
}

// FUNCTION: DAO 0x5DF880
void __cdecl fn_001df880(void* first, void* last, Pred pred) {
  unsigned n = (unsigned)(((char*)last - (char*)first) >> 3);
  while (n > 1) {
    unsigned* p = (unsigned*)((char*)last - 8);
    fn_001de080(first, 0, n - 1, (void*)p[0], (void*)p[1], pred);
    last = (char*)last - 8;
    n = (unsigned)(((char*)last - (char*)first) >> 3);
  }
}

// FUNCTION: DAO 0x5DFB00
void __thiscall C001DFB00::fn_001dfb00(void* unused, void* pos, void* first, void* last, void* extra) {
  if (pos && pos != last) fn_004e11f2();
  if (first != extra) {
    void* res = fn_001df980(extra, this->end, first);
    void* oldEnd = this->end;
    for (void* p = res; p != oldEnd; p = (char*)p + 0x28) {
      void** vtbl = *(void***)p;
      ((void (__thiscall*)(void*, int))vtbl[1])(p, 0);
    }
    this->end = res;
  }
}

// FUNCTION: DAO 0x5E0A40
Pair __thiscall C001E0A40::fn_001e0a40(void* pos, void* first, void* last) {
  if (this->begin) {
    unsigned n = (unsigned)(((char*)this->end - (char*)this->begin) / 40);
    if (n == 0) fn_004e11f2();
    if ((char*)this->begin > (char*)this->end) fn_004e11f2();
  }
  if (first && first == (void*)this) fn_004e11f2();
  unsigned idx = (unsigned)(((char*)first - (char*)this->begin) / 40);
  fn_001e0290(this, 0, first, pos, 1, last);
  void* newEnd = (char*)this->begin + idx * 40;
  Pair r;
  r.first = this;
  r.second = newEnd;
  return r;
}

// FUNCTION: DAO 0x5E1280
Pair __thiscall C001E1280::fn_001e1280(void* pos, void* first, void* last) {
  if (this->begin) {
    unsigned n = (unsigned)(((char*)this->end - (char*)this->begin) >> 4);
    if (n == 0) fn_004e11f2();
  }
  if (first && first == (void*)this) fn_004e11f2();
  unsigned idx = (unsigned)(((char*)first - (char*)this->begin) >> 4);
  fn_001e0af0(this, 0, pos, first, 1, last);
  void* newEnd = (char*)this->begin + idx * 16;
  Pair r;
  r.first = this;
  r.second = newEnd;
  return r;
}

// FUNCTION: DAO 0x768F20
void __thiscall C00368F20::fn_00368f20() {
  if (this->begin) {
    void* p = this->begin;
    void* e = this->end;
    while (p != e) {
      void** vtbl = *(void***)p;
      ((void (__thiscall*)(void*, int))vtbl[1])(p, 0);
      p = (char*)p + 0x10;
    }
    fn_000136c0(this->begin);
  }
  this->begin = 0;
  this->end = 0;
  this->cap = 0;
}

// FUNCTION: DAO 0x8EA89C
int __cdecl fn_004ea89c(int c) {
  if (g_00c3eee0 == 0) {
    unsigned x = (unsigned)c;
    if ((unsigned)(x - 0x61) <= 0x19) return (int)(x - 0x20);
    return (int)x;
  }
  fn_004ea784((void*)c, 0);
  return c;
}
