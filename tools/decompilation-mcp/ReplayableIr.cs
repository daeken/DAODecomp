using System.Text.Json;
using System.Text.Json.Serialization;
namespace Decompilation;

// Architecture-only symbolic expressions. No compiler spelling occurs here.
[JsonPolymorphic(TypeDiscriminatorPropertyName="kind")]
[JsonDerivedType(typeof(Constant),"constant")]
[JsonDerivedType(typeof(RegisterInput),"register_input")]
[JsonDerivedType(typeof(AddValue),"add")]
[JsonDerivedType(typeof(UnknownValue),"unknown")]
[JsonDerivedType(typeof(SegmentInput),"segment_input")]
[JsonDerivedType(typeof(SegmentedAddress),"segmented_address")]
[JsonDerivedType(typeof(IncomingStackInput),"incoming_stack_input")]
[JsonDerivedType(typeof(IncomingStackAddress),"incoming_stack_address")]
[JsonDerivedType(typeof(BitValue),"bit_operation")]
[JsonDerivedType(typeof(IncomingStackRead),"incoming_stack_read")]
[JsonDerivedType(typeof(MemoryReadValue),"memory_read")]
[JsonDerivedType(typeof(ExternalRegisterValue),"external_register")]
[JsonDerivedType(typeof(BlockRegisterValue),"block_register")]
[JsonDerivedType(typeof(BlockFlagValue),"block_flag")]
[JsonDerivedType(typeof(WrappedStackAddress),"wrapped_stack_address")]
public abstract record RecoveredValue;
public sealed record BlockRegisterValue(ulong Block,int Register):RecoveredValue;
public sealed record BlockFlagValue(ulong Block,int Flag):RecoveredValue;
public sealed record WrappedStackAddress(long Offset,int Bits=32):RecoveredValue;
public sealed record Constant(ulong Value, int Bits) : RecoveredValue;
public sealed record RegisterInput(int Index) : RecoveredValue;
public sealed record AddValue(RecoveredValue Left, long Offset) : RecoveredValue;
public sealed record UnknownValue(string Reason) : RecoveredValue;
public sealed record SegmentInput(int Index) : RecoveredValue;
public sealed record SegmentedAddress(SegmentInput Segment, RecoveredValue Offset) : RecoveredValue;
public sealed record RecoveredEffect(string Kind, RecoveredValue? Address, RecoveredValue? Value, int Bits, ulong Pc, RecoveredValue[]? Inputs=null);
public sealed record RecoveryAbi(string Id,int ReturnRegister,int[] ArgumentRegisters,int[] VolatileRegisters,int[] PreservedRegisters);
public sealed record RecoveredStackEffect(RecoveredValue Address,RecoveredValue Value,int Bits,ulong Pc,bool WithinAllocatedFrame);
public sealed record RecoveredFunction(List<RecoveredEffect> Effects, RecoveredValue Return, List<string> Hypotheses,List<RecoveredStackEffect> StackEffects,string ExitKind="return",bool BareNearReturn=false);
public sealed record IncomingStackInput(int Offset,int Bits) : RecoveredValue;
public sealed record IncomingStackAddress(int Offset,int Bits) : RecoveredValue;
public sealed record MemoryReadValue(RecoveredValue Address,int Bits,ulong Pc,int Epoch,int ReadOrdinal=0):RecoveredValue;
public sealed record ExternalRegisterValue(ulong CallPc,int Register,int Bits):RecoveredValue;
public sealed record BitValue(string Operation,RecoveredValue[] Operands,int Bits) : RecoveredValue;
public sealed record IncomingStackRead(int Offset,int Bits,ulong Pc,int MemoryEpoch) : RecoveredValue;
public sealed record CalleeStackLift(ulong Target,JsonElement Lift);
public sealed record NormalReturnStackEvidence(ulong Target,int CleanupBytes,int ReturnSites,int CallSites,string Basis,bool Proof=false,ArchitecturalFaultSite[]? ArchitecturalFaults=null,ulong[]? ExceptionalCallSites=null,RuntimeTerminalEvidence? TerminalRuntime=null);
public sealed record RecoveredStackCall(ulong Pc,NormalReturnStackEvidence Evidence,RecoveredValue[] Arguments);
public sealed record StackArgumentFunction(RecoveredFunction Function,int ReturnCleanupBytes,IncomingStackInput[] IncomingSlots,RecoveredStackCall[] Calls);

