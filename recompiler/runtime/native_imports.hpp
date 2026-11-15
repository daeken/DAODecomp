#pragma once
#if defined(_WIN32) && defined(__i386__) && defined(RECOMP_NATIVE_EXECUTION)
#include "native_abi.hpp"
namespace recomp_generated {
inline void invoke_native_import(const ImportEntry& entry,sharp_retro::State& state,sharp_retro::Memory& memory) {
    if(entry.translated_module) throw std::runtime_error("native fallback forbidden for translated module");
    if(!uses_native_execution(memory)) throw std::runtime_error("native production requires NativeX86Memory; validation fixtures need the explicit strict profile");
    invoke_native_abi_import(entry,state,memory);
}
}
#else
#include "runtime_api.hpp"
#include "native_access.hpp"
#include "native_abi.hpp"
#include "native_registry.hpp"
#include <algorithm>
#include <array>
#include <bit>
#include <cstring>
#include <type_traits>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <mmsystem.h>
#include <shlobj.h>
#endif
#include "native_callbacks.hpp"
#include "native_floating.hpp"
#include "native_registry_keys.hpp"
#if defined(_WIN32) && defined(__i386__)
#include "native_sync.hpp"
#endif
#include "native_resources.hpp"
#include "native_system_info.hpp"
#include "native_error.hpp"

