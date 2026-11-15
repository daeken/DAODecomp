/* Isolated fn_0052ab70 experiment. Original bytes are supplied from the pinned
 * private image, never embedded here. Object/source spans may overlap. */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc,char **argv) {
    if(argc!=2) return 2;
    FILE *file=fopen(argv[1],"rb");
    if(!file) return 3;
    unsigned char bytes[103];
    if(fread(bytes,1,sizeof(bytes),file)!=sizeof(bytes) || fgetc(file)!=EOF || fclose(file)) return 4;
    void *code=VirtualAlloc(NULL,sizeof(bytes),MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
    if(!code) return 5;
    memcpy(code,bytes,sizeof(bytes));
    DWORD old;
    if(!VirtualProtect(code,sizeof(bytes),PAGE_EXECUTE_READ,&old) ||
       !FlushInstructionCache(GetCurrentProcess(),code,sizeof(bytes))) return 6;
    unsigned object,source,seed;
    while(scanf("%u %u %u",&object,&source,&seed)==3) {
        if(object>476 || source>476) return 7;
        unsigned char arena[512]; uint32_t random=seed;
        for(unsigned i=0;i<512;i++) { random^=random<<13; random^=random>>17; random^=random<<5; arena[i]=(unsigned char)random; }
        void *ecx=arena+object; void *argument=arena+source; uint32_t result;
        __asm__ volatile("push %[argument]\n\tcall *%[target]" : "=a"(result), "+c"(ecx)
            : [argument]"r"(argument), [target]"r"(code) : "edx","memory","cc");
        printf("%u %u ",(uint32_t)(result-(uintptr_t)arena),(uint32_t)(uintptr_t)ecx);
        for(unsigned i=0;i<512;i++) printf("%02x",arena[i]);
        putchar('\n');
    }
    if(!feof(stdin)) return 8;
    return !VirtualFree(code,0,MEM_RELEASE);
}
