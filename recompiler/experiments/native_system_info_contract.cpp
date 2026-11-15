// Pinned native-provider refinement controls; no game acceptance.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main(){try{
 if(!reviewed_system_info_reserved_writer())throw std::runtime_error("native provider differs from reviewed writer");
 if(system_info_provider_file(::GetModuleHandleW(L"kernel32.dll"),"0000000000000000000000000000000000000000000000000000000000000000"))return 1;
 Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("output",0x50010000,4096,true,true);memory.seal();
 auto invoke=[&](std::uint32_t destination){sharp_retro::State s;s.gpr[4]=0x50000800;memory.store(0x50000800,0x12345678,32);memory.store(0x50000804,destination,32);invoke_native_import({0,"KERNEL32.dll","GetSystemInfo",false},s,memory);if(s.pc!=0x12345678 || s.gpr[4]!=0x50000808 || (s.defined_gpr&7))throw std::runtime_error("system info ABI mismatch");};
 unsigned cases=0;for(unsigned poison:{0u,0xffu,0xa5u,0x5au,0x11u,0xefu}){
  SYSTEM_INFO expected;std::memset(&expected,poison,sizeof(expected));::SetLastError(0x13579);::GetSystemInfo(&expected);auto error=::GetLastError();
  for(unsigned i=0;i<36;i++)memory.store_unknown(0x50010000+i,poison,8);memory.store(0x50010024,0xa5c33c5a,32);native_error_context.value=0x13579;invoke(0x50010000);
  if(native_error_context.value!=error || std::memcmp(memory.native_pointer(0x50010000,36,false),&expected,36) || memory.load(0x50010002,16)!=expected.wReserved || memory.load(0x50010024,32)!=0xa5c33c5a)return 2;++cases;
 }
 unsigned guards=0;for(auto destination:{0u,0x50010ff0u})try{invoke(destination);}catch(const std::runtime_error&){++guards;}
 std::printf("{\"native_output_cases\":%u,\"exact_provider_matched\":true,\"reserved_word_matches_actual_output\":true,\"all_bytes_defined\":true,\"neighbor_preserved\":true,\"bad_provider_hash_refused\":true,\"output_guards\":%u}\n",cases,guards);return cases!=6 || guards!=2 ? 3:0;
}catch(const std::exception& e){std::fprintf(stderr,"system info contract: %s\n",e.what());return 4;}}
