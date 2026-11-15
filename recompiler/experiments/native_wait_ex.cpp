// Actual Windows wait/APC transport; native control threads/APCs are not guest
// thread or guest callback support, and these cases do not establish gameplay.
#include "native_imports.hpp"
#include "image_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
static unsigned apc_calls=0;
static void CALLBACK control_apc(ULONG_PTR value) { ++apc_calls;::SetLastError(DWORD(value)); }
struct Holder {
    HANDLE mutex=nullptr,ready=nullptr,release=nullptr,thread=nullptr;
    DWORD result=WAIT_FAILED;
    static DWORD WINAPI run(void* input) {
        auto& h=*static_cast<Holder*>(input);h.result=::WaitForSingleObject(h.mutex,1000);::SetEvent(h.ready);
        if(h.result==WAIT_OBJECT_0) { (void)::WaitForSingleObject(h.release,10000);(void)::ReleaseMutex(h.mutex); } return 0;
    }
    void finish() {
        if(thread){::SetEvent(release);if(::WaitForSingleObject(thread,10000)!=WAIT_OBJECT_0)throw std::runtime_error("native holder did not finish");::CloseHandle(thread);thread=nullptr;}
    }
    ~Holder(){if(thread){::SetEvent(release);(void)::WaitForSingleObject(thread,10000);::CloseHandle(thread);}if(ready)::CloseHandle(ready);if(release)::CloseHandle(release);if(mutex)::CloseHandle(mutex);}
};
int main() {
 try {
    Holder h;h.mutex=::CreateMutexW(nullptr,FALSE,nullptr);h.ready=::CreateEventW(nullptr,FALSE,FALSE,nullptr);h.release=::CreateEventW(nullptr,FALSE,FALSE,nullptr);
    if(!h.mutex || !h.ready || !h.release)return 1;
    auto token=std::uint32_t(reinterpret_cast<std::uintptr_t>(h.mutex));register_native_kernel_handle(token,NativeKernelHandleKind::mutex);
    h.thread=::CreateThread(nullptr,0,Holder::run,&h,0,nullptr);
    if(!h.thread || ::WaitForSingleObject(h.ready,10000)!=WAIT_OBJECT_0 || h.result!=WAIT_OBJECT_0)return 2;
    ImageMemory memory;memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;capture_native_fp(host);native_floating_bridge_enabled=true;
    auto invoke=[&](DWORD timeout,std::uint32_t alertable,bool legacy=false) {
        auto state=host;state.gpr[4]=0x8800;
        for(unsigned reg:{3u,5u,6u,7u})state.gpr[reg]=0x12340000u+reg;
        { auto fixture=host;NativeFloatingScope fp(fixture,false);
          memory.store(0x8804,token,32);memory.store(0x8808,timeout,32);
          if(legacy)memory.store_unknown(0x880c,0,32);else memory.store(0x880c,alertable,32); }
        invoke_native_import({0,"KERNEL32.dll",legacy ? "WaitForSingleObject" : "WaitForSingleObjectEx",false},state,memory);
        if(state.pc!=0x12345678 || state.gpr[4]!=(legacy ? 0x880c : 0x8810) || !(state.defined_gpr&1) || (state.defined_gpr&6) ||
           state.gpr[3]!=0x12340003 || state.gpr[5]!=0x12340005 || state.gpr[6]!=0x12340006 || state.gpr[7]!=0x12340007)
            throw std::runtime_error("wait ABI mismatch");
        return std::uint32_t(state.gpr[0]);
    };
    unsigned cases=0,observed_apc_returns=0;
    for(DWORD timeout:std::array<DWORD,2>{0,1})for(std::uint32_t flag:{0u,1u,2u,0x80000000u}) {
        auto baseline=apc_calls;
        if(!::QueueUserAPC(control_apc,::GetCurrentThread(),0x2468))return 3;
        ::SetLastError(0x13579);auto expected=::WaitForSingleObjectEx(h.mutex,timeout,std::bit_cast<BOOL>(flag));auto error=::GetLastError();auto delivered=apc_calls-baseline;
        (void)::SleepEx(0,TRUE);if(apc_calls!=baseline+1)return 4;
        baseline=apc_calls;if(!::QueueUserAPC(control_apc,::GetCurrentThread(),0x2468))return 5;
        native_error_context.value=0x13579;auto result=invoke(timeout,flag);auto actual_error=native_error_context.value;auto actual_delivered=apc_calls-baseline;
        (void)::SleepEx(0,TRUE);
        if(result!=expected || actual_error!=error || actual_delivered!=delivered || apc_calls!=baseline+1)throw std::runtime_error("native wait/APC/result/error mismatch");
        if(result==WAIT_IO_COMPLETION)++observed_apc_returns;
        ++cases;
    }
    if(invoke(0,0,true)!=WAIT_TIMEOUT)return 6; // The legacy form cannot read the unknown third argument.
    h.finish();
    for(std::uint32_t flag:{0u,1u,0x80000000u}) {
        ::SetLastError(0x13579);auto expected=::WaitForSingleObjectEx(h.mutex,0,std::bit_cast<BOOL>(flag));auto error=::GetLastError();if(expected!=WAIT_OBJECT_0 || !::ReleaseMutex(h.mutex))return 7;
        native_error_context.value=0x13579;auto actual=invoke(0,flag);
        if(actual!=expected || native_error_context.value!=error || !::ReleaseMutex(h.mutex))return 8;
        ++cases;
    }
    native_kernel_handles.erase(token);bool refused=false;try{(void)invoke(0,0);}catch(const std::runtime_error&){refused=true;}
    sharp_retro::State after;capture_native_fp(after);bool restored=host.x87_control==after.x87_control && host.x87_status==after.x87_status && host.x87_tag==after.x87_tag && host.x87_st==after.x87_st && host.mxcsr==after.mxcsr;
    std::printf("{\"native_wait_cases\":%u,\"observed_APC_returns\":%u,\"legacy_unknown_third_argument\":true,\"unowned_handle_refused\":%s,\"host_fp_restored\":%s}\n",cases,observed_apc_returns,refused ? "true" : "false",restored ? "true" : "false");
    return cases!=11 || !observed_apc_returns || !refused || !restored ? 9 : 0;
 }catch(const std::exception& e){std::fprintf(stderr,"wait debug: %s\n",e.what());return 10;}
}
