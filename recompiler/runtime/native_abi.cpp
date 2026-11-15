#include "native_abi.hpp"
#if defined(_WIN32) && defined(__i386__)
#include "native_abi_frame.hpp"
#include "native_floating.hpp"
#include "native_access.hpp"
#include "native_error.hpp"
#include "native_provider_identity.hpp"
#include <map>
#include <mutex>
#include <atomic>
#include <cstdio>
#include <cstdlib>
extern "C" {DWORD recomp_native_abi_tls_slot=TLS_OUT_OF_INDEXES;}
namespace recomp_generated {
namespace {
std::once_flag initialized;
std::mutex module_mutex;
std::map<std::string,HMODULE> modules;
std::atomic<std::uint64_t> trace_serial{0};
bool trace_enabled() {
    static const bool enabled=[] {auto* value=std::getenv("RECOMP_TRACE_NATIVE_CALLS");return value && std::strcmp(value,"1")==0;}();
    return enabled;
}
std::string trace_quote(const char* value) {
    std::string result="\"";
    for(auto* p=reinterpret_cast<const unsigned char*>(value);*p;++p) {
        if(*p=='"' || *p=='\\') {result+='\\';result+=char(*p);}
        else if(*p<32) {char text[7];std::snprintf(text,sizeof(text),"\\u%04x",unsigned(*p));result+=text;}
        else result+=char(*p);
    }
    return result+'"';
}
void trace_line(const std::string& line) {
    // One stdio write per record keeps concurrent entry/exit records intact.
    std::fwrite(line.data(),1,line.size(),stderr);std::fflush(stderr);
}
// Keep real TEB state across bridge bookkeeping and C++ local destruction.
// This is declared first in public entry points so it restores last.
struct NativeLastError {
    DWORD value=::GetLastError();
    ~NativeLastError() {::SetLastError(value);}
};
std::string lower(std::string value) {for(auto& c:value) if(c>='A' && c<='Z') c+=32;return value;}
void initialize() {
    std::call_once(initialized,[]{
        auto slot=::TlsAlloc();
        if(slot>=64) {if(slot!=TLS_OUT_OF_INDEXES) ::TlsFree(slot);throw std::runtime_error("native ABI requires an inline x86 TEB TLS slot");}
        recomp_native_abi_tls_slot=slot;
    });
}
void invoke(std::uint32_t target,sharp_retro::State& state,sharp_retro::Memory& memory,DWORD& last_error,const char* provider) {
    auto* execution=dynamic_cast<NativeExecution*>(&memory);
    if(!execution) throw std::runtime_error("native ABI requires the native execution address-space contract");
    if(state.segments[2] || sharp_retro::read_flags(state,10)) throw std::runtime_error("native ABI requires flat SS and clear DF");
    if(sharp_retro::read_flags(state,8) || sharp_retro::read_flags(state,14) || sharp_retro::read_flags(state,18))
        throw std::runtime_error("native ABI trap/alignment/task exception transport is not implemented");
    constexpr std::uint32_t forwarded_flags=0x200cd5u; // Arithmetic flags, DF and user-mode ID.
    if((state.defined_flags&forwarded_flags)!=forwarded_flags) {
        std::string message="native ABI input flags have no concrete CPU observation";
        for(unsigned bit=0;bit<32;++bit) if((forwarded_flags&(1u<<bit)) && !(state.defined_flags&(1u<<bit)))
            message+="; bit "+std::to_string(bit)+" producer "+std::to_string(sharp_retro::native_undefined_flag_pc(state,bit));
        throw std::runtime_error(message);
    }
    NativeAbiFrame frame{};frame.split_mmx=native_mmx_is_split();frame.input_mmx=state.native_mmx;
    if(frame.split_mmx && state.defined_native_mmx!=0xff)throw std::runtime_error("native ABI input MMX state has not been captured");
    frame.target=target;frame.flags=std::uint32_t(state.flags)&forwarded_flags;frame.flags|=0x202;
    for(unsigned i=0;i<8;++i) frame.gpr[i]=std::uint32_t(sharp_retro::read_gpr(state,i));
    auto bounds=execution->native_stack(frame.gpr[4]);frame.stack_low=bounds.first;frame.stack_high=bounds.second;
    if((state.defined_xmm&0xff)!=0xff) throw std::runtime_error("native ABI input SIMD state has not been captured");
    validate_native_fp(state,false);
    std::uint64_t trace_id=0;
    if(trace_enabled()) {
        trace_id=trace_serial.fetch_add(1,std::memory_order_relaxed)+1;
        auto line=std::string("{\"event\":\"native_abi_enter\",\"id\":")+std::to_string(trace_id)+
            ",\"thread_id\":"+std::to_string(::GetCurrentThreadId())+",\"target\":"+std::to_string(target)+
            ",\"provider\":"+trace_quote(provider)+",\"esp\":"+std::to_string(frame.gpr[4])+",\"stack_words\":[";
        auto count=std::min<std::uint32_t>(9,(frame.stack_high-frame.gpr[4])/4);
        for(unsigned i=0;i<count;++i) {if(i) line+=',';line+=std::to_string(std::uint32_t(memory.load(frame.gpr[4]+i*4,32)));}
        trace_line(line+"]}\n");
    }
    initialize();
    auto previous=::TlsGetValue(recomp_native_abi_tls_slot);
    if(!::TlsSetValue(recomp_native_abi_tls_slot,&frame)) throw std::runtime_error("cannot bind native call frame");
    {
        NativeFloatingScope floating(state,false);
        // Preserve full tags independently of FXRSTOR. The current Wine/ARM64
        // host misclassifies a live FLD1 tag in a direct FXSAVE/FXRSTOR control.
        asm volatile("fnsave %0\n\tfrstor %0" : "=m"(frame.input_x87) : : "memory");
        asm volatile("fxsave %0" : "=m"(frame.input_fx) : : "memory");
        for(unsigned i=0;i<8;++i) std::memcpy(frame.input_fx.data()+160+i*16,&state.xmm[i],16);
        ::SetLastError(last_error);
        recomp_native_abi_call(&frame);
        last_error=frame.last_error;
        // The assembly restores the host FP snapshot it entered with. The
        // outer floating scope subsequently restores the original C++ host FP.
    }
    if(!::TlsSetValue(recomp_native_abi_tls_slot,previous)) throw std::runtime_error("cannot restore native call frame binding");
#if !defined(RECOMP_NATIVE_EXECUTION)
    native_error_context.value=frame.last_error;
#endif
    for(unsigned i=0;i<8;++i) {state.gpr[i]=frame.gpr[i];state.partial_gpr[i]=0;state.gpr_origins[i]={};}
    state.defined_gpr|=0xff;state.flags=frame.flags;state.defined_flags=0xffffffffu;state.flag_origins={};state.pc=frame.return_pc;
    NativeX87Image x87;std::memcpy(x87.data(),frame.output_x87.data(),108);std::uint32_t mxcsr;
    std::memcpy(&mxcsr,frame.output_fx.data()+24,4);read_native_fp_image(state,x87,mxcsr,false);
    auto top=(state.x87_status>>11)&7;
    for(unsigned i=0;i<8;++i) if(((state.x87_tag>>(((top+i)&7)*2))&3)!=3) state.defined_x87_st|=std::uint8_t(1u<<i);
    for(unsigned i=0;i<8;++i) std::memcpy(&state.xmm[i],frame.output_fx.data()+160+i*16,16);
    state.defined_xmm|=0xff;state.native_mmx=frame.output_mmx;state.defined_native_mmx=0xff;
    if(trace_id) trace_line(std::string("{\"event\":\"native_abi_exit\",\"id\":")+std::to_string(trace_id)+
        ",\"thread_id\":"+std::to_string(::GetCurrentThreadId())+",\"pc\":"+std::to_string(frame.return_pc)+
        ",\"esp\":"+std::to_string(frame.gpr[4])+",\"eax\":"+std::to_string(frame.gpr[0])+"}\n");
}
}
bool uses_native_execution(sharp_retro::Memory& memory) {return dynamic_cast<NativeExecution*>(&memory)!=nullptr;}
void capture_native_context(sharp_retro::State& state) {
    auto initial_error=::GetLastError();
    NativeAbiFrame frame{};recomp_native_abi_capture(&frame);state={};
    for(unsigned i=0;i<8;++i) state.gpr[i]=frame.gpr[i];
    state.defined_gpr=0xff;state.flags=frame.flags;state.defined_flags=0xffffffffu;
    state.segments[4]=reinterpret_cast<std::uintptr_t>(::NtCurrentTeb());
    NativeX87Image image;std::memcpy(image.data(),frame.output_x87.data(),108);std::uint32_t mxcsr;
    std::memcpy(&mxcsr,frame.output_fx.data()+24,4);state.mxcsr_mask=native_mxcsr_mask();read_native_fp_image(state,image,mxcsr,false);
    auto top=(state.x87_status>>11)&7;
    for(unsigned i=0;i<8;++i) if(((state.x87_tag>>(((top+i)&7)*2))&3)!=3) state.defined_x87_st|=std::uint8_t(1u<<i);
    for(unsigned i=0;i<8;++i) std::memcpy(&state.xmm[i],frame.output_fx.data()+160+i*16,16);
    state.defined_xmm=0xff;state.native_mmx=frame.output_mmx;state.defined_native_mmx=0xff;
#if !defined(RECOMP_NATIVE_EXECUTION)
    native_error_context.value=initial_error;
#endif
    ::SetLastError(initial_error);
}
void invoke_native_abi_import(const ImportEntry& entry,sharp_retro::State& state,sharp_retro::Memory& memory) {
    NativeLastError last_error;
    auto library=lower(entry.library);
    if(entry.translated_module || library=="umbra.dll" || library=="daorigins.exe")
        throw std::runtime_error("native fallback forbidden for translated game modules");
    HMODULE module=nullptr;
    {
        std::lock_guard guard(module_mutex);auto found=modules.find(library);
        if(found!=modules.end()) module=found->second;
    }
    if(!module) {
        // DLL initialization can reenter application code. Never hold a C++
        // registry lock across the Windows loader or DLL attach callbacks.
        auto loaded=::LoadLibraryA(library.c_str());if(!loaded) throw std::runtime_error("native import provider failed to load: "+library);
        bool inserted;
        {std::lock_guard guard(module_mutex);auto result=modules.emplace(library,loaded);module=result.first->second;inserted=result.second;}
        if(!inserted) ::FreeLibrary(loaded);
    }
    const char* symbol=entry.symbol;std::string spelling=symbol;
    if(spelling.starts_with("@ordinal:")) {
        auto value=std::stoul(spelling.substr(9));if(!value || value>65535) throw std::runtime_error("invalid native import ordinal");
        symbol=MAKEINTRESOURCEA(value);
    }
    auto target=::GetProcAddress(module,symbol);
    if(!target) throw std::runtime_error("native export is missing: "+library+"!"+entry.symbol);
    invoke(std::uint32_t(reinterpret_cast<std::uintptr_t>(target)),state,memory,last_error.value,library.c_str());
}
bool invoke_native_abi_address(std::uint32_t target,sharp_retro::State& state,sharp_retro::Memory& memory) {
    NativeLastError last_error;
    auto* backing=dynamic_cast<NativeAccess*>(&memory);
    if(!uses_native_execution(memory) || !backing || backing->guest_image_address(target)) return false;
    HMODULE module=nullptr;
    if(!::GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                           reinterpret_cast<LPCSTR>(std::uintptr_t(target)),&module)) return false;
    auto name=native_provider_identity(module);
    if(name=="umbra.dll" || (name=="daorigins.exe" && module!=::GetModuleHandleW(nullptr)))
        throw std::runtime_error("native indirect fallback forbidden for original game code");
    MEMORY_BASIC_INFORMATION info{};
    if(!::VirtualQuery(reinterpret_cast<LPCVOID>(std::uintptr_t(target)),&info,sizeof(info)) || info.State!=MEM_COMMIT ||
       (info.Protect&(PAGE_GUARD|PAGE_NOACCESS)) || !(info.Protect&(PAGE_EXECUTE|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY))) return false;
    invoke(target,state,memory,last_error.value,name.c_str());return true;
}
}
#endif
