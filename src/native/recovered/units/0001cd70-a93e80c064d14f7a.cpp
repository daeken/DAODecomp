extern "C" unsigned int g_007f1084;
extern "C" void* g_0081d9e0;
extern "C" void __cdecl fn_004e4696(unsigned int);
extern "C" void* __cdecl fn_004e47aa(void*);
extern "C" void __cdecl fn_004e1a5a(void*);
extern "C" void __fastcall fn_00436ac0(void*, int, unsigned int);
extern "C" void __fastcall fn_00436aa0(void*, int, unsigned int);
extern "C" void __fastcall fn_00436b80(void*, int, void*);
extern "C" void __fastcall fn_00436ae0(void*, int, void*);
extern "C" void __fastcall fn_00040390(void*, int, void*);
extern "C" void* __fastcall fn_0001ce70(void*, int, void*);
extern "C" char* __cdecl fn_004e29f0(char*, const char*, unsigned int);

struct S41ccb0 { S41ccb0* __thiscall fn_0001ccb0(); };
struct S41cd10 { int __thiscall fn_0001cd10(void*); };
struct S41cd40 { int __thiscall fn_0001cd40(void*); };
struct S41cd70 { void __thiscall fn_0001cd70(unsigned int); };
struct S41e2d0 { void __thiscall fn_0001e2d0(unsigned int); };
struct S4362b0 { void __thiscall fn_000362b0(void*); };
struct S442dd0 { S442dd0* __thiscall fn_00042dd0(); };

// FUNCTION: DAO 0x41ccb0
S41ccb0* S41ccb0::fn_0001ccb0() {
  unsigned int v = g_007f1084;
  if (!v) {
    *(unsigned char*)this = (unsigned char)v;
    *(unsigned int*)((char*)this + 0x20) = v;
    *(unsigned int*)((char*)this + 0x24) = v;
  } else {
    fn_004e29f0((char*)this, (const char*)v, 0x20);
    *(unsigned int*)((char*)this + 0x20) = 0;
    *(unsigned int*)((char*)this + 0x24) = 0;
  }
  return this;
}

// FUNCTION: DAO 0x41cd10
int S41cd10::fn_0001cd10(void* arg) {
  unsigned int a = *(unsigned int*)((char*)this + 4);
  unsigned int w = *(unsigned short*)((char*)this + 8);
  fn_00436ac0(arg, 0, a);
  fn_00436aa0(arg, 0, w);
  unsigned int edx = *(unsigned int*)((char*)arg + 4);
  return *(int*)(edx + 0x414);
}

// FUNCTION: DAO 0x41cd40
int S41cd40::fn_0001cd40(void* arg) {
  fn_00436b80(arg, 0, (char*)this + 4);
  fn_00436ae0(arg, 0, (char*)this + 8);
  unsigned int ecx = *(unsigned int*)((char*)arg + 4);
  return *(int*)(ecx + 0x414);
}

// FUNCTION: DAO 0x41cd70
void S41cd70::fn_0001cd70(unsigned int v) {
  *(unsigned int*)((char*)this + 8) = v;
}

// FUNCTION: DAO 0x41cdf0
extern "C" void __cdecl fn_0001cdf0(void* arg) {
  void* obj = g_0081d9e0;
  if (!obj) {
    fn_004e4696(0xAE19F0);
    obj = g_0081d9e0;
  }
  if (!obj) {
    fn_004e47aa(arg);
    return;
  }
  void** vt = *(void***)obj;
  typedef void (__fastcall *Fn)(void*, int, void*, int);
  ((Fn)vt[7])(obj, 0, arg, 0);
}

// FUNCTION: DAO 0x41ce30
extern "C" void __cdecl fn_0001ce30(void* arg) {
  void* obj = g_0081d9e0;
  if (!obj) {
    fn_004e4696(0xAE19F0);
    obj = g_0081d9e0;
  }
  if (!obj) {
    fn_004e1a5a(arg);
    return;
  }
  void** vt = *(void***)obj;
  typedef void (__fastcall *Fn)(void*, int, void*, int);
  ((Fn)vt[8])(obj, 0, arg, 0);
}

// FUNCTION: DAO 0x41ce80
extern "C" void __stdcall fn_0001ce80(void* arg1, unsigned int arg2) {
  void* obj = g_0081d9e0;
  if (!obj) {
    fn_004e4696(0xAE19F0);
    obj = g_0081d9e0;
  }
  if (!obj) {
    fn_004e47aa(arg1);
    return;
  }
  void** vt = *(void***)obj;
  typedef void (__fastcall *Fn)(void*, int, void*, unsigned int);
  ((Fn)vt[7])(obj, 0, arg1, 0);
}

// FUNCTION: DAO 0x41cec0
extern "C" void __stdcall fn_0001cec0(void* arg1, unsigned int arg2) {
  void* obj = g_0081d9e0;
  if (!obj) {
    fn_004e4696(0xAE19F0);
    obj = g_0081d9e0;
  }
  if (!obj) {
    fn_004e1a5a(arg1);
    return;
  }
  void** vt = *(void***)obj;
  typedef void (__fastcall *Fn)(void*, int, void*, unsigned int);
  ((Fn)vt[8])(obj, 0, arg1, 0);
}

// FUNCTION: DAO 0x41e2d0
void S41e2d0::fn_0001e2d0(unsigned int v) {
  unsigned int* p = (unsigned int*)((char*)this + 8);
  for (unsigned int i = 0; i < 0x10; ++i) {
    if (p[i] == 0) {
      p[i] = v;
      break;
    }
  }
}

// FUNCTION: DAO 0x4362b0
void S4362b0::fn_000362b0(void* arg) {
  if (arg) {
    fn_00040390((char*)this + 0x48, 0, arg);
  }
}

// FUNCTION: DAO 0x442dd0
S442dd0* S442dd0::fn_00042dd0() {
  unsigned int local[2];
  unsigned int dummy = 0;
  fn_0001ce70(local, 0, 0);
  *(unsigned int*)((char*)this) = 0;
  *(unsigned int*)((char*)this + 4) = 0;
  *(unsigned int*)((char*)this + 8) = 0;
  fn_0001ce70((char*)this + 0xc, 0, &dummy);
  *(unsigned int*)((char*)this + 0x10) = 0;
  void* edi = (char*)this + 0x14;
  *(void**)((char*)this + 4) = edi;
  *(void**)((char*)this) = edi;
  edi = (char*)edi + 0x20;
  *(void**)((char*)this + 8) = edi;
  return this;
}

// FUNCTION: DAO 0x8e29f0
extern "C" char* __cdecl fn_004e29f0(char* dest, const char* src, unsigned int count) {
  char* d = dest;
  while (count && *src) {
    *d++ = *src++;
    --count;
  }
  if (count) {
    *d++ = 0;
    --count;
  }
  while (count) {
    *d++ = 0;
    --count;
  }
  return dest;
}
