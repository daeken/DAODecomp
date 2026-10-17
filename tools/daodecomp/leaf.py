"""Strict concrete backend for reviewed, read-only single-argument x86 leaves.

This is deliberately not a PE loader or an automatic function runner. The caller
must supply a reviewed contiguous slice with no relocations or dependencies.
"""
import hashlib
from pathlib import Path
import struct

from .pe import fingerprint


def load_slice(path, module_sha256, rva, size, code_sha256):
    if type(rva) is not int or type(size) is not int or rva < 0 or size <= 0:
        raise ValueError("invalid slice range")
    metadata = fingerprint(path)
    data = Path(path).read_bytes()
    if metadata["sha256"] != module_sha256 or hashlib.sha256(data).hexdigest() != module_sha256:
        raise ValueError("reference module hash mismatch")
    if metadata["architecture"] != "x86" or metadata["format"] != "PE32":
        raise ValueError("leaf backend requires PE32 x86")
    sections = [s for s in metadata["sections"] if s["rva"] <= rva and
                rva + size <= s["rva"] + min(s["file_size"], s["virtual_size"])]
    if len(sections) != 1:
        raise ValueError("slice is not uniquely file-backed in one section")
    section = sections[0]
    offset = section["file_offset"] + rva - section["rva"]
    code = data[offset:offset + size]
    if hashlib.sha256(code).hexdigest() != code_sha256:
        raise ValueError("instruction slice hash mismatch")
    return metadata["image_base"] + rva, code


def execute_leaf(address, code, value, *, argument="stack", return_bits=32, stack_cleanup=0,
                 preserved_registers=()):
    from unicorn import (Uc, UC_ARCH_X86, UC_MODE_32, UC_PROT_READ, UC_PROT_WRITE,
                         UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE)
    from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
                                  UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI,
                                  UC_X86_REG_EBP, UC_X86_REG_ESP, UC_X86_REG_EIP,
                                  UC_X86_REG_EFLAGS)
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise ValueError("expected u32 input")
    if (argument not in ("stack", "eax", "ecx") or type(return_bits) is not int
            or return_bits not in (8, 32) or type(stack_cleanup) is not int
            or stack_cleanup not in (0, 4) or (argument != "stack" and stack_cleanup != 0)
            or any(reg not in ("ecx", "edx") for reg in preserved_registers)):
        raise ValueError("unsupported scalar ABI")
    if not code or address < 0 or address + len(code) > 0x100000000:
        raise ValueError("invalid instruction range")
    machine = Uc(UC_ARCH_X86, UC_MODE_32)
    page = address & ~0xfff
    end_page = (address + len(code) + 0xfff) & ~0xfff
    stack, stop = 0x0e000000, 0x0f000000
    machine.mem_map(page, end_page - page, UC_PROT_READ | UC_PROT_EXEC)
    machine.mem_write(address, code)
    machine.mem_map(stack, 4096, UC_PROT_READ | UC_PROT_WRITE)
    machine.mem_map(stop, 4096, UC_PROT_READ | UC_PROT_EXEC)
    sp = stack + 0x800
    machine.mem_write(sp, struct.pack("<II", stop, value))
    saved = {reg: (0xa5c3197b ^ (i * 0x1020304) ^ value) & 0xffffffff
             for i, reg in enumerate((UC_X86_REG_EBX, UC_X86_REG_ESI,
                                      UC_X86_REG_EDI, UC_X86_REG_EBP))}
    for reg, contents in saved.items():
        machine.reg_write(reg, contents)
    for i, reg in enumerate((UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EDX)):
        machine.reg_write(reg, (value ^ (0x12345678 * (i + 1))) & 0xffffffff)
    if argument != "stack":
        machine.reg_write({"eax": UC_X86_REG_EAX, "ecx": UC_X86_REG_ECX}[argument], value)
    for name in preserved_registers:
        reg = {"ecx": UC_X86_REG_ECX, "edx": UC_X86_REG_EDX}[name]
        saved[reg] = machine.reg_read(reg)
    machine.reg_write(UC_X86_REG_ESP, sp)
    machine.reg_write(UC_X86_REG_EFLAGS, 0x202)  # DF clear, normal cdecl entry.

    def on_code(uc, pc, size, _):
        if not address <= pc or pc + size > address + len(code):
            raise RuntimeError("execution escaped reviewed function slice")

    def on_read(uc, access, location, size, contents, _):
        readable_end = sp + (8 if argument == "stack" else 4)
        if not sp <= location or location + size > readable_end:
            raise RuntimeError("read outside return-address/argument footprint")

    def on_write(uc, access, location, size, contents, _):
        raise RuntimeError("unexpected memory write in read-only leaf")

    machine.hook_add(UC_HOOK_CODE, on_code)
    machine.hook_add(UC_HOOK_MEM_READ, on_read)
    machine.hook_add(UC_HOOK_MEM_WRITE, on_write)
    machine.emu_start(address, stop, count=100)
    if machine.reg_read(UC_X86_REG_EIP) != stop or machine.reg_read(UC_X86_REG_ESP) != sp + 4 + stack_cleanup:
        raise RuntimeError("leaf did not return with declared stack balance within budget")
    if any(machine.reg_read(reg) != contents for reg, contents in saved.items()):
        raise RuntimeError("leaf clobbered a nonvolatile register")
    if machine.reg_read(UC_X86_REG_EFLAGS) & 0x400:
        raise RuntimeError("leaf returned with direction flag set")
    return machine.reg_read(UC_X86_REG_EAX) & ((1 << return_bits) - 1)
