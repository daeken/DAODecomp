// Integrated file/memory boundary debugging under Windows x86; no game acceptance.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
#define CHECK(x) do {if(!(x)) throw std::runtime_error(std::string("line ")+std::to_string(__LINE__)+": "+#x);} while(false)
struct NotifyControl {std::wstring directory;LONG stop=0;};
DWORD WINAPI notify_control(void* input) {
    auto& control=*static_cast<NotifyControl*>(input);
    for(unsigned i=0;i<1000 && !::InterlockedCompareExchange(&control.stop,0,0);++i) {
        ::Sleep(10);auto path=control.directory+L"\\notify-"+std::to_wstring(i)+L".txt";
        auto file=::CreateFileW(path.c_str(),GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,CREATE_NEW,0,nullptr);
        if(file!=INVALID_HANDLE_VALUE) {::CloseHandle(file);::DeleteFileW(path.c_str());}
    }
    return 0;
}
int main() {try {
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);
    memory.map_bytes("data",0x50010000,65536,true,true);memory.map_bytes("readonly",0x50030000,4096,true,false);memory.seal();
    unsigned calls=0,guards=0;
    auto invoke=[&](const char* name,std::initializer_list<std::uint32_t> arguments) {
        sharp_retro::State state;state.gpr[4]=0x50000800;
        for(unsigned r:{3u,5u,6u,7u}) state.gpr[r]=0x12340000+r;
        memory.store(0x50000800,0x12345678,32);unsigned index=0;
        for(auto value:arguments) memory.store(0x50000804+4*index++,value,32);
        native_error_context.value=0x13579;
        invoke_native_import({0,"KERNEL32.dll",name,false},state,memory);
        CHECK(state.pc==0x12345678 && state.gpr[4]==0x50000804+arguments.size()*4 && (state.defined_gpr&1) && !(state.defined_gpr&6));
        for(unsigned r:{3u,5u,6u,7u}) CHECK(state.gpr[r]==0x12340000+r);
        ++calls;return std::uint32_t(state.gpr[0]);
    };
    auto refuse=[&](auto operation) {try {operation();throw std::logic_error("missing refusal");}catch(const std::runtime_error&){++guards;}};
    auto put=[&](std::uint32_t address,const auto& text) {
        using Char=typename std::decay_t<decltype(text)>::value_type;
        for(std::size_t i=0;i<=text.size();++i) memory.store(address+i*sizeof(Char),std::make_unsigned_t<Char>(text.c_str()[i]),sizeof(Char)*8);
    };
    wchar_t temp[MAX_PATH],unique[MAX_PATH];CHECK(::GetTempPathW(MAX_PATH,temp));CHECK(::GetTempFileNameW(temp,L"DCF",0,unique));CHECK(::DeleteFileW(unique));CHECK(::CreateDirectoryW(unique,nullptr));
    std::wstring directory=unique,path=directory+L"\\probe.bin";put(0x50010000,path);
    CHECK(invoke("CreateFileW",{0x50010000,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,0,0})==0xffffffffu);
    CHECK(native_error_context.value==ERROR_FILE_NOT_FOUND);
    auto file=invoke("CreateFileW",{0x50010000,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,0,CREATE_NEW,0,0});CHECK(file!=0xffffffffu);
    CHECK(invoke("GetFileType",{file})==FILE_TYPE_DISK);
    std::string content="0123456789abcdef";put(0x50011000,content);
    CHECK(invoke("WriteFile",{file,0x50011000,16,0x50012000,0}) && memory.load(0x50012000,32)==16);
    CHECK(invoke("FlushFileBuffers",{file}));CHECK(invoke("GetFileSize",{file,0x50012000})==16 && memory.load(0x50012000,32)==0);
    CHECK(invoke("SetFilePointer",{file,0,0,FILE_BEGIN})==0);
    for(unsigned i=0;i<32;++i) memory.store_unknown(0x50013000+i,0xa5,8);
    CHECK(invoke("ReadFile",{file,0x50013000,32,0x50012000,0}) && memory.load(0x50012000,32)==16);
    for(unsigned i=0;i<16;++i) CHECK(memory.load(0x50013000+i,8)==unsigned(content[i]));
    refuse([&]{(void)memory.load(0x50013010,8);}); // Unwritten tail is still unknown.
    memory.store(0x50013000,0xabcdef12,32);
    CHECK(invoke("ReadFile",{file,0x50013000,4,0x50012000,0}) && memory.load(0x50012000,32)==0 && memory.load(0x50013000,32)==0xabcdef12);
    CHECK(invoke("SetFilePointer",{file,0,0,FILE_BEGIN})==0);
    CHECK(invoke("ReadFile",{file,0x50013000,8,0x50013000,0}) && memory.load(0x50013000,32)==8);
    for(unsigned i=4;i<8;++i) CHECK(memory.load(0x50013000+i,8)==unsigned(content[i]));
    CHECK(invoke("SetFilePointer",{file,0,0,FILE_BEGIN})==0);
    CHECK(invoke("ReadFile",{file,0x50013000,4,0x50000804,0}) && memory.load(0x50000804,32)==4);
    CHECK(invoke("SetFilePointer",{file,4,0,FILE_BEGIN})==4 && invoke("SetEndOfFile",{file}) && invoke("GetFileSize",{file,0})==4);
    CHECK(invoke("CancelIo",{file}));
    // Compare alias-sensitive WriteFile against a real native control file.
    auto alias_path=directory+L"\\alias.tmp";auto control=::CreateFileW(alias_path.c_str(),GENERIC_READ|GENERIC_WRITE,0,nullptr,CREATE_NEW,0,nullptr);CHECK(control!=INVALID_HANDLE_VALUE);
    DWORD expected_alias[2]={0x41424344,0x45464748};CHECK(::WriteFile(control,expected_alias,8,&expected_alias[0],nullptr));
    memory.store(0x50014000,0x41424344,32);memory.store(0x50014004,0x45464748,32);
    CHECK(invoke("SetFilePointer",{file,0,0,FILE_BEGIN})==0 && invoke("WriteFile",{file,0x50014000,8,0x50014000,0}));
    CHECK(::SetFilePointer(control,0,nullptr,FILE_BEGIN)==0);DWORD expected_bytes[2],count=0;CHECK(::ReadFile(control,expected_bytes,8,&count,nullptr) && count==8);
    CHECK(invoke("SetFilePointer",{file,0,0,FILE_BEGIN})==0 && invoke("ReadFile",{file,0x50015000,8,0x50012000,0}));
    for(unsigned i=0;i<8;++i) CHECK(memory.load(0x50015000+i,8)==reinterpret_cast<unsigned char*>(expected_bytes)[i]);
    CHECK(::CloseHandle(control) && ::DeleteFileW(alias_path.c_str()));
    auto write_only=invoke("CreateFileW",{0x50010000,GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,0,0});CHECK(write_only!=0xffffffffu);
    memory.store(0x50013000,0xabcdef12,32);CHECK(!invoke("ReadFile",{write_only,0x50013000,4,0x50012000,0}));
    CHECK(native_error_context.value==ERROR_ACCESS_DENIED && memory.load(0x50012000,32)==0);
    refuse([&]{(void)memory.load(0x50013000,32);});CHECK(invoke("CloseHandle",{write_only}));
    auto overlapped=invoke("CreateFileW",{0x50010000,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,FILE_FLAG_OVERLAPPED,0});CHECK(overlapped!=0xffffffffu);
    refuse([&]{(void)invoke("ReadFile",{overlapped,0x50013000,4,0x50012000,0});});CHECK(invoke("CloseHandle",{overlapped}));
    refuse([&]{(void)invoke("WriteFile",{file,0x50013000,4,0x50012000,0});});
    refuse([&]{(void)invoke("ReadFile",{file,0x50030000,4,0x50012000,0});});
    refuse([&]{(void)invoke("ReadFile",{file,0x50013000,4,0x50012000,0x50016000});});
    CHECK(invoke("CloseHandle",{file}));refuse([&]{(void)invoke("GetFileSize",{file,0});});
    // Find records: compare defined fields against a real search of the same file.
    WIN32_FIND_DATAW expected_find{};auto reference_search=::FindFirstFileW(path.c_str(),&expected_find);CHECK(reference_search!=INVALID_HANDLE_VALUE && ::FindClose(reference_search));
    auto search=invoke("FindFirstFileW",{0x50010000,0x50016000});CHECK(search!=0xffffffffu);
    for(unsigned i=0;i<36;++i) CHECK(memory.load(0x50016000+i,8)==reinterpret_cast<unsigned char*>(&expected_find)[i]);
    for(unsigned i=0;i<=std::wcslen(expected_find.cFileName);++i) CHECK(memory.load(0x50016000+44+i*2,16)==std::uint16_t(expected_find.cFileName[i]));
    refuse([&]{(void)memory.load(0x50016000+40,32);});refuse([&]{(void)invoke("CloseHandle",{search});});
    CHECK(!invoke("FindNextFileW",{search,0x50016000}) && native_error_context.value==ERROR_NO_MORE_FILES);
    refuse([&]{(void)memory.load(0x50016000,32);});CHECK(invoke("FindClose",{search}));refuse([&]{(void)invoke("FindClose",{search});});
    char ansi[MAX_PATH*4];CHECK(::WideCharToMultiByte(CP_ACP,0,path.c_str(),-1,ansi,sizeof(ansi),nullptr,nullptr));put(0x50017000,std::string(ansi));
    auto ansi_file=invoke("CreateFileA",{0x50017000,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,0,0});CHECK(ansi_file!=0xffffffffu && invoke("CloseHandle",{ansi_file}));
    auto ansi_search=invoke("FindFirstFileA",{0x50017000,0x50016000});CHECK(ansi_search!=0xffffffffu && invoke("FindClose",{ansi_search}));
    wchar_t cwd[32768];auto cwd_length=::GetCurrentDirectoryW(32768,cwd);CHECK(cwd_length);
    CHECK(invoke("GetCurrentDirectoryW",{32768/2,0x50018000})==cwd_length);
    for(unsigned i=0;i<=cwd_length;++i) CHECK(memory.load(0x50018000+i*2,16)==std::uint16_t(cwd[i]));
    auto needed=invoke("GetCurrentDirectoryA",{0,0});CHECK(needed && invoke("GetCurrentDirectoryA",{1,0x50018000})==needed);
    refuse([&]{(void)memory.load(0x50018000,8);});
    put(0x50017000,std::string(".\\somewhere\\..\\probe.bin"));char full[32768],*part=nullptr;
    auto full_length=::GetFullPathNameA(".\\somewhere\\..\\probe.bin",sizeof(full),full,&part);CHECK(full_length);
    CHECK(invoke("GetFullPathNameA",{0x50017000,4096,0x50018000,0x50012000})==full_length);
    CHECK(memory.load(0x50012000,32)-0x50018000==unsigned(part-full));
    for(unsigned i=0;i<=full_length;++i) CHECK(memory.load(0x50018000+i,8)==static_cast<unsigned char>(full[i]));
    put(0x50017000,std::wstring(L".\\probe.bin"));CHECK(invoke("GetFullPathNameW",{0x50017000,4096,0x50018000,0x50012000}));
    CHECK(memory.load(0x50012000,32)>=0x50018000 && memory.load(0x50012000,32)<0x5001a000);
    CHECK(invoke("GetDiskFreeSpaceExA",{0,0x50012000,0x50012008,0x50012010}));CHECK(memory.load(0x50012008,64)>0);
    // A real native control thread produces notifications. It runs no guest code.
    put(0x50017000,directory);auto watched=invoke("CreateFileW",{0x50017000,FILE_LIST_DIRECTORY,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,0,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS,0});CHECK(watched!=0xffffffffu);
    NotifyControl notification{directory};auto thread=::CreateThread(nullptr,0,notify_control,&notification,0,nullptr);CHECK(thread);
    auto notified=invoke("ReadDirectoryChangesW",{watched,0x50018000,4096,0,FILE_NOTIFY_CHANGE_FILE_NAME,0x50012000,0,0});
    ::InterlockedExchange(&notification.stop,1);CHECK(::WaitForSingleObject(thread,15000)==WAIT_OBJECT_0 && ::CloseHandle(thread));
    CHECK(notified && memory.load(0x50012000,32)>=12 && memory.load(0x50018008,32)>=sizeof(wchar_t)*7);
    CHECK(memory.load(0x5001800c,16)=='n');CHECK(invoke("CloseHandle",{watched}));
    // Heap destruction retires all of its blocks while another heap survives.
    auto process_heap=invoke("GetProcessHeap",{}),heap=invoke("HeapCreate",{0,0,0});CHECK(heap);
    CHECK(invoke("HeapLock",{heap}) && invoke("HeapUnlock",{heap}));
    auto survivor=invoke("HeapAlloc",{process_heap,HEAP_ZERO_MEMORY,64});auto allocation=invoke("HeapAlloc",{heap,HEAP_ZERO_MEMORY,64});CHECK(survivor && allocation);
    sharp_retro::State unknown;unknown.defined_gpr=0;auto scalar=sharp_retro::scalar_gpr32(unknown,0);memory.store_scalar32(allocation+8,scalar);
    auto resized=invoke("HeapReAlloc",{heap,HEAP_ZERO_MEMORY,allocation,8192});CHECK(resized && memory.load_scalar32(resized+8).origins==scalar.origins);
    CHECK(invoke("HeapDestroy",{heap}));refuse([&]{(void)memory.load(resized,8);});refuse([&]{(void)invoke("HeapLock",{heap});});
    CHECK(memory.load(survivor,32)==0 && invoke("HeapFree",{process_heap,0,survivor}));refuse([&]{(void)invoke("HeapDestroy",{process_heap});});
    // Reserve, commit, partial decommit, recommit and release share one identity.
    auto reservation=invoke("VirtualAlloc",{0,65536,MEM_RESERVE,PAGE_READWRITE});CHECK(reservation);
    refuse([&]{(void)memory.load(reservation,8);});
    CHECK(invoke("VirtualAlloc",{reservation,12288,MEM_COMMIT,PAGE_READWRITE})==reservation && memory.load(reservation,32)==0);
    memory.store_scalar32(reservation+16,scalar);memory.store(reservation+8192,0x12345678,32);memory.store_unknown(reservation+4096,0x13579,32);
    CHECK(invoke("VirtualFree",{reservation+4096,4096,MEM_DECOMMIT}));
    refuse([&]{(void)memory.load(reservation+4096,8);});
    CHECK(memory.load_scalar32(reservation+16).origins==scalar.origins && memory.load(reservation+8192,32)==0x12345678);
    CHECK(invoke("VirtualAlloc",{reservation+4096,4096,MEM_COMMIT,PAGE_READWRITE})==reservation+4096 && memory.load(reservation+4096,32)==0);
    CHECK(invoke("VirtualAlloc",{reservation,4096,MEM_COMMIT,PAGE_READWRITE})==reservation && memory.load_scalar32(reservation+16).origins==scalar.origins);
    CHECK(!invoke("VirtualFree",{reservation,4096,MEM_RELEASE}) && memory.load(reservation+8192,32)==0x12345678);
    auto read_only=invoke("VirtualAlloc",{0,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READONLY});CHECK(read_only && memory.load(read_only,32)==0);
    refuse([&]{memory.store(read_only,1,8);});CHECK(invoke("VirtualFree",{read_only,0,MEM_RELEASE}));
    auto no_access=invoke("VirtualAlloc",{0,4096,MEM_RESERVE|MEM_COMMIT,PAGE_NOACCESS});CHECK(no_access);
    refuse([&]{(void)memory.load(no_access,8);});CHECK(invoke("VirtualFree",{no_access,0,MEM_RELEASE}));
    refuse([&]{(void)invoke("VirtualAlloc",{0x50010000,4096,MEM_COMMIT,PAGE_READWRITE});});
    refuse([&]{(void)invoke("VirtualAlloc",{0,4096,MEM_RESERVE|MEM_COMMIT,PAGE_EXECUTE_READWRITE});});
    refuse([&]{(void)invoke("VirtualFree",{0x50010000,0,MEM_RELEASE});});
    CHECK(invoke("VirtualFree",{reservation,0,MEM_DECOMMIT}));refuse([&]{(void)memory.load(reservation+8192,8);});
    CHECK(invoke("VirtualAlloc",{reservation,4096,MEM_COMMIT,PAGE_READWRITE})==reservation && memory.load(reservation+16,32)==0);
    CHECK(invoke("VirtualFree",{reservation,0,MEM_RELEASE}));refuse([&]{(void)memory.native_pointer(reservation,1,false);});
    CHECK(native_virtual_allocations.empty() && native_find_handles.empty() && native_file_handles.empty() && native_owned_heaps.empty());
    CHECK(::DeleteFileW(path.c_str()) && ::RemoveDirectoryW(directory.c_str()));
    std::printf("{\"native_calls\":%u,\"refusal_guards\":%u,\"file_bytes_and_eof\":true,\"native_alias_write_compared\":true,\"find_fields_compared\":true,\"path_interior_pointer\":true,\"real_directory_notification\":true,\"heap_destroy_retires_blocks\":true,\"partial_decommit_preserves_neighbors\":true,\"recommit_zeroes_new_pages\":true,\"recommit_preserves_live_unknowns\":true,\"all_owned_resources_retired\":true}\n",calls,guards);
    return 0;
}catch(const std::exception& e){std::fprintf(stderr,"native file/memory: %s\n",e.what());return 10;}}
