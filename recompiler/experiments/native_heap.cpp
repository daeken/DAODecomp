// Bounded Windows x86 heap bridge debugging; no game-equivalence claim.
#include "native_imports.hpp"
#include "process_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main() {
 try {
    ProcessMemory memory; memory.map_bytes("stack",0x50000000,65536,true,true); memory.seal();
    auto invoke=[&](const char* symbol,std::initializer_list<std::uint32_t> args) {
        sharp_retro::State state; state.gpr[4]=0x50000800;
        memory.store(state.gpr[4],0x12345678,32); unsigned index=1;
        for(auto arg:args) memory.store(state.gpr[4]+4u*index++,arg,32);
        invoke_native_import({0,"KERNEL32.dll",symbol,false},state,memory);
        if(state.pc!=0x12345678 || state.gpr[4]!=0x50000800+4u*index || !(state.defined_gpr&1)) throw std::runtime_error("heap ABI mismatch");
        return std::uint32_t(state.gpr[0]);
    };
    auto heap=invoke("GetProcessHeap",{});
    if(!heap || !invoke("HeapLock",{heap}) || !invoke("HeapUnlock",{heap})) return 1;
    unsigned moved=0,unchanged=0;
    for(unsigned iteration=0;iteration<16;iteration++) {
        auto address=invoke("HeapAlloc",{heap,HEAP_ZERO_MEMORY,128});
        auto barrier=invoke("HeapAlloc",{heap,0,128});
        if(!address || !barrier || memory.load(address,32)!=0 || invoke("HeapSize",{heap,0,address})<128) return 2;
        sharp_retro::State unknown; unknown.defined_gpr=0; unknown.gpr[0]=0x13579bdf;
        auto scalar=sharp_retro::scalar_gpr32(unknown,0);
        scalar.known|=0xff00u; // Preserve both known bits and copied unknown IDs.
        for(unsigned bit=8;bit<16;bit++) scalar.origins[bit]=0;
        memory.store_scalar32(address+8,scalar); memory.store(address+24,0x89abcdef,32);
        auto resized=invoke("HeapReAlloc",{heap,HEAP_ZERO_MEMORY,address,65536});
        if(!resized) return 3;
        moved+=resized!=address; unchanged+=resized==address;
        auto copy=memory.load_scalar32(resized+8);
        if(copy.value!=scalar.value || copy.known!=scalar.known || copy.origins!=scalar.origins ||
           memory.load(resized+24,32)!=0x89abcdef || memory.load(resized+65532,32)!=0) {
            std::fprintf(stderr,"copy value=%08x/%08x known=%08x/%08x origins=%d data=%08x tail=%08x\n",copy.value,scalar.value,copy.known,scalar.known,int(copy.origins==scalar.origins),unsigned(memory.load(resized+24,32)),unsigned(memory.load(resized+65532,32)));
            return 4;
        }
        bool refused=false;
        try { (void)memory.native_pointer(resized+8,4,false); } catch(const sharp_retro::UnknownMemoryRead&) { refused=true; }
        if(!refused) return 5;
        refused=false;
        try { (void)invoke("HeapSize",{heap,0,resized+8}); } catch(const std::runtime_error&) { refused=true; }
        if(!refused) return 6;
        refused=false;
        try { (void)invoke("HeapReAlloc",{heap+1,0,resized,32}); } catch(const std::runtime_error&) { refused=true; }
        if(!refused) return 7;
        auto smaller=invoke("HeapReAlloc",{heap,HEAP_REALLOC_IN_PLACE_ONLY,resized,64});
        if(smaller!=resized || memory.load_scalar32(smaller+8).origins!=scalar.origins) return 8;
        auto failed=invoke("HeapReAlloc",{heap,HEAP_REALLOC_IN_PLACE_ONLY,smaller,0xfffffff0u});
        if(failed || memory.load_scalar32(smaller+8).origins!=scalar.origins || memory.load(smaller+24,32)!=0x89abcdef) return 9;
        // Freeing unknown contents is valid; released byte identities cannot leak
        // into a subsequent registration at the same address.
        auto* backing=memory.heap_pointer(smaller,heap);
        if(!invoke("HeapFree",{heap,0,smaller})) return 10;
        refused=false;
        try { (void)memory.heap_pointer(smaller,heap); } catch(const std::runtime_error&) { refused=true; }
        if(!refused) return 11;
        memory.register_native(backing,64,true,true); memory.check_known(smaller+8,32); memory.forget_native(backing);
        if(!invoke("HeapFree",{heap,0,barrier})) return 12;
    }
    // Force a moved-metadata transition independently of allocator placement.
    auto* old_block=::HeapAlloc(::GetProcessHeap(),0,64); auto* new_block=::HeapAlloc(::GetProcessHeap(),0,128);
    if(!old_block || !new_block) return 13;
    auto old_address=memory.register_heap(old_block,64,heap,64);
    sharp_retro::State state; state.defined_gpr=0; auto scalar=sharp_retro::scalar_gpr32(state,0);
    memory.store_scalar32(old_address+4,scalar); std::memcpy(new_block,old_block,64); ::HeapFree(::GetProcessHeap(),0,old_block);
    auto new_address=memory.replace_heap(old_address,heap,new_block,128,128);
    if(memory.load_scalar32(new_address+4).origins!=scalar.origins || !invoke("HeapFree",{heap,0,new_address})) return 14;
    constexpr std::uint32_t large_size=(257u<<20)+13u;
    auto large=invoke("HeapAlloc",{heap,0,large_size});
    if(!large || invoke("HeapSize",{heap,0,large})<large_size) return 15;
    memory.store(large,0x12345678,32); memory.store(large+large_size-4u,0x89abcdef,32);
    if(memory.load(large,32)!=0x12345678 || memory.load(large+large_size-4u,32)!=0x89abcdef || !invoke("HeapFree",{heap,0,large})) return 16;
    std::printf("{\"resize_cases\":16,\"native_moves\":%u,\"native_in_place\":%u,\"forced_metadata_move\":true,\"taint_preserved\":true,\"failed_resize_preserves_block\":true,\"heap_owner_checked\":true,\"free_clears_taint\":true,\"large_allocation_bytes\":%u,\"large_allocation_endpoints\":true}\n",moved,unchanged,large_size);
    return 0;
 } catch(const std::exception& error) { std::fprintf(stderr,"%s\n",error.what()); return 20; }
}
