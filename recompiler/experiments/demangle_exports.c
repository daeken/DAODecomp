/* Inspect decorated export names only. This never loads/calls game middleware. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <dbghelp.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    char name[8192], declaration[16384];
    while(fgets(name,sizeof(name),stdin)) {
        size_t length=strlen(name);
        if(!length || name[length-1]!='\n') return 2;
        name[--length]=0;
        if(length && name[length-1]=='\r') name[--length]=0;
        if(!length || name[0]!='?' || strchr(name,'\t')) return 3;
        if(!UnDecorateSymbolName(name,declaration,sizeof(declaration),UNDNAME_COMPLETE) ||
           !strcmp(name,declaration) || strchr(declaration,'\n') || strchr(declaration,'\t')) return 4;
        if(printf("%s\t%s\n",name,declaration)<0) return 5;
    }
    return ferror(stdin) || fflush(stdout) ? 6 : 0;
}
