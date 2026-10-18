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
 else if(name=="fn_00018760") result^=1u;
 else if(name=="fn_00018770") result^=1u;
 else if(name=="fn_0001cd70") after[object+8]^=1u;
 else if(name=="fn_0001f050") result^=1u;
 else if(name=="fn_0001f060") result^=1u;
 else if(name=="fn_00022c80") after[object+60]^=1u;
 else if(name=="fn_00023e40") result^=1u;
 else if(name=="fn_00023ed0") after[object+12]^=1u;
 else if(name=="fn_00023ee0") after[object+16]^=1u;
 else if(name=="fn_00023ef0") after[object+20]^=1u;
 else if(name=="fn_00024030") after[object+72]^=1u;
 else if(name=="fn_00024050") after[object+76]^=1u;
 else if(name=="fn_00024060") result^=1u;
 else if(name=="fn_00024090") after[object+84]^=1u;
 else if(name=="fn_0002f940") result^=1u;
 else if(name=="fn_0002fa20") result^=1u;
 else if(name=="fn_000621c0") result^=1u;
 else if(name=="fn_00065f30") after[object+324]^=1u;
 else if(name=="fn_00065f40") result^=1u;
 else if(name=="fn_000a52c0") after[object+345]^=1u;
 else if(name=="fn_000a54e0") after[object+33]^=1u;
 else if(name=="fn_000ecf70") result^=1u;
 else if(name=="fn_000f25a0") after[object+24]^=1u;
 else if(name=="fn_0013ba50") after[object+56]^=1u;
}
