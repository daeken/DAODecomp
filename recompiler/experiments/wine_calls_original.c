/* Synthetic native-x86 reference for call_fixture.py. Not a game loader. */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#ifndef FIXTURE_BASE
#define FIXTURE_BASE 0x30000000u
#endif

int main(int argc,char **argv) {
    if(argc!=2 || sizeof(void*)!=4) return 2;
    void *image=VirtualAlloc((void*)(uintptr_t)FIXTURE_BASE,0x4000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    if(image!=(void*)(uintptr_t)FIXTURE_BASE) {
        DWORD error=GetLastError(); MEMORY_BASIC_INFORMATION info={0};
        (void)VirtualQuery((void*)(uintptr_t)FIXTURE_BASE,&info,sizeof(info));
        fprintf(stderr,"fixture mapping failed: error=%lu main=%p allocation=%p state=%lx type=%lx\n",
            (unsigned long)error,(void*)GetModuleHandleA(NULL),info.AllocationBase,(unsigned long)info.State,(unsigned long)info.Type);
        return 5;
    }
    FILE *file=fopen(argv[1],"rb"); if(!file) return 3;
    unsigned char code[0x300];
    if(fread(code,1,sizeof(code),file)!=sizeof(code) || fgetc(file)!=EOF || fclose(file)) return 4;
    memcpy((void*)(uintptr_t)(FIXTURE_BASE+0x1000),code,sizeof(code));
    *(uint32_t*)(uintptr_t)(FIXTURE_BASE+0x3000)=FIXTURE_BASE+0x1040;
    DWORD old;
    if(!VirtualProtect((void*)(uintptr_t)(FIXTURE_BASE+0x1000),0x1000,PAGE_EXECUTE_READ,&old) ||
       !FlushInstructionCache(GetCurrentProcess(),(void*)(uintptr_t)(FIXTURE_BASE+0x1000),sizeof(code))) return 6;
    const uint32_t offsets[]={0x1000,0x1080,0x10a0,0x10c0,0x10e0,0x1160,0x11a0,0x1160};
    unsigned kind,first,second;
    while(scanf("%u %u %u",&kind,&first,&second)==3) {
        if(kind>=8 || (kind==4 && first>8)) return 7;
        *(uintptr_t*)(uintptr_t)(FIXTURE_BASE+0x2050)=kind==7 ? FIXTURE_BASE+0x11e0 : (uintptr_t)&MulDiv;
        void *target=(void*)(uintptr_t)(FIXTURE_BASE+offsets[kind]); uint32_t ecx=FIXTURE_BASE+0x3000,result,balanced;
        __asm__ volatile("mov %%esp,%%edi\n\tpush %[second]\n\tpush %[first]\n\tcall *%[target]\n\tadd $8,%%esp\n\tcmp %%edi,%%esp\n\tsete %%dl\n\tmovzbl %%dl,%%edx"
            : "=a"(result), "+c"(ecx), "=d"(balanced)
            : [first]"r"(first), [second]"r"(second), [target]"r"(target)
            : "edi","memory","cc");
        if(!balanced) return 8;
        printf("%u\n",result);
    }
    if(!feof(stdin)) return 9;
    return !VirtualFree(image,0,MEM_RELEASE);
}
