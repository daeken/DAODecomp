using System.Text.Json;
namespace Decompilation;

public sealed record ReceiverReturnRelation(ulong Target,string Basis,bool EffectsUnknown=true,bool ThrowBehaviorUnknown=true,bool TerminationUnknown=true);
public sealed record EhSourcePlan(ulong AllocationTarget,ulong ReceiverCallTarget,ulong CleanupForwarder,ulong CleanupTerminal,ulong GlobalTarget,int AllocationBytes,ulong HandlerTarget,ulong CookieTarget);
public sealed record EhSavedFrameReload(ulong SavePc,ulong RegistrationPc,ulong ReloadPc,ulong RestorationPc,long EntryStackOffset,int WidthBits,RecoveredValue SavedEntryValue,RecoveredValue CurrentValue,ulong[] InterveningCalls,ulong[] InterveningMemoryWrites,bool RestoredEntryValueProven=false,bool FrameDisjointnessProven=false);
public sealed record Vc8EhFunction(FlowFunction Function,JsonElement OriginalEhEvidence,ReceiverReturnRelation ReceiverReturn,EhSourcePlan Plan,string[] Hypotheses,EhSavedFrameReload[]? SavedFrameReloads=null);

// Compiler-specific interpretation; architecture recovery above retains FS,
// cookie/state words, call results, every ordered store and both normal exits.
public static class Vc8EhProfile
{
    public const string Version="vc8-x86-flat32-EH-two-exit-v1";
    public static RecoveryAbi Abi=>new(Version,0,[1],[0,1,2],[3,5,6,7]);
    // Necessary marker only; the original rooted EH graph is still independently derived.
    public static bool MayHaveFrame(JsonElement lift)
    {
        bool Has(JsonElement n) {
            if(n.ValueKind==JsonValueKind.Object) {
                if(n.TryGetProperty("type",out var t)&&t.GetString()!.EndsWith("IlReadReg")&&n.GetProperty("Kind").GetProperty("name").GetString()=="X86Seg"&&n.GetProperty("Idx").GetInt32()==4)return true;
                return n.EnumerateObject().Any(p=>Has(p.Value));
            }
            return n.ValueKind==JsonValueKind.Array&&n.EnumerateArray().Any(Has);
        }
        return Has(lift.GetProperty("instructions"));
    }

