#include "dao/object_bitfields.hpp"
#include "object_bitfield_mutant.hpp"
#include <algorithm>
#include <array>
#include <exception>
#include <string_view>
extern "C" int dao_object_bitfield_case(const char* raw, const std::uint8_t* before,
 std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax,
 const dao::MemoryRange* readable, std::uint32_t read_count,
 const dao::MemoryRange* writable, std::uint32_t write_count,
 std::uint32_t* result, std::uint32_t* exit_ecx, std::uint8_t* after) {
 if(!raw || !before || !result || !exit_ecx || !after || object>=512 || read_count>4 || write_count>2 || (read_count&&!readable) || (write_count&&!writable)) return 2;
 std::array<std::uint8_t,512> bytes{}; std::copy_n(before,512,bytes.begin());
 dao::GuestMemory memory{bytes,{readable,read_count},{writable,write_count}};
 std::string_view name{raw};
 try {
  if (name=="fn_0052a680") *result=dao::fn_0052a680(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052a820") *result=dao::fn_0052a820(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052a840") *result=dao::fn_0052a840(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052a860") *result=dao::fn_0052a860(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052a950") *result=dao::fn_0052a950(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052a9d0") *result=dao::fn_0052a9d0(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052a9f0") *result=dao::fn_0052a9f0(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052aa10") *result=dao::fn_0052aa10(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052aa30") *result=dao::fn_0052aa30(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052aa50") *result=dao::fn_0052aa50(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052aa70") *result=dao::fn_0052aa70(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052aa90") *result=dao::fn_0052aa90(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052ab30") *result=dao::fn_0052ab30(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052ab70") *result=dao::fn_0052ab70(memory,object,value,source,entry_eax,*exit_ecx);
  else if (name=="fn_0052abe0") *result=dao::fn_0052abe0(memory,object,value,source,entry_eax,*exit_ecx);
  else return 2;
 } catch(const std::exception&) { return 3; }
#ifdef DAO_OBJECT_BITFIELD_MUTANT
 object_bitfield_mutate(name,{before,512},bytes,object,source,*result,*exit_ecx);
#endif
 std::copy(bytes.begin(),bytes.end(),after); return 0;
}
