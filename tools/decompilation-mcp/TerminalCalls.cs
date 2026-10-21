using System.Security.Cryptography;
using System.Text.Json;
namespace Decompilation;

// Compiler/runtime evidence is separate from the generic architectural CFG.
// There is no invented cleanup, formal arity or successful unknown return.
public sealed record RuntimeTerminalEvidence(ulong Target,string Profile,string BytesSha256,bool CompleteBytesCompared,bool NormalReturnSupported,string LibrarySha256,string ObjectSha256,string[] Assumptions,string Effects,bool Proof=false);
public sealed record TerminalCalleeSummary(ulong Target,RuntimeTerminalEvidence Runtime,ulong[] InstructionOrigins,ulong[] TerminalCallSites,int UnknownOrdinaryCalls,string SliceSha256,bool MemoryEffectsUnknown=true,bool ExceptionalDestinationsUnknown=true,bool Proof=false);
public static class X86TerminalCallRecovery
{
    static void Need(bool ok,string reason){if(!ok)throw new ArgumentException(reason);}
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static string Name(JsonElement n,string p)=>n.GetProperty(p).GetProperty("name").GetString()!;
    static JsonElement[] Nodes(JsonElement r)=>r.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();
    public static ulong DirectCallTarget(JsonElement row,JsonElement branch)
    {
        Need(Name(branch,"Kind")=="Call"&&branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"terminal_conditional_call");var raw=Convert.FromHexString(row.GetProperty("raw_hex").GetString()!);ulong pc=row.GetProperty("pc").GetUInt64();Need(raw.Length==5&&raw[0]==0xe8,"terminal_direct_near_call_required");var target=branch.GetProperty("Target");
        if(Tag(target)=="IlTmp"){int id=target.GetProperty("Id").GetInt32();var definitions=Nodes(row).Where(n=>Tag(n)=="IlLet"&&n.GetProperty("Id").GetInt32()==id).ToArray();Need(definitions.Length==1,"terminal_target_temporary");target=definitions[0].GetProperty("Val");}
        Need(Tag(target)=="IlConst"&&!target.GetProperty("Ty").GetProperty("Signed").GetBoolean()&&target.GetProperty("Ty").GetProperty("Bits").GetInt32()==32&&ulong.TryParse(target.GetProperty("Bits").GetProperty("decimal").GetString(),out _),"terminal_typed_direct_target");ulong dest=ulong.Parse(target.GetProperty("Bits").GetProperty("decimal").GetString()!);Need(dest==unchecked((uint)(pc+5+(ulong)System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(raw.AsSpan(1)))),"terminal_encoding_target_disagrees");return dest;
    }
    public static void ValidateRuntime(RuntimeTerminalEvidence runtime)
    {
        Need(runtime.Target<=uint.MaxValue&&!string.IsNullOrWhiteSpace(runtime.Profile)&&runtime.CompleteBytesCompared&&!runtime.NormalReturnSupported&&!runtime.Proof&&new[]{runtime.BytesSha256,runtime.LibrarySha256,runtime.ObjectSha256}.All(h=>h.Length==64&&h.All(Uri.IsHexDigit))&&runtime.Assumptions.Length>0,"terminal_runtime_evidence_domain");
        Need(runtime.Profile=="vc8-CxxThrowException-noncontinuable-v1","unsupported_VC8_terminal_runtime_profile");
    }
    public static TerminalCalleeSummary Inspect(ulong target,JsonElement lift,RuntimeTerminalEvidence runtime)
    {
        ValidateRuntime(runtime);
        Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"terminal_incomplete_lift");var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length is >0 and <=128,"terminal_instruction_budget");ulong expected=target;var index=new Dictionary<ulong,int>();var bytes=new List<byte>();
        foreach(var row in rows){var raw=Convert.FromHexString(row.GetProperty("raw_hex").GetString()!);var prefix=row.GetProperty("decoded").GetProperty("P");Need(row.GetProperty("pc").GetUInt64()==expected&&raw.Length==row.GetProperty("length").GetInt32()&&raw.Length is >0 and <=15&&Tag(row.GetProperty("tree"))=="IlBlock"&&!prefix.GetProperty("Lock").GetBoolean()&&!prefix.GetProperty("Rep").GetBoolean()&&!prefix.GetProperty("RepNz").GetBoolean(),"terminal_boundary_or_prefix");index.Add(expected,index.Count);expected+=(ulong)raw.Length;bytes.AddRange(raw);}
        var pending=new Queue<int>();pending.Enqueue(0);var seen=new HashSet<int>();var terminals=new List<ulong>();int calls=0;
        while(pending.TryDequeue(out int at)){
            if(!seen.Add(at))continue;var row=rows[at];var nodes=Nodes(row);Need(ArchitecturalFaults.Inspect(row).Length==0,"terminal_architectural_fault_path_unproven");var branches=nodes.Where(n=>Tag(n)=="IlBranch").ToArray();Need(branches.Length<=1&&(branches.Length==0||nodes[^1].Equals(branches[0])),"terminal_control_effect_shape");bool fall=true;
            if(branches.Length==1){var branch=branches[0];string kind=Name(branch,"Kind");if(kind=="Call"){ulong destination=DirectCallTarget(row,branch);if(destination==runtime.Target){terminals.Add(row.GetProperty("pc").GetUInt64());fall=false;}else calls++;}
                else {Need(kind is "Jmp" or "CondJmp","terminal_normal_return_or_unknown_exit");var dest=branch.GetProperty("Target");Need(Tag(dest)=="IlConst"&&ulong.TryParse(dest.GetProperty("Bits").GetProperty("decimal").GetString(),out _)&&index.ContainsKey(ulong.Parse(dest.GetProperty("Bits").GetProperty("decimal").GetString()!)),"terminal_external_or_misaligned_branch");int next=index[ulong.Parse(dest.GetProperty("Bits").GetProperty("decimal").GetString()!)];Need(next>at,"terminal_backedge_not_proven");pending.Enqueue(next);if(kind=="Jmp"){Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"terminal_branch_condition");fall=false;}else Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Object,"terminal_branch_condition");}}
            if(fall){Need(at+1<rows.Length,"terminal_unproven_fallthrough");pending.Enqueue(at+1);}
        }
        Need(seen.Count==rows.Length&&terminals.Count>0,"terminal_unreachable_or_missing_terminal");return new(target,runtime,rows.Select(r=>r.GetProperty("pc").GetUInt64()).ToArray(),terminals.ToArray(),calls,Convert.ToHexStringLower(SHA256.HashData(bytes.ToArray())));
    }
}

public static class Vc8TerminalCallProfile
{
    public const string Version="vc8-x86-flat32-terminal-aware-memory-control-v1";
    public static TerminalCalleeSummary Inspect(ulong target,JsonElement lift,RuntimeTerminalEvidence runtime)
    {
        if(runtime.Profile!="vc8-CxxThrowException-noncontinuable-v1")throw new ArgumentException("unsupported_VC8_terminal_runtime_profile");
        return X86TerminalCallRecovery.Inspect(target,lift,runtime);
    }
}
