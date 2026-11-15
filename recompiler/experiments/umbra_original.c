/* Original pinned DLL execution under Wine; no translated oracle or API stubs. */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include "umbra_fixture.h"
#include "umbra_contract.hpp"
uint32_t observed[9],arguments[2],entry_this,entry_target,saved_host_sp;
extern void invoke_umbra(void);
int main(int argc,char** argv) {
    if(argc!=2) return 2;
    HMODULE module=LoadLibraryA(argv[1]);
    if(!module || (uintptr_t)module!=0x10000000) { fprintf(stderr,"module load/base: %lu\n",GetLastError()); return 3; }
    unsigned char* arena=VirtualAlloc((void*)0x30000000,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    unsigned char* stack=VirtualAlloc((void*)0x50000000,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    if((uintptr_t)arena!=0x30000000 || (uintptr_t)stack!=0x50000000) return 4;
    static unsigned char data_before[umbra_data_size];
    unsigned kind,object,inner,nested,mode,word,first,second,seed;
    while(scanf("%u %u %u %u %u %u %u %u %u",&kind,&object,&inner,&nested,&mode,&word,&first,&second,&seed)==9) {
        if(kind>=umbra_function_count || object>960 || inner>960 || nested>960) return 5;
        memset(arena,0x6b,4096); memset(stack,0xa5,4096);
        prepare_arena(arena,object,inner,nested,word,seed,umbra_function_rvas[kind]);
        *(volatile uint32_t*)(uintptr_t)0x1010fb10=mode;
        memcpy(data_before,(void*)(uintptr_t)umbra_data_base,umbra_data_size);
        arguments[0]=first; arguments[1]=second; entry_this=0x30000000u+object;
        entry_target=0x10000000u+umbra_function_rvas[kind];
        invoke_umbra();
        if(observed[4]!=0x50000804u+umbra_cleanups[kind] || observed[3]!=0xaabbccdd || observed[5]!=0x33445566 ||
           observed[6]!=0x778899aa || observed[7]!=0xbbccddee ||
           memcmp(data_before,(void*)(uintptr_t)umbra_data_base,umbra_data_size)) return 6;
        for(unsigned i=0;i<4096;i++) {
            if(i>=1024 && arena[i]!=0x6b) return 7;
            if((i<0x780 || i>=0x810) && stack[i]!=0xa5) return 8;
        }
        for(unsigned i=0;i<8;i++) printf("%u ",observed[i]);
        printf("%u %u ",observed[8]&0x8c5,*(volatile uint32_t*)(uintptr_t)0x1010fb10);
        for(unsigned i=0;i<1024;i++) printf("%02x",arena[i]);
        putchar('\n');
    }
    return feof(stdin) ? 0 : 9;
}
