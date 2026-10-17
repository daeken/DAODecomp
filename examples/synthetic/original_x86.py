"""Hand-authored fixture, not Dragon Age code. x86 cdecl: u32 bump(Counter*, u32).

00  mov ecx, [esp+4]      ; counter pointer
04  mov eax, [ecx]        ; old value / return
06  mov edx, [esp+8]      ; delta
0a  add edx, eax
0c  jnc 0x16             ; no unsigned overflow
0e  mov edx, 0xffffffff
13  inc dword [ecx+4]    ; saturation count, wraps
16  mov [ecx], edx
18  ret
"""
CODE = bytes.fromhex("8b4c2404 8b01 8b542408 01c2 7308 baffffffff ff4104 8911 c3")