namespace recomp_generated {
// The replacement's logical command line is supplied by its launch configuration.
// Host diagnostic arguments (view directory/budget) are never game arguments.
inline std::uint32_t process_command_line_a=0,process_command_line_w=0;
inline std::string logical_main_module_path_a;
inline std::wstring logical_main_module_path_w;
#ifdef _WIN32
inline std::set<void*> native_environment_blocks;
template<class Function> auto call_native(Function&& function) {
    static_assert(!std::is_floating_point_v<decltype(function())>,"native floating-point return transport is unimplemented");
    // Guest last-error state must survive bridge logging, heap bookkeeping and
    // registry locks. Capture the API's actual result before that work runs.
    ::SetLastError(native_error_context.value);
    NativeFloatingScope floating;
    if constexpr(std::is_void_v<decltype(function())>) {
        function(); auto error=::GetLastError(); floating.finish(); native_error_context.value=error;
    } else {
        auto result=function(); auto error=::GetLastError(); floating.finish(); native_error_context.value=error; return result;
    }
}
#endif
} // namespace recomp_generated
#if defined(_WIN32) && defined(__i386__)
#include "native_batch.hpp"
#endif
namespace recomp_generated {
// Explicit Win32 contracts only. Native pointers come exclusively from checked
// live backing; opaque handles and non-dereferenced pointer bits round-trip.
inline void invoke_native_import(const ImportEntry& import,sharp_retro::State& state,sharp_retro::Memory& memory) {
#if defined(_WIN32) && defined(__i386__) && defined(RECOMP_NATIVE_EXECUTION)
    if(import.translated_module) throw std::runtime_error("native fallback forbidden for translated module");
    if(!uses_native_execution(memory)) throw std::runtime_error("native Windows execution requires NativeX86Memory; strict fixtures need the explicit strict build profile");
    invoke_native_abi_import(import,state,memory);
#else
    if(import.translated_module) throw std::runtime_error("native fallback forbidden for translated module");
#if defined(_WIN32) && defined(__i386__)
    if(uses_native_execution(memory)) {invoke_native_abi_import(import,state,memory);return;}
#endif
    bool kernel=std::strcmp(import.library,"KERNEL32.dll")==0 || std::strcmp(import.library,"kernel32.dll")==0;
    bool registry=std::strcmp(import.library,"ADVAPI32.dll")==0 || std::strcmp(import.library,"advapi32.dll")==0;
    bool multimedia=std::strcmp(import.library,"WINMM.dll")==0 || std::strcmp(import.library,"winmm.dll")==0;
    bool user=std::strcmp(import.library,"USER32.dll")==0 || std::strcmp(import.library,"user32.dll")==0;
    bool shell=std::strcmp(import.library,"SHELL32.dll")==0 || std::strcmp(import.library,"shell32.dll")==0;
#if defined(_WIN32) && defined(__i386__)
    // This bridge writes Win32 layouts and transports 32-bit native handles.
    static_assert(sizeof(int)==4);
    NativeFloatingBinding floating_binding(state);
    if(state.segments[2]!=0) throw std::runtime_error("native Win32 scalar bridge requires flat SS");
    if((state.defined_flags&(std::uint64_t(1)<<10))==0 || (state.flags&(std::uint64_t(1)<<10))!=0)
        throw std::runtime_error("native x86 ABI requires a known clear direction flag");
    auto stack=std::uint32_t(sharp_retro::read_gpr(state,4));
    auto return_address=std::uint32_t(memory.load(stack,32));
    auto argument=[&](unsigned index) { return std::uint32_t(memory.load(std::uint32_t(stack+4u+index*4u),32)); };
    auto access=[&]() -> NativeAccess& {
        auto* bridge=dynamic_cast<NativeAccess*>(&memory);
        if(!bridge || sizeof(void*)!=4) throw std::runtime_error("native pointer API requires checked Windows x86 process backing");
        return *bridge;
    };
    // These are opaque Windows HANDLE tokens, never memory dereferences.
    auto handle=[](std::uint32_t token) { return reinterpret_cast<HANDLE>(std::uintptr_t(token)); };
    unsigned cleanup=0; bool returns_eax=true; std::uint32_t result=0;
    if(invoke_batch_native_import(import,memory,argument,result,cleanup,returns_eax)) {
        // Generated bindings share the existing native FP, last-error and ABI
        // transport. The SDK verifies their prototypes at compile time.
    } else if(!kernel && !registry && !multimedia && !user && !shell) {
        throw std::runtime_error("unmodeled native DLL import");
    } else if(shell) {
        if(std::strcmp(import.symbol,"SHGetFolderPathW")!=0) throw std::runtime_error("unmodeled native SHELL32 function signature");
        static_assert(sizeof(wchar_t)==2 && MAX_PATH==260 && sizeof(HRESULT)==4);
        auto owner=argument(0),csidl=argument(1),token=argument(2),flags=argument(3),destination=argument(4);
        if(owner) throw std::runtime_error("SHGetFolderPathW reserved owner requires NULL");
        if(token && token!=0xffffffffu) throw std::runtime_error("SHGetFolderPathW user-token ownership is unimplemented");
        auto& bridge=access();
        auto* output=static_cast<wchar_t*>(bridge.native_pointer(destination,MAX_PATH*sizeof(wchar_t),true,false));
        result=std::uint32_t(call_native([&]{ return ::SHGetFolderPathW(nullptr,std::bit_cast<int>(csidl),handle(token),flags,output); }));
        // The API guarantees an empty string on error/S_FALSE. Preserve the
        // actual bytes and HRESULT; only the resulting string has a defined
        // output footprint. Unknown/unwritten tail bytes stay unknown.
        unsigned length=0;
        while(length<MAX_PATH && output[length]!=0) ++length;
        if(length==MAX_PATH || (result!=std::uint32_t(S_OK) && length))
            throw std::runtime_error("SHGetFolderPathW violated declared output-string contract");
        bridge.complete_native_write(destination,(length+1u)*sizeof(wchar_t));
        cleanup=20;
    } else if(user) {
        bool icon=std::strcmp(import.symbol,"LoadIconW")==0;
        if(!icon && std::strcmp(import.symbol,"LoadCursorW")!=0) throw std::runtime_error("unmodeled native USER32 function signature");
        auto module=checked_resource_module(memory,access(),argument(0)); auto name=argument(1);
        auto text=name>0xffffu ? read_guest_utf16(memory,name) : std::wstring{};
        auto resource=name<=0xffffu ? MAKEINTRESOURCEW(name) : text.c_str();
        result=call_native([&] {
            return icon ? std::uint32_t(reinterpret_cast<std::uintptr_t>(::LoadIconW(module,resource))) :
                std::uint32_t(reinterpret_cast<std::uintptr_t>(::LoadCursorW(module,resource)));
        });
        if(result) { if(icon) native_shared_icons.insert(result); else native_shared_cursors.insert(result); }
        cleanup=8;
    } else if(multimedia) {
        if(std::strcmp(import.symbol,"timeGetTime")!=0) throw std::runtime_error("unmodeled native multimedia function signature");
        result=call_native([&]{ return ::timeGetTime(); });
    } else if(registry) {
        static_assert(sizeof(HKEY)==4 && sizeof(wchar_t)==2);
        if(std::strcmp(import.symbol,"RegOpenKeyExW")==0) {
            auto parent=checked_registry_key(argument(0)); auto name_address=argument(1),options=argument(2),rights=argument(3),destination=argument(4);
            (void)access().native_pointer(destination,4,true,false);
            auto name=name_address ? read_guest_utf16(memory,name_address) : std::wstring{};
            HKEY opened=nullptr;
            result=std::uint32_t(call_native([&]{ return ::RegOpenKeyExW(parent,name_address ? name.c_str() : nullptr,options,rights,&opened); }));
            auto token=std::uint32_t(reinterpret_cast<std::uintptr_t>(opened));
            if(result==ERROR_SUCCESS) {
                if(!token) throw std::runtime_error("RegOpenKeyExW returned success without a key");
                if(!predefined_registry_key(token) && !native_open_registry_keys.insert(token).second)
                    throw std::runtime_error("duplicate live registry key identity");
                memory.store(destination,token,32);
            } else {
                // The status is a real native failure, not a successful stub.
                // Failed out-key contents have no declared contract.
                memory.store_unknown(destination,token,32);
            }
            cleanup=20;
        } else if(std::strcmp(import.symbol,"RegCloseKey")==0) {
            auto token=argument(0); auto key=checked_registry_key(token);
            result=std::uint32_t(call_native([&]{ return ::RegCloseKey(key); })); cleanup=4;
            if(result==ERROR_SUCCESS && !predefined_registry_key(token)) native_open_registry_keys.erase(token);
        } else throw std::runtime_error("unmodeled native registry function signature");
    } else if(std::strcmp(import.symbol,"CreateMutexW")==0) {
        auto attributes_address=argument(0),initial_owner=argument(1),name_address=argument(2);
        SECURITY_ATTRIBUTES attributes{};
        if(attributes_address) attributes=read_native_security_attributes(memory,access(),attributes_address);
        auto name=name_address ? read_guest_utf16(memory,name_address) : std::wstring{};
        auto created=call_native([&]{ return ::CreateMutexW(attributes_address ? &attributes : nullptr,
            std::bit_cast<BOOL>(initial_owner),name_address ? name.c_str() : nullptr); });
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(created)); cleanup=12;
        if(result) register_native_kernel_handle(result,NativeKernelHandleKind::mutex);
    } else if(std::strcmp(import.symbol,"CreateEventW")==0) {
        auto attributes_address=argument(0),manual_reset=argument(1),initial_state=argument(2),name_address=argument(3);
        SECURITY_ATTRIBUTES attributes{};
        if(attributes_address) attributes=read_native_security_attributes(memory,access(),attributes_address);
        auto name=name_address ? read_guest_utf16(memory,name_address) : std::wstring{};
        auto created=call_native([&]{ return ::CreateEventW(attributes_address ? &attributes : nullptr,
            std::bit_cast<BOOL>(manual_reset),std::bit_cast<BOOL>(initial_state),name_address ? name.c_str() : nullptr); });
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(created));cleanup=16;
        if(result) register_native_kernel_handle(result,NativeKernelHandleKind::event);
    } else if(std::strcmp(import.symbol,"CreateSemaphoreW")==0) {
        auto attributes_address=argument(0),initial=argument(1),maximum=argument(2),name_address=argument(3);
        SECURITY_ATTRIBUTES attributes{};
        if(attributes_address) attributes=read_native_security_attributes(memory,access(),attributes_address);
        auto name=name_address ? read_guest_utf16(memory,name_address) : std::wstring{};
        auto created=call_native([&]{ return ::CreateSemaphoreW(attributes_address ? &attributes : nullptr,
            std::bit_cast<LONG>(initial),std::bit_cast<LONG>(maximum),name_address ? name.c_str() : nullptr); });
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(created));cleanup=16;
        if(result) register_native_kernel_handle(result,NativeKernelHandleKind::semaphore);
    } else if(std::strcmp(import.symbol,"WaitForSingleObject")==0 || std::strcmp(import.symbol,"WaitForSingleObjectEx")==0) {
        auto object=checked_native_kernel_handle(argument(0)); auto timeout=argument(1);
        bool extended=std::strcmp(import.symbol,"WaitForSingleObjectEx")==0;
        auto alertable=extended ? std::bit_cast<BOOL>(argument(2)) : FALSE;
        result=call_native([&]{ return extended ? ::WaitForSingleObjectEx(object,timeout,alertable) : ::WaitForSingleObject(object,timeout); });
        cleanup=extended ? 12 : 8;
    } else if(std::strcmp(import.symbol,"ReleaseMutex")==0) {
        auto object=checked_native_kernel_handle(argument(0));
        result=std::uint32_t(call_native([&]{ return ::ReleaseMutex(object); })); cleanup=4;
    } else if(std::strcmp(import.symbol,"CloseHandle")==0) {
        auto token=argument(0); auto object=checked_native_kernel_handle(token);
        std::lock_guard guard(native_kernel_handle_mutex);
        result=std::uint32_t(call_native([&]{ return ::CloseHandle(object); })); cleanup=4;
        if(result) {native_kernel_handles.erase(token);native_file_handles.erase(token);}
    } else if(std::strcmp(import.symbol,"SetUnhandledExceptionFilter")==0) {
        auto& bridge=access(); auto target=argument(0); bool translated=target && bridge.guest_image_address(target);
        result=call_native([&]{ return install_guest_unhandled_filter(target,translated); }); cleanup=4;
    } else if(std::strcmp(import.symbol,"GetCommandLineA")==0 || std::strcmp(import.symbol,"GetCommandLineW")==0) {
        result=import.symbol[14]=='A' ? process_command_line_a : process_command_line_w;
        if(!result) throw std::runtime_error("logical process command line is not initialized");
    } else if(std::strcmp(import.symbol,"GetModuleFileNameA")==0) {
        auto& bridge=access(); auto module=argument(0),destination=argument(1),capacity=argument(2); cleanup=12;
        if(module==0 || module==0x00400000) {
            if(logical_main_module_path_a.empty()) throw std::runtime_error("logical executable path is not initialized");
            if(!capacity) result=call_native([&]{ return ::GetModuleFileNameA(nullptr,nullptr,0); });
            else {
                auto* output=static_cast<char*>(bridge.native_pointer(destination,capacity,true,false));
                bool truncated=logical_main_module_path_a.size()>=capacity;
                // Keep this host's actual last-error and truncation convention.
                // In particular, Wine 11's ANSI truncation does not terminate
                // the buffer, despite the current Windows documentation.
                std::array<char,32768> probe{};
                auto probe_size=truncated ? DWORD(1) : DWORD(probe.size());
                auto observed=call_native([&]{ return ::GetModuleFileNameA(nullptr,probe.data(),probe_size); });
                if(!observed || (!truncated && observed>=probe_size)) throw std::runtime_error("native module-path convention probe failed");
                bool terminates=!truncated || probe[0]==0;
                if(truncated && std::any_of(logical_main_module_path_a.begin(),logical_main_module_path_a.end(),[](unsigned char c){ return c>=128; }))
                    throw std::runtime_error("truncated non-ASCII logical module paths require a code-page boundary adapter");
                auto copied=std::min<std::size_t>(logical_main_module_path_a.size(),capacity-(terminates ? 1u : 0u));
                std::memcpy(output,logical_main_module_path_a.data(),copied);
                if(terminates) output[copied]=0;
                bridge.complete_native_write(destination,copied+(terminates ? 1u : 0u));
                result=truncated ? capacity : std::uint32_t(copied);
            }
        } else {
            if(bridge.guest_image_address(module)) throw std::runtime_error("translated DLL path identity is not initialized");
            (void)registered_native_module(module);
            auto* output=capacity ? static_cast<char*>(bridge.native_pointer(destination,capacity,true,false)) : nullptr;
            result=call_native([&]{ return ::GetModuleFileNameA(reinterpret_cast<HMODULE>(std::uintptr_t(module)),output,capacity); });
            if(result) bridge.complete_native_write(destination,result<capacity ? result+1u : capacity);
        }
    } else if(std::strcmp(import.symbol,"GetModuleFileNameW")==0) {
        static_assert(sizeof(wchar_t)==2);
        auto& bridge=access(); auto module=argument(0),destination=argument(1),capacity=argument(2); cleanup=12;
        auto bytes=std::uint64_t(capacity)*sizeof(wchar_t);
        if(module==0 || module==0x00400000) {
            if(logical_main_module_path_w.empty()) throw std::runtime_error("logical UTF16 executable path is not initialized");
            if(!capacity) result=call_native([&]{ return ::GetModuleFileNameW(nullptr,nullptr,0); });
            else {
                auto* output=static_cast<wchar_t*>(bridge.native_pointer(destination,bytes,true,false));
                bool truncated=logical_main_module_path_w.size()>=capacity;
                std::array<wchar_t,32768> probe{};
                auto probe_size=truncated ? DWORD(1) : DWORD(probe.size());
                auto observed=call_native([&]{ return ::GetModuleFileNameW(nullptr,probe.data(),probe_size); });
                if(!observed || (!truncated && observed>=probe_size)) throw std::runtime_error("native UTF16 module-path convention probe failed");
                bool terminates=!truncated || probe[0]==0;
                auto copied=std::min<std::size_t>(logical_main_module_path_w.size(),capacity-(terminates ? 1u : 0u));
                std::memcpy(output,logical_main_module_path_w.data(),copied*sizeof(wchar_t));
                if(terminates) output[copied]=0;
                bridge.complete_native_write(destination,(copied+(terminates ? 1u : 0u))*sizeof(wchar_t));
                result=truncated ? capacity : std::uint32_t(copied);
            }
        } else {
            if(bridge.guest_image_address(module)) throw std::runtime_error("translated DLL UTF16 path identity is not initialized");
            (void)registered_native_module(module);
            auto* output=capacity ? static_cast<wchar_t*>(bridge.native_pointer(destination,bytes,true,false)) : nullptr;
            result=call_native([&]{ return ::GetModuleFileNameW(reinterpret_cast<HMODULE>(std::uintptr_t(module)),output,capacity); });
            if(result) bridge.complete_native_write(destination,(result<capacity ? std::uint64_t(result)+1u : capacity)*sizeof(wchar_t));
        }
    } else if(std::strcmp(import.symbol,"GetPrivateProfileStringW")==0) {
        auto& bridge=access(); auto section=argument(0),key=argument(1),fallback=argument(2),destination=argument(3),capacity=argument(4),filename=argument(5);
        if(!section || !key) throw std::runtime_error("GetPrivateProfileStringW section/key enumeration output contract is unimplemented");
        auto input=[&](std::uint32_t address) -> const wchar_t* {
            if(!address) return nullptr;
            auto text=read_guest_utf16(memory,address);
            return static_cast<const wchar_t*>(bridge.native_pointer(address,(std::uint64_t(text.size())+1u)*sizeof(wchar_t),false));
        };
        auto* native_section=input(section); auto* native_key=input(key); auto* native_fallback=input(fallback); auto* native_filename=input(filename);
        auto* output=capacity ? static_cast<wchar_t*>(bridge.native_pointer(destination,std::uint64_t(capacity)*sizeof(wchar_t),true,false)) : nullptr;
        result=call_native([&]{ return ::GetPrivateProfileStringW(native_section,native_key,native_fallback,output,capacity,native_filename); });
        if(capacity) {
            if(result>=capacity || output[result]!=0) throw std::runtime_error("GetPrivateProfileStringW violated declared scalar-string output contract");
            bridge.complete_native_write(destination,(std::uint64_t(result)+1u)*sizeof(wchar_t));
        }
        cleanup=24;
    } else if(std::strcmp(import.symbol,"CreateDirectoryW")==0) {
        auto address=argument(0),attributes_address=argument(1);
        if(!address) throw std::runtime_error("CreateDirectoryW requires a known nonnull path");
        auto path=read_guest_utf16(memory,address); SECURITY_ATTRIBUTES attributes{};
        if(attributes_address) attributes=read_native_security_attributes(memory,access(),attributes_address);
        result=std::uint32_t(call_native([&]{ return ::CreateDirectoryW(path.c_str(),attributes_address ? &attributes : nullptr); }));
        cleanup=8;
    } else if(std::strcmp(import.symbol,"SetCurrentDirectoryW")==0) {
        auto address=argument(0); auto path=address ? read_guest_utf16(memory,address) : std::wstring{};
        result=std::uint32_t(call_native([&]{ return ::SetCurrentDirectoryW(address ? path.c_str() : nullptr); }));
        cleanup=4;
    } else if(std::strcmp(import.symbol,"GetLastError")==0) result=native_error_context.value;
    else if(std::strcmp(import.symbol,"SetLastError")==0) {
        native_error_context.value=argument(0); ::SetLastError(native_error_context.value); cleanup=4; returns_eax=false;
    } else if(std::strcmp(import.symbol,"InterlockedIncrement")==0 || std::strcmp(import.symbol,"InterlockedDecrement")==0) {
        auto address=argument(0);
        if(address%alignof(LONG)) throw std::runtime_error("unaligned native interlocked operand");
        auto* value=static_cast<volatile LONG*>(access().native_pointer(address,sizeof(LONG),true));
        result=std::uint32_t(call_native([&]{ return import.symbol[11]=='I' ? ::InterlockedIncrement(value) : ::InterlockedDecrement(value); }));
        cleanup=4;
    } else if(std::strcmp(import.symbol,"InitializeCriticalSectionAndSpinCount")==0 || std::strcmp(import.symbol,"InitializeCriticalSectionEx")==0) {
        auto& bridge=access(); auto* section=static_cast<CRITICAL_SECTION*>(bridge.native_pointer(argument(0),sizeof(CRITICAL_SECTION),true));
        auto spin=argument(1);
        if(std::strcmp(import.symbol,"InitializeCriticalSectionEx")==0) {
            auto flags=argument(2); result=std::uint32_t(call_native([&]{ return ::InitializeCriticalSectionEx(section,spin,flags); })); cleanup=12;
        } else { result=std::uint32_t(call_native([&]{ return ::InitializeCriticalSectionAndSpinCount(section,spin); })); cleanup=8; }
    } else if(std::strcmp(import.symbol,"InitializeCriticalSection")==0 || std::strcmp(import.symbol,"DeleteCriticalSection")==0 ||
              std::strcmp(import.symbol,"EnterCriticalSection")==0 || std::strcmp(import.symbol,"LeaveCriticalSection")==0 ||
              std::strcmp(import.symbol,"TryEnterCriticalSection")==0) {
        auto& bridge=access(); auto* section=static_cast<CRITICAL_SECTION*>(bridge.native_pointer(argument(0),sizeof(CRITICAL_SECTION),true)); cleanup=4;
        if(std::strcmp(import.symbol,"TryEnterCriticalSection")==0) result=std::uint32_t(call_native([&]{ return ::TryEnterCriticalSection(section); }));
        else {
            call_native([&] {
                if(std::strcmp(import.symbol,"InitializeCriticalSection")==0) ::InitializeCriticalSection(section);
                else if(std::strcmp(import.symbol,"DeleteCriticalSection")==0) ::DeleteCriticalSection(section);
                else if(std::strcmp(import.symbol,"EnterCriticalSection")==0) ::EnterCriticalSection(section);
                else ::LeaveCriticalSection(section);
            });
            returns_eax=false;
        }
    }
    else if(std::strcmp(import.symbol,"MulDiv")==0) {
        auto first=argument(0),second=argument(1),third=argument(2);
        result=std::uint32_t(call_native([&]{ return ::MulDiv(std::bit_cast<std::int32_t>(first),std::bit_cast<std::int32_t>(second),std::bit_cast<std::int32_t>(third)); }));
        cleanup=12;
    } else if(std::strcmp(import.symbol,"GetCurrentProcessId")==0) result=call_native([&]{ return ::GetCurrentProcessId(); });
    else if(std::strcmp(import.symbol,"GetCurrentThreadId")==0) result=call_native([&]{ return ::GetCurrentThreadId(); });
    else if(std::strcmp(import.symbol,"GetTickCount")==0) result=call_native([&]{ return ::GetTickCount(); });
    else if(std::strcmp(import.symbol,"IsProcessorFeaturePresent")==0) {
        auto feature=argument(0); result=std::uint32_t(call_native([&]{ return ::IsProcessorFeaturePresent(feature); })); cleanup=4;
    }
    else if(std::strcmp(import.symbol,"GetACP")==0) result=call_native([&]{ return ::GetACP(); });
    else if(std::strcmp(import.symbol,"GetOEMCP")==0) result=call_native([&]{ return ::GetOEMCP(); });
    else if(std::strcmp(import.symbol,"IsValidCodePage")==0) {
        auto page=argument(0); result=std::uint32_t(call_native([&]{ return ::IsValidCodePage(page); })); cleanup=4;
    }
    else if(std::strcmp(import.symbol,"GetCPInfo")==0) {
        auto page=argument(0),destination=argument(1); auto& bridge=access();
        auto* info=static_cast<CPINFO*>(bridge.native_pointer(destination,sizeof(CPINFO),true,false));
        result=std::uint32_t(call_native([&]{ return ::GetCPInfo(page,info); })); cleanup=8;
        if(!result) throw std::runtime_error("GetCPInfo failed; output memory is unspecified");
        // Publish documented fields through the lead-range terminator. Do not
        // claim defined padding or unused array slots beyond that terminator.
        unsigned lead_bytes=0;
        while(lead_bytes+2<=sizeof(info->LeadByte)) {
            auto index=lead_bytes; lead_bytes+=2;
            if(!info->LeadByte[index] && !info->LeadByte[index+1]) break;
        }
        bridge.complete_native_write(destination+offsetof(CPINFO,MaxCharSize),sizeof(info->MaxCharSize));
        bridge.complete_native_write(destination+offsetof(CPINFO,DefaultChar),sizeof(info->DefaultChar));
        bridge.complete_native_write(destination+offsetof(CPINFO,LeadByte),lead_bytes);
    } else if(std::strcmp(import.symbol,"SetHandleCount")==0) {
        auto count=argument(0); result=call_native([&]{ return ::SetHandleCount(count); }); cleanup=4;
    } else if(std::strcmp(import.symbol,"LCMapStringW")==0) {
        auto& bridge=access(); auto locale=argument(0),flags=argument(1),source=argument(2),destination=argument(4);
        auto count=std::bit_cast<std::int32_t>(argument(3)),capacity=std::bit_cast<std::int32_t>(argument(5));
        if(count==0 || capacity<0)
            throw std::runtime_error("unsupported LCMapStringW count/capacity contract");
        std::uint64_t characters=count<0 ? 0 : std::uint32_t(count);
        if(count<0) {
            while(characters<8*1024*1024 && source+characters*2<=0xfffffffeULL && memory.load(source+characters*2,16)) ++characters;
            if(characters==8*1024*1024 || source+characters*2>0xfffffffeULL)
                throw std::runtime_error("locale-map input exceeds supported terminated-string bound");
            ++characters;
        }
        auto* input=static_cast<const wchar_t*>(bridge.native_pointer(source,characters*2,false));
        auto output_bytes=std::uint64_t(capacity)*((flags&LCMAP_SORTKEY) ? 1u : unsigned(sizeof(wchar_t)));
        auto* output=capacity ? static_cast<wchar_t*>(bridge.native_pointer(destination,output_bytes,true,false)) : nullptr;
        result=std::uint32_t(call_native([&]{ return ::LCMapStringW(locale,flags,input,count,output,capacity); })); cleanup=24;
        if(!result) throw std::runtime_error("LCMapStringW failed; output memory is unspecified");
        if(capacity) {
            if(result>std::uint32_t(capacity)) throw std::runtime_error("LCMapStringW result exceeds checked output capacity");
            bridge.complete_native_write(destination,std::uint64_t(result)*((flags&LCMAP_SORTKEY) ? 1u : unsigned(sizeof(wchar_t))));
        }
    } else if(std::strcmp(import.symbol,"GetStringTypeW")==0) {
        auto& bridge=access(); auto kind=argument(0),source=argument(1),destination=argument(3);
        auto count=std::bit_cast<std::int32_t>(argument(2));
        if(count==0) throw std::runtime_error("unsupported zero-length GetStringTypeW contract");
        std::uint64_t characters=count<0 ? 0 : std::uint32_t(count);
        if(count<0) {
            while(characters<8*1024*1024 && source+characters*2<=0xfffffffeULL && memory.load(source+characters*2,16)) ++characters;
            if(characters==8*1024*1024 || source+characters*2>0xfffffffeULL)
                throw std::runtime_error("classification input exceeds supported terminated-string bound");
            ++characters;
        }
        auto* input=static_cast<const wchar_t*>(bridge.native_pointer(source,characters*2,false));
        auto* output=static_cast<WORD*>(bridge.native_pointer(destination,characters*sizeof(WORD),true,false));
        result=std::uint32_t(call_native([&]{ return ::GetStringTypeW(kind,input,count,output); })); cleanup=16;
        if(!result) throw std::runtime_error("GetStringTypeW failed; output memory is unspecified");
        bridge.complete_native_write(destination,characters*sizeof(WORD));
    } else if(std::strcmp(import.symbol,"MultiByteToWideChar")==0) {
        auto& bridge=access(); auto page=argument(0),flags=argument(1),source=argument(2),destination=argument(4);
        auto count=std::bit_cast<std::int32_t>(argument(3)),capacity=std::bit_cast<std::int32_t>(argument(5));
        if(count==0 || count< -1 || capacity<0)
            throw std::runtime_error("unsupported MultiByteToWideChar count/capacity contract");
        std::uint64_t bytes=count==-1 ? 0 : std::uint32_t(count);
        if(count==-1) {
            while(bytes<8*1024*1024 && source+bytes<=0xffffffffULL && memory.load(source+bytes,8)) ++bytes;
            if(bytes==8*1024*1024 || source+bytes>0xffffffffULL)
                throw std::runtime_error("multibyte input exceeds supported terminated-string bound");
            ++bytes;
        }
        auto* input=static_cast<const char*>(bridge.native_pointer(source,bytes,false));
        auto* output=capacity ? static_cast<wchar_t*>(bridge.native_pointer(destination,std::uint64_t(capacity)*sizeof(wchar_t),true,false)) : nullptr;
        result=std::uint32_t(call_native([&]{ return ::MultiByteToWideChar(page,flags,input,count,output,capacity); })); cleanup=24;
        if(!result) throw std::runtime_error("MultiByteToWideChar failed; output memory is unspecified");
        if(capacity) {
            if(result>std::uint32_t(capacity)) throw std::runtime_error("MultiByteToWideChar result exceeds checked output capacity");
            bridge.complete_native_write(destination,std::uint64_t(result)*sizeof(wchar_t));
        }
    } else if(std::strcmp(import.symbol,"WideCharToMultiByte")==0) {
        auto& bridge=access(); auto page=argument(0),flags=argument(1),source=argument(2),destination=argument(4);
        auto count=std::bit_cast<std::int32_t>(argument(3)),capacity=std::bit_cast<std::int32_t>(argument(5));
        auto fallback=argument(6),used=argument(7);
        if(count==0 || count< -1 || capacity<0 || fallback)
            throw std::runtime_error("unsupported WideCharToMultiByte count/default-character contract");
        std::uint64_t characters=count==-1 ? 0 : std::uint32_t(count);
        if(count==-1) {
            while(characters<8*1024*1024 && source+characters*2<=0xfffffffeULL && memory.load(source+characters*2,16)) ++characters;
            if(characters==8*1024*1024 || source+characters*2>0xfffffffeULL)
                throw std::runtime_error("wide input exceeds supported terminated-string bound");
            ++characters;
        }
        auto* input=static_cast<const wchar_t*>(bridge.native_pointer(source,characters*2,false));
        auto* output=capacity ? static_cast<char*>(bridge.native_pointer(destination,std::uint32_t(capacity),true,false)) : nullptr;
        auto* changed=used ? static_cast<BOOL*>(bridge.native_pointer(used,sizeof(BOOL),true,false)) : nullptr;
        result=std::uint32_t(call_native([&]{ return ::WideCharToMultiByte(page,flags,input,count,output,capacity,nullptr,changed); })); cleanup=32;
        if(!result) throw std::runtime_error("WideCharToMultiByte failed; output memory is unspecified");
        if(capacity) {
            if(result>std::uint32_t(capacity)) throw std::runtime_error("WideCharToMultiByte result exceeds checked output capacity");
            bridge.complete_native_write(destination,result);
        }
        if(used) bridge.complete_native_write(used,sizeof(BOOL));
    } else if(std::strcmp(import.symbol,"GetEnvironmentStringsW")==0) {
        auto& bridge=access(); auto* block=call_native([&]{ return ::GetEnvironmentStringsW(); });
        if(block) {
            std::size_t length=0;
            while(length<8*1024*1024 && (block[length] || block[length+1])) ++length;
            if(length==8*1024*1024) throw std::runtime_error("native environment block exceeds supported bound");
            result=bridge.register_native(block,(length+2)*sizeof(wchar_t),true,false);
            std::lock_guard guard(native_registry_mutex); native_environment_blocks.insert(block);
        }
    } else if(std::strcmp(import.symbol,"FreeEnvironmentStringsW")==0) {
        auto& bridge=access(); auto* block=static_cast<wchar_t*>(bridge.native_pointer(argument(0),2,false));
        { std::lock_guard guard(native_registry_mutex);
          if(!native_environment_blocks.contains(block)) throw std::runtime_error("free of unowned environment block"); }
        result=std::uint32_t(call_native([&]{ return ::FreeEnvironmentStringsW(block); })); cleanup=4;
        if(result) {
            bridge.forget_native(block);
            std::lock_guard guard(native_registry_mutex); native_environment_blocks.erase(block);
        }
    } else if(std::strcmp(import.symbol,"GetStdHandle")==0) {
        auto kind=argument(0);
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(call_native([&]{ return ::GetStdHandle(kind); }))); cleanup=4;
    } else if(std::strcmp(import.symbol,"GetFileType")==0) {
        auto file=handle(argument(0)); result=call_native([&]{ return ::GetFileType(file); }); cleanup=4;
    }
    else if(std::strcmp(import.symbol,"TlsAlloc")==0) {
        (void)access(); result=call_native([&]{ return ::TlsAlloc(); }); auto error=::GetLastError();
        if(result!=TLS_OUT_OF_INDEXES) { std::lock_guard guard(native_registry_mutex); guest_tls_slots.insert(result); }
        ::SetLastError(error);
    } else if(std::strcmp(import.symbol,"TlsSetValue")==0 || std::strcmp(import.symbol,"FlsSetValue")==0) {
        (void)access(); bool fls=import.symbol[0]=='F'; auto index=argument(0),value=argument(1); require_guest_slot(index,fls);
        // TLS/FLS stores an opaque value without dereferencing it. These tokens
        // may represent guest data or code and round-trip unchanged.
        auto token=reinterpret_cast<PVOID>(std::uintptr_t(value));
        result=std::uint32_t(call_native([&]{ return fls ? ::FlsSetValue(index,token) : ::TlsSetValue(index,token); })); cleanup=8;
    } else if(std::strcmp(import.symbol,"TlsGetValue")==0 || std::strcmp(import.symbol,"FlsGetValue")==0) {
        (void)access(); bool fls=import.symbol[0]=='F'; auto index=argument(0); require_guest_slot(index,fls);
        auto token=call_native([&]{ return fls ? ::FlsGetValue(index) : ::TlsGetValue(index); });
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(token)); cleanup=4;
    } else if(std::strcmp(import.symbol,"TlsFree")==0) {
        (void)access(); auto index=argument(0); require_guest_slot(index,false); result=std::uint32_t(call_native([&]{ return ::TlsFree(index); })); auto error=::GetLastError();
        if(result) { std::lock_guard guard(native_registry_mutex); guest_tls_slots.erase(index); }
        ::SetLastError(error); cleanup=4;
    } else if(std::strcmp(import.symbol,"FlsAlloc")==0) {
        (void)access(); auto target=argument(0); result=call_native([&]{ return allocate_guest_fls(target); }); cleanup=4;
    } else if(std::strcmp(import.symbol,"FlsFree")==0) {
        (void)access(); auto index=argument(0); result=std::uint32_t(call_native([&]{ return free_guest_fls(index); })); cleanup=4;
    } else if(std::strcmp(import.symbol,"EncodePointer")==0 || std::strcmp(import.symbol,"DecodePointer")==0) {
        (void)access(); auto token=reinterpret_cast<PVOID>(std::uintptr_t(argument(0)));
        auto encoded=call_native([&]{ return import.symbol[0]=='E' ? ::EncodePointer(token) : ::DecodePointer(token); });
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(encoded)); cleanup=4;
    }
    else if(std::strcmp(import.symbol,"GetModuleHandleA")==0) {
        auto& bridge=access(); auto pointer=argument(0);
        if(!pointer) throw std::runtime_error("main translated module handle needs process identity adapter");
        auto name=read_guest_ansi(memory,pointer); auto key=native_module_key(name);
        if(key=="umbra.dll" || key=="daorigins.exe") throw std::runtime_error("translated module handle needs process identity adapter");
        auto module=call_native([&]{ return ::GetModuleHandleA(name.c_str()); }); auto error=::GetLastError();
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(module));
        if(bridge.guest_image_address(result)) throw std::runtime_error("native module overlaps translated image namespace");
        register_native_module(result,name);
        if(native_binding_trace) native_binding_trace("module_lookup",result,name.c_str(),"");
        ::SetLastError(error); cleanup=4;
    } else if(std::strcmp(import.symbol,"GetProcAddress")==0) {
        auto& bridge=access(); auto module=argument(0),token=argument(1); auto library=registered_native_module(module);
        std::string name=token<=65535 ? "@ordinal:"+std::to_string(token) : read_guest_ansi(memory,token);
        auto symbol=token<=65535 ? reinterpret_cast<LPCSTR>(std::uintptr_t(token)) : name.c_str();
        auto pointer=call_native([&]{ return ::GetProcAddress(reinterpret_cast<HMODULE>(std::uintptr_t(module)),symbol); }); auto error=::GetLastError();
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(pointer));
        if(bridge.guest_image_address(result)) throw std::runtime_error("native export overlaps translated image namespace");
        register_dynamic_native_import(result,library,name);
        if(native_binding_trace) native_binding_trace("symbol_lookup",result,library.c_str(),name.c_str());
        ::SetLastError(error); cleanup=8;
    }
    else if(std::strcmp(import.symbol,"GetProcessHeap")==0) {
        (void)access(); result=std::uint32_t(reinterpret_cast<std::uintptr_t>(call_native([&]{ return ::GetProcessHeap(); })));
        if(result) native_process_heaps.insert(result);
    } else if(std::strcmp(import.symbol,"HeapLock")==0 || std::strcmp(import.symbol,"HeapUnlock")==0) {
        (void)access(); auto heap=handle(argument(0));
        result=std::uint32_t(call_native([&]{ return std::strcmp(import.symbol,"HeapLock")==0 ? ::HeapLock(heap) : ::HeapUnlock(heap); })); cleanup=4;
    } else if(std::strcmp(import.symbol,"HeapCreate")==0) {
        (void)access(); auto flags=argument(0),initial=argument(1),maximum=argument(2);
        if(flags&HEAP_GENERATE_EXCEPTIONS) throw std::runtime_error("native heap exceptions are not implemented");
        result=std::uint32_t(reinterpret_cast<std::uintptr_t>(call_native([&]{ return ::HeapCreate(flags,initial,maximum); }))); cleanup=12;
        if(result && !native_owned_heaps.insert(result).second) throw std::runtime_error("duplicate live heap identity");
    } else if(std::strcmp(import.symbol,"HeapDestroy")==0) {
        (void)access();
        throw std::runtime_error("HeapDestroy requires allocation-owner lifetime tracking");
    } else if(std::strcmp(import.symbol,"HeapAlloc")==0) {
        auto& bridge=access(); auto heap=checked_native_heap(argument(0)); auto flags=argument(1); auto size=argument(2);
        if(flags&HEAP_GENERATE_EXCEPTIONS) throw std::runtime_error("native heap exceptions are not implemented");
        auto* pointer=call_native([&]{ return ::HeapAlloc(heap,flags,size); });
        if(pointer) {
            auto actual_size=::HeapSize(heap,0,pointer);
            if(actual_size==SIZE_T(-1) || actual_size<size) throw std::runtime_error("native heap allocation size unknown");
            result=bridge.register_heap(pointer,actual_size ? actual_size : 1,argument(0),size);
        }
        cleanup=12;
    } else if(std::strcmp(import.symbol,"HeapSize")==0) {
        auto& bridge=access(); auto heap=checked_native_heap(argument(0)); auto flags=argument(1); auto token=argument(2);
        auto* pointer=bridge.heap_pointer(token,argument(0));
        result=std::uint32_t(call_native([&]{ return ::HeapSize(heap,flags,pointer); })); cleanup=12;
    } else if(std::strcmp(import.symbol,"HeapReAlloc")==0) {
        auto& bridge=access(); auto heap_token=argument(0); auto heap=handle(heap_token);
        auto flags=argument(1),token=argument(2),size=argument(3);
        if(flags&HEAP_GENERATE_EXCEPTIONS) throw std::runtime_error("native heap exceptions are not implemented");
        auto* pointer=bridge.heap_pointer(token,heap_token);
        auto* resized=call_native([&]{ return ::HeapReAlloc(heap,flags,pointer,size); });
        if(resized) {
            auto actual_size=::HeapSize(heap,0,resized);
            if(actual_size==SIZE_T(-1) || actual_size<size) throw std::runtime_error("native resized heap allocation size unknown");
            result=bridge.replace_heap(token,heap_token,resized,actual_size ? actual_size : 1,size);
        }
        cleanup=16;
    } else if(std::strcmp(import.symbol,"HeapFree")==0) {
        auto& bridge=access(); auto heap=checked_native_heap(argument(0)); auto flags=argument(1); auto token=argument(2);
        auto* pointer=token ? bridge.heap_pointer(token,argument(0)) : nullptr;
        result=std::uint32_t(call_native([&]{ return ::HeapFree(heap,flags,pointer); }));
        if(result && pointer) bridge.forget_native(pointer);
        cleanup=12;
    } else if(std::strcmp(import.symbol,"GetVersionExA")==0) {
        auto& bridge=access(); auto address=argument(0); auto size=std::uint32_t(memory.load(address,32));
        if(size!=sizeof(OSVERSIONINFOA) && size!=sizeof(OSVERSIONINFOEXA)) throw std::runtime_error("unsupported version-info layout");
        auto* pointer=static_cast<OSVERSIONINFOA*>(bridge.native_pointer(address,size,true));
        result=std::uint32_t(call_native([&]{ return ::GetVersionExA(pointer); })); cleanup=4;
    } else if(std::strcmp(import.symbol,"GetStartupInfoA")==0) {
        auto& bridge=access(); auto destination=argument(0); STARTUPINFOA info{}; call_native([&]{ ::GetStartupInfoA(&info); });
        if(sizeof(STARTUPINFOA)!=68) throw std::runtime_error("unsupported startup-info host layout");
        auto keep_string=[&](char* text) {
            if(!text) return;
            std::size_t length=0; while(length<65536 && text[length]) ++length;
            if(length==65536) throw std::runtime_error("native startup string exceeds supported bound");
            bridge.register_native(text,length+1,true,false);
        };
        if(info.lpReserved) throw std::runtime_error("non-null reserved startup field is unsupported");
        keep_string(info.lpDesktop); keep_string(info.lpTitle);
        if(info.lpReserved2 && info.cbReserved2) bridge.register_native(info.lpReserved2,info.cbReserved2,true,false);
        const auto* bytes=reinterpret_cast<const std::uint8_t*>(&info);
        for(unsigned i=0;i<68;i++) memory.store(std::uint32_t(destination+i),bytes[i],8);
        cleanup=4; returns_eax=false;
    }
    else if(std::strcmp(import.symbol,"GetSystemInfo")==0) {
        static_assert(sizeof(SYSTEM_INFO)==36 && offsetof(SYSTEM_INFO,dwPageSize)==4 &&
                      offsetof(SYSTEM_INFO,lpMinimumApplicationAddress)==8 && offsetof(SYSTEM_INFO,lpMaximumApplicationAddress)==12 &&
                      offsetof(SYSTEM_INFO,dwActiveProcessorMask)==16 && offsetof(SYSTEM_INFO,dwNumberOfProcessors)==20 &&
                      offsetof(SYSTEM_INFO,dwProcessorType)==24 && offsetof(SYSTEM_INFO,dwAllocationGranularity)==28 &&
                      offsetof(SYSTEM_INFO,wProcessorLevel)==32 && offsetof(SYSTEM_INFO,wProcessorRevision)==34);
        auto destination=argument(0); auto& bridge=access();
        (void)bridge.native_pointer(destination,36,true,false);
        auto reserved_written=reviewed_system_info_reserved_writer();
        SYSTEM_INFO info{}; call_native([&]{ ::GetSystemInfo(&info); });
        if(reserved_written && (!info.dwPageSize || !info.dwNumberOfProcessors || !info.dwAllocationGranularity))
            throw std::runtime_error("reviewed GetSystemInfo provider did not produce complete output");
        // Address limits are numeric process bounds, not owned live allocations.
        memory.store(destination,info.wProcessorArchitecture,16);
        if(reserved_written) memory.store(std::uint32_t(destination+2u),info.wReserved,16);
        else memory.store_unknown(std::uint32_t(destination+2u),info.wReserved,16);
        memory.store(std::uint32_t(destination+4u),info.dwPageSize,32);
        memory.store(std::uint32_t(destination+8u),std::uintptr_t(info.lpMinimumApplicationAddress),32);
        memory.store(std::uint32_t(destination+12u),std::uintptr_t(info.lpMaximumApplicationAddress),32);
        memory.store(std::uint32_t(destination+16u),info.dwActiveProcessorMask,32);
        memory.store(std::uint32_t(destination+20u),info.dwNumberOfProcessors,32);
        memory.store(std::uint32_t(destination+24u),info.dwProcessorType,32);
        memory.store(std::uint32_t(destination+28u),info.dwAllocationGranularity,32);
        memory.store(std::uint32_t(destination+32u),info.wProcessorLevel,16);
        memory.store(std::uint32_t(destination+34u),info.wProcessorRevision,16);
        cleanup=4; returns_eax=false;
    }
    else if(std::strcmp(import.symbol,"GetSystemTimeAsFileTime")==0) {
        auto destination=argument(0); FILETIME time;
        call_native([&]{ ::GetSystemTimeAsFileTime(&time); });
        memory.store(destination,std::uint64_t(time.dwLowDateTime)|(std::uint64_t(time.dwHighDateTime)<<32),64);
        cleanup=4; returns_eax=false;
    } else if(std::strcmp(import.symbol,"QueryPerformanceFrequency")==0) {
        static_assert(sizeof(LARGE_INTEGER)==8);
        auto& bridge=access(); auto destination=argument(0);
        auto* frequency=static_cast<LARGE_INTEGER*>(bridge.native_pointer(destination,sizeof(LARGE_INTEGER),true,false));
        result=std::uint32_t(call_native([&]{ return ::QueryPerformanceFrequency(frequency); }));
        if(result) bridge.complete_native_write(destination,sizeof(LARGE_INTEGER));
        else {
            std::uint64_t value; std::memcpy(&value,frequency,sizeof(value));
            memory.store_unknown(destination,value,64);
        }
        cleanup=4;
    } else if(std::strcmp(import.symbol,"QueryPerformanceCounter")==0) {
        auto destination=argument(0); LARGE_INTEGER counter;
        auto succeeded=call_native([&]{ return ::QueryPerformanceCounter(&counter); });
        if(!succeeded) throw std::runtime_error("QueryPerformanceCounter failed; output memory is unspecified");
        memory.store(destination,std::uint64_t(counter.QuadPart),64);
        result=std::uint32_t(succeeded); cleanup=4;
    } else throw std::runtime_error("unmodeled native function signature");
    if(returns_eax) state.gpr[0]=result;
    state.gpr[4]=std::uint32_t(stack+4u+cleanup);
    state.pc=return_address;
    sharp_retro::invalidate_gprs(state,7);
    state.defined_xmm&=~std::uint16_t(0xff); // All XMM registers are volatile in the Win32 ABI.
    if(!native_floating_bridge_enabled) { state.x87_status_defined=0; state.mxcsr_defined&=~std::uint32_t(0x3f); }
    state.defined_gpr=std::uint16_t(state.defined_gpr | (returns_eax ? 1u : 0u) | (1u<<4));
    state.flags &= ~(std::uint64_t(1)<<10);
    state.defined_flags=std::uint64_t(1)<<10; // ABI returns DF clear; arithmetic flags remain unknown.
    state.flag_origins={};
#else
    (void)state; (void)memory;
    throw std::runtime_error("native Windows x86 import bridge unavailable on this host");
#endif
#endif // native production versus explicit strict validation profile
}
} // namespace recomp_generated

#endif // Native production has no per-API dispatch/ownership headers.
