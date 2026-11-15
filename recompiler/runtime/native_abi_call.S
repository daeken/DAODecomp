/* Experimental x86 native ABI transport, not original game code. Layout is
 * asserted in native_abi_frame.hpp. TLS points to the current nested call frame.
 * Normal translated callbacks use native_callback_entry.hpp; nonlocal native
 * exception/unwind continuation remains unsupported. */
    .text
    .globl _recomp_native_abi_call
    .def _recomp_native_abi_call; .scl 2; .type 32; .endef
_recomp_native_abi_call:
    pushfl
    pushal
    movl 40(%esp),%eax
    movl %esp,40(%eax)
    fxsave 1104(%eax)
    movq %mm0,1968(%eax)
    movq %mm1,1976(%eax)
    movq %mm2,1984(%eax)
    movq %mm3,1992(%eax)
    movq %mm4,2000(%eax)
    movq %mm5,2008(%eax)
    movq %mm6,2016(%eax)
    movq %mm7,2024(%eax)
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
    frstor 1728(%eax)
    cmpl $0,2032(%eax)
    je 1f
    movq 1840(%eax),%mm0
    movq 1848(%eax),%mm1
    movq 1856(%eax),%mm2
    movq 1864(%eax),%mm3
    movq 1872(%eax),%mm4
    movq 1880(%eax),%mm5
    movq 1888(%eax),%mm6
    movq 1896(%eax),%mm7
1:
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
    fnsave 1616(%eax)
    movq %mm0,1904(%eax)
    movq %mm1,1912(%eax)
    movq %mm2,1920(%eax)
    movq %mm3,1928(%eax)
    movq %mm4,1936(%eax)
    movq %mm5,1944(%eax)
    movq %mm6,1952(%eax)
    movq %mm7,1960(%eax)
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
    cmpl $0,2032(%eax)
    je 2f
    movq 1968(%eax),%mm0
    movq 1976(%eax),%mm1
    movq 1984(%eax),%mm2
    movq 1992(%eax),%mm3
    movq 2000(%eax),%mm4
    movq 2008(%eax),%mm5
    movq 2016(%eax),%mm6
    movq 2024(%eax),%mm7
2:
    movl 40(%eax),%esp
    popal
    popfl
    ret

    .globl _recomp_native_abi_capture
    .def _recomp_native_abi_capture; .scl 2; .type 32; .endef
_recomp_native_abi_capture:
    pushfl
    pushal
    movl 40(%esp),%eax
    fxsave 592(%eax)
    fnsave 1616(%eax)
    movq %mm0,1904(%eax)
    movq %mm1,1912(%eax)
    movq %mm2,1920(%eax)
    movq %mm3,1928(%eax)
    movq %mm4,1936(%eax)
    movq %mm5,1944(%eax)
    movq %mm6,1952(%eax)
    movq %mm7,1960(%eax)
    fxrstor 592(%eax)
    frstor 1616(%eax)
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
    popal
    popfl
    ret
