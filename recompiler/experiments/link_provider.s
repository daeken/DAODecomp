.text
.globl _translated_transform@8
_translated_transform@8:
    movl 4(%esp), %eax
    imull $3, %eax, %eax
    addl 8(%esp), %eax
    addl _provider_bias, %eax
    addl _provider_counter, %eax
    incl _provider_counter
    retl $8
.globl _provider_end
_provider_end:
    int3
.data
.globl _provider_bias
_provider_bias:
    .long 11
.bss
.globl _provider_counter
_provider_counter:
    .zero 4
