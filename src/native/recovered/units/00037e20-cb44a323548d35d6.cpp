typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed int i32;

typedef void (__thiscall *TCb1)(void*, int);
typedef void (__thiscall *TCb2)(void*, int, int);

extern "C" {
  int fn_008e1e2e(char*, const char*, ...);
  int fn_00420bc0(char*, int);
  void fn_0041ce70(void*, const void*);
  void fn_00421070(void*, int, int, int, int, int);
  int fn_0051af70(const void*, const void*, u32);
  void fn_00420ff0(void*, const void*, const void*);
  void fn_0041cec0(void*, int);
  void fn_00437920(void*, const void*);
  void fn_004379d0(void*, const void*);
  void fn_00437a50(void*, const void*);
  void fn_00437ad0(void*, const void*);
  extern unsigned char g_006e55d8[];
  extern unsigned char g_006e5658[];
  extern unsigned char g_006e8840[];
  extern unsigned char g_006e5504[];
}

static int dao_streq(const char* a, const char* b)
{
  while (*a && *a == *b) { ++a; ++b; }
  return (unsigned char)*a - (unsigned char)*b;
}

struct DAOState {
  void fn_00037c80(void* dest, u32 size);
  void fn_00037e20(TCb2 cb, int a, int b);
  void fn_00037e70(void* a, void* b);
  void fn_00037f20(void* a, void* b, void* c, void* d, void* e, void* f);
  void fn_00038090(TCb1 cb, int a);
  DAOState* fn_00038140(void* arg);
  int fn_00038210(void* a, void* b);
  void* fn_00038280(const char* name);
  void* fn_00038300(const char* name, int a, int b);
  void fn_00038420(void* a, void* b, void* c, void* d);
  void fn_00038470(void* a, void* b, void* c, void* d, void* e);
  void fn_000384c0();
};

// FUNCTION: DAO 0x00437c80
void DAOState::fn_00037c80(void* dest, u32 size)
{
  u8* d = (u8*)dest;
  if (!d || size <= 0x80) return;
  d[0x80] = 0;
  u8* self = (u8*)this;
  u8* p = *(u8**)(self + 0xe0);
  u8* end = *(u8**)(self + 0xe4);
  if (p != end) {
    u8* outer = p;
    while (outer != end) {
      u8* cur = *(u8**)(outer + 0x50);
      u8* limit = *(u8**)(outer + 0x54);
      while (cur != limit) {
        u8* ebx = cur + 0x74;
        if (ebx[0x10] != 0) {
          char buf[0x100];
          fn_008e1e2e(buf, (const char*)g_006e55d8, (void*)(ebx - 0x28), (void*)(ebx - 0x4c), *(void**)ebx);
          u8* dst = d + 0x80;
          while (*dst) ++dst;
          const char* s = buf;
          while ((*dst++ = (u8)*s++) != 0) {}
        }
        cur += 0x88;
      }
      outer += 0x64;
    }
  }
  u8* s2 = d + 0x80;
  u32 len = 0;
  while (s2[len]) ++len;
  fn_00420bc0((char*)s2, (int)len);
  fn_008e1e2e((char*)d, (const char*)g_006e5658, (void*)3, (void*)s2, (void*)len);
}

// FUNCTION: DAO 0x00437e20
void DAOState::fn_00037e20(TCb2 cb, int a, int b)
{
  u8* self = (u8*)this;
  *(u32*)(self + 0x3c) += 1;
  u8** begin = *(u8***)(self + 4);
  u8** end = *(u8***)(self + 8);
  for (u8** it = begin; it != end; ++it) {
    void* obj = *it;
    if (obj) cb(obj, a, b);
  }
  void* extra = *(void**)(self + 0x38);
  if (extra) cb(extra, a, b);
  *(u32*)(self + 0x3c) -= 1;
}

// FUNCTION: DAO 0x00437e70
void DAOState::fn_00037e70(void* a, void* b)
{
  u8* arg1 = (u8*)a;
  u8* arg2 = (u8*)b;
  if (!arg1 || arg1 == arg2) return;
  u8* ebx = *(u8**)arg1;
  if (ebx == arg2) return;
  u8 tmp[0x70];
  fn_00437920(tmp, ebx + 8);
  u8* edi = *(u8**)(ebx + 4);
  u8* esi = ebx;
  while (esi != arg1) {
    u8 tmp2[0x70];
    fn_00437920(tmp2, edi + 8);
    if (*(u32*)(esi + 8) != 0) {
      fn_004379d0(esi + 8, edi + 8);
    }
    esi = *(u8**)(esi + 4);
    edi = *(u8**)(edi + 4);
    if (esi == 0) break;
  }
}

// FUNCTION: DAO 0x00437f20
void DAOState::fn_00037f20(void* a, void* b, void* c, void* d, void* e, void* f)
{
  u8* arg1 = (u8*)a;
  u8* arg2 = (u8*)b;
  if (!arg1 || arg1 == arg2) return;
  u8* edi = arg1;
  u8* ebx = arg2;
  u8* esi = *(u8**)edi;
  if (esi == ebx) return;
  while (esi != ebx) {
    u8 tmp[0x60];
    fn_00437a50(tmp, esi + 8);
    u8* next = *(u8**)(esi + 4);
    if (!next) next = ebx;
    esi = next;
    if (esi == ebx) break;
  }
}

