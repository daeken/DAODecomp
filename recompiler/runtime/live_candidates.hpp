#pragma once
// Only compiled into the Windows startup explorer. Candidate DLLs contain our
// generated C++, never original executable code. Accepted DLLs remain loaded.
#include "candidate_api.hpp"
#include "image_memory.hpp"
#include "native_registry.hpp"
#include "live_identity.hpp"
#include <cstring>
#include <cstdio>
#include <iostream>
#include <map>
#include <windows.h>
namespace recomp_generated {
inline std::map<std::uint32_t,GuestStep> live_steps;
inline std::map<std::uint32_t,GuestFunction> live_functions;
inline std::vector<HMODULE> live_modules;
inline bool sha_text(const std::string& text) {
    return text.size()==64 && text.find_first_not_of("0123456789abcdef")==std::string::npos;
}
inline std::uint64_t live_origin() { return sharp_retro::fresh_unknown_origin(); }
inline std::string candidate_file_sha(const std::string& path) {
    std::ifstream file(path,std::ios::binary|std::ios::ate);
    auto size=file.tellg();
    if(!file || size<=0 || size>64*1024*1024) throw std::runtime_error("invalid candidate DLL file/size");
    file.seekg(0); std::vector<std::uint8_t> bytes(static_cast<std::size_t>(size));
    if(!file.read(reinterpret_cast<char*>(bytes.data()),size)) throw std::runtime_error("candidate DLL read failed");
    return image_sha256(bytes);
}
inline void load_candidate(const std::string& path,const std::string& dll_sha,const std::string& manifest_sha,std::uint32_t needed) {
    if(!sha_text(dll_sha) || !sha_text(manifest_sha) || path.size()>30000 || path.size()<3 || path[1]!=':' ||
       (path[2]!='\\' && path[2]!='/') || path.find('\0')!=std::string::npos)
        throw std::runtime_error("invalid candidate load command");
    // Retain a non-writable handle through loading so the checked bytes cannot
    // be replaced between hashing and LoadLibrary. This file is controller-owned.
    HANDLE file=::CreateFileA(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(file==INVALID_HANDLE_VALUE) throw std::runtime_error("candidate DLL lock failed");
    HMODULE module=nullptr;
    try {
        if(candidate_file_sha(path)!=dll_sha) throw std::runtime_error("candidate DLL hash mismatch");
        module=::LoadLibraryExA(path.c_str(),nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
        if(!module) throw std::runtime_error("candidate DLL load failed: "+std::to_string(::GetLastError()));
        auto entry=reinterpret_cast<CandidateEntry>(::GetProcAddress(module,"recomp_candidate_v1"));
        if(!entry) throw std::runtime_error("candidate DLL descriptor missing");
        const auto* d=entry();
        if(!d || !candidate_layout_matches(*d) || !d->abi_sha256 || candidate_abi!=std::string(d->abi_sha256) ||
           !d->manifest_sha256 || manifest_sha!=d->manifest_sha256 || !d->module_sha256 || !d->bind_origin ||
           !d->code || !d->functions || !d->code_count || d->code_count>100000 || !d->function_count || d->function_count>512)
            throw std::runtime_error("candidate ABI/identity mismatch");
        const CandidateModuleIdentity* owner=nullptr;
        for(const auto& item:candidate_module_identities)
            if(item.base==d->image_base && std::strcmp(item.sha256,d->module_sha256)==0) owner=&item;
        if(!owner) throw std::runtime_error("candidate module is not a pinned translated module");
        std::map<std::uint32_t,GuestStep> steps;
        std::map<std::uint32_t,GuestFunction> functions;
        auto original=compiled_code(); auto imports=declared_imports();
        for(unsigned i=0;i<d->code_count;i++) {
            auto item=d->code[i]; auto pc=item.address;
            auto old=std::lower_bound(original.begin(),original.end(),pc,[](const auto& a,auto b){return a.address<b;});
            auto imported=std::lower_bound(imports.begin(),imports.end(),pc,[](const auto& a,auto b){return a.address<b;});
            if(!item.step || pc<owner->base || std::uint64_t(pc)-owner->base>=owner->size ||
               (old!=original.end() && old->address==pc) || (imported!=imports.end() && imported->address==pc) ||
               resolve_dynamic_native_import(pc) || live_steps.contains(pc) || !steps.emplace(pc,item.step).second)
                throw std::runtime_error("candidate PC ownership collision/out of range");
        }
        if(!steps.contains(needed)) throw std::runtime_error("candidate omits requested missing PC");
        for(unsigned i=0;i<d->function_count;i++) {
            auto item=d->functions[i];
            if(!item.function || !steps.contains(item.address) || live_functions.contains(item.address) ||
               !functions.emplace(item.address,item.function).second) throw std::runtime_error("candidate entry ownership mismatch");
        }
        d->bind_origin(live_origin);
        // Allocate before publishing any callable pointers. Existing candidates
        // remain immutable and the module must outlive all stored function refs.
        live_modules.push_back(module);
        live_steps.merge(steps); live_functions.merge(functions);
        extra_guest_step=[](std::uint32_t pc)->GuestStep { auto i=live_steps.find(pc); return i==live_steps.end() ? nullptr : i->second; };
        extra_guest_function=[](std::uint32_t pc)->GuestFunction { auto i=live_functions.find(pc); return i==live_functions.end() ? nullptr : i->second; };
        std::printf("{\"event\":\"candidate_loaded\",\"sequence\":%u,\"pc\":%u,\"code_count\":%u,\"dll_sha256\":\"%s\",\"manifest_sha256\":\"%s\",\"game_started\":false}\n",
            unsigned(live_modules.size()),needed,d->code_count,dll_sha.c_str(),manifest_sha.c_str());
        std::fflush(stdout); module=nullptr;
    } catch(...) { if(module) ::FreeLibrary(module); ::CloseHandle(file); throw; }
    ::CloseHandle(file);
}
inline bool await_candidate(std::uint32_t address,std::uint64_t consumed,std::uint64_t budget) {
    std::printf("{\"event\":\"candidate_needed\",\"pc\":%u,\"consumed\":%llu,\"remaining_budget\":%llu,\"game_started\":false}\n",
        address,(unsigned long long)consumed,(unsigned long long)budget);
    std::fflush(stdout);
    std::string command;
    // Bounded input; EOF/stop preserves the ordinary explicit missing-code stop.
    for(char c;std::cin.get(c);) { if(c=='\n') break; if(command.size()>=32768) throw std::runtime_error("candidate command too long"); command+=c; }
    if(command=="stop" || command.empty()) return false;
    if(command.size()<135 || command.substr(0,5)!="load " || command[69]!=' ' || command[134]!=' ')
        throw std::runtime_error("malformed candidate command");
    load_candidate(command.substr(135),command.substr(5,64),command.substr(70,64),address);
    return true;
}
}