// Retain ordered conditional architectural exits when deriving normal-only ABI
// facts. This is not fault delivery/unwind support, and never proves a return.
public sealed record ArchitecturalFaultSite(ulong Pc,int EffectOrdinal,string Architecture,int Vector,JsonElement Condition,JsonElement[] PrecedingEffects,bool HandlerSemanticsUnknown=true);
public static class ArchitecturalFaults
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static void Need(bool ok,string why){if(!ok)throw new ArgumentException(why);}
    public static bool Contains(JsonElement n,string kind)=>n.ValueKind==JsonValueKind.Object?(n.TryGetProperty("type",out var t)&&t.ValueKind==JsonValueKind.String&&Tag(n)==kind)||n.EnumerateObject().Any(p=>Contains(p.Value,kind)):n.ValueKind==JsonValueKind.Array&&n.EnumerateArray().Any(x=>Contains(x,kind));
    public static JsonElement Guard(JsonElement n)
    {
        Need(Tag(n)=="IlIf"&&n.GetProperty("Else").GetArrayLength()==0,"architectural_fault_guard_shape");var yes=n.GetProperty("Then").EnumerateArray().ToArray();
        Need(yes.Length==1&&Tag(yes[0])=="IlFault","architectural_fault_guard_shape");var fault=yes[0];Need(fault.GetProperty("Architecture").GetString()=="x86"&&fault.GetProperty("Vector").GetInt32()==0,"unsupported_architectural_fault");
        var c=n.GetProperty("Cond");Need(Tag(c.GetProperty("Ty"))=="I"&&c.GetProperty("Ty").GetProperty("Bits").GetInt32()==1&&!c.GetProperty("Ty").GetProperty("Signed").GetBoolean()&&!Contains(c,"IlFault")&&!Contains(c,"IlTrap")&&!Contains(c,"IlIf")&&!Contains(c,"IlBranch")&&!Contains(c,"IlStore")&&!Contains(c,"IlWriteReg"),"architectural_fault_condition");return c;
    }
    static void NonControlEffects(JsonElement n,int depth=0)
    {
        Need(depth<=8,"architectural_effect_nesting_budget");string tag=Tag(n);Need(!Contains(n,"IlFault")&&!Contains(n,"IlTrap")&&!Contains(n,"IlBranch"),"nested_architectural_control_effect");
        if(tag=="IlIf") {foreach(var arm in new[]{"Then","Else"})foreach(var child in n.GetProperty(arm).EnumerateArray())NonControlEffects(child,depth+1);return;}
        Need(tag is "IlLet" or "IlWriteReg" or "IlStore","unsupported_architectural_control_effect:"+tag);Need(!Contains(n,"IlIf"),"nested_architectural_control_effect");
    }
    public static ArchitecturalFaultSite[] Inspect(JsonElement row)
    {
        var body=row.GetProperty("tree");Need(Tag(body)=="IlBlock","architectural_control_block_required");var nodes=body.GetProperty("Body").EnumerateArray().ToArray();var sites=new List<ArchitecturalFaultSite>();
        for(int i=0;i<nodes.Length;i++) {
            var n=nodes[i];string tag=Tag(n);
            if(tag=="IlIf"&&!Contains(n,"IlFault")) {NonControlEffects(n);continue;}
            if(tag=="IlIf") {var condition=Guard(n);sites.Add(new(row.GetProperty("pc").GetUInt64(),i,"x86",0,condition.Clone(),nodes.Take(i).Select(x=>x.Clone()).ToArray()));continue;}
            Need(tag is "IlLet" or "IlWriteReg" or "IlStore" or "IlBranch","unsupported_architectural_control_effect:"+tag);
            Need(!Contains(n,"IlFault")&&!Contains(n,"IlTrap")&&!Contains(n,"IlIf"),"nested_architectural_control_effect");
            if(tag=="IlBranch")Need(i==nodes.Length-1,"nonterminal_architectural_branch");else NonControlEffects(n);
        }
        return sites.ToArray();
    }
}

