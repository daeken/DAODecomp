#pragma once
#include <cstdint>
#include <span>
#include <string_view>
// Post-candidate controls: corrupt one declared written byte, or invert low EAX bit on readers.
inline void direct_object_field_mutate(std::string_view name,std::span<std::uint8_t> after,std::uint32_t object,std::uint32_t& result) {
 if(name=="fn_00319290") after[object+134]^=1u;
 else if(name=="fn_00342080") after[object+0]^=1u;
 else if(name=="fn_00342090") after[object+2]^=1u;
 else if(name=="fn_00347b40") after[object+90]^=1u;
 else if(name=="fn_00347b50") after[object+80]^=1u;
 else if(name=="fn_00347b70") after[object+32]^=1u;
 else if(name=="fn_00347b80") after[object+24]^=1u;
 else if(name=="fn_00347b90") after[object+48]^=1u;
 else if(name=="fn_003480b0") result^=1u;
 else if(name=="fn_003480c0") result^=1u;
 else if(name=="fn_003b51e0") result^=1u;
 else if(name=="fn_003cd030") after[object+285]^=1u;
 else if(name=="fn_003cd040") after[object+288]^=1u;
 else if(name=="fn_003cd0d0") result^=1u;
 else if(name=="fn_003cd140") after[object+448]^=1u;
 else if(name=="fn_003cd350") after[object+132]^=1u;
 else if(name=="fn_003edbc0") after[object+68]^=1u;
 else if(name=="fn_00515af0") result^=1u;
 else if(name=="fn_00515b00") result^=1u;
 else if(name=="fn_00515b10") result^=1u;
 else if(name=="fn_0054f6e0") result^=1u;
 else if(name=="fn_0054fa40") result^=1u;
}
