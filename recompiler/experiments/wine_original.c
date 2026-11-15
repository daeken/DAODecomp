/* Isolated PE32 integer/memory leaf experiment, not a game loader.
 * The controller admits only the two pinned, relocation-independent slices.
 * Input: mode object_offset value seed. Output: EAX ECX-relative all-arena-bytes.
 */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if(argc!=3) return 2;
    FILE *file=fopen(argv[1],"rb");
    if(!file || fseek(file,0,SEEK_END)) return 3;
    long length=ftell(file);
    if(length<=0 || length>4096 || fseek(file,0,SEEK_SET)) return 4;
    void *code=VirtualAlloc(NULL,(SIZE_T)length,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
    if(!code || fread(code,1,(size_t)length,file)!=(size_t)length || fclose(file)) return 5;
    DWORD old;
    if(!VirtualProtect(code,(SIZE_T)length,PAGE_EXECUTE_READ,&old) ||
       !FlushInstructionCache(GetCurrentProcess(),code,(SIZE_T)length)) return 6;
    unsigned object,value,seed;
    while(scanf("%u %u %u",&object,&value,&seed)==3) {
        if(object>400) return 7;
        unsigned char arena[512];
        uint32_t random=seed;
        for(unsigned i=0;i<512;i++) { random^=random<<13; random^=random>>17; random^=random<<5; arena[i]=(unsigned char)random; }
        void *ecx=arena+object;
        uint32_t result;
        if(argv[2][0]=='0') {
            __asm__ volatile("call *%[target]" : "=a"(result), "+c"(ecx)
                : [target]"r"(code) : "edx","memory","cc");
        } else if(argv[2][0]=='1') {
            __asm__ volatile("push %[argument]\n\tcall *%[target]" : "=a"(result), "+c"(ecx)
                : [argument]"r"(value), [target]"r"(code) : "edx","memory","cc");
        } else return 8;
        printf("%u %u ",result,(uint32_t)((uintptr_t)ecx-(uintptr_t)arena));
        for(unsigned i=0;i<512;i++) printf("%02x",arena[i]);
        putchar('\n');
    }
    if(!feof(stdin)) return 9;
    return !VirtualFree(code,0,MEM_RELEASE);
}
