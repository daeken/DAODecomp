"""Guarded execution of reviewed leaf slices over one explicit guest allocation.

No calls, private stack writes, globals, exceptions or OS runtime are supported.
Readable/writable byte ranges are supplied by the independently reviewed fixture.
"""
import struct

ARENA_BASE = 0x02000000


def execute_memory(address, code, arena, *, registers, stack_arguments, readable,
                   writable, stack_cleanup, instruction_budget=1000):
    from unicorn import (Uc, UC_ARCH_X86, UC_MODE_32, UC_PROT_READ, UC_PROT_WRITE,
                         UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE)
    from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
                                  UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI,
                                  UC_X86_REG_EBP, UC_X86_REG_ESP, UC_X86_REG_EIP,
                                  UC_X86_REG_EFLAGS)
    if type(arena) is not bytes or not 1 <= len(arena) <= 4096:
        raise ValueError("expected nonempty arena of at most one page")
    if not code or not 0 <= address < address + len(code) <= 0x100000000:
        raise ValueError("invalid code range")
    if (type(stack_cleanup) is not int or stack_cleanup not in (0, 4 * len(stack_arguments))
            or len(stack_arguments) > 16 or type(instruction_budget) is not int or instruction_budget <= 0
            or not set(registers) <= {"eax", "ecx", "edx"}
            or any(type(v) is not int or not 0 <= v <= 0xffffffff
                   for v in [*registers.values(), *stack_arguments])):
        raise ValueError("unsupported memory ABI")
    for offset, size in [*readable, *writable]:
        if type(offset) is not int or type(size) is not int or not 0 <= offset < offset + size <= len(arena):
            raise ValueError("invalid memory footprint")

    machine = Uc(UC_ARCH_X86, UC_MODE_32)
    page = address & ~0xfff
    end_page = (address + len(code) + 0xfff) & ~0xfff
    stack, stop = 0x0e000000, 0x0f000000
    machine.mem_map(page, end_page - page, UC_PROT_READ | UC_PROT_EXEC)
    machine.mem_write(address, code)
    machine.mem_map(ARENA_BASE, 4096, UC_PROT_READ | UC_PROT_WRITE)
    machine.mem_write(ARENA_BASE, arena)
    machine.mem_map(stack, 4096, UC_PROT_READ | UC_PROT_WRITE)
    machine.mem_map(stop, 4096, UC_PROT_READ | UC_PROT_EXEC)
    sp = stack + 0x800
    machine.mem_write(sp, struct.pack("<" + "I" * (1 + len(stack_arguments)), stop, *stack_arguments))
    seed = int.from_bytes((arena + b"\0\0\0\0")[:4], "little")
    saved = {reg: (seed ^ (0xa5c3197b + i * 0x1020304)) & 0xffffffff
             for i, reg in enumerate((UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP))}
    for reg, value in saved.items():
        machine.reg_write(reg, value)
    reg_ids = {"eax": UC_X86_REG_EAX, "ecx": UC_X86_REG_ECX, "edx": UC_X86_REG_EDX}
    for i, (name, reg) in enumerate(reg_ids.items()):
        machine.reg_write(reg, registers.get(name, (seed ^ (0x12345678 * (i + 1))) & 0xffffffff))
    machine.reg_write(UC_X86_REG_ESP, sp)
    machine.reg_write(UC_X86_REG_EFLAGS, 0x202)

    def in_ranges(location, size, ranges):
        return any(ARENA_BASE + off <= location and location + size <= ARENA_BASE + off + count
                   for off, count in ranges)

    def on_code(uc, pc, size, _):
        if not address <= pc or pc + size > address + len(code):
            raise RuntimeError("execution escaped reviewed function slice")

    def on_read(uc, access, location, size, contents, _):
        if sp <= location and location + size <= sp + 4 * (1 + len(stack_arguments)):
            return
        if not in_ranges(location, size, readable):
            raise RuntimeError("read outside declared footprint")

    def on_write(uc, access, location, size, contents, _):
        if not in_ranges(location, size, writable):
            raise RuntimeError("write outside declared footprint")

    machine.hook_add(UC_HOOK_CODE, on_code)
    machine.hook_add(UC_HOOK_MEM_READ, on_read)
    machine.hook_add(UC_HOOK_MEM_WRITE, on_write)
    machine.emu_start(address, stop, count=instruction_budget)
    if machine.reg_read(UC_X86_REG_EIP) != stop or machine.reg_read(UC_X86_REG_ESP) != sp + 4 + stack_cleanup:
        raise RuntimeError("leaf did not return with declared stack balance within budget")
    if any(machine.reg_read(reg) != value for reg, value in saved.items()):
        raise RuntimeError("leaf clobbered a nonvolatile register")
    if machine.reg_read(UC_X86_REG_EFLAGS) & 0x400:
        raise RuntimeError("leaf returned with direction flag set")
    return machine.reg_read(UC_X86_REG_EAX), bytes(machine.mem_read(ARENA_BASE, len(arena)))