    static void Need(bool b,string why){if(!b)throw new ArgumentException(why);}
    static bool Same(RecoveredValue a,RecoveredValue b)=>JsonSerializer.Serialize<RecoveredValue>(a)==JsonSerializer.Serialize<RecoveredValue>(b);
    static RecoveredValue U(RecoveredValue v){while(v is BitValue{Operands.Length:1} b&&b.Operation is "Trunc" or "Zext")v=b.Operands[0];return v;}
    static RecoveredValue CompleteWord(RecoveredValue v){while(v is BitValue{Operands.Length:1} b&&b.Operation is "Trunc" or "Zext"){Need(b.Bits is 32 or 64,"EH_saved_FS_word_width_required");v=b.Operands[0];}return v;}
    static long? Slot(RecoveredValue? v)=>v switch{SegmentedAddress{Segment:{Index:2},Offset:AddValue{Left:RegisterInput{Index:4}} a}=>a.Offset,AddValue{Left:RegisterInput{Index:4}} a=>a.Offset,_=>null};
    static bool Address(RecoveredValue? v,int segment,ulong offset)=>v is SegmentedAddress a&&a.Segment.Index==segment&&U(a.Offset)==new Constant(offset,64);
    static ulong Global(RecoveredValue? v){Need(v is SegmentedAddress{Segment:{Index:3},Offset:Constant},"EH_global_address_required");return ((Constant)((SegmentedAddress)v!).Offset).Value;}
    static bool EqZero(RecoveredValue condition,ExternalRegisterValue result)
    {
        condition=U(condition);if(condition is not BitValue{Operation:"Eq",Operands.Length:2} b||U(b.Operands[1]) is not Constant{Value:0})return false;
        var x=U(b.Operands[0]);return Same(x,result)||(x is BitValue{Operation:"And",Operands.Length:2} a&&Same(U(a.Operands[0]),result)&&Same(U(a.Operands[1]),result));
    }
    public static Vc8EhFunction Raise(JsonElement lift,IEnumerable<CalleeStackLift> supplied,JsonElement evidence)
    {
        var callees=supplied.ToArray();var f=X86FlowRecovery.Raise(lift,new(Abi,true,true,[new SegmentedAddress(new SegmentInput(4),new Constant(0,64))],evidence.GetProperty("image_base").GetUInt64(),evidence.GetProperty("image_end").GetUInt64()),callees);
        Need(f.NormalPaths.Length==2&&f.ReturnCleanupBytes.SequenceEqual([0])&&f.Incoming.RequiredReadBytes==0,"EH_two_C3_paths_without_observed_incoming_reads_required");
        var yes=f.NormalPaths.SingleOrDefault(p=>p.Predicates.Length==1&&p.Predicates[0].Taken);var no=f.NormalPaths.SingleOrDefault(p=>p.Predicates.Length==1&&!p.Predicates[0].Taken);Need(yes!=null&&no!=null&&yes.Predicates[0].Pc==no.Predicates[0].Pc&&Same(yes.Predicates[0].Value,no.Predicates[0].Value),"EH_single_two_terminal_branch_required");
        var taken=yes!;var body=no!;var calls=body.Effects.Where(e=>e.Kind=="external_call").Select(e=>(e.Pc,e.Call!)).ToArray();Need(calls.Length==2&&taken.Effects.Count(e=>e.Kind=="external_call")==1,"EH_external_call_roles");
        var alloc=calls[0];var construct=calls[1];Need(alloc.Item2.Arguments.Length==1&&alloc.Item2.Arguments[0] is Constant{Bits:32,Value:>=4 and <=4096} size&&size.Value%4==0&&alloc.Item2.CalleeCleanup==0&&alloc.Item2.CallerCleanup==4,"EH_observed_word_request_with_caller_cleanup");int bytes=(int)((Constant)alloc.Item2.Arguments[0]).Value;
        var firstResult=new ExternalRegisterValue(alloc.Pc,Abi.ReturnRegister,32);var secondResult=new ExternalRegisterValue(construct.Pc,Abi.ReturnRegister,32);
        Need(EqZero(taken.Predicates[0].Value,firstResult)&&Same(construct.Item2.Receiver,firstResult)&&construct.Item2.Arguments.Length==0&&construct.Item2.CalleeCleanup==0&&construct.Item2.CallerCleanup==0,"EH_result_guard_or_receiver_call");
        Need(Same(body.Exit.Return,secondResult)&&U(taken.Exit.Return) is Constant{Value:0},"EH_path_specific_result_required");
        // A source constructor ABI is only a candidate spelling after a complete
        // original normal-path dataflow establishes the receiver-return relation.
        var callee=callees.Single(c=>c.Target==construct.Item2.Target);var rr=X86Recovery.Raise(callee.Lift,Abi);Need(rr.ExitKind=="return"&&rr.Return==new RegisterInput(1),"EH_missing_original_receiver_return_relation");
        var graph=evidence.GetProperty("graph");var h=graph.GetProperty("handler");ulong handler=h.GetProperty("va").GetUInt64(),cookie=evidence.GetProperty("security_cookie_va").GetUInt64();
        Need(h.GetProperty("profile").GetProperty("cookie_checked").GetBoolean()&&graph.GetProperty("FuncInfo").GetProperty("fields").GetProperty("states").GetInt32()==1&&graph.GetProperty("action").GetProperty("profile").GetProperty("kind").GetString()=="load_word_push_call_pop_ret"&&graph.GetProperty("action").GetProperty("profile").GetProperty("parent_ebp_offset").GetInt32()==-16,"EH_supported_complete_runtime_frame_required");
        var initialSaves=body.Effects.Where(e=>e.Kind=="stack_store"&&Slot(e.Address)==-12).ToArray();Need(initialSaves.Length==1&&initialSaves[0].Bits==32,"EH_unique_saved_FS_word_required");
        var initialFs=CompleteWord(initialSaves[0].Value!);Need(initialFs is MemoryReadValue fs&&Address(fs.Address,4,0)&&fs.Bits==32,"EH_saved_FS_registration_required");
        var reloads=new List<EhSavedFrameReload>();
        foreach(var path in f.NormalPaths) {
            var reads=path.Effects.Where(e=>e.Kind=="memory_read").ToArray();Need(reads.Length==2&&reads.All(e=>e.Bits==32)&&Address(reads[0].Address,4,0)&&Address(reads[1].Address,3,cookie),"EH_unmodeled_external_read");
            var memory=path.Effects.Where(e=>e.Kind=="memory_store").ToArray();Need(memory.Length==3&&memory.All(e=>e.Bits==32),"EH_extra_or_partial_memory_effect");
            // A compiler-frame role is location provenance, not an equality proof
            // after opaque calls. Keep the fresh unknown load in architectural IR.
            Need(Address(memory[0].Address,4,0)&&memory[0].Value==new AddValue(new RegisterInput(4),-12)&&Address(memory[2].Address,4,0),"EH_registration_and_restoration_locations_required");
            var saves=path.Effects.Where(e=>e.Kind=="stack_store"&&Slot(e.Address)==-12).ToArray();
            var savedReads=path.Effects.Where(e=>e.Kind=="stack_read"&&Slot(e.Address)==-12).ToArray();
            Need(saves.Length==1&&saves[0].Bits==32&&Same(CompleteWord(saves[0].Value!),initialFs),"EH_unique_saved_FS_word_required");
            Need(savedReads.Length==1&&savedReads[0].Bits==32&&CompleteWord(savedReads[0].Value!) is MemoryReadValue{Bits:32},"EH_saved_FS_reload_required");
            var reload=savedReads[0];var current=(MemoryReadValue)CompleteWord(reload.Value!);
            Need(current.Pc==reload.Pc&&Slot(current.Address)==-12&&Same(current.Address,reload.Address!)&&Same(CompleteWord(memory[2].Value!),current)&&current.Epoch>((MemoryReadValue)initialFs).Epoch,"EH_saved_FS_current_reload_required");
            int Position(FlowEffect effect)=>Array.IndexOf(path.Effects,effect);
            var callEffects=path.Effects.Where(e=>e.Kind=="external_call").ToArray();
            Need(Position(reads[0])<Position(saves[0])&&Position(saves[0])<Position(memory[0])&&callEffects.All(e=>Position(memory[0])<Position(e)&&Position(e)<Position(memory[1]))&&Position(memory[1])<Position(reload)&&Position(reload)<Position(memory[2]),"EH_saved_FS_effect_order_required");
            reloads.Add(new(saves[0].Pc,memory[0].Pc,reload.Pc,memory[2].Pc,-12,32,initialFs,current,callEffects.Select(e=>e.Pc).ToArray(),[memory[1].Pc]));
            Need(Global(memory[1].Address)==Global(body.Effects.Single(e=>e.Kind=="memory_store"&&!Address(e.Address,4,0)).Address)&&Same(U(memory[1].Value!),U(path.Exit.Return)),"EH_ordered_global_result_store_required");
            var stores=path.Effects.Where(e=>e.Kind=="stack_store").ToArray();var expected=new long[]{-4,-8,-12,-16,-20,-24,-28,-16,-4}.Concat(path==body?new long[]{-24}:Array.Empty<long>()).ToArray();Need(stores.Select(e=>Slot(e.Address)).SequenceEqual(expected.Select(x=>(long?)x)),"EH_unmodeled_frame_word_effect");
            Need(U(stores[0].Value!)==new Constant(uint.MaxValue,32)&&U(stores[1].Value!)==new Constant(handler,32)&&Same(U(stores[2].Value!),initialFs)&&U(stores[3].Value!)==new RegisterInput(1),"EH_entry_frame_roles");
            var cv=U(stores[4].Value!);Need(cv is BitValue{Operation:"Xor",Operands.Length:2} xor&&U(xor.Operands[0]) is MemoryReadValue cr&&Address(cr.Address,3,cookie)&&cr.Bits==32&&U(xor.Operands[1])==new AddValue(new RegisterInput(4),-16),"EH_PE_cookie_frame_value_required");
            Need(U(stores[5].Value!)==new Constant((ulong)bytes,32)&&Same(U(stores[7].Value!),firstResult)&&U(stores[8].Value!)==new Constant(0,32)&&stores[8].Pc<path.Predicates[0].Pc,"EH_call_slot_and_state_transition_required");
        }
        var dependencies=evidence.GetProperty("code_dependencies").EnumerateArray().ToArray();Need(dependencies.Length==3&&dependencies.Select(d=>d.GetProperty("role").GetString()).Order().SequenceEqual(new[]{"action","cleanup_forwarder","handler"}),"EH_complete_typed_dependencies_required");
        foreach(var dep in dependencies) {var l=dep.GetProperty("lift");int length=dep.GetProperty("size").GetInt32();Need(l.GetProperty("mode").GetString()=="Bits32"&&l.GetProperty("decode_complete").GetBoolean()&&l.GetProperty("lift_errors").GetInt32()==0&&l.GetProperty("opaque_instructions").GetInt32()==0&&l.GetProperty("decoded_bytes").GetInt32()==length,"EH_incomplete_typed_dependency");
            var code=l.GetProperty("instructions").EnumerateArray().ToArray();ulong start=dep.GetProperty("va").GetUInt64();Need(code.Length>0&&code[0].GetProperty("pc").GetUInt64()==start&&code.Sum(r=>r.GetProperty("length").GetInt32())==length&&code.All(r=>r.GetProperty("length").GetInt32() is >0 and <=15),"EH_dependency_range_binding");var dependencyBytes=Convert.FromHexString(string.Concat(code.Select(r=>r.GetProperty("raw_hex").GetString())));Need(Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(dependencyBytes))==dep.GetProperty("slice_sha256").GetString(),"EH_dependency_slice_binding");
            string role=dep.GetProperty("role").GetString()!;if(role=="cleanup_forwarder")Need(start==evidence.GetProperty("cleanup_forwarder_va").GetUInt64()&&NormalReturnResolver.PureForwardTarget(start,l)==evidence.GetProperty("cleanup_terminal_va").GetUInt64(),"EH_cleanup_forwarder_binding");else {var originalNode=graph.GetProperty(role);Need(start==originalNode.GetProperty("va").GetUInt64()&&Convert.ToHexString(dependencyBytes).ToLowerInvariant()==originalNode.GetProperty("bytes_hex").GetString(),"EH_code_graph_binding");}
        }
        ulong global=Global(body.Effects.Single(e=>e.Kind=="memory_store"&&!Address(e.Address,4,0)).Address);
        var plan=new EhSourcePlan(alloc.Item2.Target,construct.Item2.Target,evidence.GetProperty("cleanup_forwarder_va").GetUInt64(),evidence.GetProperty("cleanup_terminal_va").GetUInt64(),global,bytes,handler,cookie);
        return new(f,evidence.Clone(),new(construct.Item2.Target,"complete original typed callee normal-return dataflow under selected preserved-register ABI; not constructor semantics proof"),plan,["cdecl pointer-result source ABI is a candidate spelling; C3 does not establish arity; only required directly observed incoming extent is zero","class-specific new/cleanup and nominal layout are compiler-lowering hypotheses from the original request, state/unwind graph and normal-return receiver relation; external semantics are not invented","module-data and FS stores retain the existing profile address classification; it proves no caller-frame disjointness, and opaque calls invalidate caller-memory contents","FS registration/restoration, cookie, state, helper/table bytes and relocation dependencies remain explicit and require complete native main/EH graph comparison","both path-specific call results/global stores/returns remain in architectural IR; unknown calls may throw or not return","saved-FS source role binds one complete saved word and its ordered post-call reload on every normal path; current contents stay unknown, entry-value equality and arbitrary frame disjointness are not proved"],reloads.ToArray());
    }
    public static string Emit(Vc8EhFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        Need((ir.Function.FaultPaths??[]).Length==0,"EH_architectural_fault_lowering_unsupported");
        uint R(ulong va){Need(va>=imageBase&&va<imageEnd,"EH_entity_outside_image");return (uint)(va-imageBase);}var p=ir.Plan;string cls=$"fn_{R(p.ReceiverCallTarget):x8}",own=$"fn_{rva:x8}",alloc=$"fn_{R(p.AllocationTarget):x8}",cleanup=$"fn_{R(p.CleanupTerminal):x8}",global=$"g_{R(p.GlobalTarget):x8}";Need(module.Length>0&&!module.Any(char.IsWhiteSpace)&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"EH_module_name");
        var tail=p.AllocationBytes>4?$"  unsigned char opaque_tail[{p.AllocationBytes-4}];":"";
        return $$"""
// FUNCTION: {{module}} 0x{{imageBase+rva:x8}}
extern "C" void* __cdecl {{alloc}}(unsigned int);
extern "C" void __cdecl {{cleanup}}(void*);
struct {{cls}} {
  unsigned int opaque_word;
{{tail}}
  {{cls}}();
  __forceinline static void* operator new(unsigned int n) { return {{alloc}}(n); }
  __forceinline static void operator delete(void* p) { {{cleanup}}(p); }
};
typedef char layout_{{rva:x8}}[(sizeof({{cls}})=={{p.AllocationBytes}})?1:-1];
extern {{cls}}* {{global}};
{{cls}}* __cdecl {{own}}() { return {{global}} = new {{cls}}; }

""";

    }
}
