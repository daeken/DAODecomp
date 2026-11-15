// Observe the actual native writer; no game function/contract acceptance.
#include <windows.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstddef>
struct Guarded {std::array<unsigned char,8> before;SYSTEM_INFO info;std::array<unsigned char,8> after;};
int main(){
 static_assert(sizeof(SYSTEM_INFO)==36 && offsetof(SYSTEM_INFO,wReserved)==2 && offsetof(Guarded,info)==8 && offsetof(Guarded,after)==44);
 auto proc=::GetProcAddress(::GetModuleHandleW(L"kernel32.dll"),"GetSystemInfo");HMODULE module=nullptr;char file[32768]{};
 if(!proc || !::GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCSTR>(proc),&module) || !::GetModuleFileNameA(module,file,sizeof(file)))return 1;
 std::printf("{\"module_path\":\"");for(auto c:file){if(!c)break;if(c=='\\')std::fputs("\\\\",stdout);else std::putchar(c);}std::printf("\",\"procedure_rva\":%u,\"observations\":[",unsigned(reinterpret_cast<std::uintptr_t>(proc)-reinterpret_cast<std::uintptr_t>(module)));
 unsigned n=0;for(unsigned poison:{0u,0xffu,0xa5u,0x5au,0x11u,0xefu}){
  Guarded probe;std::memset(&probe,poison,sizeof(probe));::SetLastError(0x13579);::GetSystemInfo(&probe.info);auto error=::GetLastError();
  for(auto c:probe.before)if(c!=poison)return 2;for(auto c:probe.after)if(c!=poison)return 3;
  std::printf("%s{\"poison\":%u,\"reserved\":%u,\"last_error\":%u,\"bytes\":\"",n++ ? ",":"",poison,unsigned(probe.info.wReserved),unsigned(error));auto* bytes=reinterpret_cast<const unsigned char*>(&probe.info);for(unsigned i=0;i<sizeof(probe.info);i++)std::printf("%02x",bytes[i]);std::fputs("\"}",stdout);
 }
 std::fputs("],\"guard_bytes_preserved\":true}\n",stdout);return 0;
}
