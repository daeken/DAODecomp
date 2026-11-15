// Controlled native reference for the reached legacy encodings. No game bytes.
.text
.globl _native_word_probe
_native_word_probe:
    pushfl
    pushl %ebx
    movl 12(%esp), %ebx
    pushl %ebx
    .byte 0x66,0x9c
    popl %eax
    movl %eax,%ebx
    xorl $0x200000,%eax
    pushl %eax
    .byte 0x66,0x9d
    .byte 0x66,0x9c
    popl %eax
    xorl %ebx,%eax
    pushl %ebx
    .byte 0x66,0x9d
    popl %ebx
    popl %ebx
    popfl
    ret

.globl _native_word_regs
_native_word_regs:
    pushal
    movl _word_inputs,%eax
    movl _word_inputs+4,%ecx
    movl _word_inputs+8,%edx
    movl _word_inputs+12,%ebx
    movl _word_inputs+20,%ebp
    movl _word_inputs+24,%esi
    movl _word_inputs+28,%edi
    movl %esp,_word_sp
    .byte 0x66,0x60
    movw 0(%esp),%ax
    movw %ax,_word_frame
    movw 2(%esp),%ax
    movw %ax,_word_frame+2
    movw 4(%esp),%ax
    movw %ax,_word_frame+4
    movw 6(%esp),%ax
    movw %ax,_word_frame+6
    movw 8(%esp),%ax
    movw %ax,_word_frame+8
    movw 10(%esp),%ax
    movw %ax,_word_frame+10
    movw 12(%esp),%ax
    movw %ax,_word_frame+12
    movw 14(%esp),%ax
    movw %ax,_word_frame+14
    movw $0xdead,6(%esp)
    movl $0xa1000011,%eax
    movl $0xa2010012,%ecx
    movl $0xa3020013,%edx
    movl $0xa4030014,%ebx
    movl $0xa6050016,%ebp
    movl $0xa7060017,%esi
    movl $0xa8070018,%edi
    .byte 0x66,0x61
    movl %eax,_word_outputs
    movl %ecx,_word_outputs+4
    movl %edx,_word_outputs+8
    movl %ebx,_word_outputs+12
    movl %esp,_word_outputs+16
    movl %ebp,_word_outputs+20
    movl %esi,_word_outputs+24
    movl %edi,_word_outputs+28
    popal
    ret

.globl _native_dword_regs
_native_dword_regs:
    pushal
    movl _word_inputs,%eax
    movl _word_inputs+4,%ecx
    movl _word_inputs+8,%edx
    movl _word_inputs+12,%ebx
    movl _word_inputs+20,%ebp
    movl _word_inputs+24,%esi
    movl _word_inputs+28,%edi
    movl %esp,_word_sp
    pushal
    movl 0(%esp),%eax
    movl %eax,_dword_frame+0
    movl 4(%esp),%eax
    movl %eax,_dword_frame+4
    movl 8(%esp),%eax
    movl %eax,_dword_frame+8
    movl 12(%esp),%eax
    movl %eax,_dword_frame+12
    movl 16(%esp),%eax
    movl %eax,_dword_frame+16
    movl 20(%esp),%eax
    movl %eax,_dword_frame+20
    movl 24(%esp),%eax
    movl %eax,_dword_frame+24
    movl 28(%esp),%eax
    movl %eax,_dword_frame+28
    movl $0xdeadbeef,12(%esp)
    movl $0xa1000011,%eax
    movl $0xa2010012,%ecx
    movl $0xa3020013,%edx
    movl $0xa4030014,%ebx
    movl $0xa6050016,%ebp
    movl $0xa7060017,%esi
    movl $0xa8070018,%edi
    popal
    movl %eax,_word_outputs
    movl %ecx,_word_outputs+4
    movl %edx,_word_outputs+8
    movl %ebx,_word_outputs+12
    movl %esp,_word_outputs+16
    movl %ebp,_word_outputs+20
    movl %esi,_word_outputs+24
    movl %edi,_word_outputs+28
    popal
    ret
