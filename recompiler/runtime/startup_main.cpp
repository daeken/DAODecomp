// Startup exploration: execute translated entries, stop explicitly at a frontier.
// This is a partial Windows process loader; only declared thread fields exist.
#include "runtime_api.hpp"
#include "process_memory.hpp"
#include "win32_memory.hpp"
#include "native_imports.hpp"
#include "image_tls.hpp"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#if defined(_WIN32) && defined(RECOMP_LIVE_CANDIDATES)
#include "live_candidates.hpp"
#endif

static std::string json_string(const std::string& value) {
    std::string out="\"";
    for(unsigned char c:value) {
        if(c=='"' || c=='\\') { out+='\\'; out+=char(c); }
        else if(c=='\n') out+="\\n";
        else if(c=='\r') out+="\\r";
        else if(c<32) { char escaped[7]; std::snprintf(escaped,sizeof escaped,"\\u%04x",c); out+=escaped; }
        else out+=char(c);
    }
    return out+'"';
}
#if defined(_WIN32) && defined(RECOMP_FLAT_MEMORY)
extern "C" __declspec(dllimport) unsigned char recomp_guestspace_marker;
using ProcessBacking=recomp_generated::Win32ProcessMemory;
#else
using ProcessBacking=recomp_generated::ProcessMemory;
#endif
struct StartupMemory : ProcessBacking {
    std::array<bool,4096> thread_known{};
    sharp_retro::State* state=nullptr;
    struct Trace {
        std::uint32_t pc,address,width;
        sharp_retro::bits payload;
        std::array<std::uint32_t,8> gpr,known;
        std::uint32_t flags,defined_flags;
        bool write;
    };
    std::array<Trace,256> trace{};
    std::uint64_t trace_count=0;
    bool trace_enabled=std::getenv("RECOMP_TRACE_MEMORY") && std::strcmp(std::getenv("RECOMP_TRACE_MEMORY"),"1")==0;
    void record_trace(std::uint64_t address,unsigned width,sharp_retro::bits payload,bool write) {
        if(!trace_enabled || !state || state->pc<0x400000 || state->pc>=0x1000000) return;
        // Retain all main-image writes (including call-stack updates), and reads
        // in the repeating node routines. This is a bounded diagnostic only.
        if(!write && (state->pc<0x4b9b20 || state->pc>=0x4b9bc2)) return;
        auto& item=trace[trace_count++%trace.size()];
        item.pc=std::uint32_t(state->pc); item.address=std::uint32_t(address); item.width=width;
        item.payload=payload; item.write=write; item.flags=std::uint32_t(state->flags); item.defined_flags=std::uint32_t(state->defined_flags);
        for(unsigned i=0;i<8;i++) {
            item.gpr[i]=std::uint32_t(state->gpr[i]);
            item.known[i]=(state->defined_gpr&(1u<<i)) ? 0xffffffffu : std::uint32_t(state->partial_gpr[i]);
        }
    }
    void dump_trace() const {
        auto begin=trace_count>trace.size() ? trace_count-trace.size() : 0;
        for(auto index=begin;index<trace_count;index++) {
            const auto& item=trace[index%trace.size()];
            std::printf("{\"event\":\"memory_history\",\"sequence\":%llu,\"pc\":%u,\"address\":%u,\"width\":%u,\"write\":%s,\"payload_only\":true,\"payload\":[%u,%u,%u,%u],\"gpr\":[",
                        (unsigned long long)index,item.pc,item.address,item.width,item.write ? "true" : "false",
                        unsigned(item.payload),unsigned(item.payload>>32),unsigned(item.payload>>64),unsigned(item.payload>>96));
            for(unsigned i=0;i<8;i++) std::printf("%s%u",i ? "," : "",item.gpr[i]);
            std::fputs("],\"gpr_known\":[",stdout);
            for(unsigned i=0;i<8;i++) std::printf("%s%u",i ? "," : "",item.known[i]);
            std::printf("],\"flags\":%u,\"defined_flags\":%u}\n",item.flags,item.defined_flags);
        }
    }
    void check_thread(std::uint64_t address,unsigned width) {
        if(address>=0x60000000 && address<0x60001000)
            for(unsigned i=0;i<width/8;i++)
                if(address-0x60000000+i>=thread_known.size() || !thread_known[address-0x60000000+i])
                    throw std::runtime_error("unimplemented thread/TEB field");
    }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        try { check_thread(address,width); auto value=ProcessBacking::load(address,width); record_trace(address,width,value,false); return value; }
        catch(const sharp_retro::UnknownMemoryRead&) { throw; }
        catch(const std::exception& e) {
            std::printf("{\"event\":\"memory_fault\",\"pc\":%llu,\"address\":%llu,\"width\":%u,\"write\":false,\"reason\":%s}\n",
                        (unsigned long long)(state ? state->pc : 0),(unsigned long long)address,width,json_string(e.what()).c_str());
            throw;
        }
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        ProcessBacking::store(address,value,width);
        record_trace(address,width,value,true);
        if(address>=0x60000000 && address<0x60001000)
            for(unsigned i=0;i<width/8;i++) thread_known.at(std::size_t(address-0x60000000+i))=true;
    }
};
static unsigned import_calls=0;
static std::uint64_t native_trace_limit=0,native_trace_suppressed=0;
static StartupMemory* callback_memory=nullptr;
static sharp_retro::State* startup_state=nullptr;
static std::uint64_t* startup_budget=nullptr;
static std::uint64_t startup_initial_budget=0;
static unsigned callback_depth=0;
#ifdef _WIN32
static DWORD startup_thread=0;
#endif
[[noreturn]] static void end_exploration(unsigned code) {
    std::fflush(nullptr);
#ifdef _WIN32
    // This is a stopped, incomplete exploration, not normal game shutdown. In
    // particular, do not invoke FLS callbacks after destroying their guest memory.
    ::TerminateProcess(::GetCurrentProcess(),code);
#endif
    std::_Exit(int(code));
}
static void native_call(const recomp_generated::ImportEntry&,sharp_retro::State&,sharp_retro::Memory&);
#ifdef _WIN32
[[noreturn]] static void unhandled_frontier(std::uint32_t target,EXCEPTION_POINTERS* pointers) noexcept {
    auto* record=pointers ? pointers->ExceptionRecord : nullptr;
    auto consumed=::GetCurrentThreadId()==startup_thread && startup_budget ? startup_initial_budget-*startup_budget : 0;
    std::printf("{\"event\":\"startup_frontier\",\"reason\":\"native exception-filter callback requires guest EXCEPTION_POINTERS/context transport\",\"pc\":%u,\"callback_target\":%u,\"native_callback\":true,\"native_exception_code\":%u,\"native_exception_address\":%u,\"consumed\":%llu,\"game_started\":false}\n",
                target,target,record ? unsigned(record->ExceptionCode) : 0,
                record ? unsigned(reinterpret_cast<std::uintptr_t>(record->ExceptionAddress)) : 0,
                (unsigned long long)consumed);
    end_exploration(3);
}
#endif
static void run_fls_callback(std::uint32_t target,std::uint32_t value) {
#ifdef _WIN32
    recomp_generated::native_error_context.value=::GetLastError();
#endif
    sharp_retro::State state; state.pc=target;
    std::uint16_t entry_control=0; std::uint32_t entry_mxcsr=0;
    auto* previous_state=callback_memory ? callback_memory->state : nullptr;
    try {
#ifdef _WIN32
        if(recomp_generated::native_floating_bridge_enabled) recomp_generated::capture_native_fp(state);
#endif
        entry_control=state.x87_control; entry_mxcsr=state.mxcsr;
#ifdef _WIN32
        if(::GetCurrentThreadId()!=startup_thread) throw std::runtime_error("callback from unimplemented guest thread context");
#endif
        if(!callback_memory || !startup_budget || callback_depth>=64) throw std::runtime_error("callback context/capacity unavailable");
        ++callback_depth;
        auto stack=0x51000000u+callback_depth*0x4000u-0x100u;
        state.gpr[4]=stack; state.gpr[3]=0xaabbccdd; state.gpr[5]=0x33445566;
        state.gpr[6]=0x778899aa; state.gpr[7]=0xbbccddee;
        sharp_retro::invalidate_gprs(state,7); state.defined_flags=std::uint64_t(1)<<10; state.flag_origins={};
        state.defined_xmm=0;
        for(unsigned i=0;i<6;i++) state.segments[i]=startup_state->segments[i];
        callback_memory->state=&state;
        callback_memory->store(stack,0x12345678,32); callback_memory->store(stack+4,value,32);
        std::printf("{\"event\":\"callback_begin\",\"target\":%u,\"argument\":%u}\n",target,value);
        auto result=recomp_generated::execute_guest(target,0x12345678,state,*callback_memory,*startup_budget,native_call);
        if(result!=sharp_retro::Exit::returned || state.pc!=0x12345678 || state.gpr[4]!=stack+8 ||
           (state.defined_gpr&0xf8)!=0xf8 ||
           state.gpr[3]!=0xaabbccdd || state.gpr[5]!=0x33445566 || state.gpr[6]!=0x778899aa || state.gpr[7]!=0xbbccddee)
            throw std::runtime_error("FLS callback did not complete its stdcall/nonvolatile obligations");
#ifdef _WIN32
        if(recomp_generated::native_floating_bridge_enabled) {
            if(state.x87_control!=entry_control || (state.mxcsr&0xffc0)!=(entry_mxcsr&0xffc0))
                throw std::runtime_error("FLS callback changed nonvolatile floating-point control");
            recomp_generated::install_native_fp(state);
        }
#endif
        std::printf("{\"event\":\"callback_return\",\"target\":%u}\n",target);
        --callback_depth; callback_memory->state=previous_state;
    } catch(const std::exception& e) {
        std::printf("{\"event\":\"startup_frontier\",\"reason\":%s,\"pc\":%u,\"esp\":%u,\"callback_target\":%u,\"native_callback\":true,\"consumed\":%llu,\"game_started\":false}\n",
                    json_string(e.what()).c_str(),unsigned(state.pc),unsigned(state.gpr[4]),target,
                    (unsigned long long)(startup_initial_budget-(startup_budget ? *startup_budget : 0)));
        end_exploration(3);
    }
}
static void binding_trace(const char* event,std::uint32_t address,const char* library,const char* symbol) {
    std::printf("{\"event\":%s,\"address\":%u,\"library\":%s,\"symbol\":%s}\n",json_string(event).c_str(),address,
                json_string(library).c_str(),json_string(symbol).c_str());
}
static void native_call(const recomp_generated::ImportEntry& entry,sharp_retro::State& state,sharp_retro::Memory& memory) {
    ++import_calls;
    auto log_call=[&] {
        std::printf("{\"event\":\"native_call\",\"library\":%s,\"symbol\":%s,\"pc\":%u,\"esp\":%u}\n",
                json_string(entry.library).c_str(),json_string(entry.symbol).c_str(),unsigned(state.pc),unsigned(state.gpr[4]));
        std::fflush(stdout);
    };
    bool logged=!native_trace_limit || import_calls<=native_trace_limit || import_calls%10000==0;
    if(logged) log_call(); else ++native_trace_suppressed;
    try { recomp_generated::invoke_native_import(entry,state,memory); }
    catch(...) { if(!logged) { --native_trace_suppressed; log_call(); } throw; }
    if(logged) std::printf("{\"event\":\"native_return\",\"pc\":%u,\"eax\":%u,\"eax_defined\":%s}\n",
                unsigned(state.pc),unsigned(state.gpr[0]),(state.defined_gpr&1) ? "true" : "false");
}
#ifdef _WIN32
static std::wstring read_launch_text(const wchar_t* name) {
    std::vector<wchar_t> text(32768);
    auto count=::GetEnvironmentVariableW(name,text.data(),DWORD(text.size()));
    if(!count || count>=text.size()) throw std::runtime_error("missing or oversized logical process launch setting");
    return {text.data(),count};
}
static std::string launch_ansi(const std::wstring& text) {
    BOOL lossy=FALSE; bool utf8=::GetACP()==CP_UTF8;
    auto flags=utf8 ? WC_ERR_INVALID_CHARS : WC_NO_BEST_FIT_CHARS;
    auto* used=utf8 ? nullptr : &lossy;
    auto count=::WideCharToMultiByte(CP_ACP,flags,text.c_str(),int(text.size()+1),nullptr,0,nullptr,used);
    if(!count || lossy || count>65536) throw std::runtime_error("logical launch setting cannot be represented in the process ANSI code page");
    std::string result(std::size_t(count),0);
    if(!::WideCharToMultiByte(CP_ACP,flags,text.c_str(),int(text.size()+1),result.data(),count,nullptr,used) || lossy)
        throw std::runtime_error("logical launch setting conversion failed");
    result.resize(std::size_t(count)-1); return result;
}
#endif
static void entry_context(sharp_retro::State& state,const wchar_t* fp_setting) {
    state={}; state.gpr[4]=0x500ff000; state.flags=0x202; state.segments[4]=0x60000000;
    // Payload zeros are not incoming register values. Only ESP and clear DF
    // are declared by this partial entry contract.
    state.defined_gpr=std::uint16_t(1u<<4); state.defined_flags=std::uint64_t(1)<<10;
#ifdef _WIN32
    auto fp=launch_ansi(read_launch_text(fp_setting)); unsigned control,status,tag,mxcsr; char extra;
    if(std::sscanf(fp.c_str(),"%x:%x:%x:%x%c",&control,&status,&tag,&mxcsr,&extra)!=4 || control>0xffff || status>0xffff || tag>0xffff)
        throw std::runtime_error("invalid declared floating-point entry state");
    state.x87_control=std::uint16_t(control); state.x87_status=std::uint16_t(status); state.x87_tag=std::uint16_t(tag);
    state.x87_control_defined=state.x87_status_defined=state.x87_tag_defined=0xffff;
    state.x87_environment_defined=true; // Captured IP/DP/selectors/opcode are zero.
    state.mxcsr=mxcsr; state.mxcsr_defined=0xffffffffu; state.mxcsr_mask=recomp_generated::native_mxcsr_mask();
    recomp_generated::validate_native_fp(state); recomp_generated::native_floating_bridge_enabled=true;
#else
    (void)fp_setting;
#endif
}
int main(int argc,char** argv) {
    if(argc<3 || argc>4) { std::fputs("startup_main VIEW_DIRECTORY main|umbra|combined [INSTRUCTION_BUDGET]\n",stderr); return 2; }
    sharp_retro::State state;
    std::uint64_t budget=argc==4 ? std::strtoull(argv[3],nullptr,0) : 1000000;
    if(!budget || (std::strcmp(argv[2],"main") && std::strcmp(argv[2],"umbra") && std::strcmp(argv[2],"combined"))) return 2;
    bool combined=std::strcmp(argv[2],"combined")==0;
    auto initial_budget=budget; bool dll=combined || std::strcmp(argv[2],"umbra")==0;
    const char* phase=dll ? "umbra_attach" : "main_entry";
    StartupMemory memory; memory.state=&state;
    recomp_generated::native_binding_trace=binding_trace;
    try {
        if(auto* limit=std::getenv("RECOMP_NATIVE_TRACE_LIMIT")) {
            char* end=nullptr; native_trace_limit=std::strtoull(limit,&end,10);
            if(!end || *end || limit==end || native_trace_limit>1000000) throw std::runtime_error("invalid native trace limit");
        }
#if defined(_WIN32) && defined(RECOMP_FLAT_MEMORY)
        auto marker=reinterpret_cast<std::uintptr_t>(&recomp_guestspace_marker);
        if(reinterpret_cast<std::uintptr_t>(::GetModuleHandleA("recomp_guestspace.dll"))!=0x00400000 ||
           marker<0x00400000 || marker>=0x00400000+RECOMP_MAIN_IMAGE_SIZE)
            throw std::runtime_error("reservation DLL was relocated away from the original EXE namespace");
#endif
        recomp_generated::reserve_linked_images(memory);
#if defined(_WIN32) && defined(RECOMP_FLAT_MEMORY)
        recomp_generated::native_tail_read_trace=[](std::uint32_t address,unsigned width,std::uint64_t prefix) {
            std::printf("{\"event\":\"native_tail_read\",\"address\":%u,\"width\":%u,\"registered_prefix_bytes\":%llu}\n",address,width,(unsigned long long)prefix);
        };
#endif
        memory.map_bytes("main thread stack",0x50000000,1024*1024,true,true);
        memory.map_bytes("native callback stacks",0x51000000,1024*1024,true,true);
        memory.map_bytes("partial thread state; only declared fields are readable",0x60000000,4096,true,true);
#ifdef _WIN32
        auto command=read_launch_text(L"RECOMP_GAME_COMMAND_LINE"); auto ansi=launch_ansi(command);
        recomp_generated::logical_main_module_path_w=read_launch_text(L"RECOMP_MAIN_MODULE_PATH");
        recomp_generated::logical_main_module_path_a=launch_ansi(recomp_generated::logical_main_module_path_w);
        memory.map_bytes("logical ANSI game command line",0x52000000,65536,true,false,
                         {reinterpret_cast<const std::uint8_t*>(ansi.c_str()),ansi.size()+1});
        memory.map_bytes("logical UTF16 game command line",0x52010000,65536,true,false,
                         {reinterpret_cast<const std::uint8_t*>(command.c_str()),(command.size()+1)*sizeof(wchar_t)});
        recomp_generated::process_command_line_a=0x52000000; recomp_generated::process_command_line_w=0x52010000;
#endif
        recomp_generated::ThreadTlsLayout tls{0x60000000,0x60010000,0x60020000};
        recomp_generated::initialize_linked_images(memory,argv[1],&tls);
        entry_context(state,L"RECOMP_FP_ENTRY");
        callback_memory=&memory; startup_state=&state; startup_budget=&budget; startup_initial_budget=initial_budget;
#ifdef _WIN32
        startup_thread=::GetCurrentThreadId(); recomp_generated::native_fls_runner=run_fls_callback;
        recomp_generated::native_unhandled_frontier=unhandled_frontier;
#ifdef RECOMP_LIVE_CANDIDATES
        if(auto* live=std::getenv("RECOMP_LIVE_CANDIDATES");live && std::strcmp(live,"1")==0)
            recomp_generated::missing_guest_code=[](std::uint32_t address) {
                if(::GetCurrentThreadId()!=startup_thread || callback_depth) return false;
                auto error=::GetLastError();
                // Exploration I/O/loading is outside guest execution. Preserve
                // host FP and last-error while all modeled guest state stays put.
                recomp_generated::NativeFloatingScope fp(*startup_state,false);
                try {
                    auto loaded=recomp_generated::await_candidate(address,startup_initial_budget-*startup_budget,*startup_budget);
                    ::SetLastError(error); return loaded;
                } catch(...) { ::SetLastError(error); throw; }
            };
#endif
#endif
        // Explicit initial exception-list state for normal-path exploration;
        // SEH dispatch remains unsupported; initial-thread image TLS is explicit.
        memory.store(0x60000000,0xffffffff,32);
        memory.store(state.gpr[4],0x12345678,32);
        if(dll) {
            memory.store(state.gpr[4]+4,0x10000000,32);
            memory.store(state.gpr[4]+8,1,32); // DLL_PROCESS_ATTACH
            memory.store(state.gpr[4]+12,0,32);
        }
        std::printf("{\"event\":\"startup_begin\",\"module\":\"%s\",\"entry\":%u,\"process_state\":\"partial; initialization incomplete\"}\n",
                    dll ? "umbra.dll" : "DAOrigins.exe",dll ? 0x100cb9b1u : 0x008e3024u);
        auto outcome=recomp_generated::execute_guest(dll ? 0x100cb9b1u : 0x008e3024u,0x12345678,state,memory,budget,native_call);
        if(combined) {
            if(outcome!=sharp_retro::Exit::returned) throw std::runtime_error("Umbra attach did not return within the shared startup budget");
            auto accepted=std::uint32_t(sharp_retro::read_gpr_mask(state,0,0xffffffffu));
            if(state.pc!=0x12345678 || sharp_retro::read_gpr(state,4)!=0x500ff010 || !accepted ||
               sharp_retro::read_flags(state,10)!=0 || memory.load(0x60000000,32)!=0xffffffff)
                throw std::runtime_error("Umbra attach failed its return/stack/DF/exception-list contract");
            std::printf("{\"event\":\"dll_attach_return\",\"module\":\"umbra.dll\",\"eax\":%u,\"consumed\":%llu,\"native_calls\":%u,\"initialization_certified\":false}\n",accepted,(unsigned long long)(initial_budget-budget),import_calls);
            // Carry guest module data, native allocations/handles and thread
            // slots into main. The loader's intervening register/stack context
            // is uncaptured; supply the explicit partial main-entry fixture.
            phase="main_entry";
            for(std::uint32_t offset=0;offset<1024*1024;offset+=4) memory.store_unknown(0x50000000u+offset,0,32);
            entry_context(state,L"RECOMP_MAIN_FP_ENTRY"); memory.store(state.gpr[4],0x12345678,32);
            std::printf("{\"event\":\"startup_begin\",\"module\":\"DAOrigins.exe\",\"entry\":%u,\"after_translated_umbra_attach\":true,\"process_state\":\"partial; fresh declared main register/FP context; stack unknown; module data and native lifetimes retained\"}\n",0x008e3024u);
            outcome=recomp_generated::execute_guest(0x008e3024u,0x12345678,state,memory,budget,native_call);
        }
        memory.dump_trace();
        std::printf("{\"event\":\"startup_stop\",\"status\":\"%s\",\"pc\":%u,\"consumed\":%llu,\"native_calls\":%u,\"native_trace_suppressed\":%llu,\"game_started\":false}\n",
                    outcome==sharp_retro::Exit::returned ? "entry_returned; initialization not certified" : "budget_exhausted",unsigned(state.pc),
                    (unsigned long long)(initial_budget-budget),import_calls,(unsigned long long)native_trace_suppressed);
        end_exploration(outcome==sharp_retro::Exit::returned ? 4 : 5);
    } catch(const std::exception& e) {
        memory.dump_trace();
        std::printf("{\"event\":\"startup_frontier\",\"phase\":\"%s\",\"reason\":%s,\"pc\":%u,\"esp\":%u,\"eax\":%u,\"defined_gpr\":%u,\"consumed\":%llu,\"native_calls\":%u,\"native_trace_suppressed\":%llu,\"game_started\":false}\n",
                    phase,json_string(e.what()).c_str(),unsigned(state.pc),unsigned(state.gpr[4]),unsigned(state.gpr[0]),unsigned(state.defined_gpr),
                    (unsigned long long)(initial_budget-budget),import_calls,(unsigned long long)native_trace_suppressed);
        end_exploration(3);
    }
}
