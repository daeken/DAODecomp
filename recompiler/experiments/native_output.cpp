// Debugging checks for the actual startup bridge's output/identity boundaries.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <array>
#include <cstdio>
#include <cstring>
using namespace recomp_generated;
static bool unknown(Win32ProcessMemory& memory,std::uint32_t address,unsigned width) {
    try { (void)memory.load(address,width); return false; }
    catch(const sharp_retro::UnknownMemoryRead&) { return true; }
}
int main() {
 try {
    Win32ProcessMemory memory;
    auto kernel=::GetModuleHandleA("KERNEL32");
    if(!kernel || kernel!=::GetModuleHandleA("kernel32.dll")) return 13;
    auto kernel_address=std::uint32_t(reinterpret_cast<std::uintptr_t>(kernel));
    register_native_module(kernel_address,"KERNEL32"); register_native_module(kernel_address,"kernel32.dll");
    if(registered_native_module(kernel_address)!="kernel32.dll") return 14;
    memory.map_bytes("scratch",0x52000000,65536,true,true);
    memory.map_bytes("readonly",0x52010000,65536,true,false); memory.seal();
    constexpr std::uint32_t source=0x52000040,output=0x52000100,stack=0x52001000;
    auto invoke=[&](const char* symbol,std::initializer_list<std::uint32_t> arguments) {
        sharp_retro::State state; state.gpr[4]=stack;
        memory.store(stack,0x12345678,32); unsigned index=1;
        for(auto value:arguments) memory.store(stack+4u*index++,value,32);
        invoke_native_import({0,"KERNEL32.dll",symbol,false},state,memory);
        if(state.pc!=0x12345678 || state.gpr[4]!=stack+4u*index || !(state.defined_gpr&1)) throw std::runtime_error("native cleanup/return mismatch");
        return std::uint32_t(state.gpr[0]);
    };
    memory.store(source,'A',8);
    memory.store_unknown(output,0x6d6d6d6d,32); memory.store_unknown(output+4,0x6d6d6d6d,32);
    bool refused=false;
    try { (void)memory.native_pointer(output,8,false); } catch(const sharp_retro::UnknownMemoryRead&) { refused=true; }
    if(!refused || invoke("MultiByteToWideChar",{CP_ACP,0,source,1,output,4})!=1 || memory.load(output,16)!='A' ||
       !unknown(memory,output+2,16) || !unknown(memory,output+4,32)) return 1;
    refused=false;
    try { (void)memory.native_pointer(0x52010000,4,true,false); } catch(const std::runtime_error&) { refused=true; }
    if(!refused) return 2;
    refused=false;
    try { memory.complete_native_write(0x5200ffff,2); } catch(const std::runtime_error&) { refused=true; }
    if(!refused) return 3;
    for(auto page:{UINT(CP_ACP),UINT(932),UINT(CP_UTF8)}) {
        CPINFO expected; std::memset(&expected,0x6d,sizeof expected);
        if(!::GetCPInfo(page,&expected)) return 15;
        for(unsigned i=0;i<sizeof(CPINFO)+4;i++) memory.store_unknown(output+i,0x6d,8);
        if(!invoke("GetCPInfo",{page,output}) || std::memcmp(memory.native_pointer(output,sizeof(CPINFO),false,false),&expected,sizeof expected)) return 16;
        unsigned used=0; do { used+=2; } while(used<sizeof expected.LeadByte && (expected.LeadByte[used-2] || expected.LeadByte[used-1]));
        auto end=offsetof(CPINFO,LeadByte)+used;
        for(unsigned i=0;i<end;i++) if(unknown(memory,output+i,8)) return 17;
        for(unsigned i=end;i<sizeof(CPINFO)+4;i++) if(!unknown(memory,output+i,8)) return 18;
    }
    auto heap=::GetProcessHeap(); auto* small=static_cast<char*>(::HeapAlloc(heap,0,3));
    if(!small) return 10;
    std::memcpy(small,"AB",3); auto small_address=memory.register_native(small,3,true,true);
    std::uint32_t observed=0; SIZE_T transferred=0;
    if(!::ReadProcessMemory(::GetCurrentProcess(),small,&observed,4,&transferred) || transferred!=4 || memory.load(small_address,32)!=observed) return 11;
    refused=false;
    try { (void)memory.native_pointer(small_address,4,false); } catch(const std::runtime_error&) { refused=true; }
    if(!refused || !::HeapFree(heap,0,small)) return 12;
    memory.forget_native(small);
    std::array<char,32768> actual_path{};
    auto length=::GetModuleFileNameA(nullptr,actual_path.data(),DWORD(actual_path.size()));
    if(!length || length>=actual_path.size()) return 4;
    logical_main_module_path_a=actual_path.data();
    for(auto capacity : std::array<DWORD,5>{0,1,length,length+1,512}) {
        std::array<char,512> expected; expected.fill(0x6d);
        ::SetLastError(0x1234);
        auto expected_result=::GetModuleFileNameA(nullptr,expected.data(),capacity); auto expected_error=::GetLastError();
        for(unsigned i=0;i<512;i+=4) memory.store_unknown(output+i,0x6d6d6d6d,32);
        native_error_context.value=0x1234;
        auto result=invoke("GetModuleFileNameA",{0,output,capacity});
        if(result!=expected_result || native_error_context.value!=expected_error ||
           std::memcmp(memory.native_pointer(output,512,false,false),expected.data(),512)) {
            std::fprintf(stderr,"filename mismatch cap=%u result=%u/%u error=%u/%u\n",unsigned(capacity),result,unsigned(expected_result),unsigned(native_error_context.value),unsigned(expected_error)); return 5;
        }
        auto written=capacity ? std::min(capacity,length+DWORD(1)) : DWORD(0);
        if(written && unknown(memory,output+written-1,8)) return 6;
        if(written<512 && !unknown(memory,output+written,8)) return 7;
    }
    logical_main_module_path_a="Z:\\game\\DAOrigins.exe";
    if(invoke("GetModuleFileNameA",{0,output,512})!=logical_main_module_path_a.size() ||
       std::strcmp(static_cast<const char*>(memory.native_pointer(output,logical_main_module_path_a.size()+1,false)),logical_main_module_path_a.c_str())) return 8;
    std::puts("{\"native_output_tail_unknown\":true,\"readonly_output_refused\":true,\"filename_matches_native\":true,\"logical_identity\":true,\"allocation_tail_matches_observed_bytes\":true,\"code_page_output_cases\":3,\"code_page_unpublished_tail_unknown\":true}");
    return 0;
 } catch(const std::exception& e) { std::fprintf(stderr,"%s\n",e.what()); return 9; }
}