public static class X86Recovery
{
    static string Tag(JsonElement n) => n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static int Bits(JsonElement n) { var ty=n.GetProperty("Ty"); if(Tag(ty)!="I"||ty.GetProperty("Signed").GetBoolean())throw new ArgumentException("unsupported_integer_type");return ty.GetProperty("Bits").GetInt32(); }
    static void Need(bool ok,string why) { if(!ok)throw new ArgumentException(why); }
    static bool UsesStackSegment(JsonElement n)
    {
        if(n.ValueKind==JsonValueKind.Object) {
            if(n.TryGetProperty("type",out var type)&&type.GetString()=="LiftIl.IlReadReg"&&n.GetProperty("Kind").GetProperty("name").GetString()=="X86Seg"&&n.GetProperty("Idx").GetInt32()==2)return true;
            return n.EnumerateObject().Any(p=>UsesStackSegment(p.Value));
        }
        return n.ValueKind==JsonValueKind.Array && n.EnumerateArray().Any(UsesStackSegment);
    }
    public static RecoveredFunction Raise(JsonElement lift,RecoveryAbi abi) => RaiseCore(lift,abi,null);
    internal static RecoveredFunction RaiseCore(JsonElement lift,RecoveryAbi abi,StackArgumentContext? stackArguments)
    {
        try { return RaiseCoreChecked(lift,abi,stackArguments); }
        catch(OverflowException) { throw new ArgumentException("symbolic_offset_out_of_supported_range"); }
    }
    static RecoveredFunction RaiseCoreChecked(JsonElement lift,RecoveryAbi abi,StackArgumentContext? stackArguments)
    {
        Need(abi.Id is {Length: >0 and <=128} && abi.ReturnRegister is >=0 and <16 && abi.ReturnRegister!=4 && new[]{abi.ArgumentRegisters,abi.VolatileRegisters,abi.PreservedRegisters}.All(a=>a!=null&&a.Distinct().Count()==a.Length&&a.All(r=>r is >=0 and <16&&r!=4)),"unsupported_ABI_contract");
        Need(lift.GetProperty("mode").GetString()=="Bits32" && lift.GetProperty("decode_complete").GetBoolean() && lift.GetProperty("lift_errors").GetInt32()==0 && lift.GetProperty("opaque_instructions").GetInt32()==0,"incomplete_or_opaque_lift");
        var regs=Enumerable.Range(0,16).ToDictionary(i=>i,i=>(RecoveredValue)new RegisterInput(i));
        var stack=new Dictionary<long,RecoveredValue>{{0,new UnknownValue("entry_return_address")}};long sp=0;bool returned=false;bool tailExit=false;var effects=new List<RecoveredEffect>();var notes=new List<string>();var stackEffects=new List<RecoveredStackEffect>();
        if(stackArguments!=null)foreach(var input in stackArguments.Inputs)stack[input.Offset]=input;
        bool segmentedStack=UsesStackSegment(lift);notes.Add(segmentedStack?"Stack slots retain symbolic SS base plus wrapped32 SP; SS is never replaced by zero.":"Stack accesses follow the lifter's unsegmented flat-stack representation.");
        long? StackOffset(RecoveredValue address) => address switch {
            SegmentedAddress {Segment: {Index:2},Offset:AddValue {Left:RegisterInput {Index:4}} a} when segmentedStack=>a.Offset,
            AddValue {Left:RegisterInput {Index:4}} a when !segmentedStack=>a.Offset,
            _=>null
        };
        var instructions=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(instructions.Length>0,"empty_instruction_range");
        var rangeStart=instructions[0].GetProperty("pc").GetUInt64();var rangeEnd=instructions[^1].GetProperty("pc").GetUInt64()+(ulong)instructions[^1].GetProperty("length").GetInt32();
        foreach(var ins in instructions)
        {
            Need(!returned,"instructions_after_return");
            var prefix=ins.GetProperty("decoded").GetProperty("P");
            Need(!prefix.GetProperty("Lock").GetBoolean()&&!prefix.GetProperty("Rep").GetBoolean()&&!prefix.GetProperty("RepNz").GetBoolean(),"unsupported_instruction_prefix");
            var body=ins.GetProperty("tree");Need(Tag(body)=="IlBlock","nonblock_instruction");
            var tmp=new Dictionary<int,RecoveredValue>();var beforeSp=sp;var pc=ins.GetProperty("pc").GetUInt64();
            RecoveredValue Eval(JsonElement n)
            {
                switch(Tag(n))
                {
                    case "IlUndefined":throw new ArgumentException("undefined_architectural_value:"+n.GetProperty("Reason").GetString());
                    case "IlConst":var cb=Bits(n);Need(cb is 8 or 16 or 32 or 64 && ulong.TryParse(n.GetProperty("Bits").GetProperty("decimal").GetString(),out _),"unsupported_constant");var cv=ulong.Parse(n.GetProperty("Bits").GetProperty("decimal").GetString()!);Need(cb==64||cv<(1UL<<cb),"constant_width_overflow");return new Constant(cv,cb);
                    case "IlReadReg":var registerKind=n.GetProperty("Kind").GetProperty("name").GetString();var idx=n.GetProperty("Idx").GetInt32();if(registerKind=="X86Seg")return new SegmentInput(idx);Need(registerKind=="X86","non_x86_register");return idx==4?new AddValue(new RegisterInput(4),sp):regs[idx];
                    case "IlTmp":return tmp[n.GetProperty("Id").GetInt32()];
                    case "IlCast":
                        var x=Eval(n.GetProperty("X"));var kind=n.GetProperty("Kind").GetProperty("name").GetString();var width=Bits(n);
                        Need(kind is "Trunc" or "Zext" && width is 32 or 64,"unsupported_cast");
                        if(x is Constant c)return new Constant(width==32?c.Value&uint.MaxValue:c.Value,width);
                        Need(x is not Constant,"bad_cast");return x;
                    case "IlBin":
                        var left=Eval(n.GetProperty("L"));var right=Eval(n.GetProperty("R"));var op=n.GetProperty("Op").GetProperty("name").GetString();if(op=="Add"&&left is SegmentInput segment)return new SegmentedAddress(segment,right);Need(right is Constant && op is "Add" or "Sub","unsupported_binary_expression");
                        var offset=checked((long)((Constant)right).Value)*(op=="Sub"?-1:1);return left is AddValue a?new AddValue(a.Left,checked(a.Offset+offset)):new AddValue(left,offset);
                    case "IlLoad":var addr=Eval(n.GetProperty("Addr"));var slot=StackOffset(addr);Need(slot!=null && Bits(n)==32,"unsupported_memory_load");return stack[slot!.Value];
                    default:throw new ArgumentException("unsupported_expression:"+Tag(n));
                }
            }
            var nodes=body.GetProperty("Body").EnumerateArray().ToArray();
            // Accept a direct-call boundary only with explicit correct Bits32 stack effects.
            // The original ec8344 eight-byte CALL push is deliberately rejected.
            bool call=nodes.LastOrDefault().ValueKind==JsonValueKind.Object && Tag(nodes.Last())=="IlBranch" && nodes.Last().GetProperty("Kind").GetProperty("name").GetString()=="Call";
            if(call)
            {
                Need(nodes.Length is 4 or 5,"unsupported_call_stack_tree");
                var cursor=0;while(cursor<nodes.Length && Tag(nodes[cursor])=="IlLet"){var let=nodes[cursor++];tmp[let.GetProperty("Id").GetInt32()]=Eval(let.GetProperty("Val"));}
                Need(cursor==nodes.Length-3 && Tag(nodes[cursor])=="IlWriteReg" && nodes[cursor].GetProperty("Idx").GetInt32()==4 && Tag(nodes[cursor+1])=="IlStore","unsupported_call_stack_tree");
                var next=Eval(nodes[cursor].GetProperty("Val"));Need(next==new AddValue(new RegisterInput(4),sp-4),"incorrect_Bits32_call_stack_width");
                sp-=4;var store=nodes[cursor+1];var ret=Eval(store.GetProperty("Val"));
                Need(StackOffset(Eval(store.GetProperty("Addr")))==sp&&Bits(store.GetProperty("Val"))==32&&ret is Constant {Bits:32} rc&&rc.Value==pc+(ulong)ins.GetProperty("length").GetInt32(),"unsupported_call_return_address");
                var branch=nodes.Last();Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"conditional_call");var target=Eval(branch.GetProperty("Target"));Need(target is Constant,"indirect_call");
                effects.Add(new("call",null,target,32,pc,abi.ArgumentRegisters.Select(r=>regs[r]).ToArray()));
                sp=stackArguments==null?beforeSp:stackArguments.Call(pc,((Constant)target).Value,beforeSp,stack);foreach(var r in abi.VolatileRegisters)regs[r]=new UnknownValue("external_call_clobber:"+abi.Id);
                notes.Add("Direct call retained as external boundary under explicit ABI profile "+abi.Id+"; callee effects remain external.");continue;
            }
            foreach(var n in nodes)
            {
                switch(Tag(n))
                {
                    case "IlLet":tmp[n.GetProperty("Id").GetInt32()]=Eval(n.GetProperty("Val"));break;
                    case "IlWriteReg":Need(n.GetProperty("Kind").GetProperty("name").GetString()=="X86","non_x86_register");var idx=n.GetProperty("Idx").GetInt32();var value=Eval(n.GetProperty("Val"));if(idx==4){Need(value is AddValue {Left:RegisterInput {Index:4}},"unsupported_stack_pointer");sp=((AddValue)value).Offset;}else regs[idx]=value;break;
                    case "IlStore":var address=Eval(n.GetProperty("Addr"));var val=Eval(n.GetProperty("Val"));var bits=Bits(n.GetProperty("Val"));var slot=StackOffset(address);if(slot!=null){Need(bits==32,"unsupported_stack_width");stack[slot.Value]=val;stackEffects.Add(new(address,val,bits,pc,slot.Value>=sp && slot.Value<0 && slot.Value+bits/8<=0));}else effects.Add(new("store",address,val,bits,pc));break;
                    case "IlBranch":
                        var branchKind=n.GetProperty("Kind").GetProperty("name").GetString();Need(n.GetProperty("Cond").ValueKind==JsonValueKind.Null,"unsupported_conditional_control_flow");
                        if(branchKind=="Jmp") {
                            // Directness is an instruction/IL property, not a result of propagation.
                            // A known register value must not turn JMP reg into a supported direct JMP.
                            var targetNode=n.GetProperty("Target");Need(Tag(targetNode)=="IlConst","unsupported_indirect_tail_call");
                            var target=Eval(targetNode);Need(target is Constant {Value:<=uint.MaxValue},"unsupported_indirect_tail_call");var direct=(Constant)target;
                            Need(direct.Value<rangeStart||direct.Value>=rangeEnd,"unsupported_internal_jump");Need(sp==0,"unbalanced_tail_call_stack");
                            effects.Add(new("tail_call",null,target,32,pc,abi.ArgumentRegisters.Select(r=>regs[r]).ToArray()));
                            notes.Add("Terminal direct jump retains external target and ordered inputs under explicit ABI profile "+abi.Id+"; return and callee effects remain external.");tailExit=true;returned=true;break;
                        }
                        Need(branchKind=="Ret","unsupported_control_flow");Need(sp==4+(stackArguments?.ReturnCleanupBytes??0)&&Eval(n.GetProperty("Target"))==new UnknownValue("entry_return_address"),"unbalanced_return");returned=true;break;
                    default:throw new ArgumentException("unsupported_effect:"+Tag(n));
                }
            }
        }
        Need(returned,"missing_return");if(stackArguments!=null)notes.Add("Normal-return cleanup is a bounded original-CFG/RET-encoding ABI hypothesis; callee termination, clobbers and memory effects remain external/unknown. VC8 emission requires an explicit flat32 stack relation for address-taken parameters.");foreach(var r in abi.PreservedRegisters)Need(regs[r]==new RegisterInput(r),"profile_preserved_register_not_restored");
        // This fact is about one complete typed near-return instruction, not
        // empty high-level effects: omitted volatile/flag effects cannot qualify.
        bool bareNearReturn=false;
        if(instructions.Length==1&&instructions[0].GetProperty("length").GetInt32()==1&&instructions[0].TryGetProperty("raw_hex",out var rawReturn)&&rawReturn.GetString()?.Equals("c3",StringComparison.OrdinalIgnoreCase)==true) {
            X86StackArgumentRecovery.VerifyReturnTree(instructions[0],0);
            bareNearReturn=true;
        }
        return new(effects,tailExit?new UnknownValue("tail_callee_result:"+abi.Id):regs[abi.ReturnRegister],notes,stackEffects,tailExit?"tail_call":"return",bareNearReturn);
    }
}

