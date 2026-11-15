// Bounded PE32 TLS template/zero-fill/thread isolation debugging under Windows.
#include "image_tls.hpp"
#include <windows.h>
#include <cstdio>
using namespace recomp_generated;
using Read=std::uint32_t(*)(); using Write=void(*)(std::uint32_t);
struct Calls { Read read,zero4,zero8; Write write; bool thread_ok=false; };
static DWORD WINAPI other_thread(void* argument) {
    auto& calls=*static_cast<Calls*>(argument);
    bool initial=calls.read()==0x13579bdf && calls.zero4()==0 && calls.zero8()==0;
    calls.write(0x2468ace0); calls.thread_ok=initial && calls.read()==0x2468ace0;
    return calls.thread_ok ? 0 : 1;
}
int main(int argc,char** argv) {
 try {
    if(argc!=2 || sizeof(void*)!=4) return 2;
    auto dll=::LoadLibraryA(argv[1]); if(!dll) { std::fprintf(stderr,"LoadLibrary: %lu\n",::GetLastError()); return 3; }
    Calls calls{reinterpret_cast<Read>(::GetProcAddress(dll,"tls_read")),reinterpret_cast<Read>(::GetProcAddress(dll,"tls_zero4")),reinterpret_cast<Read>(::GetProcAddress(dll,"tls_zero8")),reinterpret_cast<Write>(::GetProcAddress(dll,"tls_write"))};
    if(!calls.read || !calls.write || !calls.zero4 || !calls.zero8) return 4;
    if(calls.read()!=0x13579bdf || calls.zero4()!=0 || calls.zero8()!=0) return 5;
    calls.write(0x11223344);
    auto thread=::CreateThread(nullptr,0,other_thread,&calls,0,nullptr); if(!thread) return 6;
    if(::WaitForSingleObject(thread,10000)!=WAIT_OBJECT_0 || !calls.thread_ok || calls.read()!=0x11223344) return 7;
    ::CloseHandle(thread);
    auto base=std::uint32_t(reinterpret_cast<std::uintptr_t>(dll));
    const auto* bytes=reinterpret_cast<const std::uint8_t*>(dll);
    auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(dll); auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS32*>(bytes+dos->e_lfanew);
    auto directory=pe->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_TLS];
    if(directory.Size!=24) return 8;
    auto* tls=reinterpret_cast<const IMAGE_TLS_DIRECTORY32*>(bytes+directory.VirtualAddress);
    if(tls->EndAddressOfRawData-tls->StartAddressOfRawData!=4 || tls->SizeOfZeroFill!=8 || tls->AddressOfCallBacks) return 9;
    // Copy headers and live data, including relocated TLS VAs. Discardable
    // sections and native instruction pages are not needed by the guest fixture.
    std::vector<std::uint8_t> image(pe->OptionalHeader.SizeOfImage,0);
    std::memcpy(image.data(),bytes,pe->OptionalHeader.SizeOfHeaders);
    auto* sections=IMAGE_FIRST_SECTION(pe);
    for(unsigned i=0;i<pe->FileHeader.NumberOfSections;i++) {
        const auto& section=sections[i];
        if((section.Characteristics&IMAGE_SCN_MEM_READ) && !(section.Characteristics&(IMAGE_SCN_MEM_EXECUTE|IMAGE_SCN_MEM_DISCARDABLE)))
            std::memcpy(image.data()+section.VirtualAddress,bytes+section.VirtualAddress,section.Misc.VirtualSize);
    }
    ImageMemory memory; memory.map_bytes("TLS fixture image",base,image.size(),true,true,image);
    memory.map_bytes("thread A",0x62000000,4096,true,true); memory.map_bytes("thread B",0x63000000,4096,true,true);
    ThreadTlsModule module{base,pe->OptionalHeader.SizeOfImage};
    ThreadTlsLayout a{0x62000000,0x62010000,0x62020000},b{0x63000000,0x63010000,0x63020000};
    initialize_image_tls(memory,{&module,1},a); initialize_image_tls(memory,{&module,1},b); memory.seal();
    auto guest_read=[&](const ThreadTlsLayout& layout,unsigned offset) {
        auto vector=std::uint32_t(memory.load(layout.fs_base+0x2c,32)); auto index=std::uint32_t(memory.load(tls->AddressOfIndex,32));
        auto block=std::uint32_t(memory.load(vector+index*4u,32)); return std::uint32_t(memory.load(block+offset,32));
    };
    if(guest_read(a,0)!=0x13579bdf || guest_read(b,0)!=0x13579bdf || guest_read(a,4)!=0 || guest_read(a,8)!=0) return 10;
    memory.store(a.data_address,0x11223344,32);
    if(guest_read(a,0)!=calls.read() || guest_read(b,0)!=0x13579bdf) return 11;
    bool bounds=false; try { (void)memory.load(a.vector_address+4,32); } catch(const std::runtime_error&) { bounds=true; }
    if(!bounds) return 12;
    // Nonempty callback lists must fail before publishing thread TLS state.
    ImageMemory callbacks; callbacks.map_bytes("callback fixture",base,image.size(),true,true,image);
    callbacks.store(base+directory.VirtualAddress+12,tls->StartAddressOfRawData,32);
    bool refused=false; try { initialize_image_tls(callbacks,{&module,1},a); } catch(const std::runtime_error& error) { refused=std::string(error.what()).find("callbacks")!=std::string::npos; }
    if(!refused) return 13;
    std::puts("{\"native_template_matches\":true,\"native_zero_fill_matches\":true,\"native_thread_isolation\":true,\"guest_thread_isolation\":true,\"unallocated_vector_slot_refused\":true,\"pending_callbacks_refused\":true}");
    return 0;
 } catch(const std::exception& error) { std::fprintf(stderr,"%s\n",error.what()); return 20; }
}
