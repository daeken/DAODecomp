// Rounded signed integer stores reached at main 0xa3d01e; debugging only.
#include "x87_arithmetic_control.inc"
struct IntegerStoreMemory : CompareMemory {
    std::uint64_t write_address=0;unsigned write_width=0;
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        if(tracing){write_address=address;write_width=width;}
        CompareMemory::store(address,value,width);
    }
};
static void integer_store_reference(unsigned form,std::uint8_t* destination) {
    switch(form) {
    case 0:asm volatile(".byte 0xdf,0x10"::"a"(destination):"memory");break;
    case 1:asm volatile(".byte 0xdb,0x10"::"a"(destination):"memory");break;
    case 2:asm volatile(".byte 0xdf,0x18"::"a"(destination):"memory");break;
    case 3:asm volatile(".byte 0xdb,0x18"::"a"(destination):"memory");break;
    case 4:asm volatile(".byte 0xdf,0x38"::"a"(destination):"memory");break;
    }
}
int main() {
    if(auto result=arithmetic_control())return result;
    IntegerStoreMemory memory;memory.map_bytes("ram",0x8000,0x2000,true,true);
    memory.map_bytes("readonly",0xa000,0x100,true,false);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;recomp_generated::capture_native_fp(host);unsigned cases=0,mismatches=0,guards=0;
    struct Raw {std::uint64_t fraction;std::uint16_t exponent;};
    const Raw values[]={
        {0,0},{0,0x8000},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0xbfff},
        {0x8000000000000000ULL,0x3ffe},{0x8000000000000000ULL,0xbffe},
        {0xc000000000000000ULL,0x3fff},{0xc000000000000000ULL,0xbfff},
        {0xa000000000000000ULL,0x4000},{0xffff000000000000ULL,0x400d},
        {0x8000000000000000ULL,0x400e},{0x8000000000000000ULL,0xc00e},
        {0x8000000000000000ULL,0x401e},{0x8000000000000000ULL,0xc01e},
        {0xfffffffffffffffeULL,0x403d},{0x8000000000000000ULL,0x403e},{0x8000000000000000ULL,0xc03e},
        {0x8000000000000000ULL,0x7fff},{0xc000000000001234ULL,0x7fff},{0x8000000000001234ULL,0x7fff},{1,0}};
    const unsigned widths[]={16,32,16,32,64};const std::uint16_t opcodes[]={0x710,0x310,0x718,0x318,0x738};
    for(unsigned form=0;form<5;++form)for(unsigned top=0;top<8;++top)for(unsigned precision:{0u,2u,3u})
    for(unsigned rounding=0;rounding<4;++rounding)for(auto value:values)for(bool empty:{false,true}) {
        auto expected=host;expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x4700|(top<<11));expected.x87_tag=0;expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;++i)raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),0x3fff);
        raw(expected,0,value.fraction,value.exponent);
        auto tag=!(value.exponent&0x7fff) ? (value.fraction ? 2u:1u) : (value.exponent&0x7fff)==0x7fff ? 2u:0u;
        expected.x87_tag|=std::uint16_t((empty?3u:tag)<<(top*2));auto candidate=expected;
        std::uint8_t bytes[16];for(unsigned i=0;i<16;++i)bytes[i]=std::uint8_t(0x91+i*7);
        sharp_retro::bits before_bytes=0;for(unsigned i=0;i<16;++i)before_bytes|=sharp_retro::bits(bytes[i])<<(i*8);
        memory.store(0x9000,before_bytes,128);
        {recomp_generated::NativeFloatingScope scope(expected,false);integer_store_reference(form,bytes+1);scope.finish();}
        sharp_retro::bits after_bytes=0;for(unsigned i=0;i<16;++i)after_bytes|=sharp_retro::bits(bytes[i])<<(i*8);
        candidate.gpr[0]=0x9001;candidate.gpr[4]=0x8800;auto before=candidate;
        memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=10;
        auto result=recomp_generated::execute_guest(0x401770+form*16,0x12345678,candidate,memory,budget);memory.tracing=false;
        bool registers=true;for(unsigned i=0;i<16;++i)if(candidate.gpr[i]!=(i==4 ? before.gpr[i]+4:before.gpr[i]))registers=false;
        bool match=result==sharp_retro::Exit::returned&&registers&&candidate.flags==before.flags&&candidate.defined_flags==before.defined_flags&&
            candidate.defined_x87_st==0xff&&same(expected,candidate)&&!memory.reads&&memory.writes==1&&
            memory.write_width==widths[form]&&memory.write_address==0x9001&&memory.load(0x9000,128)==after_bytes;
        ++cases;if(!match){++mismatches;if(mismatches<5)std::fprintf(stderr,"integer store form=%u top=%u empty=%u SW=%x/%x TAG=%x/%x\n",form,top,unsigned(empty),expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    for(unsigned form=0;form<5;++form)for(unsigned mode=0;mode<4;++mode) {
        auto state=host;state.x87_control=mode==0?0x37e:0x37f;state.x87_status=0;state.x87_tag=0xfffc;state.defined_x87_st=mode==1?0xfe:0xff;
        raw(state,0,0x8000000000000000ULL,0x3fff);auto before=state;auto before_bytes=memory.load(0x9000,128);
        auto address=mode==2 ? 0x9fffu:mode==3 ? 0xa001u:0x9001u;memory.reads=memory.writes=0;memory.tracing=true;
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401770,address,opcodes[form]);}
        catch(const std::runtime_error&){if(same(state,before)&&state.defined_x87_st==before.defined_x87_st&&!memory.reads&&!memory.writes&&memory.load(0x9000,128)==before_bytes)++guards;}
        memory.tracing=false;
    }
    // 0x338 is now supported FSTP m80; D9 D1 (0x1d1) is reserved.
    for(unsigned opcode:{0x8738u,0x7f8u,0x1d1u}){auto state=host;auto before=state;
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401770,0x9001,std::uint16_t(opcode));}
        catch(const std::runtime_error&){if(same(state,before)&&state.defined_x87_st==before.defined_x87_st)++guards;}}
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_integer_store_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,guards,restored?"true":"false");
    return mismatches||guards!=23||!restored?1:0;
}