public static class Vc8Profile
{
    public const string Version="vc8-x86-thiscall-stores-tail-v2";
    public static RecoveryAbi Abi=>new(Version,0,[1],[0,1,2],[3,5,6,7]);
    public static string Emit(RecoveredFunction ir,uint rva,uint imageBase,uint imageEnd,string module) => EmitCore(ir,rva,imageBase,imageEnd,module,null);
    internal static string EmitCore(RecoveredFunction ir,uint rva,uint imageBase,uint imageEnd,string module,StackArgumentFunction? stackArguments)
    {
        if(module.Length is <1 or >128 || module.Any(c=>!(char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-')))throw new ArgumentException("unsupported_module_annotation");
        if(ir.StackEffects.Any(e=>!e.WithinAllocatedFrame))throw new ArgumentException("caller_or_unallocated_stack_write_not_emittable");
        bool tail=ir.ExitKind=="tail_call";
        // A void declaration is a compiler proposal, not proof that the entry
        // return register is unobservable. Complete artifact checking remains required.
        bool voidStores=stackArguments==null&&ir.ExitKind=="return"&&ir.Return==new RegisterInput(0)&&ir.StackEffects.Count==0&&ir.Effects.Count>0&&ir.Effects.All(e=>e.Kind=="store");
        bool voidReturn=stackArguments==null&&ir.BareNearReturn&&ir.ExitKind=="return"&&ir.Return==new RegisterInput(0)&&ir.StackEffects.Count==0&&ir.Effects.Count==0;
        if(tail) {if(ir.Effects.Count==0||ir.Effects[^1].Kind!="tail_call"||ir.Effects.Count(e=>e.Kind=="tail_call")!=1)throw new ArgumentException("unsupported_tail_exit");}
        else if(!voidStores&&!voidReturn&&(ir.ExitKind!="return"||ir.Return!=new RegisterInput(1)))throw new ArgumentException("unsupported_return_ABI");
        var decl=new List<string>();var statements=new List<string>();
        foreach(var e in ir.Effects)
        {
            if(e.Kind is "call" or "tail_call")
            {
                if(e.Inputs is not {Length:1} || e.Inputs[0]!=new RegisterInput(1)||e.Value is not Constant target||target.Value<imageBase||target.Value>=imageEnd)throw new ArgumentException("unsupported_call_ABI");
                var name=$"fn_{target.Value-imageBase:x8}";string parameter="",argument="";
                if(stackArguments!=null) {
                    var calls=stackArguments.Calls.Where(c=>c.Pc==e.Pc).ToArray();
                    if(calls.Length!=1||calls[0].Evidence.Target!=target.Value||calls[0].Evidence.CleanupBytes!=4||calls[0].Arguments.Length!=1||calls[0].Arguments[0]!=new IncomingStackAddress(4,32))throw new ArgumentException("unsupported_stack_call_ABI");
                    parameter="unsigned int*";argument="&arg_0";
                }
                decl.Add($"    void {name}({parameter});");statements.Add($"    {name}({argument});");continue;
            }
            if(e.Kind!="store")throw new ArgumentException("unsupported_emitted_effect");
            long offset=e.Address switch {RegisterInput {Index:1}=>0,AddValue {Left:RegisterInput {Index:1}} a=>a.Offset,_=>throw new ArgumentException("unsupported_store_address")};
            if(offset<0||offset>int.MaxValue||e.Value is not Constant c)throw new ArgumentException("unsupported_store_value");
            string expr;if(c.Value>=imageBase&&c.Value<imageEnd&&e.Bits==32){var name=$"g_{c.Value-imageBase:x8}";decl.Insert(0,$"GLOBAL:{name}");expr=$"&{name}";statements.Add($"    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + {offset}) = {expr};");}
            else {var type=e.Bits switch {8=>"unsigned char",16=>"unsigned short",32=>"unsigned int",_=>throw new ArgumentException("unsupported_store_width")};statements.Add($"    *reinterpret_cast<{type}*>(reinterpret_cast<char*>(this) + {offset}) = {c.Value}u;");}
        }
        var globals=decl.Where(d=>d.StartsWith("GLOBAL:")).Distinct().Select(d=>"extern unsigned char "+d[7..]+";");
        var returnType=tail||voidStores||voidReturn?"void":"void*";
        var parameters=stackArguments==null?"":"unsigned int arg_0";
        return string.Join("\n",globals)+$"\nstruct Recovered {{\n"+string.Join("\n",decl.Where(d=>!d.StartsWith("GLOBAL:")).Distinct())+$"\n    {returnType} fn_{rva:x8}({parameters});\n}};\n// FUNCTION: {module} 0x{imageBase+rva:x8}\n{returnType} Recovered::fn_{rva:x8}({parameters}) {{\n"+string.Join("\n",statements)+(tail||voidStores||voidReturn?"":"\n    return this;")+"\n}\n";
    }
}

// Separate opt-in prototype: no current/default recipe acquires these assumptions.
// Complete CFG/RET encoding is ABI evidence for *normal return*, not a claim
// that calls terminate, preserve arbitrary state, or have no memory effects.
internal sealed class StackArgumentContext
{
    public int ReturnCleanupBytes {get;}
    public IncomingStackInput[] Inputs {get;}
    readonly Dictionary<ulong,NormalReturnStackEvidence> Evidence;
    public List<RecoveredStackCall> Calls {get;}=[];
    public StackArgumentContext(int cleanup,IEnumerable<CalleeStackLift> callees)
    {
        ReturnCleanupBytes=cleanup;Inputs=Enumerable.Range(0,cleanup/4).Select(i=>new IncomingStackInput(4+i*4,32)).ToArray();
        Evidence=[];foreach(var c in callees)if(!Evidence.TryAdd(c.Target,X86StackArgumentRecovery.InspectNormalReturn(c.Target,c.Lift)))throw new ArgumentException("duplicate_callee_cleanup_evidence");
    }
    public long Call(ulong pc,ulong target,long sp,Dictionary<long,RecoveredValue> stack)
    {
        if(!Evidence.TryGetValue(target,out var e))throw new ArgumentException("missing_callee_cleanup_evidence");
        if(sp+e.CleanupBytes>0)throw new ArgumentException("callee_cleanup_exceeds_outgoing_frame");
        var args=new List<RecoveredValue>();
        for(int n=0;n<e.CleanupBytes;n+=4) {
            if(!stack.TryGetValue(sp+n,out var value))throw new ArgumentException("missing_outgoing_stack_argument");
            if(value is AddValue {Left:RegisterInput {Index:4}} a) {
                if(a.Offset<4||a.Offset%4!=0||a.Offset>ReturnCleanupBytes)throw new ArgumentException("invalid_incoming_stack_address");
                value=new IncomingStackAddress((int)a.Offset,32);
            }
            args.Add(value);
        }
        Calls.Add(new(pc,e,args.ToArray()));
        foreach(var a in args.OfType<IncomingStackAddress>())stack[a.Offset]=new UnknownValue("external_call_addressable_input_clobber");
        return checked(sp+e.CleanupBytes);
    }
}

public static class X86StackArgumentRecovery
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static void Need(bool condition,string error){if(!condition)throw new ArgumentException(error);}
    static IEnumerable<JsonElement> Branches(JsonElement n)
    {
        if(n.ValueKind==JsonValueKind.Object) {
            if(n.TryGetProperty("type",out var t)&&t.GetString()=="LiftIl.IlBranch")yield return n;
            foreach(var p in n.EnumerateObject())foreach(var b in Branches(p.Value))yield return b;
        } else if(n.ValueKind==JsonValueKind.Array)foreach(var item in n.EnumerateArray())foreach(var b in Branches(item))yield return b;
    }
    internal static int RetCleanup(JsonElement instruction)
    {
        Need(instruction.TryGetProperty("raw_hex",out var raw),"missing_original_return_encoding");
        byte[] bytes;try{bytes=Convert.FromHexString(raw.GetString()!);}catch{throw new ArgumentException("invalid_original_return_encoding");}
        if(bytes.Length==1&&bytes[0]==0xc3)return 0;
        Need(bytes.Length==3&&bytes[0]==0xc2,"unsupported_return_encoding");
        int cleanup=bytes[1]|bytes[2]<<8;Need(cleanup%4==0&&cleanup<=64,"unsupported_return_cleanup");return cleanup;
    }
    static JsonElement Unwrap(JsonElement n) {
        while(Tag(n)=="IlCast") {
            Need(n.GetProperty("Kind").GetProperty("name").GetString() is "Trunc" or "Zext","unsupported_return_cast");
            Need(n.GetProperty("Ty").GetProperty("Bits").GetInt32() is 32 or 64,"unsupported_return_width");n=n.GetProperty("X");
        }
        return n;
    }
    static long ReturnStackDelta(JsonElement value) {
        value=Unwrap(value);
        if(Tag(value)=="IlReadReg") {Need(value.GetProperty("Kind").GetProperty("name").GetString()=="X86"&&value.GetProperty("Idx").GetInt32()==4,"unsupported_return_stack_tree");return 0;}
        Need(Tag(value)=="IlBin","unsupported_return_stack_tree");var right=value.GetProperty("R");
        Need(Tag(right)=="IlConst"&&ulong.TryParse(right.GetProperty("Bits").GetProperty("decimal").GetString(),out _),"unsupported_return_stack_tree");
        ulong delta=ulong.Parse(right.GetProperty("Bits").GetProperty("decimal").GetString()!);Need(delta<=68,"unsupported_return_stack_tree");
        var op=value.GetProperty("Op").GetProperty("name").GetString();Need(op is "Add" or "Sub","unsupported_return_stack_tree");
        return ReturnStackDelta(value.GetProperty("L"))+(op=="Add"?(long)delta:-(long)delta);
    }
    internal static void VerifyReturnTree(JsonElement row,int cleanup) {
        var nodes=row.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();Need(nodes.Length is >=3 and <=8,"unsupported_return_stack_tree");
        Need(Tag(nodes[0])=="IlLet"&&Tag(nodes[^1])=="IlBranch","unsupported_return_stack_tree");var load=nodes[0].GetProperty("Val");
        Need(Tag(load)=="IlLoad"&&load.GetProperty("Ty").GetProperty("Bits").GetInt32()==32,"unsupported_return_width");
        var address=Unwrap(load.GetProperty("Addr"));
        if(Tag(address)=="IlBin") {Need(address.GetProperty("Op").GetProperty("name").GetString()=="Add","unsupported_return_stack_address");var seg=address.GetProperty("L");Need(Tag(seg)=="IlReadReg"&&seg.GetProperty("Kind").GetProperty("name").GetString()=="X86Seg"&&seg.GetProperty("Idx").GetInt32()==2,"unsupported_return_stack_address");address=Unwrap(address.GetProperty("R"));}
        Need(Tag(address)=="IlReadReg"&&address.GetProperty("Kind").GetProperty("name").GetString()=="X86"&&address.GetProperty("Idx").GetInt32()==4,"unsupported_return_stack_address");
        var returnTemps=new HashSet<int>{nodes[0].GetProperty("Id").GetInt32()};
        long delta=0;foreach(var n in nodes.Skip(1).SkipLast(1)) {
            if(Tag(n)=="IlLet") {var v=n.GetProperty("Val");Need(Tag(v)=="IlTmp"&&v.GetProperty("Ty").GetProperty("Bits").GetInt32()==32&&returnTemps.Contains(v.GetProperty("Id").GetInt32())&&returnTemps.Add(n.GetProperty("Id").GetInt32()),"unsupported_return_target");continue;}
            Need(Tag(n)=="IlWriteReg"&&n.GetProperty("Kind").GetProperty("name").GetString()=="X86"&&n.GetProperty("Idx").GetInt32()==4,"unsupported_return_stack_tree");delta+=ReturnStackDelta(n.GetProperty("Val"));
        }
        var target=nodes[^1].GetProperty("Target");Need(Tag(target)=="IlTmp"&&returnTemps.Contains(target.GetProperty("Id").GetInt32())&&target.GetProperty("Ty").GetProperty("Bits").GetInt32()==32,"unsupported_return_target");
        Need(delta==4+cleanup,"conflicting_return_encoding_and_effects");
    }
    public static NormalReturnStackEvidence InspectNormalReturn(ulong target,JsonElement lift,RuntimeTerminalEvidence? terminalRuntime=null)
    {
        Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"incomplete_callee_cleanup_evidence");
        if(terminalRuntime!=null)X86TerminalCallRecovery.ValidateRuntime(terminalRuntime);var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length>0&&rows[0].GetProperty("pc").GetUInt64()==target,"callee_entry_mismatch");
        var indices=new Dictionary<ulong,int>();ulong expected=target;
        foreach(var row in rows) {
            var pc=row.GetProperty("pc").GetUInt64();int len=row.GetProperty("length").GetInt32();
            Need(pc==expected&&len is >0 and <=15&&row.GetProperty("raw_hex").GetString()!.Length==2*len,"ambiguous_callee_range");
            Need(indices.TryAdd(pc,indices.Count),"ambiguous_callee_range");expected=checked(pc+(ulong)len);
        }
        var pending=new Queue<int>();pending.Enqueue(0);var seen=new HashSet<int>();var cleanup=new HashSet<int>();int returns=0,calls=0;var faults=new List<ArchitecturalFaultSite>();var exceptionalCalls=new List<ulong>();
        while(pending.Count>0) {
            int i=pending.Dequeue();if(!seen.Add(i))continue;var row=rows[i];
            faults.AddRange(ArchitecturalFaults.Inspect(row));var branches=Branches(row.GetProperty("tree")).ToArray();Need(branches.Length<=1,"ambiguous_callee_control_flow");
            bool fall=true;
            if(branches.Length==1) {
                var branch=branches[0];var kind=branch.GetProperty("Kind").GetProperty("name").GetString();
                if(kind=="Ret") {Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"conditional_callee_return");var amount=RetCleanup(row);VerifyReturnTree(row,amount);cleanup.Add(amount);returns++;fall=false;}
                else if(kind=="Call") {calls++;Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"conditional_callee_call");if(terminalRuntime!=null&&row.GetProperty("raw_hex").GetString() is {Length:10} rawCall&&rawCall.StartsWith("e8",StringComparison.OrdinalIgnoreCase)&&X86TerminalCallRecovery.DirectCallTarget(row,branch)==terminalRuntime.Target){fall=false;exceptionalCalls.Add(row.GetProperty("pc").GetUInt64());}}
                else {
                    Need(kind is "Jmp" or "CondJmp","unsupported_callee_control_flow");var dest=branch.GetProperty("Target");
                    Need(Tag(dest)=="IlConst"&&ulong.TryParse(dest.GetProperty("Bits").GetProperty("decimal").GetString(),out _),"ambiguous_callee_branch");
                    ulong address=ulong.Parse(dest.GetProperty("Bits").GetProperty("decimal").GetString()!);Need(indices.TryGetValue(address,out _),"external_or_misaligned_callee_exit");pending.Enqueue(indices[address]);
                    if(kind=="Jmp"){Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"ambiguous_callee_branch");fall=false;}
                    else Need(branch.GetProperty("Cond").ValueKind!=JsonValueKind.Null,"ambiguous_callee_branch");
                }
            }
            if(fall){Need(i+1<rows.Length,"callee_falls_out_of_range");pending.Enqueue(i+1);}
        }
        Need(seen.Count==rows.Length,"unreachable_callee_range_bytes");Need(returns>0,"missing_callee_return");Need(cleanup.Count==1,"conflicting_callee_cleanup");
        return new(target,cleanup.Single(),returns,calls,"complete-reachable-CFG-uniform-RET-encoding; normal-return-ABI-hypothesis; nested-call-effects-unknown; explicit conditional faults retained with unknown handler semantics",ArchitecturalFaults:faults.ToArray(),ExceptionalCallSites:exceptionalCalls.ToArray(),TerminalRuntime:exceptionalCalls.Count>0?terminalRuntime:null);
    }
    public static StackArgumentFunction Raise(JsonElement lift,RecoveryAbi abi,IEnumerable<CalleeStackLift> callees)
    {
        var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length>0,"empty_instruction_range");
        var last=rows[^1];var branch=Branches(last.GetProperty("tree")).ToArray();Need(branch.Length==1&&branch[0].GetProperty("Kind").GetProperty("name").GetString()=="Ret","stack_arguments_require_normal_return");
        var outerCleanup=RetCleanup(last);VerifyReturnTree(last,outerCleanup);
        var context=new StackArgumentContext(outerCleanup,callees);var function=X86Recovery.RaiseCore(lift,abi,context);
        return new(function,context.ReturnCleanupBytes,context.Inputs,context.Calls.ToArray());
    }
}

