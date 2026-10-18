#include "../validation/object_bitfield_mutant.hpp"
#include <array>
#undef NDEBUG
#include <cassert>
int main(){
 std::array<std::uint8_t,512> before{},after{};
 std::uint32_t result=0xaabbccdd,ecx=0x12345678;
 object_bitfield_mutate("fn_0052a680",before,after,0,0,result,ecx);assert(result==0xdd && ecx==0x12345678);
 result=0x12345678;object_bitfield_mutate("fn_0052ab30",before,after,0,0,result,ecx);assert(result==0x345678);
 result=0x02000001;object_bitfield_mutate("fn_0052abe0",before,after,0,0,result,ecx);assert(result==1);
 for(unsigned i=0;i<512;++i)before[i]=static_cast<std::uint8_t>(i);
 after=before;after[33]=99;result=16;
 object_bitfield_mutate("fn_0052ab70",before,after,16,17,result,ecx);
 assert(after[32]==before[33] && after[51]==before[52] && result==16);
 assert(ecx==0x34333231);
}
