/* Constructed state for the bounded machine contracts, not a game object factory. */
#pragma once
#include <stdint.h>
#include <string.h>
static void put_word(unsigned char* bytes,unsigned offset,uint32_t value) {
    for(unsigned j=0;j<4;j++) bytes[offset+j]=(unsigned char)(value>>(j*8));
}
static void prepare_arena(unsigned char* bytes,unsigned object,unsigned inner,unsigned nested,uint32_t word,uint32_t seed,unsigned rva) {
    for(unsigned i=0;i<1024;i++) { seed^=seed<<13; seed^=seed>>17; seed^=seed<<5; bytes[i]=(unsigned char)seed; }
    put_word(bytes,inner,word);
    put_word(bytes,inner+4,0x30000000u+nested);
    put_word(bytes,inner+12,word^0x5a5aa5a5u);
    put_word(bytes,inner+16,word);
    put_word(bytes,inner+56,word);
    put_word(bytes,nested,word^0x12345678u);
    put_word(bytes,nested+4,word^0x87654321u);
    put_word(bytes,nested+56,word);
    put_word(bytes,object,0x30000000u+inner);
    put_word(bytes,object+4,0x30000000u+inner);
    if(rva==0x5e3e0) bytes[inner+5]=(unsigned char)word;
}
