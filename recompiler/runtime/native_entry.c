// A normal C CRT entry leaves the original image's static TLS to Windows. C++
// runtime TLS and all compiled translations live in recomp_runtime.dll instead.
#include "native_image_config.hpp"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
__declspec(dllimport) unsigned __cdecl recomp_native_entry(unsigned,unsigned,unsigned,unsigned,HINSTANCE,unsigned,void*);
#if RECOMP_IS_DLL
BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,LPVOID reserved) {
    return recomp_native_entry(RECOMP_IMAGE_BASE,RECOMP_IMAGE_EXTENT,RECOMP_ENTRY,1,instance,reason,reserved)!=0;
}
#else
int main(void) {
    return (int)recomp_native_entry(RECOMP_IMAGE_BASE,RECOMP_IMAGE_EXTENT,RECOMP_ENTRY,0,GetModuleHandleW(NULL),DLL_PROCESS_ATTACH,NULL);
}
#endif
