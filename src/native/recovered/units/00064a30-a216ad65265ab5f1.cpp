typedef unsigned int u32;
typedef unsigned char u8;
extern "C" unsigned char g_00671858[];
extern "C" unsigned char g_00815234[];
extern "C" int fn_00413660(int, ...);
extern "C" int fn_004136c0(int, ...);
extern "C" int fn_004621c0(int, ...);
extern "C" int fn_00462920(int, ...);
extern "C" int fn_00462940(int, ...);
extern "C" int fn_004629e0(int, ...);
extern "C" int fn_00462a10(int, ...);
extern "C" int fn_00462cc0(int, ...);
extern "C" int fn_00462d20(int, ...);
extern "C" int fn_00462ee0(int, ...);
extern "C" int fn_004630e0(int, ...);
extern "C" int fn_00463280(int, ...);
extern "C" int fn_004633c0(int, ...);
extern "C" int fn_00463430(int, ...);
extern "C" int fn_004637d0(int, ...);
extern "C" int fn_00463870(int, ...);
extern "C" int fn_00463e40(int, ...);
extern "C" int fn_0086bce0(int, ...);
extern "C" int fn_00871e20(int, ...);
extern "C" int fn_008e11f2(int, ...);

struct Vec8 {
  u32 field0;
  u8* begin;
  u8* end;
  u8* cap;
  u32 size8() const { return begin ? (u32)((end - begin) >> 3) : 0; }
  u32 cap8() const { return begin ? (u32)((cap - begin) >> 3) : 0; }
  int __thiscall fn_000638a0(u32 a, u32 b, u32 c, u32 d);
  int __thiscall fn_00063c30(u32 n);
  int __thiscall fn_00063d20(u32 a, u32 b, u32 c, u32 d);
  int __thiscall fn_00063db0(u32 v);
  int __thiscall fn_00064200(u32 flags, u32 p, float f, u32 q);
  int __thiscall fn_000648f0(u32 n);
  int __thiscall fn_00064960(u32 idx);
  int __thiscall fn_00064a30();
  int __thiscall fn_00064a50(u32 key);
};

// FUNCTION: DAO 0x004638A0
int __thiscall Vec8::fn_000638a0(u32 a, u32 b, u32 c, u32 d) {
  u8 tmp[32];
  u32 n = a;
  u32 z = 0;
  fn_004629e0(0, tmp, d);
  if (n != 0) {
    u32 oldsize = size8();
    u32 oldcap = cap8();
    if (oldcap < oldsize + n) {
      u32 newcap = oldcap + (oldcap >> 1);
      if (newcap < oldsize + n) newcap = oldsize + n;
      if (((u32)0x1fffffff - oldsize) < n) fn_00871e20(0);
      u8* p = (u8*)(u32)fn_0086bce0(0, newcap);
      fn_00462ee0(0, begin, end, p, 0);
      if (begin) fn_00462940(0, begin, end);
      fn_004136c0(0, begin);
      begin = p;
      end = p + oldsize * 8;
      cap = p + newcap * 8;
    }
    u8* q = (u8*)(u32)fn_0086bce0(0, n);
    fn_004637d0(0, this, q, n, tmp);
    fn_00462ee0(0, begin, c, q, n);
    if (begin) fn_00462940(0, begin, end);
    fn_004136c0(0, begin);
    begin = q;
    end = q + n * 8;
    cap = q + n * 8;
  } else {
    fn_00463870(0, this, c, b, z);
    fn_00463430(0, begin, c, b);
  }
  fn_00462d20(0, tmp);
  fn_00462920(0, tmp);
  return (int)this;
}

// FUNCTION: DAO 0x00463C30
int __thiscall Vec8::fn_00063c30(u32 n) {
  u32 s = size8();
  if (s < n) {
    u32 add = n - s;
    u8* oldend = end;
    fn_004633c0(0, this, oldend, add);
    this->fn_000638a0(add, (u32)oldend, 0, 0);
  } else if (n < s) {
    u8* newend = begin + n * 8;
    if (newend < begin || newend > end) fn_008e11f2(0);
    end = newend;
    fn_00462920(0, this);
  }
  return (int)this;
}

