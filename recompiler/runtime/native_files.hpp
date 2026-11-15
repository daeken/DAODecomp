#pragma once
#ifdef _WIN32
#include <map>
#include <set>
namespace recomp_generated {
inline std::map<std::uint32_t,DWORD> native_file_handles;
inline std::map<std::uint32_t,bool> native_find_handles;
inline HANDLE checked_native_file(std::uint32_t token,bool synchronous=false) {
    auto found=native_file_handles.find(token);
    if(found==native_file_handles.end()) throw std::runtime_error("file API requires a live created file handle");
    if(synchronous && (found->second&FILE_FLAG_OVERLAPPED))
        throw std::runtime_error("overlapped file I/O requires pending-operation lifetime transport");
    return checked_native_kernel_handle(token);
}
template<class A> void* file_span(NativeBatchArguments<A>& a,std::uint32_t address,std::uint64_t size,bool write,bool known) {
    return a.access().native_pointer(address,size,write,known);
}
template<bool Wide,class A> void file_create(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto attributes_address=a.argument(3),flags=a.argument(5),template_token=a.argument(6);
    auto rights=a.argument(1),sharing=a.argument(2),creation=a.argument(4);
    SECURITY_ATTRIBUTES attributes{};
    if(attributes_address) attributes=read_native_security_attributes(a.memory,a.access(),attributes_address);
    auto template_file=template_token ? checked_native_file(template_token) : nullptr;
    HANDLE opened;
    if constexpr(Wide) {
        auto name=a.template text<wchar_t>(0,false,-1);
        opened=call_native([&]{return ::CreateFileW(name,rights,sharing,attributes_address ? &attributes:nullptr,creation,flags,template_file);});
    } else {
        auto name=a.template text<char>(0,false,-1);
        opened=call_native([&]{return ::CreateFileA(name,rights,sharing,attributes_address ? &attributes:nullptr,creation,flags,template_file);});
    }
    result=std::uint32_t(reinterpret_cast<std::uintptr_t>(opened));
    if(opened!=INVALID_HANDLE_VALUE) {
        if(!opened || !native_file_handles.emplace(result,flags).second) throw std::runtime_error("duplicate or null created file handle");
        register_native_kernel_handle(result,NativeKernelHandleKind::file);
    }
}
template<class A> void native_bridge_CreateFileA(NativeBatchArguments<A>& a,std::uint32_t& r) {file_create<false>(a,r);}
template<class A> void native_bridge_CreateFileW(NativeBatchArguments<A>& a,std::uint32_t& r) {file_create<true>(a,r);}
template<bool Write,class A> void file_transfer(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto file=checked_native_file(a.argument(0),true);
    auto address=a.argument(1),size=a.argument(2),count_address=a.argument(3),overlapped=a.argument(4);
    if(overlapped) throw std::runtime_error("OVERLAPPED I/O requires explicit pending-operation transport");
    if(!count_address) throw std::runtime_error("synchronous file transfer contract requires a count output");
    auto* buffer=file_span(a,address,size,!Write,Write);
    auto* count=static_cast<DWORD*>(file_span(a,count_address,4,true,false));
    result=std::uint32_t(call_native([&]{
        if constexpr(Write) return ::WriteFile(file,buffer,size,count,nullptr);
        else return ::ReadFile(file,buffer,size,count,nullptr);
    }));
    DWORD transferred;std::memcpy(&transferred,count,4);
    if(transferred>size) throw std::runtime_error("native transfer count exceeds checked buffer");
    // The actual shared count pointer preserves buffer/stack aliases and the
    // native API's initial zeroing. Both APIs define this DWORD for sync calls.
    if constexpr(!Write) {
        if(result) a.access().complete_native_write(address,transferred);
        else a.finish_output(address,size,false);
    }
    a.access().complete_native_write(count_address,4);
}
template<class A> void native_bridge_ReadFile(NativeBatchArguments<A>& a,std::uint32_t& r) {file_transfer<false>(a,r);}
template<class A> void native_bridge_WriteFile(NativeBatchArguments<A>& a,std::uint32_t& r) {file_transfer<true>(a,r);}
template<class A> void native_bridge_GetFileSize(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto file=checked_native_file(a.argument(0));auto address=a.argument(1);
    auto* high=address ? static_cast<DWORD*>(file_span(a,address,4,true,false)):nullptr;
    result=call_native([&]{return ::GetFileSize(file,high);});
    if(high) a.finish_output(address,4,result!=INVALID_FILE_SIZE || native_error_context.value==NO_ERROR);
}
template<class A> void native_bridge_SetFilePointer(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto file=checked_native_file(a.argument(0));auto low=a.template scalar<LONG>(1);
    auto address=a.argument(2),method=a.argument(3);
    auto* high=address ? static_cast<LONG*>(file_span(a,address,4,true,true)):nullptr;
    result=call_native([&]{return ::SetFilePointer(file,low,high,method);});
    if(high) a.finish_output(address,4,result!=INVALID_SET_FILE_POINTER || native_error_context.value==NO_ERROR);
}
template<class A> void native_bridge_SetEndOfFile(NativeBatchArguments<A>& a,std::uint32_t& r) {
    auto file=checked_native_file(a.argument(0));r=std::uint32_t(call_native([&]{return ::SetEndOfFile(file);}));
}
template<class A> void native_bridge_FlushFileBuffers(NativeBatchArguments<A>& a,std::uint32_t& r) {
    auto file=checked_native_file(a.argument(0));r=std::uint32_t(call_native([&]{return ::FlushFileBuffers(file);}));
}
template<class A> void native_bridge_CancelIo(NativeBatchArguments<A>& a,std::uint32_t& r) {
    auto file=checked_native_file(a.argument(0));r=std::uint32_t(call_native([&]{return ::CancelIo(file);}));
}
template<bool Wide,class A> void find_output(NativeBatchArguments<A>& a,std::uint32_t address,bool success) {
    using Data=std::conditional_t<Wide,WIN32_FIND_DATAW,WIN32_FIND_DATAA>;
    static_assert(offsetof(Data,cFileName)==44 && offsetof(Data,dwReserved0)==36);
    Data storage;std::memcpy(&storage,file_span(a,address,sizeof(Data),true,false),sizeof(Data));auto* value=&storage;
    a.finish_output(address,sizeof(Data),false);
    if(!success) return;
    // Reserved fields, unused string tails and A-layout padding stay unknown.
    a.access().complete_native_write(address,36);
    if(value->dwFileAttributes&FILE_ATTRIBUTE_REPARSE_POINT) a.access().complete_native_write(address+36,4);
    auto string=[&](const auto& text,std::size_t offset) {
        unsigned count=0;while(count<std::size(text) && text[count]) ++count;
        if(count==std::size(text)) throw std::runtime_error("unterminated native find-result string");
        a.access().complete_native_write(address+offset,(count+1)*sizeof(text[0]));
    };
    string(value->cFileName,offsetof(Data,cFileName));string(value->cAlternateFileName,offsetof(Data,cAlternateFileName));
}
template<bool Wide,class A> void find_first(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto address=a.argument(1);HANDLE found;
    if constexpr(Wide) {
        auto name=a.template text<wchar_t>(0,false,-1);auto* data=static_cast<WIN32_FIND_DATAW*>(file_span(a,address,sizeof(WIN32_FIND_DATAW),true,false));
        found=call_native([&]{return ::FindFirstFileW(name,data);});
    } else {
        auto name=a.template text<char>(0,false,-1);auto* data=static_cast<WIN32_FIND_DATAA*>(file_span(a,address,sizeof(WIN32_FIND_DATAA),true,false));
        found=call_native([&]{return ::FindFirstFileA(name,data);});
    }
    result=std::uint32_t(reinterpret_cast<std::uintptr_t>(found));bool success=found!=INVALID_HANDLE_VALUE;
    if(success && !native_find_handles.emplace(result,Wide).second) throw std::runtime_error("duplicate find handle");
    find_output<Wide>(a,address,success);
}
template<class A> void native_bridge_FindFirstFileA(NativeBatchArguments<A>& a,std::uint32_t& r) {find_first<false>(a,r);}
template<class A> void native_bridge_FindFirstFileW(NativeBatchArguments<A>& a,std::uint32_t& r) {find_first<true>(a,r);}
template<class A> void native_bridge_FindNextFileW(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto token=a.argument(0),address=a.argument(1);
    auto found=native_find_handles.find(token);
    if(found==native_find_handles.end() || !found->second) throw std::runtime_error("FindNextFileW requires a live wide-character search");
    auto* data=static_cast<WIN32_FIND_DATAW*>(file_span(a,address,sizeof(WIN32_FIND_DATAW),true,false));
    result=std::uint32_t(call_native([&]{return ::FindNextFileW(reinterpret_cast<HANDLE>(std::uintptr_t(token)),data);}));
    find_output<true>(a,address,result!=0);
}
template<class A> void native_bridge_FindClose(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto token=a.argument(0);
    if(!native_find_handles.contains(token)) throw std::runtime_error("FindClose requires a live search handle");
    result=std::uint32_t(call_native([&]{return ::FindClose(reinterpret_cast<HANDLE>(std::uintptr_t(token)));}));
    if(result) native_find_handles.erase(token);
}
template<bool Wide,bool Full,class A> void file_path_output(NativeBatchArguments<A>& a,std::uint32_t& result) {
    using Char=std::conditional_t<Wide,wchar_t,char>;
    const Char* source=nullptr;
    if constexpr(Full) source=a.template text<Char>(0,false,-1);
    auto capacity=a.argument(Full ? 1:0),address=a.argument(Full ? 2:1);
    auto* buffer=capacity ? static_cast<Char*>(file_span(a,address,std::uint64_t(capacity)*sizeof(Char),true,false)):nullptr;
    auto part_address=Full ? a.argument(3):0;
    auto** part=part_address ? static_cast<Char**>(file_span(a,part_address,4,true,false)):nullptr;
    result=call_native([&] {
        if constexpr(Full && Wide) return ::GetFullPathNameW(source,capacity,buffer,part);
        else if constexpr(Full) return ::GetFullPathNameA(source,capacity,buffer,part);
        else if constexpr(Wide) return ::GetCurrentDirectoryW(capacity,buffer);
        else return ::GetCurrentDirectoryA(capacity,buffer);
    });
    bool complete=result && result<capacity;
    if(capacity) {
        if(complete) a.access().complete_native_write(address,(std::uint64_t(result)+1)*sizeof(Char));
        else a.finish_output(address,std::uint64_t(capacity)*sizeof(Char),false);
    }
    if(part) {
        Char* part_value=nullptr;std::memcpy(&part_value,part,sizeof(part_value));
        if(complete && part_value) {
            auto token=reinterpret_cast<std::uintptr_t>(part_value);
            if(token<address || token>std::uint64_t(address)+std::uint64_t(result)*sizeof(Char) || (token-address)%sizeof(Char))
                throw std::runtime_error("native file-part pointer outside returned path");
        }
        a.finish_output(part_address,4,complete);
    }
}
template<class A> void native_bridge_GetCurrentDirectoryA(NativeBatchArguments<A>& a,std::uint32_t& r) {file_path_output<false,false>(a,r);}
template<class A> void native_bridge_GetCurrentDirectoryW(NativeBatchArguments<A>& a,std::uint32_t& r) {file_path_output<true,false>(a,r);}
template<class A> void native_bridge_GetFullPathNameA(NativeBatchArguments<A>& a,std::uint32_t& r) {file_path_output<false,true>(a,r);}
template<class A> void native_bridge_GetFullPathNameW(NativeBatchArguments<A>& a,std::uint32_t& r) {file_path_output<true,true>(a,r);}
template<class A> void native_bridge_GetDiskFreeSpaceExA(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto path=a.template text<char>(0,true,-1);std::array<std::uint32_t,3> addresses{};std::array<PULARGE_INTEGER,3> outputs{};
    for(unsigned i=0;i<3;++i) {addresses[i]=a.argument(i+1);if(addresses[i]) outputs[i]=static_cast<PULARGE_INTEGER>(file_span(a,addresses[i],8,true,false));}
    result=std::uint32_t(call_native([&]{return ::GetDiskFreeSpaceExA(path,outputs[0],outputs[1],outputs[2]);}));
    for(auto address:addresses) if(address) a.finish_output(address,8,result!=0);
}
template<class A> void native_bridge_ReadDirectoryChangesW(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto file=checked_native_file(a.argument(0),true);
    auto address=a.argument(1),size=a.argument(2),filter=a.argument(4),count_address=a.argument(5);
    auto subtree=a.template scalar<BOOL>(3);auto overlapped=a.argument(6),callback=a.argument(7);
    if(overlapped || callback || !count_address) throw std::runtime_error("directory notification requires synchronous count-output contract");
    auto* buffer=file_span(a,address,size,true,false);
    auto* count=static_cast<DWORD*>(file_span(a,count_address,4,true,false));
    if(address%sizeof(DWORD)) throw std::runtime_error("directory notification buffer requires DWORD alignment");
    result=std::uint32_t(call_native([&]{return ::ReadDirectoryChangesW(file,buffer,size,subtree,filter,count,nullptr,nullptr);}));
    if(result) {
        DWORD bytes;std::memcpy(&bytes,count,4);if(bytes>size) throw std::runtime_error("directory notification exceeds checked buffer");
        a.access().complete_native_write(address,bytes);a.access().complete_native_write(count_address,4);
    } else {a.finish_output(address,size,false);a.finish_output(count_address,4,false);}
}
} // namespace recomp_generated
#endif
