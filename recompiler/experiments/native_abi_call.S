/* Experimental x86 native ABI transport, not original game code. Layout is
 * asserted in native_abi_call.cpp. TLS points to the current nested call frame.
 * Native exception/unwind delivery and translated callbacks remain unsupported. */
    .text
    .globl _recomp_native_abi_call
    .def _recomp_native_abi_call; .scl 2; .type 32; .endef
_recomp_native_abi_call:
    pushfl
    pushal
    movl 40(%esp),%eax
    movl %esp,40(%eax)
    fxsave 1104(%eax)
    movl %fs:4,%edx
    movl %edx,68(%eax)
    movl %fs:8,%edx
    movl %edx,64(%eax)
    movl 60(%eax),%edx
    movl %edx,%fs:4
    movl 56(%eax),%edx
    movl %edx,%fs:8
    movl 20(%eax),%edx
    movl %edx,44(%eax)
    movl (%edx),%ecx
    movl %ecx,48(%eax)
    movl $recomp_native_abi_return,(%edx)
    fxrstor 80(%eax)
    pushl 36(%eax)
    popfl
    movl 20(%eax),%esp
    pushl 0(%eax)
    movl 8(%eax),%ecx
    movl 12(%eax),%edx
    movl 16(%eax),%ebx
    movl 24(%eax),%ebp
    movl 28(%eax),%esi
    movl 32(%eax),%edi
    movl 4(%eax),%eax
    ret
recomp_native_abi_return:
    pushfl
    pushal
    movl _recomp_native_abi_tls_slot,%eax
    movl %fs:0xe10(,%eax,4),%eax
    fxsave 592(%eax)
    movl %esp,%edx
    movl 28(%edx),%ecx
    movl %ecx,4(%eax)
    movl 24(%edx),%ecx
    movl %ecx,8(%eax)
    movl 20(%edx),%ecx
    movl %ecx,12(%eax)
    movl 16(%edx),%ecx
    movl %ecx,16(%eax)
    movl 12(%edx),%ecx
    leal 4(%ecx),%ecx
    movl %ecx,20(%eax)
    movl 8(%edx),%ecx
    movl %ecx,24(%eax)
    movl 4(%edx),%ecx
    movl %ecx,28(%eax)
    movl 0(%edx),%ecx
    movl %ecx,32(%eax)
    movl 32(%edx),%ecx
    movl %ecx,36(%eax)
    movl %fs:0x34,%ecx
    movl %ecx,52(%eax)
    movl 44(%eax),%ecx
    movl 48(%eax),%edx
    movl %edx,(%ecx)
    movl 68(%eax),%ecx
    movl %ecx,%fs:4
    movl 64(%eax),%ecx
    movl %ecx,%fs:8
    fxrstor 1104(%eax)
    movl 40(%eax),%esp
    popal
    popfl
    ret