// FUNCTION: DAO 0x00463D20
int __thiscall Vec8::fn_00063d20(u32 a, u32 b, u32 c, u32 d) {
  u32 s = size8();
  if (b <= s) {
    u8* oldend = end;
    this->fn_000638a0(a, c, d, 1);
    if (oldend) {
      u8* q = begin + (b + a) * 8;
      if (q < begin || q > end) fn_008e11f2(0);
      end = q;
    }
  } else {
    fn_008e11f2(0);
  }
  return (int)this;
}

// FUNCTION: DAO 0x00463DB0
int __thiscall Vec8::fn_00063db0(u32 v) {
  u32 s = size8();
  u32 c = cap8();
  if (begin && s < c) {
    fn_004630e0(0, end, this, v, 1, 0, 0, 0);
    end += 8;
  } else {
    this->fn_00063d20(1, (u32)end, v, 0);
  }
  return (int)this;
}

// FUNCTION: DAO 0x00464200
int __thiscall Vec8::fn_00064200(u32 flags, u32 p, float f, u32 q) {
  u8* base = (u8*)this;
  if (flags & 1) fn_00463e40(0, base + 0xc, p, f, q, 0, 0, 1, -1, -1, 0xff, 0);
  if (flags & 2) fn_00463e40(0, base + 0x54, p, f, q + 0x30, 0, 0, 0, -1, -1, 0xff, 0);
  if (flags & 4) fn_00463e40(0, base + 0x24, p, f, q + 0x10, 0, 0, 0, -1, -1, 0xff, 0);
  if (flags & 8) fn_00463e40(0, base + 0x3c, p, f, q + 0x20, 0, 0, 0, -1, -1, 0xff, 0);
  if (flags & 0x10) fn_00463e40(0, base + 0x6c, p, f, q + 0x10, 0, 0, 0, -1, -1, 0xff, 0);
  if (flags & 0x20) fn_00463e40(0, base + 0x84, p, f, q, 0, 0, 0, -1, -1, 0xff, 0);
  return (int)this;
}

// FUNCTION: DAO 0x004648F0
int __thiscall Vec8::fn_000648f0(u32 n) {
  field0 = 0;
  begin = 0;
  end = 0;
  cap = 0;
  if (n > 0) {
    u32 z = 0;
    fn_00462cc0(0, &z, 0);
    this->fn_00063c30(n);
  }
  return (int)this;
}

// FUNCTION: DAO 0x00464960
int __thiscall Vec8::fn_00064960(u32 idx) {
  u32 s = size8();
  if (begin && idx < s) {
    u8* p = begin + idx * 8;
    u8* last = end - 8;
    while (p < last) {
      fn_00462a10(0, p, p + 8);
      p += 8;
    }
    u32 z = 0;
    fn_00462cc0(0, &z, 0);
    this->fn_00063c30(s - 1);
    fn_00462920(0, &z);
  }
  return (int)this;
}

// FUNCTION: DAO 0x00464A30
int __thiscall Vec8::fn_00064a30() {
  Vec8* sub = (Vec8*)((u8*)this + 8);
  sub->fn_000648f0(0);
  return (int)this;
}

// FUNCTION: DAO 0x00464A50
int __thiscall Vec8::fn_00064a50(u32 key) {
  Vec8* sub = (Vec8*)((u8*)this + 8);
  u32 n = sub->size8();
  u32 i = 0;
  bool found = false;
  while (i < n && !found) {
    u8* e = sub->begin + i * 8;
    int r = fn_004621c0(0, e);
    if (r != 0 && *(u32*)((u8*)(u32)r + 0x18) == key) found = true;
    ++i;
  }
  if (!found) {
    void* mem = (void*)(u32)fn_00413660(0, 0x1c);
    if (mem) fn_00463280(0, mem, key);
    u32 z = 0;
    fn_00462cc0(0, &z, 0);
    sub->fn_00063db0((u32)mem);
    fn_00462920(0, &z);
  }
  return (int)this;
}
