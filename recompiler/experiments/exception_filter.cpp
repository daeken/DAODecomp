// Registration/identity debugging only; guest exception contexts stay unsupported.
#include "native_imports.hpp"
#include <cstdio>
static LONG WINAPI native_filter(EXCEPTION_POINTERS*) { return EXCEPTION_CONTINUE_SEARCH; }
[[noreturn]] static void reached(std::uint32_t target,EXCEPTION_POINTERS* pointers) noexcept {
    bool match=target==0x401000 && pointers && pointers->ExceptionRecord && pointers->ExceptionRecord->ExceptionCode==0xe0424242;
    std::printf("{\"callback_context_unimplemented\":true,\"target_and_exception_match\":%s}\n",match ? "true" : "false");
    std::fflush(nullptr); ::TerminateProcess(::GetCurrentProcess(),match ? 3 : 5); std::terminate();
}
int main(int argc,char**) {
    using namespace recomp_generated;
    native_unhandled_frontier=reached;
    auto original=::SetUnhandledExceptionFilter(native_filter);
    if(argc==2) {
        install_guest_unhandled_filter(0x401000,true);
        EXCEPTION_RECORD record{}; record.ExceptionCode=0xe0424242;
        CONTEXT context{}; EXCEPTION_POINTERS pointers{&record,&context};
        ::UnhandledExceptionFilter(&pointers); return 6; // Must reach the explicit callback frontier.
    }
    ::SetLastError(0x12345678);
    auto first=install_guest_unhandled_filter(0x401000,true); bool error_preserved=::GetLastError()==0x12345678;
    auto second=install_guest_unhandled_filter(0x402000,true);
    auto removed=install_guest_unhandled_filter(0,false);
    auto restored=install_guest_unhandled_filter(first,false);
    auto native_previous=::SetUnhandledExceptionFilter(original);
    bool unknown_refused=false;
    try { install_guest_unhandled_filter(0xdeadbeef,false); } catch(const std::runtime_error&) { unknown_refused=true; }
    bool match=first==std::uint32_t(reinterpret_cast<std::uintptr_t>(native_filter)) && second==0x401000 && removed==0x402000 && restored==0 && native_previous==native_filter;
    std::printf("{\"registration_and_previous_identity\":%s,\"last_error_preserved\":%s,\"unknown_native_pointer_refused\":%s}\n",match ? "true" : "false",error_preserved ? "true" : "false",unknown_refused ? "true" : "false");
    return match && error_preserved && unknown_refused ? 0 : 1;
}
