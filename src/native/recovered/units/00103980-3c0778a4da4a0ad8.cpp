typedef unsigned int u32;
typedef unsigned char u8;
typedef void* VP;

struct CTree;
struct S27a970 { void fn_0027a970(); };
struct S40e140 { u8 fn_0040e140(VP); };
struct Sfff30 { void fn_000fff30(VP, u32, VP, VP); };
struct Sff930 { void fn_000ff930(VP, VP, VP, VP); };
struct S91460 { void fn_00091460(); };
struct Sf26b0 { void fn_000f26b0(); };
struct S1670 { void fn_00001670(u32, const char*); };
struct S19d0 { void fn_000019d0(VP); };
struct S4e1202 { void fn_004e1202(const char*, VP); };
struct S123b30 { void fn_00123b30(VP); };
struct S3f8390 { void fn_003f8390(VP); };
struct S0c2ab0 { void fn_000c2ab0(); };

void fn_004e11f2();
void* fn_0048e8c0(VP, VP, VP, VP, u32);

struct CTree {
  VP f0;
  VP f4;
  VP f8;
  VP fc;
  VP fn_001002a0(u32, u32, u32, u32);
  void fn_00100670(u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32, u32);
  void fn_00100760(u32, u32, u32, u32);
  VP fn_001007f0(VP);
  void fn_00100bb0(u32);
  void fn_001195f0(u32, u32);
  void fn_00442060(VP, VP, u32, VP);
  void fn_0065d890();
};

struct S503980 { void fn_00103980(); };

// FUNCTION: DAO 0x5002a0
VP CTree::fn_001002a0(u32 a0, u32 a1, u32 a2, u32 a3) {
  u8* b = reinterpret_cast<u8*>(this);
  if (*reinterpret_cast<VP*>(b + 8) == 0) {
    VP p4 = *reinterpret_cast<VP*>(b + 4);
    this->fn_00442060(reinterpret_cast<VP>(a0), p4, 1, reinterpret_cast<VP>(a3));
    return reinterpret_cast<VP>(a0);
  }
  this->fn_00442060(reinterpret_cast<VP>(a1), reinterpret_cast<VP>(a2), 1, reinterpret_cast<VP>(a3));
  return reinterpret_cast<VP>(a0);
}

// FUNCTION: DAO 0x500670
void CTree::fn_00100670(u32 a0, u32 a1, u32 a2, u32 a3, u32 a4, u32 a5, u32 a6, u32 a7, u32 a8, u32 a9, u32 a10, u32 a11, u32 a12, u32 a13, u32 a14, u32 a15, u32 a16) {
  u8* b = reinterpret_cast<u8*>(this);
  if (*reinterpret_cast<VP*>(b + 4) != 0) {
    ((Sfff30*)this)->fn_000fff30(reinterpret_cast<VP>(a0), a1, reinterpret_cast<VP>(a2), reinterpret_cast<VP>(a3));
  }
  ((Sff930*)this)->fn_000ff930(reinterpret_cast<VP>(a4), reinterpret_cast<VP>(a5), reinterpret_cast<VP>(a6), reinterpret_cast<VP>(a7));
  ((S91460*)b)->fn_00091460();
}

// FUNCTION: DAO 0x500760
void CTree::fn_00100760(u32 a0, u32 a1, u32 a2, u32 a3) {
  ((Sfff30*)this)->fn_000fff30(reinterpret_cast<VP>(a0), a1, reinterpret_cast<VP>(a2), reinterpret_cast<VP>(a3));
  u8* b = reinterpret_cast<u8*>(this);
  *reinterpret_cast<VP*>(b + 8) = reinterpret_cast<VP>(a0);
}

// FUNCTION: DAO 0x5007f0
VP CTree::fn_001007f0(VP key) {
  u8* b = reinterpret_cast<u8*>(this);
  VP r = this->fn_001002a0(reinterpret_cast<u32>(key), 0, 0, 0);
  if (r == 0) fn_004e11f2();
  if (r == *reinterpret_cast<VP*>(b + 4)) fn_004e11f2();
  return r;
}

// FUNCTION: DAO 0x500bb0
void CTree::fn_00100bb0(u32 n) {
  u8* b = reinterpret_cast<u8*>(this);
  *reinterpret_cast<VP*>(b + 4) = 0;
  *reinterpret_cast<VP*>(b + 8) = 0;
  *reinterpret_cast<VP*>(b + 12) = 0;
  if (n > 0) {
    u8 buf[0x40];
    ((Sf26b0*)buf)->fn_000f26b0();
    this->fn_00100670(n, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
  }
}

// FUNCTION: DAO 0x503980
void S503980::fn_00103980() {
  ((S0c2ab0*)(reinterpret_cast<u8*>(this) + 4))->fn_000c2ab0();
}

// FUNCTION: DAO 0x5195f0
void CTree::fn_001195f0(u32 a0, u32 a1) {
  this->fn_00442060(reinterpret_cast<VP>(a0), reinterpret_cast<VP>(a1), 0, 0);
  this->fn_0065d890();
}

// FUNCTION: DAO 0x842060
void CTree::fn_00442060(VP a0, VP a1, u32 a2, VP a3) {
  u8* b = reinterpret_cast<u8*>(this);
  ((S1670*)b)->fn_00001670(0x13, 0);
  ((S19d0*)b)->fn_000019d0(a0);
  ((S4e1202*)b)->fn_004e1202(0, a1);
  VP n = fn_0048e8c0(a0, a1, *reinterpret_cast<VP*>(b + 4), a2 ? a1 : a0, a2);
  if (n != 0) {
    *reinterpret_cast<VP*>(b + 4) = n;
  }
  ((S123b30*)this)->fn_00123b30(a3);
  ((S3f8390*)this)->fn_003f8390(n);
}

// FUNCTION: DAO 0xa5d890
void CTree::fn_0065d890() {
  u8* b = reinterpret_cast<u8*>(this);
  if (*reinterpret_cast<VP*>(b) == 0) fn_004e11f2();
  *reinterpret_cast<VP*>(b + 4) = *reinterpret_cast<VP*>(b);
}
