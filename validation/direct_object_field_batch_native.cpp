#include "dao/direct_object_fields.hpp"
#include "direct_object_field_mutant.hpp"
#include <algorithm>
#include <array>
#include <exception>
#include <string_view>
extern "C" int dao_direct_object_field_case(const char* raw,const std::uint8_t* before,
 std::uint32_t object,std::uint32_t value,std::uint32_t entry_eax,
 const dao::MemoryRange* readable,std::uint32_t read_count,
 const dao::MemoryRange* writable,std::uint32_t write_count,
 std::uint32_t* result,std::uint32_t* exit_ecx,std::uint8_t* after) {
 if(!raw||!before||!result||!exit_ecx||!after||object>=512||read_count>2||write_count>2||(read_count&&!readable)||(write_count&&!writable)) return 2;
 std::array<std::uint8_t,512> bytes{};std::copy_n(before,512,bytes.begin());
 dao::GuestMemory memory{bytes,{readable,read_count},{writable,write_count}};
 const std::string_view name{raw};
 try {
  if(name=="fn_00319290") *result=dao::fn_00319290(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00342080") *result=dao::fn_00342080(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00342090") *result=dao::fn_00342090(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00347b40") *result=dao::fn_00347b40(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00347b50") *result=dao::fn_00347b50(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00347b70") *result=dao::fn_00347b70(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00347b80") *result=dao::fn_00347b80(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00347b90") *result=dao::fn_00347b90(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003480b0") *result=dao::fn_003480b0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003480c0") *result=dao::fn_003480c0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003b51e0") *result=dao::fn_003b51e0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003cd030") *result=dao::fn_003cd030(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003cd040") *result=dao::fn_003cd040(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003cd0d0") *result=dao::fn_003cd0d0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003cd140") *result=dao::fn_003cd140(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003cd350") *result=dao::fn_003cd350(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_003edbc0") *result=dao::fn_003edbc0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00515af0") *result=dao::fn_00515af0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00515b00") *result=dao::fn_00515b00(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00515b10") *result=dao::fn_00515b10(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0054f6e0") *result=dao::fn_0054f6e0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0054fa40") *result=dao::fn_0054fa40(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00018760") *result=dao::fn_00018760(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00018770") *result=dao::fn_00018770(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0001cd70") *result=dao::fn_0001cd70(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0001f050") *result=dao::fn_0001f050(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0001f060") *result=dao::fn_0001f060(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00022c80") *result=dao::fn_00022c80(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00023e40") *result=dao::fn_00023e40(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00023ed0") *result=dao::fn_00023ed0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00023ee0") *result=dao::fn_00023ee0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00023ef0") *result=dao::fn_00023ef0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00024030") *result=dao::fn_00024030(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00024050") *result=dao::fn_00024050(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00024060") *result=dao::fn_00024060(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00024090") *result=dao::fn_00024090(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0002f940") *result=dao::fn_0002f940(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0002fa20") *result=dao::fn_0002fa20(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_000621c0") *result=dao::fn_000621c0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00065f30") *result=dao::fn_00065f30(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_00065f40") *result=dao::fn_00065f40(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_000a52c0") *result=dao::fn_000a52c0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_000a54e0") *result=dao::fn_000a54e0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_000ecf70") *result=dao::fn_000ecf70(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_000f25a0") *result=dao::fn_000f25a0(memory,object,value,entry_eax,*exit_ecx);
  else if(name=="fn_0013ba50") *result=dao::fn_0013ba50(memory,object,value,entry_eax,*exit_ecx);
  else return 2;
 } catch(const std::exception&) {return 3;}
#ifdef DAO_DIRECT_OBJECT_FIELD_MUTANT
 direct_object_field_mutate(name,bytes,object,*result);
#endif
 std::copy(bytes.begin(),bytes.end(),after);return 0;
}
