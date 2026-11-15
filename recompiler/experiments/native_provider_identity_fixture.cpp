// Owned DLL fixture: two builds deliberately reuse the same image/export address.
#include <windows.h>
#ifndef RECOMP_IDENTITY_VALUE
#error RECOMP_IDENTITY_VALUE must identify the fixture build
#endif
extern "C" BOOL WINAPI DllMain(HINSTANCE,DWORD,LPVOID) {return TRUE;}
extern "C" __declspec(dllexport) unsigned __cdecl identity_marker() {
    return RECOMP_IDENTITY_VALUE;
}
