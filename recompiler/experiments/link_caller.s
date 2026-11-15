.text
.globl _experiment_entry
_experiment_entry:
    pushl 8(%esp)
    pushl 8(%esp)
    calll *__imp__translated_transform@8
    xorl $0x5a5aa5a5, %eax
    retl
.globl _experiment_end
_experiment_end:
    int3
