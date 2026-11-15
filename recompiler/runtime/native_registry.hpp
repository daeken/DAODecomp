#pragma once
#include "runtime_api.hpp"
#include <deque>
#include <mutex>
#include <string>
#include <utility>
namespace recomp_generated {
struct DynamicNativeImport {
    std::string library,symbol;
    ImportEntry entry;
    DynamicNativeImport(std::uint32_t address,std::string lib,std::string name)
        : library(std::move(lib)),symbol(std::move(name)),entry{address,library.c_str(),symbol.c_str(),false} {}
};
inline std::deque<DynamicNativeImport> dynamic_native_imports;
inline std::deque<std::pair<std::uint32_t,std::string>> native_modules;
inline std::mutex native_registry_mutex;
// Optional tracing hook; no native function is called through a guessed type.
inline void (*native_binding_trace)(const char*,std::uint32_t,const char*,const char*)=nullptr;
inline std::string native_module_key(std::string name) {
    auto split=name.find_last_of("/\\"); if(split!=std::string::npos) name.erase(0,split+1);
    for(auto& c:name) if(c>='A' && c<='Z') c=char(c-'A'+'a');
    // GetModuleHandle applies the default DLL extension to names without one.
    // A trailing dot explicitly suppresses it. Both spellings can name the
    // same live module and must share one dispatch identity.
    if(!name.empty() && name.back()=='.') name.pop_back();
    else if(name.find('.')==std::string::npos) name+=".dll";
    return name;
}
inline void register_native_module(std::uint32_t handle,std::string name) {
    if(!handle) return;
    auto key=native_module_key(std::move(name));
    std::lock_guard guard(native_registry_mutex);
    for(const auto& module:native_modules) if(module.first==handle) {
        if(module.second!=key) throw std::runtime_error("ambiguous native module handle identity");
        return;
    }
    native_modules.emplace_back(handle,std::move(key));
}
inline std::string registered_native_module(std::uint32_t handle) {
    std::lock_guard guard(native_registry_mutex);
    for(const auto& module:native_modules) if(module.first==handle) return module.second;
    throw std::runtime_error("GetProcAddress requires a registered native module handle");
}
inline void register_dynamic_native_import(std::uint32_t address,const std::string& library,const std::string& symbol) {
    if(!address) return;
    std::lock_guard guard(native_registry_mutex);
    for(const auto& old:dynamic_native_imports) if(old.entry.address==address) {
        if(old.library!=library || old.symbol!=symbol) throw std::runtime_error("ambiguous dynamically resolved native target");
        return;
    }
    dynamic_native_imports.emplace_back(address,library,symbol);
}
inline const ImportEntry* resolve_dynamic_native_import(std::uint32_t address) {
    std::lock_guard guard(native_registry_mutex);
    for(const auto& binding:dynamic_native_imports) if(binding.entry.address==address) return &binding.entry;
    return nullptr; // Unknown target remains an explicit dispatcher failure.
}
inline std::wstring read_guest_utf16(sharp_retro::Memory& memory,std::uint32_t address) {
    std::wstring value;
    for(unsigned i=0;i<32768;i++) {
        auto cursor=std::uint64_t(address)+std::uint64_t(i)*2;
        if(cursor>0xfffffffeULL) throw std::runtime_error("wrapping UTF16 string");
        auto unit=std::uint16_t(memory.load(cursor,16));
        if(!unit) return value;
        value+=wchar_t(unit);
    }
    throw std::runtime_error("UTF16 string exceeds supported bound");
}
inline std::string read_guest_ansi(sharp_retro::Memory& memory,std::uint32_t address) {
    if(!address) throw std::runtime_error("null guest string");
    std::string value;
    for(unsigned i=0;i<65536;i++) {
        if(std::uint64_t(address)+i>0xffffffffULL) throw std::runtime_error("wrapping guest string");
        auto c=std::uint8_t(memory.load(address+i,8)); if(!c) return value;
        value+=char(c);
    }
    throw std::runtime_error("guest string exceeds supported bound");
}
}
