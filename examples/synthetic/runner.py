"""One request per process. x86 emulator oracle or native C++ adapter."""
import json
import struct
import subprocess
import sys
from original_x86 import CODE


def original(values):
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_PROT_READ, UC_PROT_WRITE, UC_PROT_EXEC
    from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EAX, UC_X86_REG_EIP
    machine = Uc(UC_ARCH_X86, UC_MODE_32)
    code, data, stack, stop = 0x100000, 0x200000, 0x300000, 0x100100
    machine.mem_map(code, 4096, UC_PROT_READ | UC_PROT_EXEC)
    machine.mem_map(data, 4096, UC_PROT_READ | UC_PROT_WRITE)
    machine.mem_map(stack, 4096, UC_PROT_READ | UC_PROT_WRITE)
    machine.mem_write(code, CODE)
    machine.mem_write(data, struct.pack("<II", values["value"], values["saturations"]))
    sp = stack + 0x800
    machine.mem_write(sp, struct.pack("<III", stop, data, values["delta"]))
    machine.reg_write(UC_X86_REG_ESP, sp)
    machine.emu_start(code, stop, count=100)
    if machine.reg_read(UC_X86_REG_EIP) != stop or machine.reg_read(UC_X86_REG_ESP) != sp + 4:
        raise RuntimeError("oracle failed to return with cdecl stack balance")
    return machine.reg_read(UC_X86_REG_EAX), bytes(machine.mem_read(data, 8)).hex()


def main():
    request = json.load(sys.stdin)
    if request["schema_version"] != 1 or request["function_id"] != "synthetic:saturating_counter":
        raise ValueError("wrong function or protocol")
    values = request["case"]["inputs"]
    if sys.argv[1] == "original":
        result, memory = original(values)
    elif sys.argv[1] == "candidate":
        raw = subprocess.run([sys.argv[2]], input=f'{values["value"]} {values["saturations"]} {values["delta"]}\n',
                             text=True, capture_output=True, check=True, timeout=3)
        result, value, saturations = map(int, raw.stdout.split())
        memory = struct.pack("<II", value, saturations).hex()
    else:
        raise ValueError("unknown runner")
    json.dump({"schema_version": 1, "case_id": request["case"]["id"], "termination": "return",
               "return": result, "memory": {"counter": memory}, "calls": []}, sys.stdout)


if __name__ == "__main__":
    main()

