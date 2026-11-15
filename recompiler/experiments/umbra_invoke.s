/* Fixed mapped guest stack permits exact integer registers/flags comparison.
 * The tested functions make no native API calls; this is a single-thread runner.
 */
.text
.globl _invoke_umbra
_invoke_umbra:
    pushfl
    pushal
    movl %esp, _saved_host_sp
    movl $0x5000080c, %esp
    pushl _arguments+4
    pushl _arguments
    pushl $0x202
    popfl
    movl $0x12344321, %eax
    movl _entry_this, %ecx
    movl $0x87655678, %edx
    movl $0xaabbccdd, %ebx
    movl $0x33445566, %ebp
    movl $0x778899aa, %esi
    movl $0xbbccddee, %edi
    calll *_entry_target
    movl %eax, _observed
    movl %ecx, _observed+4
    movl %edx, _observed+8
    movl %ebx, _observed+12
    movl %esp, _observed+16
    movl %ebp, _observed+20
    movl %esi, _observed+24
    movl %edi, _observed+28
    pushfl
    popl _observed+32
    movl _saved_host_sp, %esp
    popal
    popfl
    retl
