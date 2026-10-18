#pragma once
#include <algorithm>
#include <cstdint>
#include <span>
#include <string_view>
// Negative observations only, applied AFTER the real candidate function returns.
inline void object_bitfield_mutate(std::string_view name, std::span<const std::uint8_t> before,
 std::span<std::uint8_t> after, std::uint32_t object, std::uint32_t source,
 std::uint32_t& result, std::uint32_t& exit_ecx) {
 if(name=="fn_0052ab70") {
  // Incorrect snapshot copy loses the original's sequential overlap effects.
  std::copy_n(before.begin()+source+0x10,20,after.begin()+object+0x10);
  exit_ecx=0;
  for(unsigned i=0;i<4;++i) exit_ecx |= std::uint32_t{before[source+0x20+i]}<<(i*8);
 } else if(name=="fn_0052ab30") {
  result &= 0x00ffffffu; // Incorrectly loses returned high color byte.
 } else if(name=="fn_0052abe0") {
  result &= 1u; // Incorrectly normalizes AL truth to full EAX boolean.
 } else {
  result &= 0xffu; // Incorrectly clears preserved incoming upper EAX bits.
 }
}
