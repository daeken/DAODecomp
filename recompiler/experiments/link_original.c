/* Synthetic Windows loader experiment; no game code. */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
extern uint32_t experiment_entry(uint32_t, uint32_t);
int main(void) {
    HMODULE provider=GetModuleHandleA("fixture_provider.dll");
    if(!provider || (uintptr_t)provider!=0x30000000u || (uintptr_t)GetModuleHandleA(NULL)!=0x20000000u) return 2;
    volatile uint32_t* counter=(volatile uint32_t*)GetProcAddress(provider,"provider_counter");
    if(!counter) return 3;
    uint32_t first,second,count;
    while(scanf("%u %u %u",&first,&second,&count)==3) {
        if(count<1 || count>2) return 4;
        *counter=0; uint32_t result=0;
        for(uint32_t i=0;i<count;i++) result=experiment_entry(first,second);
        printf("%u %u\n",result,*counter);
    }
    return ferror(stdin) ? 5 : 0;
}