public static class Vc8StackArgsProfile
{
    // Only one opaque member call, with an exactly observed constant outgoing
    // word span and no incoming parameters or additional effects. No arity,
    // return-value, no-throw or memory-retention theorem follows from this source.
    static string EmitConstantMemberCall(StackArgumentFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        void Need(bool ok,string why){if(!ok)throw new ArgumentException(why);}
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"unsupported_module_annotation");
        var f=ir.Function;
        Need(f.ExitKind=="return"&&ir.IncomingSlots.Length==0&&ir.Calls.Length==1&&f.Effects.Count==1&&f.Return==new UnknownValue("external_call_clobber:"+Vc8Profile.Abi.Id),"constant_member_call_shape");
        var call=ir.Calls[0];var e=f.Effects[0];
        Need(e.Kind=="call"&&e.Pc==call.Pc&&e.Inputs is {Length:1}&&e.Inputs[0]==new RegisterInput(1)&&e.Value is Constant target&&target.Value==call.Evidence.Target&&target.Value>=imageBase&&target.Value<imageEnd,"constant_member_call_target_receiver");
        Need(call.Arguments.Length is >=1 and <=4&&call.Evidence.CleanupBytes==4*call.Arguments.Length&&call.Arguments.All(a=>a is Constant{Bits:32,Value:<=uint.MaxValue}),"constant_member_call_words");
        Need(f.StackEffects.Count==call.Arguments.Length,"constant_member_call_extra_stack_effect");
        for(int i=0;i<f.StackEffects.Count;i++) {
            var push=f.StackEffects[i];long expected=-4L*(i+1);
            bool address=push.Address==new AddValue(new RegisterInput(4),expected)||push.Address==new SegmentedAddress(new SegmentInput(2),new AddValue(new RegisterInput(4),expected));
            Need(address&&push.WithinAllocatedFrame&&push.Bits==32&&push.Value==call.Arguments[^(i+1)]&&push.Pc<call.Pc,"constant_member_call_push_span");
        }
        var name=$"fn_{call.Evidence.Target-imageBase:x8}";var parameters=string.Join(", ",Enumerable.Repeat("unsigned int",call.Arguments.Length));var arguments=string.Join(", ",call.Arguments.Cast<Constant>().Select(c=>$"{c.Value}u"));
        return $"struct Recovered {{\n    void {name}({parameters});\n    void fn_{rva:x8}();\n}};\n// FUNCTION: {module} 0x{imageBase+rva:x8}\nvoid Recovered::fn_{rva:x8}() {{\n    {name}({arguments});\n}}\n";
    }
    public const string Version="vc8-x86-flat32-addressable-stack-v1";
    public static StackArgumentFunction Raise(JsonElement lift,IEnumerable<CalleeStackLift> callees)=>X86StackArgumentRecovery.Raise(lift,Vc8Profile.Abi,callees);
    public static string Emit(StackArgumentFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        if(ir.ReturnCleanupBytes==0)return EmitConstantMemberCall(ir,rva,imageBase,imageEnd,module);
        if(ir.Function.ExitKind!="return"||ir.ReturnCleanupBytes!=4||ir.IncomingSlots.Length!=1||ir.IncomingSlots[0]!=new IncomingStackInput(4,32))throw new ArgumentException("unsupported_stack_parameter_ABI");
        if(ir.Calls.Length!=ir.Function.Effects.Count(e=>e.Kind=="call")||ir.Calls.Select(c=>c.Pc).Distinct().Count()!=ir.Calls.Length)throw new ArgumentException("missing_stack_call_effect");
        return Vc8Profile.EmitCore(ir.Function,rva,imageBase,imageEnd,module,ir);
    }
}
