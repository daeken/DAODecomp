// Real directory creation transport in a private temporary tree, not game acceptance.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main(){try{
 wchar_t temp[MAX_PATH],unique[MAX_PATH];if(!::GetTempPathW(MAX_PATH,temp) || !::GetTempFileNameW(temp,L"DCD",0,unique) || !::DeleteFileW(unique) || !::CreateDirectoryW(unique,nullptr))return 1;std::wstring base=unique;
 Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("input",0x50010000,8192,true,true);memory.seal();
 auto put=[&](const std::wstring& text){for(unsigned i=0;i<=text.size();i++)memory.store(0x50010000+i*2,std::uint16_t(text.c_str()[i]),16);};
 auto invoke=[&](std::uint32_t address,std::uint32_t attributes){sharp_retro::State s;s.gpr[4]=0x50000800;for(unsigned r:{3u,5u,6u,7u})s.gpr[r]=0x12340000u+r;memory.store(0x50000800,0x12345678,32);memory.store(0x50000804,address,32);memory.store(0x50000808,attributes,32);invoke_native_import({0,"KERNEL32.dll","CreateDirectoryW",false},s,memory);if(s.pc!=0x12345678 || s.gpr[4]!=0x5000080c || !(s.defined_gpr&1) || (s.defined_gpr&6) || s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)throw std::runtime_error("directory ABI mismatch");return std::uint32_t(s.gpr[0]);};
 SECURITY_ATTRIBUTES attrs{12,nullptr,TRUE};attrs.bInheritHandle=std::bit_cast<BOOL>(0xffffffffu);memory.store(0x50011000,12,32);memory.store(0x50011004,0,32);memory.store(0x50011008,0xffffffffu,32);
 unsigned cases=0,failures=0;
 auto compare=[&](const std::wstring& expected_path,const std::wstring& candidate_path,bool attributes){
  ::SetLastError(0x13579);auto expected=::CreateDirectoryW(expected_path.c_str(),attributes ? &attrs:nullptr);auto error=::GetLastError();put(candidate_path);native_error_context.value=0x13579;auto actual=invoke(0x50010000,attributes ? 0x50011000:0);
  if(actual!=std::uint32_t(expected) || native_error_context.value!=error)throw std::runtime_error("directory native result/error mismatch");
  if(actual){if(!(::GetFileAttributesW(expected_path.c_str())&FILE_ATTRIBUTE_DIRECTORY) || !(::GetFileAttributesW(candidate_path.c_str())&FILE_ATTRIBUTE_DIRECTORY) || !::RemoveDirectoryW(expected_path.c_str()) || !::RemoveDirectoryW(candidate_path.c_str()))throw std::runtime_error("directory side effect mismatch");}else ++failures;++cases;
 };
 compare(base+L"\\plain_ref",base+L"\\plain_candidate",false);
 compare(base+L"\\\u0394ao_\U0001d11e_ref",base+L"\\\u0394ao_\U0001d11e_candidate",false);
 compare(base+L"\\attributes_ref",base+L"\\attributes_candidate",true);
 compare(base,base,false);compare(base+L"\\missing_ref\\child",base+L"\\missing_candidate\\child",false);compare(L"",L"",false);
 auto collision=base+L"\\file";auto file=::CreateFileW(collision.c_str(),GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);if(file==INVALID_HANDLE_VALUE || !::CloseHandle(file))return 2;compare(collision,collision,false);if(!::DeleteFileW(collision.c_str()))return 3;
 auto guard=base+L"\\guard";put(guard);memory.store(0x50011004,0x50011200,32);unsigned refused=0;
 for(auto args:std::array<std::array<std::uint32_t,2>,4>{{{0,0},{0x12340,0},{0x50010000,0x12340},{0x50010000,0x50011000}}})try{(void)invoke(args[0],args[1]);}catch(const std::runtime_error&){++refused;}
 if(::GetFileAttributesW(guard.c_str())!=INVALID_FILE_ATTRIBUTES || !::RemoveDirectoryW(base.c_str()))return 4;
 std::printf("{\"native_directory_cases\":%u,\"native_failures\":%u,\"creation_observed\":true,\"default_security_forwarded\":true,\"refusal_guards\":%u}\n",cases,failures,refused);return cases!=7 || failures!=4 || refused!=4 ? 5:0;
}catch(const std::exception& e){std::fprintf(stderr,"directory debug: %s\n",e.what());return 6;}}
