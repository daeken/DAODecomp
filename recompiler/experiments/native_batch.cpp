// One native boundary exercise for the shared generated marshaler, not game acceptance.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main() { try {
    Win32ProcessMemory memory;
    memory.map_bytes("stack",0x50000000,4096,true,true);
    memory.map_bytes("data",0x50010000,8192,true,true);
    memory.map_bytes("readonly",0x50020000,4096,true,false);
    memory.seal();
    unsigned calls=0,comparisons=0,guards=0;
    auto put=[&](std::uint32_t address,const auto& value) {
        const auto* bytes=reinterpret_cast<const unsigned char*>(&value);
        for(unsigned i=0;i<sizeof(value);++i) memory.store(address+i,bytes[i],8);
    };
    auto invoke=[&](const char* lib,const char* name,std::initializer_list<std::uint32_t> args) {
        sharp_retro::State state;
        state.gpr[4]=0x50000800;
        for(unsigned r:{3u,5u,6u,7u}) state.gpr[r]=0x12340000u+r;
        memory.store(0x50000800,0x12345678,32);
        unsigned index=0; for(auto value:args) memory.store(0x50000804+4*index++,value,32);
        native_error_context.value=0x13579;
        invoke_native_import({0,lib,name,false},state,memory);
        if(state.pc!=0x12345678 || state.gpr[4]!=0x50000804+args.size()*4 ||
           (state.defined_gpr&6) || state.gpr[3]!=0x12340003 || state.gpr[5]!=0x12340005 ||
           state.gpr[6]!=0x12340006 || state.gpr[7]!=0x12340007)
            throw std::runtime_error("batch ABI mismatch");
        ++calls;return state;
    };
    auto compare=[&](const char* lib,const char* name,std::initializer_list<std::uint32_t> args,auto native) {
        // These comparisons use query/idempotent controls only. Initialize the
        // real provider first: its first lazy USER32 query can clear last-error,
        // whereas subsequent calls preserve it. Do not compare different states.
        (void)native();
        ::SetLastError(0x13579);auto expected=std::uint32_t(native());auto error=::GetLastError();
        auto actual=invoke(lib,name,args);
        if(!(actual.defined_gpr&1) || actual.gpr[0]!=expected || native_error_context.value!=error) {
            std::fprintf(stderr,"%s expected=%08x error=%08lx actual=%08x error=%08lx\n",name,expected,error,unsigned(actual.gpr[0]),native_error_context.value);
            throw std::runtime_error(std::string("native batch result/error mismatch: ")+name);
        }
        ++comparisons;
    };
    compare("KeRnEl32.DlL","GetUserDefaultLCID",{},[]{return ::GetUserDefaultLCID();});
    compare("kernel32.dll","GetThreadLocale",{},[]{return ::GetThreadLocale();});
    compare("kernel32.dll","IsDebuggerPresent",{},[]{return ::IsDebuggerPresent();});
    compare("kernel32.dll","GetConsoleCP",{},[]{return ::GetConsoleCP();});
    compare("kernel32.dll","GetConsoleOutputCP",{},[]{return ::GetConsoleOutputCP();});
    compare("kernel32.dll","IsValidLocale",{LOCALE_INVARIANT,LCID_SUPPORTED},[]{return ::IsValidLocale(LOCALE_INVARIANT,LCID_SUPPORTED);});
    compare("kernel32.dll","IsValidLocale",{0xffffffffu,LCID_SUPPORTED},[]{return ::IsValidLocale(0xffffffffu,LCID_SUPPORTED);});
    compare("USER32.dll","GetSystemMetrics",{SM_CXSCREEN},[]{return ::GetSystemMetrics(SM_CXSCREEN);});
    compare("gdi32.dll","GdiFlush",{},[]{return ::GdiFlush();});
    auto mode=::SetErrorMode(0);::SetErrorMode(mode);
    compare("kernel32.dll","SetErrorMode",{mode},[&]{return ::SetErrorMode(mode);});
    auto sleeping=invoke("kernel32.dll","Sleep",{0});
    if(sleeping.defined_gpr&1) throw std::runtime_error("void native call invented EAX");
    auto yielded=invoke("kernel32.dll","SwitchToThread",{});
    if(!(yielded.defined_gpr&1)) throw std::runtime_error("scalar native call lacks EAX");
    put(0x50010000,"C:\\");
    compare("kernel32.dll","GetDriveTypeA",{0x50010000},[]{return ::GetDriveTypeA("C:\\");});
    compare("kernel32.dll","GetDriveTypeA",{0},[]{return ::GetDriveTypeA(nullptr);});
    put(0x50010100,L"A\u0394\u03b2");
    compare("kernel32.dll","lstrlenW",{0x50010100},[]{return ::lstrlenW(L"A\u0394\u03b2");});
    put(0x50010200,"A\0B");put(0x50010300,"a\0C");
    compare("kernel32.dll","CompareStringA",{LOCALE_INVARIANT,NORM_IGNORECASE,0x50010200,3,0x50010300,3},
        []{return ::CompareStringA(LOCALE_INVARIANT,NORM_IGNORECASE,"A\0B",3,"a\0C",3);});
    compare("kernel32.dll","CompareStringA",{LOCALE_INVARIANT,NORM_IGNORECASE,0x50010200,0xffffffffu,0x50010300,0xfffffffeu},
        []{return ::CompareStringA(LOCALE_INVARIANT,NORM_IGNORECASE,"A\0B",-1,"a\0C",-2);});
    compare("kernel32.dll","CompareStringA",{LOCALE_INVARIANT,0,0,0,0,0},
        []{return ::CompareStringA(LOCALE_INVARIANT,0,nullptr,0,nullptr,0);});
    put(0x50010400,L"A\0B");put(0x50010500,L"a\0C");
    compare("kernel32.dll","CompareStringW",{LOCALE_INVARIANT,NORM_IGNORECASE,0x50010400,3,0x50010500,3},
        []{return ::CompareStringW(LOCALE_INVARIANT,NORM_IGNORECASE,L"A\0B",3,L"a\0C",3);});
    // Counted inputs must not consume the unknown byte just beyond their span.
    memory.store_unknown(0x50010201,0,8);
    compare("kernel32.dll","CompareStringA",{LOCALE_INVARIANT,0,0x50010200,1,0x50010200,1},
        []{return ::CompareStringA(LOCALE_INVARIANT,0,"A",1,"A",1);});
    FILETIME fixed{0x12345678,0x01da0000},local{};SYSTEMTIME expected{};
    put(0x50010600,fixed);
    compare("kernel32.dll","FileTimeToSystemTime",{0x50010600,0x50010700},[&]{return ::FileTimeToSystemTime(&fixed,&expected);});
    for(unsigned i=0;i<sizeof(expected);++i) if(memory.load(0x50010700+i,8)!=reinterpret_cast<unsigned char*>(&expected)[i]) return 1;
    compare("kernel32.dll","FileTimeToLocalFileTime",{0x50010600,0x50010700},[&]{return ::FileTimeToLocalFileTime(&fixed,&local);});
    if(memory.load(0x50010700,64)!=(std::uint64_t(local.dwHighDateTime)<<32|local.dwLowDateTime)) return 2;
    // Output aliases its stack argument. Completion must use the pre-call address.
    compare("kernel32.dll","FileTimeToSystemTime",{0x50010600,0x50000808},[&]{return ::FileTimeToSystemTime(&fixed,&expected);});
    for(unsigned i=0;i<sizeof(expected);++i) if(memory.load(0x50000808+i,8)!=reinterpret_cast<unsigned char*>(&expected)[i]) return 3;
    fixed={0,0x80000000};put(0x50010600,fixed);
    for(unsigned i=0;i<16;++i) memory.store(0x50010700+i,0xa5,8);
    compare("kernel32.dll","FileTimeToSystemTime",{0x50010600,0x50010700},[&]{return ::FileTimeToSystemTime(&fixed,&expected);});
    try { (void)memory.load(0x50010700,8);return 4; } catch(const std::runtime_error&) {++guards;}
    (void)invoke("kernel32.dll","GetLocalTime",{0x50010700});
    for(unsigned i=0;i<16;++i) (void)memory.load(0x50010700+i,8);
    SYSTEMTIME before{},after{},actual{};
    ::GetSystemTime(&before);(void)invoke("kernel32.dll","GetSystemTime",{0x50010700});::GetSystemTime(&after);
    for(unsigned i=0;i<16;++i) reinterpret_cast<unsigned char*>(&actual)[i]=std::uint8_t(memory.load(0x50010700+i,8));
    FILETIME b{},a{},v{};if(!::SystemTimeToFileTime(&before,&b) || !::SystemTimeToFileTime(&after,&a) || !::SystemTimeToFileTime(&actual,&v)) return 5;
    auto ticks=[](FILETIME f){return std::uint64_t(f.dwHighDateTime)<<32|f.dwLowDateTime;};
    if(ticks(v)<ticks(b) || ticks(v)>ticks(a)) return 6;
    auto refuse=[&](auto operation){try {operation();throw std::logic_error("missing batch guard");}catch(const std::runtime_error&){++guards;}};
    refuse([&]{(void)invoke("kernel32.dll","CompareStringA",{LOCALE_INVARIANT,0,0x50010200,2,0x50010300,2});});
    refuse([&]{(void)invoke("kernel32.dll","lstrlenW",{0});});
    refuse([&]{(void)invoke("kernel32.dll","lstrlenW",{0x12340});});
    refuse([&]{(void)invoke("kernel32.dll","CompareStringW",{LOCALE_INVARIANT,0,0xfffffff0,32,0x50010400,1});});
    refuse([&]{(void)invoke("kernel32.dll","GetSystemTime",{0x50020000});});
    memory.store_unknown(0x50010600,0,8);
    refuse([&]{(void)invoke("kernel32.dll","FileTimeToSystemTime",{0x50010600,0x50010700});});
    refuse([&]{sharp_retro::State s;invoke_native_import({0,"kernel32.dll","Sleep",true},s,memory);});
    refuse([&]{(void)invoke("other.dll","IsDebuggerPresent",{});});
    std::printf("{\"native_calls\":%u,\"direct_comparisons\":%u,\"refusal_guards\":%u,\"aliased_stack_output\":true,\"counted_input_bounds\":true,\"failed_output_unknown\":true}\n",calls,comparisons,guards);
    return 0;
} catch(const std::exception& e) {std::fprintf(stderr,"native batch: %s\n",e.what());return 10;} }
