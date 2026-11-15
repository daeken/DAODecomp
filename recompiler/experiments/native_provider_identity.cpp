// Native loader/cache debugging, not recovered-function or game acceptance.
#include "native_provider_identity.hpp"
#include <cstdio>
#include <cstring>
#include <vector>

namespace {
void require(bool value,const char* reason) {if(!value) throw std::runtime_error(reason);}
std::string independently_query(HMODULE module) {
    char path[32768];auto size=GetModuleFileNameA(module,path,sizeof(path));
    require(size && size<sizeof(path),"independent filename query failed");
    std::string result(path,size);
    for(char& c:result) if(c>='A' && c<='Z') c=char(c-'A'+'a');
    auto slash=result.find_last_of("/\\");
    return result.substr(slash==std::string::npos ? 0:slash+1);
}
struct Worker {
    std::atomic<unsigned> phase{0};
    std::atomic<HMODULE> module{nullptr};
    std::string names[2];
};
void wait_phase(Worker& worker,unsigned expected) {
    auto started=GetTickCount();
    while(worker.phase.load(std::memory_order_acquire)!=expected) {
        require(worker.phase.load()!=99,"worker identity query failed");
        require(DWORD(GetTickCount()-started)<10000,"worker synchronization timed out");
        Sleep(1);
    }
}
DWORD WINAPI observe_worker(void* argument) {
    auto& worker=*static_cast<Worker*>(argument);
    try {
        for(unsigned i=0;i<2;++i) {
            wait_phase(worker,i*2+1);
            worker.names[i]=recomp_generated::native_provider_identity(worker.module.load());
            worker.phase.store(i*2+2,std::memory_order_release);
        }
        return 0;
    } catch(...) {worker.phase.store(99,std::memory_order_release);return 10;}
}
}
int main(int argc,char** argv) try {
    using namespace recomp_generated;
    namespace detail=native_provider_identity_detail;
    require(argc==3,"expected two owned fixed-base fixture DLL paths");
    auto kernel=GetModuleHandleW(L"kernel32.dll");
    auto one=native_provider_identity(kernel);auto first=detail::queries.load();
    auto two=native_provider_identity(kernel);auto second=detail::queries.load();
    bool available=detail::notifications_available;
    require(one==two && two==independently_query(kernel),"warm identity differs from independent query");
    require(available ? second==first:second==first+1,"warm query/fallback count differs");
    unsigned reused=0,unloaded=0,rounds=0;void* prior_base=nullptr;FARPROC prior_target=nullptr;
    auto epoch_before=detail::epoch.load();
    for(unsigned round=0;round<8;++round) for(unsigned variant=0;variant<2;++variant) {
        auto module=LoadLibraryA(argv[variant+1]);require(module!=nullptr,"fixture load failed");
        auto target=GetProcAddress(module,"identity_marker");require(target!=nullptr,"fixture export missing");
        auto marker=reinterpret_cast<unsigned (__cdecl*)()>(target)();
        require(marker==(variant ? 0xb2u:0xa1u),"wrong fixture function executed");
        auto name=native_provider_identity(module);
        require(name==independently_query(module),"cached name survived module replacement");
        auto queries=detail::queries.load();
        require(native_provider_identity(module)==name,"second fixture query changed identity");
        require(available ? detail::queries.load()==queries:detail::queries.load()==queries+1,
                "fixture warm query/fallback count differs");
        if(prior_base) {require(module==prior_base && target==prior_target,"fixed-base target reuse not observed");++reused;}
        prior_base=module;prior_target=target;
        require(FreeLibrary(module)!=0,"fixture release failed");
        HMODULE remaining=nullptr;
        require(!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                    reinterpret_cast<LPCSTR>(target),&remaining),"cache retained a fixture DLL reference");
        ++unloaded;++rounds;
    }
    // The loader and the thread owning a warm cache are different here.
    // Unloading is synchronized while the worker is idle, never during a call.
    Worker worker;auto thread=CreateThread(nullptr,0,observe_worker,&worker,0,nullptr);
    require(thread!=nullptr,"worker creation failed");
    std::string expected[2];
    for(unsigned variant=0;variant<2;++variant) {
        auto module=LoadLibraryA(argv[variant+1]);require(module!=nullptr,"worker fixture load failed");
        auto target=GetProcAddress(module,"identity_marker");
        require(module==prior_base && target==prior_target,"worker target address reuse missing");
        expected[variant]=independently_query(module);
        worker.module.store(module);worker.phase.store(variant*2+1,std::memory_order_release);
        wait_phase(worker,variant*2+2);
        require(FreeLibrary(module)!=0,"worker fixture release failed");
        HMODULE remaining=nullptr;
        require(!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                    reinterpret_cast<LPCSTR>(target),&remaining),"worker cache retained a DLL reference");
        ++rounds;++reused;++unloaded;
    }
    require(WaitForSingleObject(thread,10000)==WAIT_OBJECT_0,"worker did not return");CloseHandle(thread);
    require(worker.names[0]==expected[0] && worker.names[1]==expected[1] && expected[0]!=expected[1],
            "cross-thread cached name survived module replacement");
    auto epoch_after=detail::epoch.load();
    require(!available || epoch_after>=epoch_before+rounds*2,"load/unload notifications missing");
    // Explicit saturation policy control; no wrapped epoch may reuse names.
    detail::epoch.store(std::numeric_limits<std::uint32_t>::max());
    auto before_saturation=detail::queries.load();
    require(native_provider_identity(kernel)==one && native_provider_identity(kernel)==one,"saturated identity changed");
    require(detail::queries.load()==before_saturation+2,"saturated epoch reused cached names");
    detail::changed(1,nullptr,nullptr);
    require(detail::epoch.load()==std::numeric_limits<std::uint32_t>::max(),"epoch wrapped");
    bool invalid_refused=false;
    try {(void)native_provider_identity(reinterpret_cast<HMODULE>(1));}
    catch(const std::runtime_error&) {invalid_refused=true;}
    require(invalid_refused,"invalid module identity did not refuse");
    std::printf("{\"notifications_available\":%s,\"fixture_loads\":%u,\"same_address_reuses\":%u,\"actual_unloads\":%u,\"epoch_before\":%u,\"epoch_after\":%u,\"cross_thread_replacement\":true,\"saturation_fallback\":true,\"invalid_refused\":true,\"game_acceptance\":false}\n",
                available ? "true":"false",rounds,reused,unloaded,epoch_before,epoch_after);
    return 0;
} catch(const std::exception& error) {
    std::fprintf(stderr,"provider identity control: %s\n",error.what());return 10;
}
