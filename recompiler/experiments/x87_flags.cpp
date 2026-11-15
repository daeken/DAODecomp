// Constructed controls isolate math precision/rounding, stack faults and special extended values.
// Reference uses opcode bytes; generated candidates use assembler mnemonics.
#include "functions.hpp"
#include "image_memory.hpp"
#include "native_x87.hpp"
#include <cstdio>
#include <cstring>
struct DebugMemory : recomp_generated::ImageMemory {
    void execute_x87(sharp_retro::X87Op op,sharp_retro::State& s,std::uint64_t pc,std::uint32_t address,std::uint16_t opcode) override {
        recomp_generated::execute_native_x87(*this,op,s,pc,address,opcode);
    }
};
static bool same(const sharp_retro::State& a,const sharp_retro::State& b,unsigned known=0xff) {
    if(a.x87_control!=b.x87_control || a.x87_status!=b.x87_status || a.x87_tag!=b.x87_tag || a.mxcsr!=b.mxcsr) return false;
    for(unsigned i=0;i<8;i++) if((known&(1u<<i)) && a.x87_st[i]!=b.x87_st[i]) return false;
    return true;
}
static void reference(sharp_retro::State& s,unsigned index) {
    recomp_generated::NativeFloatingScope fp(s,false);
    unsigned result=0,seed=0x202u|(s.flags&0x8d5u);
    switch(index) {
    case 0:asm volatile("pushfl; pushl %1; popfl; .byte 218,192; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 1:asm volatile("pushfl; pushl %1; popfl; .byte 218,193; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 2:asm volatile("pushfl; pushl %1; popfl; .byte 218,194; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 3:asm volatile("pushfl; pushl %1; popfl; .byte 218,195; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 4:asm volatile("pushfl; pushl %1; popfl; .byte 218,196; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 5:asm volatile("pushfl; pushl %1; popfl; .byte 218,197; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 6:asm volatile("pushfl; pushl %1; popfl; .byte 218,198; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 7:asm volatile("pushfl; pushl %1; popfl; .byte 218,199; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 8:asm volatile("pushfl; pushl %1; popfl; .byte 218,200; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 9:asm volatile("pushfl; pushl %1; popfl; .byte 218,201; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 10:asm volatile("pushfl; pushl %1; popfl; .byte 218,202; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 11:asm volatile("pushfl; pushl %1; popfl; .byte 218,203; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 12:asm volatile("pushfl; pushl %1; popfl; .byte 218,204; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 13:asm volatile("pushfl; pushl %1; popfl; .byte 218,205; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 14:asm volatile("pushfl; pushl %1; popfl; .byte 218,206; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 15:asm volatile("pushfl; pushl %1; popfl; .byte 218,207; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 16:asm volatile("pushfl; pushl %1; popfl; .byte 218,208; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 17:asm volatile("pushfl; pushl %1; popfl; .byte 218,209; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 18:asm volatile("pushfl; pushl %1; popfl; .byte 218,210; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 19:asm volatile("pushfl; pushl %1; popfl; .byte 218,211; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 20:asm volatile("pushfl; pushl %1; popfl; .byte 218,212; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 21:asm volatile("pushfl; pushl %1; popfl; .byte 218,213; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 22:asm volatile("pushfl; pushl %1; popfl; .byte 218,214; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 23:asm volatile("pushfl; pushl %1; popfl; .byte 218,215; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 24:asm volatile("pushfl; pushl %1; popfl; .byte 218,216; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 25:asm volatile("pushfl; pushl %1; popfl; .byte 218,217; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 26:asm volatile("pushfl; pushl %1; popfl; .byte 218,218; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 27:asm volatile("pushfl; pushl %1; popfl; .byte 218,219; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 28:asm volatile("pushfl; pushl %1; popfl; .byte 218,220; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 29:asm volatile("pushfl; pushl %1; popfl; .byte 218,221; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 30:asm volatile("pushfl; pushl %1; popfl; .byte 218,222; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 31:asm volatile("pushfl; pushl %1; popfl; .byte 218,223; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 32:asm volatile("pushfl; pushl %1; popfl; .byte 219,192; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 33:asm volatile("pushfl; pushl %1; popfl; .byte 219,193; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 34:asm volatile("pushfl; pushl %1; popfl; .byte 219,194; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 35:asm volatile("pushfl; pushl %1; popfl; .byte 219,195; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 36:asm volatile("pushfl; pushl %1; popfl; .byte 219,196; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 37:asm volatile("pushfl; pushl %1; popfl; .byte 219,197; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 38:asm volatile("pushfl; pushl %1; popfl; .byte 219,198; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 39:asm volatile("pushfl; pushl %1; popfl; .byte 219,199; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 40:asm volatile("pushfl; pushl %1; popfl; .byte 219,200; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 41:asm volatile("pushfl; pushl %1; popfl; .byte 219,201; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 42:asm volatile("pushfl; pushl %1; popfl; .byte 219,202; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 43:asm volatile("pushfl; pushl %1; popfl; .byte 219,203; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 44:asm volatile("pushfl; pushl %1; popfl; .byte 219,204; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 45:asm volatile("pushfl; pushl %1; popfl; .byte 219,205; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 46:asm volatile("pushfl; pushl %1; popfl; .byte 219,206; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 47:asm volatile("pushfl; pushl %1; popfl; .byte 219,207; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 48:asm volatile("pushfl; pushl %1; popfl; .byte 219,208; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 49:asm volatile("pushfl; pushl %1; popfl; .byte 219,209; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 50:asm volatile("pushfl; pushl %1; popfl; .byte 219,210; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 51:asm volatile("pushfl; pushl %1; popfl; .byte 219,211; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 52:asm volatile("pushfl; pushl %1; popfl; .byte 219,212; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 53:asm volatile("pushfl; pushl %1; popfl; .byte 219,213; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 54:asm volatile("pushfl; pushl %1; popfl; .byte 219,214; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 55:asm volatile("pushfl; pushl %1; popfl; .byte 219,215; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 56:asm volatile("pushfl; pushl %1; popfl; .byte 219,216; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 57:asm volatile("pushfl; pushl %1; popfl; .byte 219,217; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 58:asm volatile("pushfl; pushl %1; popfl; .byte 219,218; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 59:asm volatile("pushfl; pushl %1; popfl; .byte 219,219; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 60:asm volatile("pushfl; pushl %1; popfl; .byte 219,220; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 61:asm volatile("pushfl; pushl %1; popfl; .byte 219,221; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 62:asm volatile("pushfl; pushl %1; popfl; .byte 219,222; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 63:asm volatile("pushfl; pushl %1; popfl; .byte 219,223; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 64:asm volatile("pushfl; pushl %1; popfl; .byte 219,232; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 65:asm volatile("pushfl; pushl %1; popfl; .byte 219,233; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 66:asm volatile("pushfl; pushl %1; popfl; .byte 219,234; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 67:asm volatile("pushfl; pushl %1; popfl; .byte 219,235; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 68:asm volatile("pushfl; pushl %1; popfl; .byte 219,236; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 69:asm volatile("pushfl; pushl %1; popfl; .byte 219,237; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 70:asm volatile("pushfl; pushl %1; popfl; .byte 219,238; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 71:asm volatile("pushfl; pushl %1; popfl; .byte 219,239; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 72:asm volatile("pushfl; pushl %1; popfl; .byte 219,240; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 73:asm volatile("pushfl; pushl %1; popfl; .byte 219,241; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 74:asm volatile("pushfl; pushl %1; popfl; .byte 219,242; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 75:asm volatile("pushfl; pushl %1; popfl; .byte 219,243; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 76:asm volatile("pushfl; pushl %1; popfl; .byte 219,244; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 77:asm volatile("pushfl; pushl %1; popfl; .byte 219,245; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 78:asm volatile("pushfl; pushl %1; popfl; .byte 219,246; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 79:asm volatile("pushfl; pushl %1; popfl; .byte 219,247; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 80:asm volatile("pushfl; pushl %1; popfl; .byte 223,232; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 81:asm volatile("pushfl; pushl %1; popfl; .byte 223,233; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 82:asm volatile("pushfl; pushl %1; popfl; .byte 223,234; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 83:asm volatile("pushfl; pushl %1; popfl; .byte 223,235; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 84:asm volatile("pushfl; pushl %1; popfl; .byte 223,236; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 85:asm volatile("pushfl; pushl %1; popfl; .byte 223,237; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 86:asm volatile("pushfl; pushl %1; popfl; .byte 223,238; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 87:asm volatile("pushfl; pushl %1; popfl; .byte 223,239; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 88:asm volatile("pushfl; pushl %1; popfl; .byte 223,240; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 89:asm volatile("pushfl; pushl %1; popfl; .byte 223,241; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 90:asm volatile("pushfl; pushl %1; popfl; .byte 223,242; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 91:asm volatile("pushfl; pushl %1; popfl; .byte 223,243; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 92:asm volatile("pushfl; pushl %1; popfl; .byte 223,244; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 93:asm volatile("pushfl; pushl %1; popfl; .byte 223,245; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 94:asm volatile("pushfl; pushl %1; popfl; .byte 223,246; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    case 95:asm volatile("pushfl; pushl %1; popfl; .byte 223,247; pushfl; popl %0; popfl" : "=&r"(result) : "r"(seed) : "memory","cc");break;
    }
    fp.finish();
    if(index>=64){s.flags=(s.flags&~std::uint64_t(0x8d5u))|(result&0x8d5u);s.defined_flags|=0x8d5u;}
}
int main() {
    sharp_retro::State host;recomp_generated::capture_native_fp(host);
    DebugMemory memory;
    { auto setup=host;recomp_generated::NativeFloatingScope scope(setup,false);
      memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32); }
    unsigned cases=0,mismatches=0;
    for(unsigned index=0;index<96;index++) for(unsigned top=0;top<8;top++)
    for(unsigned precision:{0u,2u,3u}) for(unsigned rounding=0;rounding<4;rounding++)
    for(unsigned stack:{0u,1u,2u,8u}) for(unsigned sticky:{0u,0x21u}) for(unsigned pattern=0;pattern<6;pattern++) for(unsigned flagSeed:{0u,0x45u,0x841u,4u}) {
        auto expected=host;
        expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x4500|(top<<11)|sticky);expected.x87_tag=0xffff;
        for(unsigned i=0;i<8;i++) {
            std::uint64_t fraction=0x8000000000000000ULL|(std::uint64_t(i)<<58);std::uint16_t exponent=0x4000;
            if(i<2){
                const std::uint64_t fractions[]={0x8000000000000000ULL,0,0x8000000000000000ULL,0xc000000000000000ULL,0x8000000000000000ULL,0xffffffffffffffffULL,0x8000000000000000ULL,0xc000000000000001ULL,0x8000000000000001ULL,1,0x8000000000000000ULL,0x8000000000000000ULL,0x4000000000000000ULL,0xb504f333f9de6484ULL};
                const std::uint16_t exponents[]={0x3ffe,0,0x8000,0x3fff,0xbfff,0x3ffe,0x7fff,0x7fff,0x7fff,0,0x403e,0x7ffe,0x3fff,0x3fff};
                fraction=fractions[(pattern+i)%14];exponent=exponents[(pattern+i)%14];
            }
            std::memcpy(expected.x87_st[i].data(),&fraction,8);std::memcpy(expected.x87_st[i].data()+8,&exponent,2);
            if(i<stack) expected.x87_tag&=std::uint16_t(~(3u<<(((top+i)&7)*2)));
        }
        expected.defined_x87_st=0xff;expected.flags=0x202u|flagSeed;auto candidate=expected;
        reference(expected,index);
        candidate.gpr[4]=0x8800;auto defined_flags=candidate.defined_flags;
        std::uint64_t budget=10;
        auto exit=recomp_generated::execute_guest(0x31001000+index*32,0x12345678,candidate,memory,budget);
        // Empty physical payloads are unobservable; compare every live value.
        unsigned live=0;
        for(unsigned i=0;i<8;i++) if(((expected.x87_tag>>(((((expected.x87_status>>11)&7)+i)&7)*2))&3)!=3) live|=1u<<i;
        bool match=exit==sharp_retro::Exit::returned && budget==8 && candidate.gpr[4]==0x8804 &&
            candidate.flags==expected.flags && candidate.defined_flags==defined_flags && candidate.defined_x87_st==0xff && same(expected,candidate,live);
        ++cases;
        if(!match) {++mismatches;if(mismatches<5)std::fprintf(stderr,"x87-flag mismatch op=%u TOP=%u PC=%u RC=%u stack=%u sticky=%x pattern=%u seed=%x FLAGS=%llx/%llx SW=%04x/%04x TAG=%04x/%04x\n",index,top,precision,rounding,stack,sticky,pattern,flagSeed,(unsigned long long)expected.flags,(unsigned long long)candidate.flags,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    unsigned refused=0;
    for(unsigned mode=0;mode<4;mode++) {
        auto s=host;s.x87_control=0x37f;s.x87_status=0;s.x87_tag=0xffff;s.defined_x87_st=0xff;
        if(mode==0)s.x87_control&=~1u;
        if(mode==1)s.x87_status=0x80;
        if(mode==2)s.x87_control_defined=0xfffe;
        auto before=s;
        try {recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,s,0x401018,0,mode==3 ? 0x1d1 : 0x1fc);}
        catch(const std::exception&) {if(same(before,s) && s.defined_x87_st==before.defined_x87_st)++refused;}
    }
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_x87_flag_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,refused,restored ? "true" : "false");
    return mismatches || refused!=4 || !restored ? 1 : 0;
}
