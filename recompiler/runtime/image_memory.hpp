#pragma once
#include "runtime.hpp"
#include <algorithm>
#include <array>
#include <bit>
#include <filesystem>
#include <fstream>
#include <span>
#include <string>
#include <unordered_set>
#include <unordered_map>
#include <vector>

namespace recomp_generated {
// Integrity of immutable initialized-data artifacts, not a function proof.
inline std::string image_sha256(std::span<const std::uint8_t> input) {
    static constexpr std::uint32_t k[]={
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
    std::array<std::uint32_t,8> h{0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    std::vector<std::uint8_t> bytes(input.begin(),input.end());
    auto bit_count=std::uint64_t(bytes.size())*8;
    bytes.push_back(0x80); while(bytes.size()%64!=56) bytes.push_back(0);
    for(int i=7;i>=0;--i) bytes.push_back(std::uint8_t(bit_count>>(i*8)));
    for(std::size_t offset=0;offset<bytes.size();offset+=64) {
        std::uint32_t w[64]{};
        for(unsigned i=0;i<16;i++) for(unsigned j=0;j<4;j++) w[i]=(w[i]<<8)|bytes[offset+i*4+j];
        for(unsigned i=16;i<64;i++) {
            auto a=w[i-15],b=w[i-2];
            w[i]=w[i-16]+(std::rotr(a,7)^std::rotr(a,18)^(a>>3))+w[i-7]+(std::rotr(b,17)^std::rotr(b,19)^(b>>10));
        }
        auto a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],v=h[7];
        for(unsigned i=0;i<64;i++) {
            auto t=v+(std::rotr(e,6)^std::rotr(e,11)^std::rotr(e,25))+((e&f)^(~e&g))+k[i]+w[i];
            auto u=(std::rotr(a,2)^std::rotr(a,13)^std::rotr(a,22))+((a&b)^(a&c)^(b&c));
            v=g; g=f; f=e; e=d+t; d=c; c=b; b=a; a=t+u;
        }
        h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=v;
    }
    std::string result; constexpr char hex[]="0123456789abcdef";
    for(auto value:h) for(int i=7;i>=0;--i) result+=hex[(value>>(i*4))&15];
    return result;
}

// Preferred-address data mappings only. No executable instruction bytes or
// host pointer casts; module initializers/TLS constructors are not executed.
class ImageMemory : public sharp_retro::Memory {
    struct Region { std::string name; std::uint64_t address; std::vector<std::uint8_t> bytes; bool readable,writable; };
    std::vector<Region> regions;
    bool sealed=false;
    std::uint64_t total=0;
    std::unordered_set<std::uint64_t> unknown_bytes;
    struct ScalarByte { std::uint8_t known; std::array<std::uint64_t,8> origins; };
    std::unordered_map<std::uint64_t,ScalarByte> scalar_bytes;
    Region& region(std::uint64_t address,unsigned width,bool write) {
        if(width==0 || width>128 || width%8 || address>0xffffffffULL || width/8>0x100000000ULL-address)
            throw std::runtime_error("invalid guest32 memory access");
        for(auto& item:regions) if(address>=item.address && address-item.address<=item.bytes.size() && width/8<=item.bytes.size()-(address-item.address)) {
            if(sealed && (write ? !item.writable : !item.readable)) throw std::runtime_error("guest memory permission violation");
            return item;
        }
        throw std::runtime_error("unmapped guest memory access");
    }
public:
    void validate_store(std::uint64_t address,unsigned width) override { (void)region(address,width,true); }
    void check_known(std::uint64_t address,unsigned width) const {
        for(unsigned i=0;i<width/8;i++) if(unknown_bytes.contains(address+i)) throw sharp_retro::UnknownMemoryRead();
    }
    void check_known(std::uint64_t address,unsigned width,sharp_retro::bits raw) const {
        if(width>32) { check_known(address,width); return; }
        sharp_retro::Scalar32 value{std::uint32_t(raw),0xffffffffu,{}}; bool unknown=false;
        for(unsigned i=0;i<width/8;i++) if(unknown_bytes.contains(address+i)) {
            unknown=true; value.known&=~(0xffu<<(i*8));
            auto found=scalar_bytes.find(address+i);
            if(found!=scalar_bytes.end()) {
                value.known|=std::uint32_t(found->second.known)<<(i*8);
                for(unsigned bit=0;bit<8;bit++) value.origins[i*8+bit]=found->second.origins[bit];
            }
        }
        if(unknown) throw sharp_retro::UnknownMemoryRead(value);
    }
    void discard_scalar_images(std::uint64_t address,std::uint64_t size) {
        std::erase_if(scalar_bytes,[&](const auto& item) { return item.first>=address && item.first-address<size; });
    }
    void forget_unknown_range(std::uint64_t address,std::uint64_t size) {
        discard_scalar_images(address,size);
        std::erase_if(unknown_bytes,[&](auto byte) { return byte>=address && byte-address<size; });
    }
    // Metadata only: the allocator may already have released the old backing.
    // Copies are guaranteed over the requested prefix. Unknown allocator slack
    // stays unknown conservatively, without claiming its old bit identities.
    void relocate_unknown_range(std::uint64_t old_address,std::uint64_t old_size,
                                std::uint64_t address,std::uint64_t size,std::uint64_t preserved) {
        struct Saved { std::uint64_t offset; ScalarByte byte; bool scalar; };
        std::vector<Saved> saved;
        for(auto byte:unknown_bytes) if(byte>=old_address && byte-old_address<std::min(old_size,size)) {
            auto found=scalar_bytes.find(byte);
            bool scalar=byte-old_address<preserved && found!=scalar_bytes.end();
            saved.push_back({byte-old_address,scalar ? found->second : ScalarByte{},scalar});
        }
        forget_unknown_range(old_address,old_size); forget_unknown_range(address,size);
        for(const auto& item:saved) {
            unknown_bytes.insert(address+item.offset);
            if(item.scalar) scalar_bytes[address+item.offset]=item.byte;
        }
    }
    void mark_known(std::uint64_t address,unsigned width) {
        discard_scalar_images(address,width/8);
        for(unsigned i=0;i<width/8;i++) unknown_bytes.erase(address+i);
    }
    sharp_retro::Scalar32 load_scalar32(std::uint64_t address) override {
        try { return {std::uint32_t(load(address,32)),0xffffffffu,{}}; }
        catch(const sharp_retro::UnknownMemoryRead& error) { return error.scalar32; }
    }
    void store_scalar32(std::uint64_t address,sharp_retro::Scalar32 value) override {
        store_scalar(address,value,32);
    }
    void store_scalar8(std::uint64_t address,sharp_retro::Scalar32 value) override {
        store_scalar(address,value,8);
    }
    void store_scalar16(std::uint64_t address,sharp_retro::Scalar32 value) override {
        store_scalar(address,value,16);
    }
    void store_scalar(std::uint64_t address,const sharp_retro::Scalar32& value,unsigned width) {
        store(address,value.value,width);
        for(unsigned i=0;i<width/8;i++) {
            auto known=std::uint8_t(value.known>>(i*8));
            if(known==0xff) continue;
            ScalarByte byte{known,{}};
            for(unsigned bit=0;bit<8;bit++) byte.origins[bit]=value.origins[i*8+bit];
            unknown_bytes.insert(address+i); scalar_bytes[address+i]=byte;
        }
    }
    void store_unknown(std::uint64_t address,sharp_retro::bits placeholder,unsigned width) override {
        store(address,placeholder,width);
        for(unsigned i=0;i<width/8;i++) unknown_bytes.insert(address+i);
    }
    virtual void reserve_image(std::uint64_t,std::uint64_t) {}
    std::size_t region_count() const { return regions.size(); }
    bool overlaps_mapping(std::uint64_t address,std::uint64_t size) const {
        if(address>0xffffffffULL || size>0x100000000ULL-address) throw std::runtime_error("invalid guest32 range");
        for(const auto& item:regions)
            if(address<item.address+item.bytes.size() && item.address<address+size) return true;
        return false;
    }
    bool is_sealed() const { return sealed; }
    virtual void map_bytes(std::string name,std::uint64_t address,std::uint64_t size,bool readable,bool writable,std::span<const std::uint8_t> bytes={}) {
        if(sealed || size==0 || size>64*1024*1024 || address>0xffffffffULL || size>0x100000000ULL-address || bytes.size()>size || total+size>256*1024*1024)
            throw std::runtime_error("invalid/oversized image mapping or image already sealed");
        for(const auto& item:regions) if(address<item.address+item.bytes.size() && item.address<address+size)
            throw std::runtime_error("overlapping guest memory mappings");
        Region item{std::move(name),address,std::vector<std::uint8_t>(std::size_t(size),0),readable,writable};
        std::copy(bytes.begin(),bytes.end(),item.bytes.begin()); regions.push_back(std::move(item)); total+=size;
    }
    void map_file(std::string name,std::uint64_t address,std::uint64_t size,bool readable,bool writable,
                  const std::filesystem::path& path,std::uint64_t expected_size,const std::string& expected_sha) {
        if(expected_size>64*1024*1024 || expected_size>size) throw std::runtime_error("oversized initialized data");
        std::ifstream file(path,std::ios::binary);
        if(!file) throw std::runtime_error("missing initialized-data artifact");
        std::vector<std::uint8_t> bytes(static_cast<std::size_t>(expected_size));
        if(expected_size) file.read(reinterpret_cast<char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));
        if((expected_size && !file) || file.peek()!=std::char_traits<char>::eof() || image_sha256(bytes)!=expected_sha)
            throw std::runtime_error("changed/truncated initialized-data artifact");
        map_bytes(std::move(name),address,size,readable,writable,bytes);
    }
    virtual void seal() { sealed=true; }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        auto& item=region(address,width,false); sharp_retro::bits value=0;
        for(unsigned i=0;i<width/8;i++) value|=sharp_retro::bits(item.bytes[std::size_t(address-item.address)+i])<<(i*8);
        check_known(address,width,value);
        return value;
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        auto& item=region(address,width,true);
        mark_known(address,width);
        for(unsigned i=0;i<width/8;i++) item.bytes[std::size_t(address-item.address)+i]=std::uint8_t(value>>(i*8));
    }
};
struct ThreadTlsLayout;
void initialize_linked_images(ImageMemory&,const std::filesystem::path& directory,const ThreadTlsLayout* tls=nullptr);
void reserve_linked_images(ImageMemory&);
} // namespace recomp_generated
