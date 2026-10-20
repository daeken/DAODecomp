using System.Text.Json;
namespace Decompilation;

public sealed record ByValueCarrier(int ArgumentIndex,RecoveredValue ByteValue,RecoveredValue PreservedUpperBits,string Basis);
public sealed record ByValueCallFunction(FlowFunction Function,FlowCall Call,ulong CallPc,ByValueCarrier[] Carriers,string[] Hypotheses);

// The shared flow retains exact word bits. Aggregate/padding spelling is a VC8
// candidate only; unspecified padding is never interpreted as zero or a fact.
public static class Vc8ByValueCallsProfile
{
    public const string Version="vc8-x86-flat32-observed-byvalue-calls-v1";
    public static RecoveryAbi Abi=>new(Version,0,[],[0,1,2],[3,5,6,7]);
    static void Need(bool value,string why){if(!value)throw new ArgumentException(why);}
    static RecoveredValue U(RecoveredValue value)=>value is BitValue{Operation:"Trunc",Bits:32,Operands.Length:1} t&&t.Operands[0] is BitValue{Operation:"Zext",Bits:64,Operands.Length:1} z&&z.Operands[0] is IncomingStackRead{Bits:32} or BitValue{Bits:32} or Constant{Bits:32}?U(z.Operands[0]):value;
    static bool Same(RecoveredValue a,RecoveredValue b)=>JsonSerializer.Serialize<RecoveredValue>(U(a))==JsonSerializer.Serialize<RecoveredValue>(U(b));
    public static ByValueCallFunction Raise(JsonElement lift,IEnumerable<CalleeStackLift> callees)
    {
        var f=X86FlowRecovery.Raise(lift,new(Abi,true,true,PrivateSubwordStack:true,ObserveOutgoingPushRegion:true,MaximumOutgoingBytes:64),callees);
        Need(f.NormalPaths.Length==1&&f.NormalPaths[0].Predicates.Length==0&&f.ReturnCleanupBytes.SequenceEqual([0])&&!f.Incoming.AddressEscapeObserved,"byvalue_single_normal_C3_path_required");
        var path=f.NormalPaths[0];var calls=path.Effects.Where(e=>e.Kind=="external_call").ToArray();Need(calls.Length==1,"byvalue_one_external_call_required");var effect=calls.Single();var call=effect.Call!;
        Need(call.CalleeCleanup==0&&call.Arguments.Length is >0 and <=12&&call.CallerCleanup==call.Arguments.Length*4+call.CallerPrivateCleanupBytes,"byvalue_observed_cdecl_cleanup_required");
        Need(path.Exit.Return==new ExternalRegisterValue(effect.Pc,Abi.ReturnRegister,32),"byvalue_return_original_external_result_required");
        Need(path.Effects.All(e=>e.Kind is "register_write" or "flag_write" or "stack_store" or "stack_read" or "incoming_read" or "external_call"),"byvalue_extra_memory_effect");
        Need(path.Effects.Where(e=>e.Kind=="incoming_read").All(e=>e.Pc<effect.Pc&&e.Value is IncomingStackRead{Bits:32,MemoryEpoch:0}),"byvalue_only_precall_word_inputs");
        Need(f.Incoming.RequiredReadBytes is >0 and <=48&&f.Incoming.RequiredReadBytes%4==0,"byvalue_incoming_extent_budget");
        var carriers=new List<ByValueCarrier>();
        for(int i=0;i<call.Arguments.Length;i++) {
            var value=U(call.Arguments[i]);
            if(value is BitValue{Operation:"Or",Bits:32,Operands.Length:2} merged&&merged.Operands[0] is BitValue{Operation:"And",Bits:32,Operands.Length:2} upper&&upper.Operands[0] is RegisterInput original&&Abi.VolatileRegisters.Contains(original.Index)&&upper.Operands[1]==new Constant(0xffffff00,32)&&merged.Operands[1] is BitValue{Operation:"Zext",Bits:32,Operands.Length:1} low) {
                Need(path.Effects.Any(e=>e.Kind=="stack_store"&&e.Bits==8&&e.Pc<effect.Pc&&e.Value!=null&&Same(e.Value,low.Operands[0]))&&path.Effects.Any(e=>e.Kind=="stack_read"&&e.Bits==32&&e.Pc<effect.Pc&&e.Value!=null&&Same(e.Value,value)),"byvalue_missing_partial_object_copy_provenance");
                carriers.Add(new(i,low.Operands[0],upper,"allocated initialized private word, explicit low-byte store and complete observed word copy; upper bits retained in IR, source aggregate padding unspecified"));
            }
        }
        Need(carriers.Count is >0 and <=4&&call.CallerPrivateCleanupBytes==carriers.Count*4,"byvalue_private_object_cleanup_required");
        foreach(var arg in call.Arguments.Select((value,index)=>(value,index)))if(!carriers.Any(c=>c.ArgumentIndex==arg.index))Need(U(arg.value) is IncomingStackRead{Bits:32,MemoryEpoch:0} or Constant{Bits:32},"byvalue_unemittable_argument");
        return new(f,call,effect.Pc,carriers.ToArray(),["flat32 cdecl normal-return candidate ABI; cleanup does not determine formal arity","complete observed outgoing push region and private cleanup kept separate","external result, memory effects, throw behavior and termination remain unknown","VC8 aggregate padding is a compiler spelling hypothesis, never initialized to zero or treated as known; complete native comparison required"]);
    }
    public static string Emit(ByValueCallFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"unsupported_module_annotation");
        var call=ir.Call;Need(call.Target>=imageBase&&call.Target<imageEnd,"byvalue_external_target_outside_module");
        string Value(RecoveredValue value)=>U(value) switch {
            IncomingStackRead{Bits:32,MemoryEpoch:0} incoming when incoming.Offset>=4&&incoming.Offset%4==0&&incoming.Offset-4<ir.Function.Incoming.RequiredReadBytes=>$"arg_{(incoming.Offset-4)/4}",
            Constant{Bits:8 or 32} c=>$"{c.Value}u",
            _=>throw new ArgumentException("byvalue_unemittable_value")
        };
        var decl=new List<string>();var statements=new List<string>();var args=new List<string>();var types=new List<string>();
        for(int i=0;i<call.Arguments.Length;i++) {
            var carrier=ir.Carriers.SingleOrDefault(c=>c.ArgumentIndex==i);
            if(carrier!=null){string type=$"ByteCarrier_{i}";decl.Add($"struct {type} {{ unsigned char value; }};");types.Add(type);statements.Add($"    {type} local_{i};\n    local_{i}.value = {Value(carrier.ByteValue)};");args.Add($"local_{i}");}
            else {types.Add("unsigned int");args.Add(Value(call.Arguments[i]));}
        }
        var repeatedReads=ir.Function.NormalPaths[0].Effects.Where(e=>e.Kind=="incoming_read").Select(e=>(IncomingStackRead)e.Value!).GroupBy(v=>v.Offset).Where(g=>g.Select(v=>v.Pc).Distinct().Count()>1).Select(g=>g.Key).ToHashSet();
        string target=$"fn_{call.Target-imageBase:x8}";decl.Add($"extern \"C\" unsigned int __cdecl {target}({string.Join(", ",types)});");string parameters=string.Join(", ",Enumerable.Range(0,ir.Function.Incoming.RequiredReadBytes/4).Select(i=>$"{(repeatedReads.Contains(4+i*4)?"volatile ":"")}unsigned int arg_{i}"));
        return string.Join("\n",decl)+$"\n// FUNCTION: {module} 0x{imageBase+rva:x8}\nextern \"C\" unsigned int __cdecl fn_{rva:x8}({parameters}) {{\n"+string.Join("\n",statements)+$"\n    return {target}({string.Join(", ",args)});\n}}\n";
    }
}
