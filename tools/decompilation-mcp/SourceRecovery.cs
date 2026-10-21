using System.Text.Json;
namespace Decompilation;

public sealed record SourceProfileAttempt(string Profile,string Status,string? Blocker);
public sealed record SourceRecovery(object Ir,string Source,SourceProfileAttempt[] Attempts);
public sealed class SourceRecoveryRefusal(string message,SourceProfileAttempt[] attempts):ArgumentException(message) { public SourceProfileAttempt[] Attempts {get;}=attempts; }

public sealed partial class Engine
{
    // This only selects an evidence-free dependency input. Every recovery and
    // emission guard below remains the existing ordinary source pipeline.
    public static bool IsCompleteCallFree(JsonElement lift)=>CallFreeBoundary(lift)==null;
    public static string? CallFreeBoundary(JsonElement lift)
    {
        try { return CheckedCallFreeBoundary(lift); }
        catch(Exception e) when(e is KeyNotFoundException or InvalidOperationException or FormatException or OverflowException) { return "analysis_control_metadata_unavailable"; }
    }
    static string? CheckedCallFreeBoundary(JsonElement lift)
    {
        if(lift.GetProperty("schema").GetString()!="sharpretro_instruction_lift_v1"||!lift.GetProperty("decode_complete").GetBoolean()||lift.GetProperty("lift_errors").GetInt32()!=0||lift.GetProperty("opaque_instructions").GetInt32()!=0)return "profile_not_implemented_or_incomplete";
        string? boundary=null;
        var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();var pcs=rows.Select(r=>r.GetProperty("pc").GetUInt64()).ToHashSet();
        bool Safe(JsonElement node) {
            if(node.ValueKind==JsonValueKind.Array)return node.EnumerateArray().All(Safe);
            if(node.ValueKind!=JsonValueKind.Object)return true;
            if(node.TryGetProperty("type",out var type)&&type.GetString()=="LiftIl.IlBranch") {
                var kind=node.GetProperty("Kind").GetProperty("name").GetString();
                if(kind=="Ret")return true;
                if(kind is not ("Jmp" or "CondJmp")){boundary=kind=="Call"?"dependency_uninspected":"unsupported_control_kind";return false;}
                var target=node.GetProperty("Target");
                if(!target.TryGetProperty("type",out var tag)||tag.GetString()!="LiftIl.IlConst"||!ulong.TryParse(target.GetProperty("Bits").GetProperty("decimal").GetString(),out var pc)||!pcs.Contains(pc)){boundary="control_target_uninspected";return false;}
            }
            return node.EnumerateObject().All(p=>Safe(p.Value));
        }
        return rows.Length>0&&rows.All(r=>!r.GetProperty("opaque_markers").EnumerateArray().Any()&&r.GetProperty("lift_error").ValueKind==JsonValueKind.Null&&Safe(r.GetProperty("tree")))?null:boundary??"incomplete_typed_analysis";
    }
    internal static JsonElement EmptyDependencies(JsonElement lifted)=>JsonSerializer.SerializeToElement(new{caller_slice_sha256=lifted.GetProperty("binary_slice_sha256").GetString(),callees=Array.Empty<object>(),runtime_terminal_evidence=(object?)null},Options);
    public static async Task<SourceRecovery> RecoverLinearSource(JsonElement request,JsonElement lifted,string module,Func<Task<JsonElement>> getDependencies,Func<Task<JsonElement>> getEh,Action<object>? observeIr=null,Action<SourceProfileAttempt[]>? observeAttempts=null)
    {
        var attempts=new List<SourceProfileAttempt>();string active="linear";
        void Refused(ArgumentException e){attempts.Add(new(active,"unsupported",e.Message));observeAttempts?.Invoke(attempts.ToArray());}
        try {
            var recipe=request.GetProperty("recipe").Deserialize<PipelineRecipe>(Options)!;recipe.Validate();
            var rva=request.GetProperty("rva").GetUInt32();var imageBase=lifted.GetProperty("image_base").GetUInt32();var imageEnd=lifted.GetProperty("image_end").GetUInt32();object ir;string source;
            try {var basic=X86Recovery.Raise(lifted.GetProperty("lift"),Vc8Profile.Abi);source=Vc8Profile.Emit(basic,rva,imageBase,imageEnd,module);ir=basic;}
            catch(ArgumentException failed1) when(recipe.UsesStackArguments) {
                Refused(failed1);active="leaf_or_stack_arguments";
                var dependencies=await getDependencies();if(dependencies.TryGetProperty("error",out var dependencyError))throw new ArgumentException(dependencyError.GetString());
                if(dependencies.GetProperty("caller_slice_sha256").GetString()!=lifted.GetProperty("binary_slice_sha256").GetString())throw new ArgumentException("callee_caller_binding_changed");
                var callees=dependencies.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();
                try {if(Vc8LeafReturnProfile.TryRaise(lifted.GetProperty("lift"),out var leaf)){ir=leaf!;source=Vc8LeafReturnProfile.Emit(leaf!,rva,imageBase,module);}else{var stackIr=Vc8StackArgsProfile.Raise(lifted.GetProperty("lift"),callees);source=Vc8StackArgsProfile.Emit(stackIr,rva,imageBase,imageEnd,module);ir=stackIr;}}
                catch(ArgumentException failed2) when(recipe.UsesConditionalCalls) {
                    Refused(failed2);active="conditional_calls";
                    try {var conditional=recipe.UsesCallAdapters?Vc8CallAdaptersProfile.Raise(lifted.GetProperty("lift"),callees):Vc8ConditionalCallsProfile.Raise(lifted.GetProperty("lift"),callees);source=Vc8ConditionalCallsProfile.Emit(conditional,rva,imageBase,imageEnd,module);ir=conditional;}
                    catch(ArgumentException failed3) when((recipe.UsesEh&&Vc8EhProfile.MayHaveFrame(lifted.GetProperty("lift")))||recipe.UsesByValueCalls) {
                        Refused(failed3);active="eh_or_byvalue";
                        if(recipe.UsesEh&&Vc8EhProfile.MayHaveFrame(lifted.GetProperty("lift"))) {
                        var evidence=await getEh();if(evidence.TryGetProperty("error",out var ehError))throw new ArgumentException(ehError.GetString());
                        if(evidence.GetProperty("caller_slice_sha256").GetString()!=lifted.GetProperty("binary_slice_sha256").GetString())throw new ArgumentException("EH_caller_binding_changed");
                        var recovered=Vc8EhProfile.Raise(lifted.GetProperty("lift"),callees,evidence);ir=recovered;observeIr?.Invoke(ir);source=Vc8EhProfile.Emit(recovered,rva,imageBase,imageEnd,module);
                        } else {
                            try {var recovered=Vc8ByValueCallsProfile.Raise(lifted.GetProperty("lift"),callees);ir=recovered;source=Vc8ByValueCallsProfile.Emit(recovered,rva,imageBase,imageEnd,module);}
                            catch(ArgumentException failed4) when(recipe.UsesCountedLoops) {
                                Refused(failed4);active="counted_loops";
                                try {var recovered=Vc8LoopsProfile.Raise(lifted.GetProperty("lift"));ir=recovered;source=Vc8LoopsProfile.Emit(recovered,rva,imageBase,module);}
                                catch(ArgumentException failed5) when(recipe.UsesOrderedMemory) {
                                    Refused(failed5);active="ordered_memory";
                                    StructuredMemoryFunction recovered;
                                    try {recovered=Vc8StructuredMemoryProfile.Raise(lifted.GetProperty("lift"),callees);}
                                    catch(ArgumentException failed6) when(recipe.UsesTerminalMemory) {Refused(failed6);active="terminal_ordered_memory";recovered=Vc8StructuredMemoryProfile.Raise(lifted.GetProperty("lift"),callees,dependencies.GetProperty("runtime_terminal_evidence").Deserialize<RuntimeTerminalEvidence>(Options));}
                                    ir=recovered;source=Vc8StructuredMemoryProfile.Emit(recovered,rva,imageBase,imageEnd,module,lifted.GetProperty("lift"),recipe.UsesTypedReceiver,recipe.UsesScalarSource,recipe.UsesIncomingSlotValues);
                                }
                            }
                        }
                    }
                }
            }
        attempts.Add(new(active,"generated",null));observeAttempts?.Invoke(attempts.ToArray());
        return new(ir,source,attempts.ToArray());
        } catch(ArgumentException e){Refused(e);throw new SourceRecoveryRefusal(e.Message,attempts.ToArray());}
    }
}
