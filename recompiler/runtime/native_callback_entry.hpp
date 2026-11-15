#pragma once
#include "functions.hpp"
#include "native_execution.hpp"
#include "native_floating.hpp"
#include <cstdlib>
#include <limits>
#include <memory>

namespace recomp_generated::native_callback {
// This bridge handles ordinary native CALL/RET entries. Nonlocal continuations
// without an executable native return word remain explicit failures.
struct Environment {NativeX86Memory& memory;std::uint64_t& budget;};
inline thread_local Environment* active=nullptr;
struct Binding {
    Environment value;Environment* previous=active;
    Binding(NativeX86Memory& memory,std::uint64_t& budget):value{memory,budget}{active=&value;}
    ~Binding(){active=previous;}
};
inline void (*adopt_images)(NativeX86Memory&)=nullptr;
// Optional diagnostics run only after translation has already failed/stopped.
// They must preserve OS error state and cannot turn a failed callback into a return.
inline void (*observe_frontier_state)(const sharp_retro::State&) noexcept=nullptr;
inline std::uint64_t configured_instruction_budget() {
    auto* text=std::getenv("RECOMP_INSTRUCTION_BUDGET");
    if(!text)return 500000000;
    std::uint64_t value=0;
    if(!*text)throw std::runtime_error("invalid native instruction budget");
    for(;*text;++text) {
        if(*text<'0'||*text>'9'||value>(std::numeric_limits<std::uint64_t>::max()-unsigned(*text-'0'))/10)
            throw std::runtime_error("invalid native instruction budget");
        value=value*10+unsigned(*text-'0');
    }
    if(!value)throw std::runtime_error("invalid native instruction budget");
    return value;
}
struct alignas(16) Resume {
    std::uint32_t pc,gpr[8],flags,last_error,source_low,source_high;
    alignas(16) std::array<std::uint8_t,512> fx;
    NativeX87Image x87;
    NativeMmxImage mmx;
    std::uint32_t split_mmx;
};
static_assert(offsetof(Resume,fx)==64 && offsetof(Resume,x87)==576 && offsetof(Resume,mmx)==688 && offsetof(Resume,split_mmx)==752);
extern "C" [[noreturn]] void recomp_callback_resume(Resume*);
asm(".text\n.globl _recomp_callback_resume\n_recomp_callback_resume:\n"
    "movl 4(%esp),%eax\nfxrstor 64(%eax)\nfrstor 576(%eax)\n"
    "cmpl $0,752(%eax)\nje 1f\n"
    "movq 688(%eax),%mm0\n"
    "movq 696(%eax),%mm1\n"
    "movq 704(%eax),%mm2\n"
    "movq 712(%eax),%mm3\n"
    "movq 720(%eax),%mm4\n"
    "movq 728(%eax),%mm5\n"
    "movq 736(%eax),%mm6\n"
    "movq 744(%eax),%mm7\n"
    "1:\n"
    "movl 48(%eax),%edx\nmovl %edx,%fs:4\nmovl 44(%eax),%edx\nmovl %edx,%fs:8\n"
    "movl 40(%eax),%edx\nmovl %edx,%fs:0x34\npushl 36(%eax)\npopfl\n"
    "movl 20(%eax),%esp\npushl 0(%eax)\npushl 4(%eax)\n"
    "movl 8(%eax),%ecx\nmovl 12(%eax),%edx\nmovl 16(%eax),%ebx\n"
    "movl 24(%eax),%ebp\nmovl 28(%eax),%esi\nmovl 32(%eax),%edi\npopl %eax\nret\n");
struct Frame {
    CONTEXT context;
    NativeMmxImage mmx;
    void* stack;
    std::uint32_t stack_low,stack_high,source_low,source_high,last_error,stop;
    Environment* environment;
    Frame* next;
    void* allocation;
    Resume resume;
};
inline unsigned context_register_order=0; // 1 logical, 2 physical; measured below.
inline void calibrate_context();
inline DWORD retired_slot=FLS_OUT_OF_INDEXES;
// Guest frames stay on their original/native stacks. This private stack holds
// only the bounded C++ dispatcher/ABI bridge; reserving 16 MiB per concurrent
// callback exhausts PE32 address space when the full translated image is loaded.
inline constexpr std::uint32_t private_stack_bytes=2*1024*1024;
inline void WINAPI release_retired(void* value) {
    auto* frame=static_cast<Frame*>(value);
    // Never release a stack on which cleanup itself is executing.
    MEMORY_BASIC_INFORMATION current{};::VirtualQuery(&frame,&current,sizeof(current));
    while(frame){auto* next=frame->next;if(current.AllocationBase!=frame->stack){
        ::VirtualFree(frame->stack,0,MEM_RELEASE);::HeapFree(::GetProcessHeap(),0,frame->allocation);
    }frame=next;}
}
inline void initialize() {
    if(retired_slot!=FLS_OUT_OF_INDEXES)return;
    retired_slot=::FlsAlloc(release_retired);
    if(retired_slot==FLS_OUT_OF_INDEXES)throw std::runtime_error("cannot allocate native callback retirement slot");
    calibrate_context();
}
// The i386 Wine/QEMU host reports even data faults as illegal instructions.
// Calibrate using a known RET on a non-executable page, and retain the page
// protection guard for every later callback. Executable-page faults never enter
// this transport, including real UD2 instructions and native data faults.
inline DWORD execute_fault_code=0;
inline bool readable_nonexecuting_page(std::uint32_t address) {
    auto error=::GetLastError();MEMORY_BASIC_INFORMATION info{};
    auto queried=::VirtualQuery(reinterpret_cast<const void*>(std::uintptr_t(address)),&info,sizeof(info));
    ::SetLastError(error);
    return queried && info.State==MEM_COMMIT &&
        !(info.Protect&(PAGE_NOACCESS|PAGE_GUARD|PAGE_EXECUTE|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY)) &&
        (info.Protect&(PAGE_READONLY|PAGE_READWRITE|PAGE_WRITECOPY));
}
inline bool is_execute_fault(EXCEPTION_POINTERS* event) {
    auto* record=event->ExceptionRecord;auto pc=event->ContextRecord->Eip;
    if(!execute_fault_code || record->ExceptionCode!=execute_fault_code)return false;
    if(record->ExceptionCode==EXCEPTION_ACCESS_VIOLATION) {
        if(record->NumberParameters<2 || record->ExceptionInformation[0]!=8 || record->ExceptionInformation[1]!=pc)return false;
    }else if(record->ExceptionCode!=EXCEPTION_ILLEGAL_INSTRUCTION || record->NumberParameters)return false;
    return readable_nonexecuting_page(pc);
}
inline bool context_uses_legacy_x87=false;
struct Probe {NativeX87Image reference;unsigned observed,legacy_observed;DWORD exception_code,context_flags,legacy_control,legacy_status,legacy_tag;unsigned extended_status,extended_tag;};
inline Probe* probe_active=nullptr;
inline const unsigned char probe_return_byte=0xc3; // Read-only constructed RET, never game code.
extern "C" void recomp_context_probe_return();
asm(".text\n.globl _recomp_context_probe_return\n_recomp_context_probe_return:\nfrstor (%eax)\nret\n");
inline LONG CALLBACK probe_exception(EXCEPTION_POINTERS* event) {
    auto* context=event->ContextRecord;auto* record=event->ExceptionRecord;
    if(!probe_active || context->Eip!=reinterpret_cast<std::uintptr_t>(&probe_return_byte))
        return EXCEPTION_CONTINUE_SEARCH;
    auto conventional=record->ExceptionCode==EXCEPTION_ACCESS_VIOLATION && record->NumberParameters>=2 &&
                      record->ExceptionInformation[0]==8 && record->ExceptionInformation[1]==context->Eip;
    auto emulated=record->ExceptionCode==EXCEPTION_ILLEGAL_INSTRUCTION && record->NumberParameters==0;
    if((!conventional && !emulated) || !readable_nonexecuting_page(context->Eip))
        return EXCEPTION_CONTINUE_SEARCH;
    probe_active->exception_code=record->ExceptionCode;
    probe_active->context_flags=context->ContextFlags;
    probe_active->legacy_control=context->FloatSave.ControlWord;probe_active->legacy_status=context->FloatSave.StatusWord;probe_active->legacy_tag=context->FloatSave.TagWord;
    std::uint16_t extended_status;std::memcpy(&extended_status,context->ExtendedRegisters+2,2);
    probe_active->extended_status=extended_status;probe_active->extended_tag=context->ExtendedRegisters[4];
    auto top=(fp_word(probe_active->reference,4)>>11)&7;bool logical=true,physical=true,legacy_logical=true,legacy_physical=true;
    for(unsigned i=0;i<8;++i){auto* expected=probe_active->reference.data()+28+i*10;
        logical&=std::memcmp(expected,context->ExtendedRegisters+32+i*16,10)==0;
        physical&=std::memcmp(expected,context->ExtendedRegisters+32+((top+i)&7)*16,10)==0;
        legacy_logical&=std::memcmp(expected,context->FloatSave.RegisterArea+i*10,10)==0;
        legacy_physical&=std::memcmp(expected,context->FloatSave.RegisterArea+((top+i)&7)*10,10)==0;}
    auto complete=(context->ContextFlags&(CONTEXT_FULL|CONTEXT_FLOATING_POINT|CONTEXT_EXTENDED_REGISTERS))==
                  (CONTEXT_FULL|CONTEXT_FLOATING_POINT|CONTEXT_EXTENDED_REGISTERS);
    std::uint16_t extended_control;std::memcpy(&extended_control,context->ExtendedRegisters,2);
    auto extended_environment=extended_control==fp_word(probe_active->reference,0)&&
        extended_status==fp_word(probe_active->reference,4)&&context->ExtendedRegisters[4]==0xff;
    auto legacy_environment=std::uint16_t(context->FloatSave.ControlWord)==fp_word(probe_active->reference,0)&&
        std::uint16_t(context->FloatSave.StatusWord)==fp_word(probe_active->reference,4)&&
        std::uint16_t(context->FloatSave.TagWord)==fp_word(probe_active->reference,8);
    probe_active->observed=complete&&extended_environment ? unsigned(logical)|(unsigned(physical)<<1):0;
    probe_active->legacy_observed=complete&&legacy_environment ? unsigned(legacy_logical)|(unsigned(legacy_physical)<<1):0;
    context->Eip=reinterpret_cast<std::uintptr_t>(&recomp_context_probe_return);
    context->Eax=reinterpret_cast<std::uintptr_t>(probe_active);
    return EXCEPTION_CONTINUE_EXECUTION;
}
inline void calibrate_context() {
    MEMORY_BASIC_INFORMATION info{};
    if(!::VirtualQuery(&probe_return_byte,&info,sizeof(info)) || (info.Protect&(PAGE_EXECUTE|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY)))
        throw std::runtime_error("native callback context probe is executable");
    auto handler=::AddVectoredExceptionHandler(1,probe_exception);
    if(!handler)throw std::runtime_error("cannot install native callback context probe");
    static const double values[]={1,2,4,8,16,32,64,128};
    unsigned extended_orders=3,legacy_orders=3,passed=0;DWORD fault_code=0;
    for(unsigned top=0;top<8;++top){
        alignas(16) NativeX87Image host{},after{};Probe probe{};probe_active=&probe;
        asm volatile("fnsave %0\n\tfninit\n\tfldl 0(%1)\n\tfldl 8(%1)\n\tfldl 16(%1)\n\tfldl 24(%1)\n\tfldl 32(%1)\n\tfldl 40(%1)\n\tfldl 48(%1)\n\tfldl 56(%1)":"=m"(host):"r"(values):"memory");
        for(unsigned i=0;i<top;++i)asm volatile("fincstp":::"memory");
        asm volatile("fnsave %0\n\tfrstor %0":"=m"(probe.reference)::"memory");
        asm volatile("call *%2\n\tfnsave %0\n\tfrstor %1":"=m"(after):"m"(host),"r"(&probe_return_byte):"memory","eax","ecx","edx","xmm0","xmm1","xmm2","xmm3","xmm4","xmm5","xmm6","xmm7");
        probe_active=nullptr;
        auto match=fp_word(probe.reference,0)==fp_word(after,0)&&fp_word(probe.reference,4)==fp_word(after,4)&&
            fp_word(probe.reference,8)==fp_word(after,8)&&std::memcmp(probe.reference.data()+28,after.data()+28,80)==0;
        extended_orders&=probe.observed;legacy_orders&=probe.legacy_observed;
        if((!extended_orders&&!legacy_orders) || !match || ((fp_word(probe.reference,4)>>11)&7)!=top ||
           !probe.exception_code || (fault_code && fault_code!=probe.exception_code)) {
            std::fprintf(stderr,"native callback calibration refused: top=%u layout=%u legacy_layout=%u restored=%u exception=%lx context=%lx legacy=%lx/%lx/%lx extended=%x/%x reference=%x/%x/%x after=%x/%x/%x\n",
                top,probe.observed,probe.legacy_observed,unsigned(match),probe.exception_code,probe.context_flags,probe.legacy_control,probe.legacy_status,probe.legacy_tag,
                probe.extended_status,probe.extended_tag,fp_word(probe.reference,0),fp_word(probe.reference,4),fp_word(probe.reference,8),fp_word(after,0),fp_word(after,4),fp_word(after,8));
            break;
        }
        fault_code=probe.exception_code;
        ++passed;
    }
    ::RemoveVectoredExceptionHandler(handler);
    auto orders=extended_orders?extended_orders:legacy_orders;
    if(passed!=8 || (orders!=1&&orders!=2))throw std::runtime_error("native callback context layout calibration failed");
    context_register_order=orders;context_uses_legacy_x87=!extended_orders;execute_fault_code=fault_code;
    std::fprintf(stderr,"{\"event\":\"native_callback_context_layout\",\"order\":\"%s\",\"x87_source\":\"%s\",\"top_controls\":8,\"execute_fault_code\":%lu,\"game_acceptance\":false}\n",orders==1 ? "logical":"physical",context_uses_legacy_x87?"legacy_fsave":"extended_fxsave",fault_code);std::fflush(stderr);
}
inline void context_state(const CONTEXT& context,sharp_retro::State& state) {
    if((context.ContextFlags&CONTEXT_FULL)!=CONTEXT_FULL ||
       (context.ContextFlags&CONTEXT_FLOATING_POINT)!=CONTEXT_FLOATING_POINT ||
       (context.ContextFlags&CONTEXT_EXTENDED_REGISTERS)!=CONTEXT_EXTENDED_REGISTERS)
        throw std::runtime_error("native callback context lacks complete CPU/FP state");
    if(context.EFlags&0x44100u)throw std::runtime_error("native callback trap/alignment/task exception modes are unsupported");
    state={};std::uint32_t gpr[]={context.Eax,context.Ecx,context.Edx,context.Ebx,context.Esp,context.Ebp,context.Esi,context.Edi};
    for(unsigned i=0;i<8;++i)state.gpr[i]=gpr[i];
    state.defined_gpr=0xff;state.flags=context.EFlags;state.defined_flags=0xffffffffu;state.pc=context.Eip;
    state.segments[4]=reinterpret_cast<std::uintptr_t>(::NtCurrentTeb());
    // Choose only a complete x87 representation measured against all eight TOP
    // controls. Extended state is still mandatory for MXCSR and every XMM value.
    if(!context_register_order)throw std::runtime_error("native callback FP layout is not calibrated");
    if(context_uses_legacy_x87) {
        NativeX87Image image{};std::memcpy(image.data(),&context.FloatSave,108);
        auto top=(fp_word(image,4)>>11)&7;
        if(context_register_order==2)for(unsigned i=0;i<8;++i)
            std::memcpy(image.data()+28+i*10,context.FloatSave.RegisterArea+((top+i)&7)*10,10);
        std::uint32_t mxcsr;std::memcpy(&mxcsr,context.ExtendedRegisters+24,4);
        state.mxcsr_mask=native_mxcsr_mask();read_native_fp_image(state,image,mxcsr,false);
        for(unsigned i=0;i<8;++i){if(((state.x87_tag>>(((top+i)&7)*2))&3)!=3)state.defined_x87_st|=std::uint8_t(1u<<i);
            std::memcpy(&state.xmm[i],context.ExtendedRegisters+160+i*16,16);}
        state.defined_xmm=0xff;validate_native_fp(state,false);return;
    }
    alignas(16) std::array<std::uint8_t,512> guest{};
    std::memcpy(guest.data(),context.ExtendedRegisters,512);
    std::uint32_t mxcsr;std::memcpy(&mxcsr,guest.data()+24,4);
    std::uint16_t control,status;std::memcpy(&control,guest.data(),2);std::memcpy(&status,guest.data()+2,2);
    if(guest[4] && !context_register_order)throw std::runtime_error("native callback FP layout is not calibrated");
    if(context_register_order==2){auto top=(status>>11)&7;
        for(unsigned i=0;i<8;++i)std::memcpy(guest.data()+32+i*16,context.ExtendedRegisters+32+((top+i)&7)*16,10);}
    state.mxcsr_mask=native_mxcsr_mask();
    if((mxcsr&~state.mxcsr_mask)||(status&0x80)||((status&0x3f)&~control))
        throw std::runtime_error("native callback has invalid/pending FP state");
    NativeX87Image image{};fp_word(image,0,control);fp_word(image,4,status);
    std::uint16_t opcode,cs,ds;std::uint32_t ip,dp;
    std::memcpy(&opcode,guest.data()+6,2);std::memcpy(&ip,guest.data()+8,4);std::memcpy(&cs,guest.data()+12,2);
    std::memcpy(&dp,guest.data()+16,4);std::memcpy(&ds,guest.data()+20,2);
    fp_word(image,18,opcode);fp_word(image,16,cs);fp_dword(image,12,ip);fp_word(image,24,ds);fp_dword(image,20,dp);
    unsigned tags=0xffff,top=(status>>11)&7;
    for(unsigned i=0;i<8;++i){auto* value=guest.data()+32+i*16;std::memcpy(image.data()+28+i*10,value,10);
        auto physical=(top+i)&7;if(!(guest[4]&(1u<<physical)))continue;
        std::uint64_t significand;std::uint16_t exponent;std::memcpy(&significand,value,8);std::memcpy(&exponent,value+8,2);exponent&=0x7fff;
        unsigned tag=exponent==0 && significand==0 ? 1 : exponent==0 || exponent==0x7fff || !(significand>>63) ? 2:0;
        tags=(tags&~(3u<<(physical*2)))|(tag<<(physical*2));}
    fp_word(image,8,tags);
    read_native_fp_image(state,image,mxcsr,false);
    for(unsigned i=0;i<8;++i){if(((state.x87_tag>>(((top+i)&7)*2))&3)!=3)state.defined_x87_st|=std::uint8_t(1u<<i);
        std::memcpy(&state.xmm[i],context.ExtendedRegisters+160+i*16,16);}
    state.defined_xmm=0xff;validate_native_fp(state,false);
}
inline void state_context(const sharp_retro::State& state,CONTEXT& context) {
    if(state.defined_gpr!=0xff || state.defined_flags!=0xffffffffu || state.defined_xmm!=0xff)
        throw std::runtime_error("native callback returned incomplete CPU state");
    if(state.flags&0x44100u)throw std::runtime_error("native callback returned unsupported trap/alignment/task exception modes");
    auto image=native_fp_image(state,false);std::memcpy(&context.FloatSave,image.data(),108);
    context.Eax=state.gpr[0];context.Ecx=state.gpr[1];context.Edx=state.gpr[2];context.Ebx=state.gpr[3];
    context.Esp=state.gpr[4];context.Ebp=state.gpr[5];context.Esi=state.gpr[6];context.Edi=state.gpr[7];
    context.EFlags=state.flags;context.Eip=state.pc;
    // Restore through the FXSAVE image; do not also request a legacy FSAVE
    // conversion when complete extended state is present.
    context.ContextFlags&=~DWORD(CONTEXT_FLOATING_POINT&~CONTEXT_i386);
    auto* fx=context.ExtendedRegisters;
    std::memcpy(fx,&state.x87_control,2);std::memcpy(fx+2,&state.x87_status,2);
    fx[4]=0;for(unsigned i=0;i<8;++i)if(((state.x87_tag>>(i*2))&3)!=3)fx[4]|=1u<<i;
    std::memcpy(fx+6,&state.x87_opcode,2);std::memcpy(fx+8,&state.x87_ip,4);std::memcpy(fx+12,&state.x87_cs,2);
    std::memcpy(fx+16,&state.x87_dp,4);std::memcpy(fx+20,&state.x87_ds,2);std::memcpy(fx+24,&state.mxcsr,4);
    for(unsigned i=0;i<8;++i){std::memcpy(fx+32+i*16,state.x87_st[i].data(),10);std::memcpy(fx+160+i*16,&state.xmm[i],16);}
}
[[noreturn]] inline void __cdecl gateway(Frame* frame) {
    sharp_retro::State state;state.pc=frame->context.Eip;state.gpr[4]=frame->context.Esp;
    std::uint64_t fresh_budget=0,initial_budget=0;
    std::uint64_t* observed_budget=nullptr;
    try {
        {
            std::unique_ptr<NativeX86Memory> owned;
            if(!frame->environment)fresh_budget=configured_instruction_budget();
            if(!frame->environment){if(!adopt_images)throw std::runtime_error("new-thread callback has no image contract");
                owned=std::make_unique<NativeX86Memory>();adopt_images(*owned);owned->add_native_stack(frame->source_low,frame->source_high);}
            auto& memory=frame->environment ? frame->environment->memory:*owned;
            auto& budget=frame->environment ? frame->environment->budget:fresh_budget;
            observed_budget=&budget;initial_budget=budget;
            Binding binding(memory,budget);
            context_state(frame->context,state);
            if(native_mmx_is_split()){state.native_mmx=frame->mmx;state.defined_native_mmx=0xff;}
            auto initial=budget;::SetLastError(frame->last_error);
            auto result=execute_guest(frame->context.Eip,frame->stop,state,memory,budget);
            frame->last_error=::GetLastError();
            if(result!=sharp_retro::Exit::returned)throw std::runtime_error("native callback exhausted its execution budget");
            state_context(state,frame->context);
            frame->resume.pc=state.pc;frame->resume.flags=state.flags;
            for(unsigned i=0;i<8;++i)frame->resume.gpr[i]=state.gpr[i];
            frame->resume.x87=native_fp_image(state,false);
            frame->resume.split_mmx=native_mmx_is_split();frame->resume.mmx=state.native_mmx;
            if(frame->resume.split_mmx && state.defined_native_mmx!=0xff)throw std::runtime_error("native callback return has unobserved MMX state");
            std::memcpy(frame->resume.fx.data(),frame->context.ExtendedRegisters,512);
            frame->resume.source_low=frame->source_low;frame->resume.source_high=frame->source_high;
            frame->resume.last_error=frame->last_error;
            std::fprintf(stderr,"{\"event\":\"native_callback_return\",\"pc\":%lu,\"esp\":%lu,\"eax\":%lu,\"consumed\":%llu,\"game_acceptance\":false}\n",
                         frame->context.Eip,frame->context.Esp,frame->context.Eax,(unsigned long long)(initial-budget));std::fflush(stderr);
        }
        frame->next=static_cast<Frame*>(::FlsGetValue(retired_slot));
        if(!::FlsSetValue(retired_slot,frame))throw std::runtime_error("cannot retire native callback execution stack");
        recomp_callback_resume(&frame->resume);
    }catch(const std::exception& error){
        if(observe_frontier_state)observe_frontier_state(state);
        std::string reason="\"";for(const char* p=error.what();*p;++p){if(*p=='\"'||*p=='\\')reason+='\\';if(static_cast<unsigned char>(*p)>=32)reason+=*p;}reason+='\"';
        std::fprintf(stderr,"{\"event\":\"native_callback_frontier\",\"pc\":%u,\"esp\":%u,\"call_return\":%u,\"entry_pc\":%lu,\"thread_id\":%lu,\"has_parent_budget\":%s,\"budget_observed\":%s,\"budget_initial\":%llu,\"budget_remaining\":%llu,\"defined_gpr\":%u,\"gpr_raw\":[%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu],\"reason\":%s,\"game_acceptance\":false}\n",
                     unsigned(state.pc),unsigned(state.gpr[4]),frame->stop,frame->context.Eip,::GetCurrentThreadId(),frame->environment?"true":"false",observed_budget?"true":"false",
                     (unsigned long long)initial_budget,(unsigned long long)(observed_budget?*observed_budget:0),unsigned(state.defined_gpr),
                     (unsigned long long)state.gpr[0],(unsigned long long)state.gpr[1],(unsigned long long)state.gpr[2],(unsigned long long)state.gpr[3],
                     (unsigned long long)state.gpr[4],(unsigned long long)state.gpr[5],(unsigned long long)state.gpr[6],(unsigned long long)state.gpr[7],reason.c_str());
    }
    std::fflush(stderr);::TerminateProcess(::GetCurrentProcess(),3);std::abort();
}
inline bool schedule(EXCEPTION_POINTERS* exception) {
    NativeMmxImage incoming_mmx{};if(native_mmx_is_split())capture_mmx_bits(incoming_mmx);
    auto last_error=::GetLastError();auto* context=exception->ContextRecord;
    DWORD stop=0;auto* tib=reinterpret_cast<NT_TIB*>(::NtCurrentTeb());
    auto source_low=reinterpret_cast<std::uintptr_t>(tib->StackLimit),source_high=reinterpret_cast<std::uintptr_t>(tib->StackBase);
    MEMORY_BASIC_INFORMATION source_page{};
    auto queried=::VirtualQuery(reinterpret_cast<void*>(context->Esp),&source_page,sizeof(source_page));
    if(context->Esp<source_low || std::uint64_t(context->Esp)+4>source_high || !queried || source_page.State!=MEM_COMMIT ||
       (source_page.Protect&(PAGE_NOACCESS|PAGE_GUARD)) ||
       !(source_page.Protect&(PAGE_READONLY|PAGE_READWRITE|PAGE_WRITECOPY|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY)) ||
       std::uint64_t(context->Esp)+4>std::uint64_t(reinterpret_cast<std::uintptr_t>(source_page.BaseAddress))+source_page.RegionSize) {
        std::fprintf(stderr,"native callback return outside readable current-thread stack: pc=%lx esp=%lx state=%lx protect=%lx stack=%p-%p\n",
            context->Eip,context->Esp,source_page.State,source_page.Protect,tib->StackLimit,tib->StackBase);
        throw std::runtime_error("native callback return word is unreadable");
    }
    // This is the captured current thread's live native stack, not a remote
    // process buffer. Some emulated hosts deny even self ReadProcessMemory.
    std::memcpy(&stop,reinterpret_cast<const void*>(context->Esp),sizeof(stop));
    MEMORY_BASIC_INFORMATION target{};
    if(!::VirtualQuery(reinterpret_cast<void*>(stop),&target,sizeof(target))||target.State!=MEM_COMMIT||
       (target.Protect&(PAGE_NOACCESS|PAGE_GUARD))||!(target.Protect&(PAGE_EXECUTE|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY)))
        throw std::runtime_error("native callback has no executable native return; nonlocal continuation unsupported");
    auto* retired=::FlsGetValue(retired_slot);if(!::FlsSetValue(retired_slot,nullptr))throw std::runtime_error("cannot clear retired native callbacks");release_retired(retired);
    auto* allocation=::HeapAlloc(::GetProcessHeap(),0,sizeof(Frame)+15);
    if(!allocation)throw std::runtime_error("cannot allocate native callback context");
    auto* frame=new(reinterpret_cast<void*>((reinterpret_cast<std::uintptr_t>(allocation)+15u)&~std::uintptr_t(15))) Frame{};
    frame->allocation=allocation;frame->mmx=incoming_mmx;
    frame->context=*context;frame->last_error=last_error;frame->stop=stop;frame->environment=active;
    frame->source_low=source_low;frame->source_high=source_high;
    frame->stack=::VirtualAlloc(nullptr,private_stack_bytes,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    if(!frame->stack){auto error=::GetLastError();::HeapFree(::GetProcessHeap(),0,frame->allocation);
        throw std::runtime_error("cannot allocate private callback stack; error "+std::to_string(error));}
    DWORD previous_protection=0;
    if(!::VirtualProtect(frame->stack,4096,PAGE_NOACCESS,&previous_protection)) {
        auto error=::GetLastError();::VirtualFree(frame->stack,0,MEM_RELEASE);::HeapFree(::GetProcessHeap(),0,frame->allocation);
        throw std::runtime_error("cannot protect private callback stack boundary; error "+std::to_string(error));
    }
    frame->stack_low=reinterpret_cast<std::uintptr_t>(frame->stack)+4096;frame->stack_high=reinterpret_cast<std::uintptr_t>(frame->stack)+private_stack_bytes;
    auto sp=(frame->stack_high-4096u)&~15u;sp-=8;
    *reinterpret_cast<DWORD*>(sp)=0;*reinterpret_cast<Frame**>(sp+4)=frame;
    context->Eip=reinterpret_cast<std::uintptr_t>(&gateway);context->Esp=sp;context->EFlags=0x202;
    // Enter ordinary compiled C++ with an empty host FP stack. The complete
    // incoming FP image is retained in frame->context, never reconstructed here.
    std::memset(&context->FloatSave,0,sizeof(context->FloatSave));context->FloatSave.ControlWord=0x37f;context->FloatSave.TagWord=0xffff;
    std::memset(context->ExtendedRegisters,0,sizeof(context->ExtendedRegisters));
    std::uint16_t control=0x37f;std::uint32_t mxcsr=0x1f80;std::memcpy(context->ExtendedRegisters,&control,2);std::memcpy(context->ExtendedRegisters+24,&mxcsr,4);
    tib->StackBase=reinterpret_cast<void*>(frame->stack_high);tib->StackLimit=reinterpret_cast<void*>(frame->stack_low);
    ::SetLastError(last_error);return true;
}
}
