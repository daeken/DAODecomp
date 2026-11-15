// Native execution prototype. No SharpRetro memory shadow or API-specific codecs.
// CPU input here is constructed/concrete; this does not concretize unknown states
// from the strict backend or change any original-function acceptance criteria.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <initializer_list>
#include <stdexcept>
#include <string>
#include <utility>
extern "C" {DWORD recomp_native_abi_tls_slot=TLS_OUT_OF_INDEXES;}
struct alignas(16) NativeFrame {
    std::uint32_t target,gpr[8],flags,host_sp,call_sp,return_pc,last_error;
    std::uint32_t stack_low,stack_high,host_stack_low,host_stack_high;
    alignas(16) std::array<unsigned char,512> input_fx,output_fx,host_fx;
};
static_assert(sizeof(void*)==4 && offsetof(NativeFrame,gpr)==4 && offsetof(NativeFrame,flags)==36 &&
    offsetof(NativeFrame,stack_low)==56 && offsetof(NativeFrame,host_stack_high)==68 &&
    offsetof(NativeFrame,input_fx)==80 && offsetof(NativeFrame,output_fx)==592 && offsetof(NativeFrame,host_fx)==1104 &&
    offsetof(NT_TIB,StackBase)==4 && offsetof(NT_TIB,StackLimit)==8);
