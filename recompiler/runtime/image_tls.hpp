#pragma once
#include "image_memory.hpp"

namespace recomp_generated {
struct ThreadTlsModule { std::uint32_t base,size; };
struct ThreadTlsLayout {
    std::uint32_t fs_base,vector_address,data_address;
    std::uint32_t slot_stride=65536,capacity=16;
};
// PE32 static TLS is a loader-owned vector, separate from the native TlsAlloc
// namespace. Copy the image template and declared zero-fill for this thread.
// Callbacks remain an explicit boundary until their execution is implemented.
inline void initialize_image_tls(ImageMemory& memory,std::span<const ThreadTlsModule> modules,const ThreadTlsLayout& layout) {
    if(memory.is_sealed() || !layout.capacity || layout.capacity>64 || layout.slot_stride!=65536 ||
       layout.vector_address%65536 || layout.data_address%65536 || layout.fs_base>0xffffffcfu ||
       std::uint64_t(layout.data_address)+std::uint64_t(layout.capacity)*layout.slot_stride>0x100000000ULL)
        throw std::runtime_error("invalid static TLS thread layout");
    struct Pending { std::uint32_t index_address; std::vector<std::uint8_t> bytes; };
    std::vector<Pending> pending;
    for(const auto& module:modules) {
        auto within=[&](std::uint64_t address,std::uint64_t size) {
            if(address<module.base || address-module.base>module.size || size>module.size-(address-module.base))
                throw std::runtime_error("static TLS metadata exceeds module image");
        };
        within(module.base,64);
        if(memory.load(module.base,16)!=0x5a4d) throw std::runtime_error("invalid static TLS PE DOS signature");
        auto pe=std::uint64_t(module.base)+std::uint32_t(memory.load(module.base+0x3c,32)); within(pe,24);
        if(memory.load(pe,32)!=0x4550) throw std::runtime_error("invalid static TLS PE signature");
        auto optional=pe+24; auto optional_size=std::uint32_t(memory.load(pe+20,16)); within(optional,optional_size);
        if(optional_size<96 || memory.load(optional,16)!=0x10b) throw std::runtime_error("static TLS requires PE32 optional headers");
        if(memory.load(optional+92,32)<=9) continue;
        if(optional_size<176) throw std::runtime_error("truncated static TLS data directory");
        auto rva=std::uint32_t(memory.load(optional+168,32)),size=std::uint32_t(memory.load(optional+172,32));
        if(!rva && !size) continue;
        if(!rva || size<24) throw std::runtime_error("invalid static TLS directory");
        auto directory=std::uint64_t(module.base)+rva; within(directory,size);
        auto start=std::uint32_t(memory.load(directory,32)),end=std::uint32_t(memory.load(directory+4,32));
        auto index=std::uint32_t(memory.load(directory+8,32)),callbacks=std::uint32_t(memory.load(directory+12,32));
        auto zero=std::uint32_t(memory.load(directory+16,32)),characteristics=std::uint32_t(memory.load(directory+20,32));
        if(end<start || (characteristics&~0x00f00000u) || (characteristics&0x00f00000u)==0x00f00000u)
            throw std::runtime_error("unsupported static TLS size/alignment characteristics");
        within(start,end-start); within(index,4);
        auto total=std::uint64_t(end)-start+zero;
        if(!total || total>layout.slot_stride || pending.size()>=layout.capacity)
            throw std::runtime_error("static TLS template exceeds declared thread capacity");
        if(callbacks) {
            within(callbacks,4);
            if(memory.load(callbacks,32)!=0) throw std::runtime_error("static TLS callbacks require translated initialization dispatch");
        }
        Pending item{index,std::vector<std::uint8_t>(std::size_t(total),0)};
        for(std::uint64_t i=0;i<std::uint64_t(end)-start;i++) item.bytes[std::size_t(i)]=std::uint8_t(memory.load(start+i,8));
        pending.push_back(std::move(item));
    }
    if(pending.empty()) return;
    memory.map_bytes("static TLS module vector",layout.vector_address,pending.size()*4u,true,true);
    for(std::size_t index=0;index<pending.size();index++) {
        auto& item=pending[index]; auto address=layout.data_address+std::uint32_t(index)*layout.slot_stride;
        memory.map_bytes("static TLS module template and zero-fill",address,item.bytes.size(),true,true,item.bytes);
        memory.store(layout.vector_address+std::uint32_t(index)*4u,address,32);
        memory.store(item.index_address,std::uint32_t(index),32);
    }
    memory.store(layout.fs_base+0x2cu,layout.vector_address,32);
}
}
