typedef unsigned int u32;
typedef unsigned char u8;
typedef int s32;
#define M32(p) (*(u32*)(p))
#define M8(p) (*(u8*)(p))
typedef u8 (__thiscall *FnThisU8)(void*);
typedef void* (__thiscall *FnThisPtr)(void*);
typedef int (__thiscall *FnThisInt)(void*);
typedef void (__thiscall *FnThisVoid)(void*);
extern "C" void* fn_0041e250();
extern "C" void* fn_004740b0();
extern "C" void* fn_00413660(u32);
struct Ctx {
  int __thiscall fn_00079620();
  u8 __thiscall fn_000796b0(int,int,int,int,int,int,int);
  void* __thiscall fn_000797b0(int,int,int,int,u8);
  int __thiscall fn_0007fc70();
  u32 __thiscall fn_000c5380();
  u8 __thiscall fn_000d5f00(void*);
  void* __thiscall fn_001d5810();
  void* __thiscall fn_001d58c0(void*);
  void* __thiscall fn_001ddb60(u32);
  u8 __thiscall fn_002b73c0(void*);
  int __thiscall fn_002f1fe0();
  void __thiscall fn_002f20e0();
};
// FUNCTION: DAO 0x00479620
int __thiscall Ctx::fn_00079620() {
  u32 edi = M32(0x00C32938u);
  if (edi) {
    FnThisU8 f = (FnThisU8)0x00838210u;
    u8 al = f((void*)(edi+0x280));
    M8((u8*)this+0x6e86)=al;
    M8((u8*)this+0x6e8c)=1;
    al=f((void*)(edi+0x2a0));
    M8((u8*)this+0x6e88)=al;
    M8((u8*)this+0x6e8c)=1;
    al=f((void*)(edi+0x290));
    M8((u8*)this+0x6e8a)=al;
    M8((u8*)this+0x6e8c)=1;
  }
  void* obj = fn_0041e250();
  void** vt = *(void***)obj;
  void* ebx = ((void* (__thiscall*)(void*))vt[0x10])(obj);
  void** ebp = *(void***)ebx;
  u8 al = ((FnThisU8)0x00838210u)((void*)(edi+0x260));
  ((void (__thiscall*)(void*, u8))ebp[2])(ebx, al);
  ((void (__thiscall*)(void*))0x00478bb0u)(this);
  return ((int (__thiscall*)(void*))0x00479ad0u)(this);
}
// FUNCTION: DAO 0x004796b0
u8 __thiscall Ctx::fn_000796b0(int a1,int a2,int a3,int a4,int a5,int a6,int a7) {
  u32 obj[8];
  int r = ((int (__thiscall*)(void*, const void*, u32))0x004c0fb0u)(obj, (const void*)0x00AEA890u, 0u);
  if (r < 0) return 0;
  int n = ((int (__cdecl*)(int, const void*, const void*, int, int, int))0x00ADA348u)(0, (const void*)0x00AEA884u, obj, 0, 0, 5);
  ((void (__thiscall*)(void*))0x004c0db0u)(obj);
  return (u8)(n > 0x20);
}
// FUNCTION: DAO 0x004797b0
void* __thiscall Ctx::fn_000797b0(int a1,int a2,int a3,int a4,u8 a5) {
  void* esi = fn_00413660(0x48u);
  if (!esi) return 0;
  M32(esi)=a1; M32((u8*)esi+4)=a2; M32((u8*)esi+8)=a3;
  ((void (__thiscall*)(void*, void*))0x005b4e20u)((u8*)esi+0xc, (void*)a4);
  M8((u8*)esi+0x44)=a5; M8((u8*)esi+0x45)=0;
  return esi;
}
// FUNCTION: DAO 0x0047fc70
int __thiscall Ctx::fn_0007fc70() {
  void* p = fn_004740b0();
  return ((int (__thiscall*)(void*))0x00479ad0u)(p);
}
// FUNCTION: DAO 0x004c5380
u32 __thiscall Ctx::fn_000c5380() { return M32(0x00C2BE24u); }
// FUNCTION: DAO 0x004d5f00
u8 __thiscall Ctx::fn_000d5f00(void* arg) {
  if (M32((u8*)this+0xc)==0) return 1;
  u32 ebx = M32(M32((u8*)this+8));
  u8* ebp = (u8*)this+4;
  u8* edi = (u8*)arg;
  while (ebx != M32(ebp+4)) {
    u32 ecx = M32(ebx+0xc);
    if (ecx) {
      void* o=(void*)ecx;
      int eax = ((int (__thiscall*)(void*))((void**)(*(void**)o))[6])(o);
      u32 beg=M32(edi+4), end=M32(edi+8), cap=M32(edi+0xc);
      if (beg && end < cap) { M32(end)=eax; M32(edi+8)=end+4; }
      else { ((void (__cdecl*)(void*,u32,void*))0x006f1160u)(edi, end, &eax); }
    }
    ebx = M32(ebx);
  }
  return 1;
}
// FUNCTION: DAO 0x005d5810
void* __thiscall Ctx::fn_001d5810() {
  void* p = ((void* (__thiscall*)(void*))0x005d4fc0u)(this);
  if (!p) return 0;
  p = ((void* (__thiscall*)(void*))0x005d4fc0u)(this);
  return *(void**)((u8*)p+0x490);
}
// FUNCTION: DAO 0x005d58c0
void* __thiscall Ctx::fn_001d58c0(void* a1) {
  void* local = 0;
  void* ecx = *(void**)((u8*)this+0xcc);
  ecx = *(void**)ecx;
  int r = ((int (__thiscall*)(void*, void*, void**))0x00A58190u)(ecx, a1, &local);
  if ((u8)r == M8(0x00B59409u) && local && M8((u8*)local+0x14) == M8(0x00B593FCu)) {
    void** vt = *(void***)local;
    return ((void* (__thiscall*)(void*))vt[4])(local);
  }
  return 0;
}
// FUNCTION: DAO 0x005ddb60
void* __thiscall Ctx::fn_001ddb60(u32 idx) {
  u32* base = *(u32**)((u8*)this+4);
  if (base) {
    u32 count = (u32)((*(u32**)((u8*)this+8) - base));
    if (idx < count) return &base[idx];
  }
  return (void*)0x00C32A30u;
}
// FUNCTION: DAO 0x006b73c0
u8 __thiscall Ctx::fn_002b73c0(void* a1) {
  void* obj = *(void**)((u8*)this+0x70);
  void* esi = ((void* (__thiscall*)(void*))((void**)(*(void**)obj))[0x18])((u8*)this+0x70);
  if (!esi) return 1;
  float f = ((float (__thiscall*)(void*))0x00748520u)(a1);
  return ((u8 (__cdecl*)(void*, float))0x006b1bc0u)(esi, f);
}
// FUNCTION: DAO 0x006f1fe0
int __thiscall Ctx::fn_002f1fe0() {
  void* esi=(u8*)this+0x150;
  void* eax=((void* (__thiscall*)(void*))0x00403c70u)(esi);
  ((void (__thiscall*)(void*, int))0x00634f20u)(eax, 0);
  if (((int (__thiscall*)(void*))0x0053cc40u)((void*)(M32(0x00C32938u)+0xa8))) {
    ((void (__thiscall*)(void*, int))0x006f1340u)(this, 0);
  }
  return 0;
}
// FUNCTION: DAO 0x006f20e0
void __thiscall Ctx::fn_002f20e0() {
  void* esi=(u8*)this+0x16c;
  void* eax=((void* (__thiscall*)(void*))0x00403c70u)(esi);
  ((void (__thiscall*)(void*, int))0x0068f840u)(eax, 0);
  if (!((int (__thiscall*)(void*))0x0053cc40u)((void*)(M32(0x00C32938u)+0xa8))) return;
  u32 tmp=0;
  ((void (__thiscall*)(void*, u32*))0x006eb4c0u)(this, &tmp);
  void* p=((void* (__thiscall*)(void*, u32))0x005d5be0u)((void*)M32(0x00C327ECu), M32((u8*)this+0x210));
  ((void (__thiscall*)(void*, void*))0x006f1340u)(this, p);
}
