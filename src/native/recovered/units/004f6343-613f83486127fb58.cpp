typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

struct S12 { u32 a; void* b; u32 c; };

extern void __cdecl fn_008e11f2(void);
extern int __cdecl fn_004bbf10(void* p1, void* p2, void* p3, void* p4);
extern int __cdecl fn_008f2c83(void* stream);
extern int __cdecl fn_008f17c3(int ch, void* stream);
extern int __cdecl fn_008ff1fd(void* out, int n, void* src, int arg4);
extern int __cdecl fn_008fef2e(u16 ch, void* stream);
extern void __cdecl fn_008e1613(void);
extern int __cdecl fn_008f2df1(int arg);
extern void* __cdecl fn_008ee2b8(void);
extern void* __cdecl fn_008eb878(void);
extern int __cdecl fn_00904df9(int arg);
extern int __cdecl fn_008f0940(int arg);
extern int __cdecl fn_008f62db(int* local);
extern void __cdecl fn_008e10d2(void);
extern u32 g_00c15c48;
extern u32 g_00c15b60;
extern u32 g_00c16284;
extern u32 g_00c16288;
extern u32 g_00c16280;
extern u32 g_00c16290;
extern u32 g_00c16294;
extern u32 g_00c1628c;

// FUNCTION: DAO 0x004BC230
void* __cdecl fn_000bc230(void* out, int a2, int a3, int a4, int a5, int a6, int a7, int a8, void* a9, int a10)
{
  int delta = a7 - a4;
  int base; int lim; int pos;
  (void)a2; (void)a8;
  if (a9 == 0) fn_008e11f2();
  base = *(int*)((char*)a9 + 0xc);
  lim = base + *(int*)((char*)a9 + 0x10);
  pos = a10 + delta;
  if ((u32)pos > (u32)lim || (u32)pos < (u32)base) fn_008e11f2();
  {
    S12 s1; S12 s2; S12 s3;
    s1.a = 0; s1.b = a9; s1.c = (u32)a10;
    s2.a = 0; s2.b = (void*)a6; s2.c = (u32)a7;
    s3.a = 0; s3.b = (void*)a3; s3.c = (u32)a4;
    *(u32*)out = 0;
    *(void**)((char*)out + 4) = a9;
    *(u32*)((char*)out + 8) = (u32)pos;
    fn_004bbf10(&s1, &s2, &s3, (void*)a5);
  }
  return out;
}

// FUNCTION: DAO 0x008E90E6
int __cdecl fn_004e90e6(u16 ch, void* stream)
{
  u8* s = (u8*)stream;
  if (s[0xc] & 0x40) {
    *(int*)(s + 4) -= 2;
    if (*(int*)(s + 4) >= 0) {
      *(u16*)(*(void**)s) = ch;
      *(void**)s = (u8*)(*(void**)s) + 2;
      return (int)ch;
    }
    return fn_008fef2e(ch, stream);
  }
  {
    int f = fn_008f2c83(stream);
    if (f != -1 && f != -2) {
      int idx = f >> 5;
      int off = (f & 0x1f) << 6;
      (void)idx; (void)off;
    }
  }
  *(int*)(s + 4) -= 1;
  if (*(int*)(s + 4) >= 0) {
    *(u8*)(*(void**)s) = (u8)ch;
    *(void**)s = (u8*)(*(void**)s) + 1;
    return (int)ch;
  }
  return fn_008f17c3((int)(signed char)ch, stream);
}

// FUNCTION: DAO 0x008E9332
int __cdecl fn_004e9332(int unused, int arg)
{
  (void)unused;
  return fn_008f2df1(arg);
}

// FUNCTION: DAO 0x008EB455
int __cdecl fn_004eb455(void)
{
  int* p = (int*)fn_008ee2b8();
  int v = p[0x6c / 4];
  if (v == (int)g_00c15c48 || (p[0x70 / 4] & (int)g_00c15b60) != 0) {
    return *(int*)((char*)v + 4);
  }
  {
    void* q = fn_008eb878();
    return *(int*)((char*)q + 4);
  }
}

// FUNCTION: DAO 0x008F36AF
int __cdecl fn_004f36af(int arg)
{
  return fn_00904df9(arg);
}

// FUNCTION: DAO 0x008F5DB2
int __cdecl fn_004f5db2(void)
{
  return fn_008f0940(7);
}

// FUNCTION: DAO 0x008F5E4C
void __cdecl fn_004f5e4c(int mode, int a2, int year, int month, int day, int hour, int minute, int second, int msec)
{
  int edi = year;
  int esi;
  int ecx;
  int local = 0;
  int local_c = 0;
  (void)a2;
  if (a2 == 1) {
    u32 r = (u32)edi & 0x80000003u;
    if ((int)r < 0) { r--; r |= 0xFFFFFFFCu; r++; }
    local_c = (int)r;
  }
  {
    int mi = (month > 0 && month < 13) ? month - 1 : 0;
    static const int mdays[12] = {0,31,59,90,120,151,181,212,243,273,304,334};
    esi = edi * 365 + (edi / 4) - (edi / 100) + (edi / 400) + mdays[mi] + day;
  }
  (void)local_c;
  ecx = ((hour * 60 + minute) * 60 + second) * 1000 + msec;
  if (mode == 1) {
    g_00c16284 = (u32)esi;
    g_00c16288 = (u32)ecx;
    g_00c16280 = (u32)edi;
  } else {
    g_00c16290 = (u32)esi;
    g_00c16294 = (u32)ecx;
    if (fn_008f62db(&local)) {
      fn_008e10d2();
    }
    g_00c16294 += (u32)(local * 1000);
    if ((int)g_00c16294 < 0) {
      g_00c16294 += 0x5265C00u;
      g_00c16290--;
    } else if (g_00c16294 >= 0x5265C00u) {
      g_00c16294 -= 0x5265C00u;
      g_00c16290++;
    }
    g_00c1628c = (u32)edi;
  }
}

// FUNCTION: DAO 0x008F6343
void* __cdecl fn_004f6343(void)
{
  return (void*)0x00C1629C;
}

// FUNCTION: DAO 0x008F6349
void* __cdecl fn_004f6349(void)
{
  return (void*)0x00C162A0;
}

// FUNCTION: DAO 0x008F634F
void* __cdecl fn_004f634f(void)
{
  return (void*)0x00C16298;
}

// FUNCTION: DAO 0x008F6355
void* __cdecl fn_004f6355(void)
{
  return (void*)0x00C16328;
}

// FUNCTION: DAO 0x00904B82
int __cdecl fn_00504b82(int arg)
{
  return fn_00904df9(arg);
}