// FUNCTION: DAO 0x00438090
void DAOState::fn_00038090(TCb1 cb, int a)
{
  u8* self = (u8*)this;
  *(u32*)(self + 0x3c) += 1;
  u8** begin = *(u8***)(self + 4);
  u8** end = *(u8***)(self + 8);
  for (u8** it = begin; it != end; ++it) {
    void* obj = *it;
    if (obj) cb(obj, a);
  }
  void* extra = *(void**)(self + 0x38);
  if (extra) cb(extra, a);
  *(u32*)(self + 0x3c) -= 1;
}

// FUNCTION: DAO 0x00438140
DAOState* DAOState::fn_00038140(void* arg)
{
  u8* self = (u8*)this;
  u8* a = (u8*)arg;
  *(u32*)(self + 4) = 0;
  u8* edi = self + 4;
  *(u32*)(edi + 4) = 0;
  *(u32*)(edi + 8) = 0;
  *(u32*)(edi + 0xc) = 0;
  *(u32*)(self + 0x14) = 0;
  u8* ebp = self + 0x18;
  *(u32*)ebp = 0;
  fn_0041ce70(ebp + 4, (const void*)g_006e5504);
  u32 ebx = *(u32*)a;
  fn_00421070(ebp, 0, 4, 0x18, 0x4b0, (int)ebx);
  *(u32*)(ebp + 8) = ebx;
  *(u32*)(ebp + 0x10) = 0x18;
  ebx += 0x4b0;
  *(u32*)(ebp + 0xc) = ebx;
  *(u32*)(self + 8) = (u32)edi;
  *(u32*)edi = (u32)edi;
  *(u32*)(self + 0xc) = 0;
  *(u8*)(self + 0x10) = 0;
  *(u32*)(self + 0x14) = 0;
  return this;
}

// FUNCTION: DAO 0x00438210
int DAOState::fn_00038210(void* a, void* b)
{
  u8* aa = (u8*)a;
  u8* bb = (u8*)b;
  u32 a0 = *(u32*)aa;
  u32 a1 = *(u32*)(aa + 4);
  u32 b0 = *(u32*)bb;
  u32 b1 = *(u32*)(bb + 4);
  int lenA = (int)(a1 - a0);
  int lenB = (int)(b1 - b0);
  int cmpLen = (lenB < lenA) ? lenB : lenA;
  int r = fn_0051af70((const void*)a0, (const void*)b0, (u32)cmpLen);
  if (r != 0) return (r < 0) ? -1 : 1;
  if (lenA < lenB) return -1;
  if (lenA > lenB) return 1;
  return 0;
}

// FUNCTION: DAO 0x00438280
void* DAOState::fn_00038280(const char* name)
{
  if (!name || !*name) return 0;
  u8* self = (u8*)this;
  u8* head = self + 4;
  u8* cur = *(u8**)head;
  while (cur != head) {
    const char* s = (const char*)(cur + 0x10);
    if (dao_streq(name, s) == 0) return cur + 8;
    cur = *(u8**)cur;
  }
  return 0;
}

// FUNCTION: DAO 0x00438300
void* DAOState::fn_00038300(const char* name, int a, int b)
{
  if (!name || !*name) return 0;
  u8* self = (u8*)this;
  u8* head = self + 4;
  u8* cur = *(u8**)head;
  while (cur != head) {
    const char* s = (const char*)(cur + 0x10);
    if (dao_streq(name, s) == 0 && (int)*(u32*)(cur + 0x18) == a && (int)*(u32*)(cur + 0x1c) == b) return cur + 8;
    cur = *(u8**)cur;
  }
  return 0;
}

// FUNCTION: DAO 0x00438420
void DAOState::fn_00038420(void* a, void* b, void* c, void* d)
{
  u8* self = (u8*)this;
  u8* arg2 = (u8*)b;
  u8* arg3 = (u8*)c;
  u8* arg4 = (u8*)d;
  u8 tmp[0x18];
  *(u32*)(tmp + 0) = 0x437b40;
  *(u32*)(tmp + 4) = (u32)arg2;
  *(u32*)(tmp + 8) = (u32)arg3;
  *(u32*)(tmp + 0xc) = 0;
  *(u32*)(tmp + 0x10) = 0;
  *(u32*)(tmp + 0x14) = 0;
  fn_00420ff0(self + 0x33d4, tmp, arg4);
}

// FUNCTION: DAO 0x00438470
void DAOState::fn_00038470(void* a, void* b, void* c, void* d, void* e)
{
  u8* self = (u8*)this;
  u32 tmp[6];
  tmp[0] = 0x437b40;
  tmp[1] = (u32)a;
  tmp[2] = (u32)b;
  tmp[3] = (u32)c;
  tmp[4] = (u32)d;
  tmp[5] = (u32)e;
  u32* vt = *(u32**)self;
  typedef int (__thiscall *Fn)(void*, void*, void*, void*);
  Fn fn = (Fn)vt[2];
  fn(self, tmp, e, d);
}

// FUNCTION: DAO 0x004384c0
void DAOState::fn_000384c0()
{
  u8* self = (u8*)this;
  u8* head = self;
  u8* cur = *(u8**)head;
  while (cur != head) {
    u8* next = *(u8**)cur;
    *(u32*)(cur + 0x24) = (u32)g_006e8840;
    *(u32*)(cur + 0x18) = (u32)g_006e8840;
    fn_0041cec0(cur, 0x78);
    cur = next;
  }
}
