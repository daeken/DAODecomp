using System.Text.Json;
namespace Decompilation;

public sealed record StructuredMemoryFunction(FlowFunction Flow,string[] Hypotheses);

// Acyclic effect-tree emission is separate from x86 recovery. Stack aliases
// remain explicit in FlowExit, and no allocator/string semantics are invented.
public static class Vc8StructuredMemoryProfile
{
    public const string Version="vc8-x86-flat32-ordered-memory-control-v1";
    static RecoveryAbi Abi=>new(Version,0,[],[0,1,2],[3,5,6,7]);
    static void Need(bool p,string s){if(!p)throw new ArgumentException(s);}
    static bool Same(object a,object b)=>JsonSerializer.Serialize(a)==JsonSerializer.Serialize(b);
    static bool SameEffect(FlowEffect a,FlowEffect b)=>a.Kind=="external_call"&&b.Kind=="external_call"?a.Pc==b.Pc&&a.Call!.Target==b.Call!.Target&&a.Call.CalleeCleanup==b.Call.CalleeCleanup&&a.Call.CallerCleanup==b.Call.CallerCleanup&&Same(a.Call.Arguments,b.Call.Arguments):Same(a,b);
    static RecoveredValue Low(RecoveredValue v)=>v is BitValue{Operation:"Trunc" or "Zext",Bits:32 or 64,Operands.Length:1} t?Low(t.Operands[0]):v;
    static long? Stack(RecoveredValue v)=>v switch{AddValue{Left:RegisterInput{Index:4}} a=>a.Offset,SegmentedAddress{Segment:{Index:2},Offset:var x}=>Stack(x),_=>null};
    static RecoveredValue Normalize(RecoveredValue v)=>v is BitValue b?b.Operands.Length==2?X86GraphRecovery.Op(b.Operation,Normalize(b.Operands[0]),Normalize(b.Operands[1]),b.Bits):new BitValue(b.Operation,b.Operands.Select(Normalize).ToArray(),b.Bits):v;
    static RecoveredValue? ReceiverOffset(RecoveredValue raw) {
        var v=Low(raw);if(v is RegisterInput{Index:1})return new Constant(0,32);
        if(v is SegmentedAddress{Segment:{Index:3},Offset:var x})return ReceiverOffset(x);
        if(v is BitValue{Operation:"Add",Operands.Length:2} sum){var left=ReceiverOffset(sum.Operands[0]);if(left!=null)return X86GraphRecovery.Op("Add",left,Low(sum.Operands[1]),32);var right=ReceiverOffset(sum.Operands[1]);if(right!=null)return X86GraphRecovery.Op("Add",Low(sum.Operands[0]),right,32);}
        return null;
    }
    static FlowEffect[] Observable(FlowPath p)=>p.Effects.Where(e=>e.Kind is "memory_read" or "memory_store" or "external_call").ToArray();
    public static StructuredMemoryFunction Raise(JsonElement lift,IEnumerable<CalleeStackLift> callees)
    {
        var f=X86FlowRecovery.Raise(lift,new(Abi,true,true,PrivateSubwordStack:true,ObserveOutgoingPushRegion:true,MaximumOutgoingBytes:64,AliasableMemoryStores:true),callees);
        Need(f.ReturnCleanupBytes.Length==1&&f.ReturnCleanupBytes[0] is >0 and <=32&&f.ReturnCleanupBytes[0]%4==0&&f.NormalPaths.Length is >=2 and <=7&&!f.Incoming.AddressEscapeObserved,"structured_memory_thiscall_normal_paths_domain");
        Need(f.Incoming.RequiredReadBytes<=f.ReturnCleanupBytes[0]&&f.NormalPaths.All(p=>p.Effects.Where(e=>e.Kind=="incoming_read").All(e=>e.Value is IncomingStackRead{MemoryEpoch:0})) ,"structured_memory_precall_incoming_extent");
        Need(f.NormalPaths.SelectMany(p=>p.Effects).Where(e=>e.Kind=="incoming_read").Select(e=>(IncomingStackRead)e.Value!).All(v=>v.Bits is 8 or 32&&v.Offset>=4&&v.Offset%4==0),"structured_memory_incoming_byte_or_word_slots_only");
        Need(f.NormalPaths.Any(p=>p.Effects.Any(e=>e.Kind=="memory_store"))&&f.NormalPaths.Any(p=>p.Effects.Any(e=>e.Kind=="external_call")),"structured_memory_calls_and_stores_required");
        foreach(var path in f.NormalPaths){foreach(var call in path.Effects.Where(e=>e.Kind=="external_call").Select(e=>e.Call!))Need(call.CalleeCleanup==0&&call.CallerPrivateCleanupBytes==0&&call.CallerCleanup==call.Arguments.Length*4&&call.Arguments.Length is >0 and <=8,"structured_memory_cdecl_observed_words");Need(path.Effects.Where(e=>e.Kind=="memory_store").All(e=>e.Bits is 8 or 32),"structured_memory_store_width");}
        return new(f,["flat32 thiscall void and observed cdecl outgoing-word signatures are compiler hypotheses; zero callee cleanup never proves arity","external target, unknown result/effects/throw/termination retained; no allocator or container interpretation","ordered potentially aliased observations retained, stack POP/RET become fresh unknown memory reads after stores; no untouched-frame proof","structured forward paths share only identical ordered effects; complete original/native comparison required"]);
    }
    sealed record Path(FlowPredicate[] Predicates,FlowEffect[] Effects);
    public static string Emit(StructuredMemoryFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"unsupported_module_annotation");var f=ir.Flow;int arguments=f.ReturnCleanupBytes[0]/4;var allEffects=f.NormalPaths.SelectMany(Observable).ToArray();var reads=allEffects.Where(e=>e.Kind=="memory_read").DistinctBy(e=>((MemoryReadValue)e.Value!).Pc).ToArray();var calls=allEffects.Where(e=>e.Kind=="external_call").GroupBy(e=>e.Call!.Target).ToArray();
        string Value(RecoveredValue raw) {
            var v=Low(Normalize(raw));return v switch{
                Constant c when c.Value<=uint.MaxValue&&c.Bits is 8 or 16 or 32 or 64=>$"{c.Value}u",
                RegisterInput{Index:1}=>"reinterpret_cast<guest_address>(this)",
                IncomingStackRead input when input.Offset>=4&&input.Offset%4==0&&input.Offset/4-1<arguments&&input.MemoryEpoch==0=>$"arg_{input.Offset/4-1}",
                MemoryReadValue m when reads.Any(e=>Same(e.Value!,m))=>$"word_{m.Pc:x}",
                SegmentedAddress{Segment:{Index:3},Offset:var x}=>Value(x),
                AddValue a when a.Offset>=0=>$"({Value(a.Left)} + {a.Offset}u)",

                BitValue{Operation:var op,Operands.Length:2} b when op is "Add" or "Sub" or "And" or "Or" or "Xor" or "Eq" or "Ne" or "Ult"=>$"({Value(b.Operands[0])} {op switch{"Add"=>"+","Sub"=>"-","And"=>"&","Or"=>"|","Xor"=>"^","Eq"=>"==","Ne"=>"!=",_=>"<"}} {Value(b.Operands[1])})",
                _=>throw new ArgumentException("structured_memory_unemittable_value:"+v.GetType().Name)
            };
        }
        string Condition(RecoveredValue predicate,bool inverted) {
            if(predicate is BitValue{Operation:"Or",Operands.Length:2} flags&&flags.Operands[0] is Constant{Value:0}&&Normalize(flags.Operands[1]) is BitValue{Operation:"Eq",Operands.Length:2} zero&&zero.Operands[1] is Constant{Value:0})return $"({Value(zero.Operands[0])} {(inverted?">":"<=")} 0u)";
            return (inverted?"!":"")+Value(predicate);
        }
        var lines=new List<string>{"extern \"C\" void * __cdecl memcpy(void *, const void *, unsigned int);","#pragma intrinsic(memcpy)","typedef unsigned int guest_address;","static __forceinline unsigned int read_word(guest_address address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }","static __forceinline void write_word(guest_address address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }","static __forceinline void write_byte(void *base, unsigned int offset, unsigned char value) { guest_address address = reinterpret_cast<guest_address>(base) + offset; *reinterpret_cast<unsigned char *>(address) = value; }"};
        foreach(var c in calls){Need(c.Key>=imageBase&&c.Key<imageEnd&&c.Select(e=>e.Call!.Arguments.Length).Distinct().Count()==1,"structured_memory_external_signature_conflict");lines.Add($"extern \"C\" void __cdecl fn_{c.Key-imageBase:x8}({string.Join(", ",Enumerable.Repeat("unsigned int",c.First().Call!.Arguments.Length))});");}
        var inputWidths=f.NormalPaths.SelectMany(p=>p.Effects).Where(e=>e.Kind=="incoming_read").Select(e=>(IncomingStackRead)e.Value!).GroupBy(v=>v.Offset).ToDictionary(g=>g.Key,g=>g.Select(v=>v.Bits).Distinct().Single());
        string Parameters()=>string.Join(", ",Enumerable.Range(0,arguments).Select(i=>$"{(inputWidths.GetValueOrDefault(4+i*4,32)==8?"unsigned char":"unsigned int")} arg_{i}"));
        string type="Recovered";lines.Add($"struct {type} {{ void fn_{rva:x8}({Parameters()}); }};");lines.Add($"// FUNCTION: {module} 0x{imageBase+rva:x8}");lines.Add($"void {type}::fn_{rva:x8}({Parameters()}) {{");
        void Effect(FlowEffect effect,int depth){string indent=new(' ',depth*4);switch(effect.Kind){case "memory_read":Need(effect.Bits is 8 or 32,"structured_memory_read_width");Need(effect.Bits==32,"structured_memory_byte_memory_read_not_selected");lines.Add($"{indent}unsigned int word_{effect.Pc:x} = read_word({Value(effect.Address!)});");break;case "memory_store":
            if(effect.Bits==8){var offset=ReceiverOffset(effect.Address!);Need(offset!=null,"structured_memory_byte_store_receiver_index");lines.Add($"{indent}write_byte(this, {Value(offset!)}, {Value(effect.Value!)});");}
            else lines.Add($"{indent}write_word({Value(effect.Address!)}, {Value(effect.Value!)});");break;case "external_call":lines.Add($"{indent}fn_{effect.Call!.Target-imageBase:x8}({string.Join(", ",effect.Call.Arguments.Select(Value))});");break;default:throw new ArgumentException("structured_memory_effect");}}
        void Tree(Path[] paths,int depth){Need(paths.Length>0,"structured_memory_empty_tree");int prefix=0;while(paths.All(p=>p.Effects.Length>prefix)&&paths.All(p=>SameEffect(p.Effects[prefix],paths[0].Effects[prefix])))prefix++;
            // Do not move effects across their controlling branch. Effect PCs
            // encode original ordered instruction provenance, including reads.
            ulong firstPredicate=paths.Where(p=>p.Predicates.Length>0).Select(p=>p.Predicates[0].Pc).DefaultIfEmpty(ulong.MaxValue).Min();while(prefix>0&&paths[0].Effects[prefix-1].Pc>firstPredicate)prefix--;
            foreach(var e in paths[0].Effects.Take(prefix))Effect(e,depth);paths=paths.Select(p=>p with{Effects=p.Effects[prefix..]}).ToArray();
            if(paths.All(p=>p.Predicates.Length==0)){Need(paths.All(p=>p.Effects.Length==0),"structured_memory_unmerged_leaf_effects");return;}
            Need(paths.All(p=>p.Predicates.Length>0&&p.Predicates[0].Pc==firstPredicate&&Same(p.Predicates[0].Value,paths[0].Predicates[0].Value)),"structured_memory_incompatible_predicate_join");
            int suffix=0;while(paths.All(p=>p.Effects.Length>suffix)&&paths.All(p=>SameEffect(p.Effects[^(suffix+1)],paths[0].Effects[^(suffix+1)])))suffix++;
            var tail=paths[0].Effects.Skip(paths[0].Effects.Length-suffix).ToArray();var trimmed=paths.Select(p=>p with{Predicates=p.Predicates[1..],Effects=p.Effects[..(p.Effects.Length-suffix)]}).ToArray();var yes=trimmed.Where((p,i)=>paths[i].Predicates[0].Taken).ToArray();var no=trimmed.Where((p,i)=>!paths[i].Predicates[0].Taken).ToArray();Need(yes.Length>0&&no.Length>0,"structured_memory_missing_branch");bool emptyYes=yes.All(p=>p.Predicates.Length==0&&p.Effects.Length==0);bool emptyNo=no.All(p=>p.Predicates.Length==0&&p.Effects.Length==0);string pad=new(' ',depth*4);string condition=Condition(paths[0].Predicates[0].Value,emptyYes);
            if(!emptyYes||!emptyNo){lines.Add($"{pad}if ({condition}) {{");Tree(emptyYes?no:yes,depth+1);if(!emptyYes&&!emptyNo){lines.Add($"{pad}}} else {{");Tree(no,depth+1);}lines.Add(pad+"}");}foreach(var e in tail)Effect(e,depth);
        }
        Tree(f.NormalPaths.Select(p=>new Path(p.Predicates,Observable(p))).ToArray(),1);lines.Add("}");return string.Join("\n",lines)+"\n";
    }
}
