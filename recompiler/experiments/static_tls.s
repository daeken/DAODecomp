.text
.globl _tls_read
_tls_read:
    movl %fs:0x2c,%ecx
    movl __tls_index,%eax
    movl (%ecx,%eax,4),%eax
    movl (%eax),%eax
    ret
.globl _tls_write
_tls_write:
    movl 4(%esp),%edx
    movl %fs:0x2c,%ecx
    movl __tls_index,%eax
    movl (%ecx,%eax,4),%eax
    movl %edx,(%eax)
    ret
.globl _tls_zero4
_tls_zero4:
    movl %fs:0x2c,%ecx
    movl __tls_index,%eax
    movl (%ecx,%eax,4),%eax
    movl 4(%eax),%eax
    ret
.globl _tls_zero8
_tls_zero8:
    movl %fs:0x2c,%ecx
    movl __tls_index,%eax
    movl (%ecx,%eax,4),%eax
    movl 8(%eax),%eax
    ret
.data
.globl __tls_index
__tls_index: .long 0
.section .tls,"dw"
tls_start: .long 0x13579bdf
tls_end:
.section .rdata,"dr"
.p2align 2
.globl __tls_used
__tls_used:
    .long tls_start
    .long tls_end
    .long __tls_index
    .long 0
    .long 8
    .long 0
