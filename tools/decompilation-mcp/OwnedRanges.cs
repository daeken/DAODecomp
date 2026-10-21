using System.Text.Json;
namespace Decompilation;

public sealed record OwnedInstructionRange(ulong StartVa,ulong EndVaExclusive,string SliceSha256,JsonElement Lift);
public sealed record OwnedControlEdge(ulong Pc,string Kind,ulong? Target,string Ownership);
public sealed record OwnedRangeProgram(ulong EntryVa,int OwnedBytes,OwnedInstructionRange[] Ranges,OwnedControlEdge[] Edges,string ExceptionalDependencies,string SourceRecovery,bool Proof=false);

// Architectural range ownership, not EH/source interpretation. No synthesized
// stream can give a nonexistent fallthrough across an excluded byte interval.
public static class OwnedRangeRecovery
{
    static void Need(bool ok,string why){if(!ok)throw new ArgumentException(why);}
    public static OwnedRangeProgram Inspect(JsonElement envelope)
    {
        Need(envelope.GetProperty("schema").GetString()=="sharpretro_owned_ranges_v1"&&envelope.GetProperty("mode").GetString()=="Bits32","owned_range_schema");
        var ranges=new List<OwnedInstructionRange>();var rows=new Dictionary<ulong,JsonElement>();int bytes=0;ulong previous=0;
        foreach(var range in envelope.GetProperty("ranges").EnumerateArray()) {
            var lo=range.GetProperty("start_va").GetUInt64();var hi=range.GetProperty("end_va_exclusive").GetUInt64();Need(lo<hi&&hi<=0x100000000UL&&(ranges.Count==0||lo>=previous),"owned_range_order_or_extent");previous=hi;
            var lift=range.GetProperty("lift");Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"owned_range_incomplete_lift");
            Need(lift.GetProperty("pc").GetUInt64()==lo&&lift.GetProperty("decoded_bytes").GetUInt64()==hi-lo&&lift.GetProperty("byte_length").GetUInt64()==hi-lo,"owned_range_lift_extent");
            ulong expected=lo;var raw=new List<byte>();
            foreach(var row in lift.GetProperty("instructions").EnumerateArray()) {
                int length=row.GetProperty("length").GetInt32();Need(row.GetProperty("pc").GetUInt64()==expected&&length is >0 and <=15,"owned_range_instruction_boundary");var code=Convert.FromHexString(row.GetProperty("raw_hex").GetString()!);Need(code.Length==length&&rows.TryAdd(expected,row.Clone()),"owned_range_instruction_overlap");raw.AddRange(code);expected+=checked((ulong)length);
            }
            Need(expected==hi,"owned_range_instruction_coverage");var hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(raw.ToArray())).ToLowerInvariant();Need(hash==range.GetProperty("slice_sha256").GetString(),"owned_range_slice_hash");bytes=checked(bytes+raw.Count);ranges.Add(new(lo,hi,hash,lift.Clone()));
        }
        Need(ranges.Count is >1 and <=64&&envelope.GetProperty("entry_va").GetUInt64()==ranges[0].StartVa&&bytes==envelope.GetProperty("owned_bytes").GetInt32(),"owned_range_entry_or_accounting");
        string Ownership(ulong target) {if(rows.ContainsKey(target))return "owned_instruction";if(ranges.Any(r=>r.StartVa<=target&&target<r.EndVaExclusive))throw new ArgumentException("owned_branch_into_instruction");return "outside_owned_ranges";}
        var edges=new List<OwnedControlEdge>();
        foreach(var (pc,row) in rows) {
            bool fall=true;int branches=0;
            foreach(var node in row.GetProperty("tree").GetProperty("Body").EnumerateArray()) {
                if(node.GetProperty("type").GetString()!="LiftIl.IlBranch")continue;
                Need(++branches==1,"owned_multiple_control_transfers");string kind=node.GetProperty("Kind").GetProperty("name").GetString()!;
                if(kind=="Ret"){edges.Add(new(pc,"return",null,"dynamic_return_unknown"));fall=false;continue;}
                Need(kind is "Call" or "Jmp" or "CondJmp","owned_unsupported_branch_kind");var target=node.GetProperty("Target");ulong? va=target.GetProperty("type").GetString()=="LiftIl.IlConst"?ulong.Parse(target.GetProperty("Bits").GetProperty("decimal").GetString()!):null;
                // CALL target can be a temporary captured before the implicit
                // return-PC write. Resolve only that same-row pure constant let.
                if(va==null&&target.GetProperty("type").GetString()=="LiftIl.IlTmp") {
                    int id=target.GetProperty("Id").GetInt32();foreach(var let in row.GetProperty("tree").GetProperty("Body").EnumerateArray())if(let.GetProperty("type").GetString()=="LiftIl.IlLet"&&let.GetProperty("Id").GetInt32()==id&&let.GetProperty("Val").GetProperty("type").GetString()=="LiftIl.IlConst")va=ulong.Parse(let.GetProperty("Val").GetProperty("Bits").GetProperty("decimal").GetString()!);
                }
                edges.Add(new(pc,kind,va,va.HasValue?Ownership(va.Value):"indirect_unknown"));if(kind=="Jmp")fall=false;
            }
            if(fall){ulong next=pc+(ulong)row.GetProperty("length").GetInt32();edges.Add(new(pc,"fallthrough",next,Ownership(next)));}
        }
        return new(ranges[0].StartVa,bytes,ranges.ToArray(),edges.ToArray(),"separate original-rooted EH evidence required; external edges never become owned bytes","unsupported: range graph is not a recovered source or accepted function");
    }
}