extern "C" void recomp_native_abi_call(NativeFrame*);
#define CHECK(x) do {if(!(x)) throw std::runtime_error(std::string("line ")+std::to_string(__LINE__)+": "+#x);} while(false)
static std::uint32_t address(const void* pointer) {return std::uint32_t(reinterpret_cast<std::uintptr_t>(pointer));}
// A conversion between address domains is explicit. Query actual Windows pages;
// no heap/handle/type registry or per-API output-length model is involved.
static void* native_span(std::uint32_t token,std::size_t size,bool write) {
    if(!size || std::uint64_t(token)+size>0x100000000ULL) throw std::runtime_error("invalid native address span");
    std::uint64_t end=std::uint64_t(token)+size,cursor=token;
    while(cursor<end) {
        MEMORY_BASIC_INFORMATION info{};
        if(!::VirtualQuery(reinterpret_cast<const void*>(std::uintptr_t(cursor)),&info,sizeof(info)) || !info.RegionSize ||
           info.State!=MEM_COMMIT || (info.Protect&(PAGE_NOACCESS|PAGE_GUARD))) throw std::runtime_error("inaccessible native span");
        auto protect=info.Protect&0xffu;
        bool readable=protect==PAGE_READONLY || protect==PAGE_READWRITE || protect==PAGE_WRITECOPY ||
                      protect==PAGE_EXECUTE_READ || protect==PAGE_EXECUTE_READWRITE || protect==PAGE_EXECUTE_WRITECOPY;
        bool writable=protect==PAGE_READWRITE || protect==PAGE_WRITECOPY || protect==PAGE_EXECUTE_READWRITE || protect==PAGE_EXECUTE_WRITECOPY;
        if(!readable || (write && !writable)) throw std::runtime_error("native address permission violation");
        auto next=std::uint64_t(reinterpret_cast<std::uintptr_t>(info.BaseAddress))+info.RegionSize;
        if(next<=cursor) throw std::runtime_error("invalid native page interval");cursor=next;
    }
    return reinterpret_cast<void*>(std::uintptr_t(token));
}
static unsigned calls=0;
struct NativeCaller {
    void* stack=::VirtualAlloc(nullptr,1<<20,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    NativeCaller() {CHECK(stack);}
    ~NativeCaller() {::VirtualFree(stack,0,MEM_RELEASE);}
    NativeFrame call(std::uint32_t target,std::initializer_list<std::uint32_t> words,
                     std::uint32_t ecx=0x22222222,std::uint32_t edx=0x33333333) {
        CHECK(target && words.size()<64);
        NativeFrame frame{};frame.target=target;frame.flags=0x246;
        frame.stack_low=address(stack);frame.stack_high=address(stack)+(1<<20);
        auto sp=frame.stack_high-4096;auto* slots=static_cast<std::uint32_t*>(native_span(sp,(words.size()+1)*4,true));
        slots[0]=0xdeadbeef;unsigned i=1;for(auto word:words) slots[i++]=word;
        std::uint32_t values[8]={0x11111111,ecx,edx,0x44444444,sp,0x66666666,0x77777777,0x88888888};
        std::memcpy(frame.gpr,values,sizeof(values));
        asm volatile("fxsave %0" : "=m"(frame.input_fx) : : "memory");
        auto previous=::TlsGetValue(recomp_native_abi_tls_slot);
        CHECK(::TlsSetValue(recomp_native_abi_tls_slot,&frame));::SetLastError(0x13579);
        recomp_native_abi_call(&frame);
        CHECK(::TlsSetValue(recomp_native_abi_tls_slot,previous));::SetLastError(frame.last_error);
        CHECK(frame.return_pc==0xdeadbeef && slots[0]==0xdeadbeef && !(frame.flags&0x400));
        for(unsigned r:{3u,5u,6u,7u}) CHECK(frame.gpr[r]==values[r]);
        ++calls;return frame;
    }
};
static std::uint32_t native_export(const char* library,const char* symbol) {
    auto module=::GetModuleHandleA(library);if(!module) module=::LoadLibraryA(library);CHECK(module);
    auto result=::GetProcAddress(module,symbol);CHECK(result);
    // Prototype uses only explicitly named system DLL exports and constructed
    // fixture functions. It never loads/calls original main/Umbra machine code.
    return address(reinterpret_cast<void*>(result));
}
extern "C" __declspec(noinline) std::uint32_t __cdecl cdecl_sum(std::uint32_t a,std::uint32_t b) {return a+b;}
extern "C" __declspec(noinline) std::uint32_t __stdcall stdcall_sum(std::uint32_t a,std::uint32_t b) {return a+b;}
extern "C" __declspec(noinline) std::uint32_t __fastcall fastcall_sum(std::uint32_t a,std::uint32_t b,std::uint32_t c) {return a+b+c;}
struct Object {std::uint32_t value;};
extern "C" __declspec(noinline) std::uint32_t __attribute__((thiscall)) thiscall_sum(Object* object,std::uint32_t b) {return object->value+b;}
extern "C" __declspec(noinline) std::uint64_t __stdcall wide_result(std::uint32_t high,std::uint32_t low) {return std::uint64_t(high)<<32|low;}
extern "C" __declspec(noinline) double __cdecl floating_result(double a,double b) {return a+b;}
struct CallbackControl {unsigned count=0;};
BOOL CALLBACK native_callback(HWND,LPARAM token) {
    auto& control=*reinterpret_cast<CallbackControl*>(token);NativeCaller nested;
    auto result=nested.call(native_export("kernel32.dll","MulDiv"),{12,9,3});
    if(result.gpr[0]!=36) return FALSE;++control.count;return FALSE;
}
int main() {try {
    recomp_native_abi_tls_slot=::TlsAlloc();CHECK(recomp_native_abi_tls_slot<64);
    NativeCaller caller;
    auto check_stack=[](const NativeFrame& frame,unsigned cleanup) {CHECK(frame.gpr[4]==frame.call_sp+4+cleanup);};
    for(auto item:std::array<std::pair<std::uint32_t,unsigned>,2>{{{address(reinterpret_cast<void*>(&cdecl_sum)),0},{address(reinterpret_cast<void*>(&stdcall_sum)),8}}}) {
        auto result=caller.call(item.first,{12,9});CHECK(result.gpr[0]==21);check_stack(result,item.second);
    }
    auto fast=caller.call(address(reinterpret_cast<void*>(&fastcall_sum)),{5},12,9);CHECK(fast.gpr[0]==26);check_stack(fast,4);
    Object object{12};auto method=caller.call(address(reinterpret_cast<void*>(&thiscall_sum)),{9},address(&object));CHECK(method.gpr[0]==21);check_stack(method,4);
    auto wide=caller.call(address(reinterpret_cast<void*>(&wide_result)),{0x12345678,0x89abcdef});CHECK(wide.gpr[0]==0x89abcdef && wide.gpr[2]==0x12345678);check_stack(wide,8);
    std::uint64_t one,two;double a=1.25,b=2.5;std::memcpy(&one,&a,8);std::memcpy(&two,&b,8);
    auto floating=caller.call(address(reinterpret_cast<void*>(&floating_result)),{std::uint32_t(one),std::uint32_t(one>>32),std::uint32_t(two),std::uint32_t(two>>32)});check_stack(floating,0);
    std::uint64_t significand;std::uint16_t exponent;std::memcpy(&significand,floating.output_fx.data()+32,8);std::memcpy(&exponent,floating.output_fx.data()+40,2);
    CHECK(significand==0xf000000000000000ULL && exponent==0x4000);
    auto pid=caller.call(native_export("kernel32.dll","GetCurrentProcessId"),{});CHECK(pid.gpr[0]==::GetCurrentProcessId());check_stack(pid,0);
    auto arithmetic=caller.call(native_export("kernel32.dll","MulDiv"),{12,9,3});CHECK(arithmetic.gpr[0]==36);check_stack(arithmetic,12);
    auto error=caller.call(native_export("kernel32.dll","SetLastError"),{0x2468ace});CHECK(error.last_error==0x2468ace && ::GetLastError()==0x2468ace);check_stack(error,4);
    auto heap=address(::GetProcessHeap());auto allocated=caller.call(native_export("kernel32.dll","HeapAlloc"),{heap,HEAP_ZERO_MEMORY,64});check_stack(allocated,12);CHECK(allocated.gpr[0]);
    auto* bytes=static_cast<unsigned char*>(native_span(allocated.gpr[0],64,true));for(unsigned i=0;i<64;++i) CHECK(bytes[i]==0);
    bytes[0]=0x5a;CHECK(*static_cast<unsigned char*>(native_span(allocated.gpr[0],1,false))==0x5a);
    auto freed=caller.call(native_export("kernel32.dll","HeapFree"),{heap,0,allocated.gpr[0]});CHECK(freed.gpr[0]);check_stack(freed,12);
    wchar_t temporary[MAX_PATH],filename[MAX_PATH];CHECK(::GetTempPathW(MAX_PATH,temporary));CHECK(::GetTempFileNameW(temporary,L"DCN",0,filename));
    auto opened=caller.call(native_export("kernel32.dll","CreateFileW"),{address(filename),GENERIC_READ|GENERIC_WRITE,0,0,OPEN_EXISTING,0,0});CHECK(opened.gpr[0]!=0xffffffffu);check_stack(opened,28);
    std::string content="native pointers, no API codecs";DWORD count=0;
    auto written=caller.call(native_export("kernel32.dll","WriteFile"),{opened.gpr[0],address(content.data()),std::uint32_t(content.size()),address(&count),0});CHECK(written.gpr[0] && count==content.size());check_stack(written,20);
    auto seek=caller.call(native_export("kernel32.dll","SetFilePointer"),{opened.gpr[0],0,0,FILE_BEGIN});CHECK(seek.gpr[0]==0);check_stack(seek,16);
    std::array<char,64> buffer{};
    auto read=caller.call(native_export("kernel32.dll","ReadFile"),{opened.gpr[0],address(buffer.data()),std::uint32_t(buffer.size()),address(&count),0});CHECK(read.gpr[0] && count==content.size() && std::string(buffer.data(),count)==content);check_stack(read,20);
    auto closed=caller.call(native_export("kernel32.dll","CloseHandle"),{opened.gpr[0]});CHECK(closed.gpr[0] && ::DeleteFileW(filename));check_stack(closed,4);
    // A real native callback reenters the same generic bridge. Translation of a
    // guest callback entry is a separate, still-unimplemented next step.
    auto window=::CreateWindowExW(0,L"STATIC",L"native ABI experiment",WS_OVERLAPPED,0,0,1,1,nullptr,nullptr,::GetModuleHandleW(nullptr),nullptr);CHECK(window);
    CallbackControl callbacks;
    auto enumerated=caller.call(native_export("user32.dll","EnumThreadWindows"),{::GetCurrentThreadId(),address(reinterpret_cast<void*>(&native_callback)),address(&callbacks)});
    CHECK(!enumerated.gpr[0] && callbacks.count==1 && ::DestroyWindow(window));check_stack(enumerated,12);
    CHECK(::TlsFree(recomp_native_abi_tls_slot));
    std::printf("{\"generic_native_calls\":%u,\"cdecl_stdcall_fastcall_thiscall\":true,\"observed_stack_cleanup\":true,\"edx_eax_return\":true,\"raw_x87_return\":true,\"last_error\":true,\"native_heap_and_file_pointers\":true,\"nested_native_callback\":true,\"per_api_codecs\":0,\"game_or_translated_callback_acceptance\":false}\n",calls);
    return 0;
}catch(const std::exception& e){std::fprintf(stderr,"native ABI prototype: %s\n",e.what());return 10;}}
