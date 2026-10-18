# Rapid candidate ABI and schema v1 (frozen)

All generated source includes `rapid/context.hpp`, uses `rapid::Context`, and
exports ordinary global C++ functions `void fn_XXXXXXXX(rapid::Context& c)` where
XXXXXXXX is the lowercase eight-digit RVA. No custom per-function signatures.
The public Context fields are uint32_t eax, ebx, ecx, edx, esi, edi, ebp, esp,
eflags, image_base, return_address; bool returned; uint64_t steps, step_budget.
Memory access is little endian guest-address uint32_t read8/read16/read32 and
write8/write16/write32; no guest address is a host pointer. Callbacks are
std::function<uint8_t(uint32_t)> memory_read,
std::function<void(uint32_t,uint8_t)> memory_write, and
std::function<void(Context&,uint32_t rva)> resolver. Missing callbacks throw
rapid::Unsupported. push32/pop32 update the guest stack. ret(cleanup=0) pops the
actual entry return address, advances esp by cleanup and records returned=true.
call_rva(rva,continuation_va)/call_va(va,continuation_va) push that observed guest
continuation VA, invoke the resolver, require the same return address, and clear
the nested returned marker. A tail call uses resolver(c,rva) directly (or throws
unsupported) and retains the callee return marker. tick(n=1) enforces a step budget.
unsupported(string) always throws. No default successful dependency behavior.
Helpers signed32 and sar32 implement signed interpretation and arithmetic shift.
Preserve all GPR exit values; EFLAGS exit comparison policy belongs to downstream
validation, but internal flag-dependent paths and DF behavior must be preserved.

Packet JSON: schema_version=1, evidence_kind=static_hypotheses,
module, module_sha256, image_base, abi_sha256 (header bytes), functions list.
Each function has name, rva, start_rva, end_rva_inclusive, bytes_sha256,
bytes_hex, instructions (address VA, bytes, mnemonic, op_str), direct_calls
(RVAs), and hypothesis (original inventory record). Identity is pinned binary
SHA256 + module + RVA; ranges and signatures remain static hypotheses.
Packet ID is SHA256 of canonical JSON packet bytes. Packets are immutable.

Provider response uses existing workers.deepseek_packet.RESPONSE_SCHEMA:
source string; functions [{name,suggested_name,explanation}]; uncertainties [str].
Exact requested name set is mandatory. Saved result.json binds packet_sha256,
response_sha256, source_sha256, abi_sha256, module_sha256, functions, outcome,
compile_ready, compiler, validation_status="unvalidated", uncertainties.
Sources are content-addressed `objects/<source_sha256>.cpp`; per-batch files are
`batches/<packet_sha256>/{packet.json,request.json,raw-response.json,response.json,
source.cpp,compile.log,result.json}`. Raw response is retained after the existing
provider transport's credential scan. Errors/partial output are retained, never
silently retried or treated as semantic success. Queue states are pending,
claimed, complete, error, interrupted_unknown. Preparation-only dispositions
needs_larger_budget and superseded_undispatched retain delayed or superseded
never-requested packets without resetting attempted work. Syntax compilation and schema
checks are mechanical evidence only. Downstream validation never promotes queue
output or edits this ABI implicitly.
