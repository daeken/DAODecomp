// FUNCTION: DAOrigins.exe 0x004010c0
extern "C" void* __cdecl fn_00013660(unsigned int);
extern "C" void __cdecl fn_000b9080(void*);
struct fn_00001000 {
  unsigned int opaque_word;
  unsigned char opaque_tail[104];
  fn_00001000();
  __forceinline static void* operator new(unsigned int n) { return fn_00013660(n); }
  __forceinline static void operator delete(void* p) { fn_000b9080(p); }
};
typedef char layout_000010c0[(sizeof(fn_00001000)==108)?1:-1];
extern fn_00001000* g_0082b588;
fn_00001000* __cdecl fn_000010c0() { return g_0082b588 = new fn_00001000; }
