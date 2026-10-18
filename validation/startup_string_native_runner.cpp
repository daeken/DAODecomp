#include "dao/startup_string.hpp"
#include <array>
#include <iostream>
#include <string>
#include <string_view>
int main(){
 std::string hex,extra;std::uint64_t pointer=0,search=0;
 if(!(std::cin>>hex>>pointer>>search)||std::cin>>extra||hex.size()!=512||pointer<dao::kStartupStringArenaBase||pointer>=dao::kStartupStringArenaBase+256||search>0xffffffff)return 2;
 std::array<std::uint8_t,256> arena{};constexpr std::string_view digits="0123456789abcdef";
 for(std::size_t i=0;i<256;++i){auto h=digits.find(hex[2*i]),l=digits.find(hex[2*i+1]);if(h==digits.npos||l==digits.npos)return 2;arena[i]=static_cast<std::uint8_t>((h<<4)|l);}
 const auto start=static_cast<std::uint32_t>(pointer-dao::kStartupStringArenaBase);auto end=start;
 while(true){if(end+2>256)return 2;const auto word=std::uint16_t{arena[end]}|(std::uint16_t{arena[end+1]}<<8);end+=2;if(word==0)break;}
 std::array<dao::MemoryRange,1> ranges{{{start,end-start}}};
 dao::GuestMemory memory(arena,ranges,{});
 try{
#ifdef DAO_STARTUP_STRING_CONTROL_ONLY
 std::uint32_t result=0; // Intentionally incorrect support probe; never a candidate.
#else
 auto result=dao::fn_004e2d29(memory,static_cast<std::uint32_t>(pointer),static_cast<std::uint32_t>(search));
#endif
#ifdef DAO_STARTUP_STRING_MUTANT
 // Intentionally wrong null/match normalization; independently detected by frozen edge matrix.
 result=0;
#endif
 std::cout<<result<<'\n';for(const auto b:arena)std::cout<<digits[b>>4]<<digits[b&15];std::cout<<'\n';
 }catch(const std::exception&){return 3;}
}
