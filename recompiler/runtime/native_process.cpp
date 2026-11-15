// Native PE entry composition. Windows loads the replacement image and original
// retained providers; generated C++ executes the pinned entry, never original x86.
#include "functions.hpp"
#include "native_execution.hpp"
#include "native_callback_entry.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <limits>
using namespace recomp_generated;
namespace {
unsigned source_module(std::uint32_t pc) noexcept {
    return pc>=0x400000 && pc<0xded000 ? 0x400000:
           pc>=0x10000000 && pc<0x1011e000 ? 0x10000000:0;
}
bool read_diagnostic_word(std::uint32_t address,std::uint32_t& value) noexcept {
    if(!address || address>0xfffffffcu) return false;
    MEMORY_BASIC_INFORMATION info{};
    if(!::VirtualQuery(reinterpret_cast<const void*>(std::uintptr_t(address)),&info,sizeof(info)) ||
       info.State!=MEM_COMMIT || (info.Type!=MEM_PRIVATE && info.Type!=MEM_IMAGE) ||
       (info.Protect&(PAGE_NOACCESS|PAGE_GUARD)) ||
       std::uint64_t(address)+4>std::uint64_t(reinterpret_cast<std::uintptr_t>(info.BaseAddress))+info.RegionSize)
        return false;
    SIZE_T read=0;
    return ::ReadProcessMemory(::GetCurrentProcess(),reinterpret_cast<const void*>(std::uintptr_t(address)),
                              &value,sizeof(value),&read) && read==sizeof(value);
}
std::uint32_t diagnostic_known32(const sharp_retro::State& state,unsigned index) noexcept {
    return state.defined_gpr&(1u<<index) ? 0xffffffffu:std::uint32_t(state.partial_gpr[index]);
}
void observe_missing_state(const sharp_retro::State& state) noexcept {
    auto incoming_error=::GetLastError();
    char line[2048];std::size_t used=0;bool complete=true;
    auto append=[&](const char* format,auto... values) {
        if(!complete) return;
        auto count=std::snprintf(line+used,sizeof(line)-used,format,values...);
        if(count<0 || std::size_t(count)>=sizeof(line)-used) complete=false;
        else used+=std::size_t(count);
    };
    append("{\"event\":\"native_frontier_state\",\"thread_id\":%lu,\"pc\":%u,\"esp\":%u,\"flags\":%u,\"defined_flags\":%u,\"gpr_raw\":[",
           ::GetCurrentThreadId(),unsigned(state.pc),unsigned(state.gpr[4]),unsigned(state.flags),unsigned(state.defined_flags));
    for(unsigned i=0;i<8;++i) append("%s%u",i ? ",":"",unsigned(state.gpr[i]));
    append("],\"gpr_known32\":[");
    for(unsigned i=0;i<8;++i) append("%s%u",i ? ",":"",unsigned(diagnostic_known32(state,i)));
    std::uint32_t word=0;
    auto readable=diagnostic_known32(state,1)==0xffffffffu && read_diagnostic_word(std::uint32_t(state.gpr[1]),word);
    append("],\"ecx_first_word\":");
    if(readable) append("%u",unsigned(word));else append("null");
    append(",\"stack_words\":[");
    for(unsigned i=0;diagnostic_known32(state,4)==0xffffffffu && i<16;++i) {
        auto address=std::uint64_t(std::uint32_t(state.gpr[4]))+i*4;
        if(address>0xffffffffu || !read_diagnostic_word(std::uint32_t(address),word)) break;
        append("%s%u",i ? ",":"",unsigned(word));
    }
    append("],\"last_error\":%lu,\"game_acceptance\":false}\n",incoming_error);
    if(complete){std::fwrite(line,1,used,stderr);std::fflush(stderr);}
    ::SetLastError(incoming_error);
}
[[noreturn]] sharp_retro::Exit stop_missing_step(sharp_retro::State& state,sharp_retro::Memory&,std::uint64_t&) {
    // A missing dispatch target has executed no instruction. Record it and stop;
    // do not unwind a host diagnostic exception through live game SEH frames.
    observe_missing_state(state);
    std::uint32_t source_return=0;
    auto readable=diagnostic_known32(state,4)==0xffffffffu &&
                  read_diagnostic_word(std::uint32_t(state.gpr[4]),source_return);
    std::fprintf(stderr,"{\"event\":\"native_startup_frontier\",\"origin\":\"uncompiled_dispatch\",\"thread_id\":%lu,\"module\":%u,\"pc\":%u,\"esp\":%u,\"call_return\":%u,\"return_word_readable\":%s,\"reason\":\"untranslated guest code/import target\",\"game_acceptance\":false}\n",
                 ::GetCurrentThreadId(),source_module(std::uint32_t(state.pc)),unsigned(state.pc),unsigned(state.gpr[4]),
                 unsigned(source_return),readable ? "true":"false");
    std::fflush(stderr);std::fflush(stdout);
    ::TerminateProcess(::GetCurrentProcess(),3);std::abort();
}
GuestStep(*previous_extra_step)(std::uint32_t)=nullptr;
GuestStep missing_step_observer(std::uint32_t address) {
    if(previous_extra_step) if(auto step=previous_extra_step(address)) return step;
    if(!source_module(address)) return nullptr;
    // Preserve the import-dispatch order and all successful existing resolvers.
    for(const auto& entry:declared_imports()) if(entry.address==address) return nullptr;
    return stop_missing_step;
}
void require_permanent_execution_protection() {
    static const bool installed=[] {
        // Some retained x86 SDKs disable DEP while loading. Read-only PE data
        // alone then permits original instruction bytes to execute. Permanently
        // enable DEP before entering translated code so callbacks must cross the
        // entry bridge rather than silently executing the original image.
        auto enabled=::SetProcessDEPPolicy(PROCESS_DEP_ENABLE|PROCESS_DEP_DISABLE_ATL_THUNK_EMULATION);
        auto error=enabled ? ERROR_SUCCESS : ::GetLastError();
        DWORD flags=0;BOOL permanent=FALSE;
        if(!::GetProcessDEPPolicy(::GetCurrentProcess(),&flags,&permanent) ||
           !(flags&PROCESS_DEP_ENABLE) || !permanent)
            throw std::runtime_error("permanent native execute protection unavailable; original callback execution cannot be excluded; policy error "+std::to_string(error));
        std::fprintf(stderr,"{\"event\":\"native_execution_policy\",\"dep_flags\":%lu,\"permanent\":true,\"game_acceptance\":false}\n",flags);
        std::fflush(stderr);
        return true;
    }();
    (void)installed;
}
LONG CALLBACK observe_native_execute(EXCEPTION_POINTERS* exception) {
    auto incoming_error=::GetLastError();
    auto* record=exception->ExceptionRecord;auto* context=exception->ContextRecord;
    auto pc=unsigned(context->Eip);
    unsigned base=pc>=0x400000 && pc<0xded000 ? 0x400000:
                  pc>=0x10000000 && pc<0x1011e000 ? 0x10000000:0;
    auto exception_line=std::string("{\"event\":\"native_exception_observed\",\"code\":")+std::to_string(record->ExceptionCode)+
        ",\"pc\":"+std::to_string(pc)+",\"esp\":"+std::to_string(context->Esp)+",\"parameters\":[";
    for(unsigned i=0;i<record->NumberParameters && i<EXCEPTION_MAXIMUM_PARAMETERS;++i)
        exception_line+=(i ? ",":"")+std::to_string(record->ExceptionInformation[i]);
    exception_line+="],\"game_acceptance\":false}\n";
    std::fwrite(exception_line.data(),1,exception_line.size(),stderr);std::fflush(stderr);
    if(!base || !native_callback::is_execute_fault(exception)) {
        ::SetLastError(incoming_error);
        return EXCEPTION_CONTINUE_SEARCH;
    }
    try {
        auto entry=context->Eip;
        ::SetLastError(incoming_error);
        if(native_callback::schedule(exception)) {
            std::fprintf(stderr,"{\"event\":\"native_callback_entry\",\"pc\":%lu,\"game_acceptance\":false}\n",entry);std::fflush(stderr);
            return EXCEPTION_CONTINUE_EXECUTION;
        }
    } catch(const std::exception& error) {
        std::fprintf(stderr,"native callback entry refused: %s\n",error.what());std::fflush(stderr);
    }
    DWORD call_return=0;SIZE_T size=0;
    auto readable=::ReadProcessMemory(::GetCurrentProcess(),reinterpret_cast<LPCVOID>(std::uintptr_t(context->Esp)),
                                      &call_return,sizeof(call_return),&size);
    DWORD words[24]{};SIZE_T word_bytes=0;
    ::ReadProcessMemory(::GetCurrentProcess(),reinterpret_cast<LPCVOID>(std::uintptr_t(context->Esp)),words,sizeof(words),&word_bytes);
    auto stack_line=std::string("{\"event\":\"native_callback_stack\",\"pc\":")+std::to_string(pc)+",\"words\":[";
    for(unsigned i=0;i<word_bytes/4;++i)stack_line+=(i ? ",":"")+std::to_string(words[i]);
    stack_line+="],\"game_acceptance\":false}\n";std::fwrite(stack_line.data(),1,stack_line.size(),stderr);std::fflush(stderr);
    std::fprintf(stderr,"{\"event\":\"native_callback_frontier\",\"module\":%u,\"pc\":%u,\"esp\":%u,\"call_return\":%u,\"return_word_readable\":%s,\"reason\":\"native execute transfer into translated image requires an entry bridge\",\"game_acceptance\":false}\n",
                 base,pc,unsigned(context->Esp),unsigned(call_return),readable && size==4 ? "true":"false");
    std::fflush(stderr);std::fflush(stdout);
    // These pages contain data, never callable original instructions. Preserve
    // the observed target and stop instead of falling back or returning zero.
    ::TerminateProcess(::GetCurrentProcess(),3);return EXCEPTION_CONTINUE_SEARCH;
}
void install_execute_observer() {
    static const bool installed=[] {
        native_callback::initialize();
        native_callback::observe_frontier_state=observe_missing_state;
        previous_extra_step=extra_guest_step;
        extra_guest_step=missing_step_observer;
        native_callback::adopt_images=[](NativeX86Memory& memory){memory.adopt_native_image(0x400000,0x9ed000);memory.adopt_native_image(0x10000000,0x11e000);};
        if(!::AddVectoredExceptionHandler(1,observe_native_execute)) throw std::runtime_error("cannot install native execute observer");
        return true;
    }();
    (void)installed;
}
void observe_loader_tls(unsigned base) {
    auto* image=reinterpret_cast<const unsigned char*>(std::uintptr_t(base));
    auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(image);
    auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS32*>(image+dos->e_lfanew);
    auto directory=pe->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_TLS];
    if(!directory.VirtualAddress) return;
    auto* tls=reinterpret_cast<const IMAGE_TLS_DIRECTORY32*>(image+directory.VirtualAddress);
    auto index=*reinterpret_cast<const DWORD*>(std::uintptr_t(tls->AddressOfIndex));
    unsigned vector;asm volatile("movl %%fs:0x2c,%0":"=r"(vector));
    auto storage=reinterpret_cast<const DWORD*>(std::uintptr_t(vector))[index];
    std::fprintf(stderr,"{\"event\":\"windows_loader_tls\",\"module\":%u,\"index\":%u,\"thread_storage\":%u,\"template_size\":%u}\n",
                 base,unsigned(index),unsigned(storage),unsigned(tls->EndAddressOfRawData-tls->StartAddressOfRawData));std::fflush(stderr);
}
std::string json_string(const char* text) {
    std::string result="\"";
    for(auto* cursor=reinterpret_cast<const unsigned char*>(text);*cursor;++cursor) {
        if(*cursor=='"' || *cursor=='\\') {result+='\\';result+=char(*cursor);}
        else if(*cursor<32) {char escaped[7];std::snprintf(escaped,sizeof(escaped),"\\u%04x",unsigned(*cursor));result+=escaped;}
        else result+=char(*cursor);
    }
    return result+'"';
}
struct Stack {
    static constexpr unsigned size=16*1024*1024;
    void* pointer=::VirtualAlloc(nullptr,size,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    Stack(){if(!pointer) throw std::runtime_error("cannot allocate translated execution stack");}
    ~Stack(){if(pointer) ::VirtualFree(pointer,0,MEM_RELEASE);}
};
unsigned execute_entry(unsigned image_base,unsigned image_extent,unsigned entry,bool is_dll,
                       HINSTANCE instance,unsigned reason,void* reserved) {
    NativeX86Memory memory;
    memory.adopt_native_image(image_base,image_extent);
    // Both modules share this real address space. Register the other pinned
    // namespace too so missing translated entries never fall into native code.
    if(image_base!=0x400000 && ::GetModuleHandleW(nullptr)==reinterpret_cast<HMODULE>(0x400000))
        memory.adopt_native_image(0x400000,0x9ed000);
    if(image_base!=0x10000000 && ::GetModuleHandleW(L"umbra.dll")==reinterpret_cast<HMODULE>(0x10000000))
        memory.adopt_native_image(0x10000000,0x11e000);
    observe_loader_tls(0x400000);
    Stack stack;
    auto low=std::uint32_t(reinterpret_cast<std::uintptr_t>(stack.pointer)),high=low+Stack::size;
    memory.add_native_stack(low,high);
    sharp_retro::State state;capture_native_context(state);
    state.gpr[4]=high-4096;
    // The stop address is a native compiled function, used only as an observed
    // return sentinel in the dispatcher. No fake executable address is mapped.
    auto stop=std::uint32_t(reinterpret_cast<std::uintptr_t>(&execute_entry));
    memory.store(state.gpr[4],stop,32);
    if(is_dll) {
        memory.store(state.gpr[4]+4,reinterpret_cast<std::uintptr_t>(instance),32);
        memory.store(state.gpr[4]+8,reason,32);
        memory.store(state.gpr[4]+12,reinterpret_cast<std::uintptr_t>(reserved),32);
    }
    auto initial_sp=state.gpr[4];
    auto budget=native_callback::configured_instruction_budget();
    auto initial_budget=budget;
    native_callback::Binding callback_binding(memory,budget);
    std::fprintf(stderr,"{\"event\":\"native_translated_entry\",\"entry\":%u,\"module\":%u,\"reason\":%u,\"stack_low\":%u,\"stack_high\":%u}\n",
                 entry,image_base,reason,low,high);std::fflush(stderr);
    try {
        auto result=execute_guest(entry,stop,state,memory,budget);
        if(result!=sharp_retro::Exit::returned) throw std::runtime_error("translated native entry exhausted its execution budget");
        if(is_dll && state.gpr[4]!=initial_sp+16) throw std::runtime_error("DLL entry returned with incorrect stack cleanup");
        std::fprintf(stderr,"{\"event\":\"native_translated_return\",\"module\":%u,\"reason\":%u,\"eax\":%u,\"consumed\":%llu,\"game_acceptance\":false}\n",
                     image_base,reason,unsigned(state.gpr[0]),(unsigned long long)(initial_budget-budget));std::fflush(stderr);
        return unsigned(state.gpr[0]);
    } catch(const std::exception& error) {
        auto reason_json=json_string(error.what());
        auto sp=state.gpr[4];unsigned call_return=(sp>=low && sp<=high-4) ? unsigned(memory.load(sp,32)):0;
        std::fprintf(stderr,"{\"event\":\"native_startup_frontier\",\"module\":%u,\"pc\":%u,\"esp\":%u,\"call_return\":%u,\"flags\":%u,\"defined_flags\":%u,\"defined_gpr\":%u,\"consumed\":%llu,\"reason\":%s,\"game_acceptance\":false}\n",
                     image_base,unsigned(state.pc),unsigned(state.gpr[4]),call_return,unsigned(state.flags),unsigned(state.defined_flags),unsigned(state.defined_gpr),
                     (unsigned long long)(initial_budget-budget),reason_json.c_str());std::fflush(stderr);
        throw;
    }
}
}
extern "C" __declspec(dllexport) unsigned __cdecl recomp_native_entry(unsigned base,unsigned extent,unsigned entry,unsigned is_dll,
                                                                       HINSTANCE instance,unsigned reason,void* reserved) {
    try {require_permanent_execution_protection();install_execute_observer();return execute_entry(base,extent,entry,is_dll!=0,instance,reason,reserved);}
    catch(const std::exception& error) {
        std::fprintf(stderr,"native translated process stopped: %s\n",error.what());std::fflush(stderr);
        std::fflush(stdout);
        // Missing semantics cannot be converted to a successful game return or
        // cross an unknown native unwind boundary. Keep the diagnostic, stop.
        ::TerminateProcess(::GetCurrentProcess(),3);std::abort();
    }
}
