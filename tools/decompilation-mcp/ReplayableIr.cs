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
public abstract record RecoveredValue;
public sealed record Constant(ulong Value, int Bits) : RecoveredValue;
public sealed record RegisterInput(int Index) : RecoveredValue;
public sealed record AddValue(RecoveredValue Left, long Offset) : RecoveredValue;
public sealed record UnknownValue(string Reason) : RecoveredValue;
public sealed record SegmentInput(int Index) : RecoveredValue;
public sealed record SegmentedAddress(SegmentInput Segment, RecoveredValue Offset) : RecoveredValue;
public sealed record RecoveredEffect(string Kind, RecoveredValue? Address, RecoveredValue? Value, int Bits, ulong Pc, RecoveredValue[]? Inputs=null);
public sealed record RecoveryAbi(string Id,int ReturnRegister,int[] ArgumentRegisters,int[] VolatileRegisters,int[] PreservedRegisters);
public sealed record RecoveredStackEffect(RecoveredValue Address,RecoveredValue Value,int Bits,ulong Pc,bool WithinAllocatedFrame);
public sealed record RecoveredFunction(List<RecoveredEffect> Effects, RecoveredValue Return, List<string> Hypotheses,List<RecoveredStackEffect> StackEffects,string ExitKind="return");
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
    public static RecoveredFunction Raise(JsonElement lift,RecoveryAbi abi)
    {
        Need(abi.Id is {Length: >0 and <=128} && abi.ReturnRegister is >=0 and <16 && abi.ReturnRegister!=4 && new[]{abi.ArgumentRegisters,abi.VolatileRegisters,abi.PreservedRegisters}.All(a=>a!=null&&a.Distinct().Count()==a.Length&&a.All(r=>r is >=0 and <16&&r!=4)),"unsupported_ABI_contract");
        Need(lift.GetProperty("mode").GetString()=="Bits32" && lift.GetProperty("decode_complete").GetBoolean() && lift.GetProperty("lift_errors").GetInt32()==0 && lift.GetProperty("opaque_instructions").GetInt32()==0,"incomplete_or_opaque_lift");
        var regs=Enumerable.Range(0,16).ToDictionary(i=>i,i=>(RecoveredValue)new RegisterInput(i));
        var stack=new Dictionary<long,RecoveredValue>{{0,new UnknownValue("entry_return_address")}};long sp=0;bool returned=false;bool tailExit=false;var effects=new List<RecoveredEffect>();var notes=new List<string>();var stackEffects=new List<RecoveredStackEffect>();
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
                effects.Add(new("call",null,target,32,pc,abi.ArgumentRegisters.Select(r=>regs[r]).ToArray()));sp=beforeSp;foreach(var r in abi.VolatileRegisters)regs[r]=new UnknownValue("external_call_clobber:"+abi.Id);
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
                        Need(branchKind=="Ret","unsupported_control_flow");Need(sp==4&&Eval(n.GetProperty("Target"))==new UnknownValue("entry_return_address"),"unbalanced_return");returned=true;break;
                    default:throw new ArgumentException("unsupported_effect:"+Tag(n));
                }
            }
        }
        Need(returned,"missing_return");foreach(var r in abi.PreservedRegisters)Need(regs[r]==new RegisterInput(r),"profile_preserved_register_not_restored");
        return new(effects,tailExit?new UnknownValue("tail_callee_result:"+abi.Id):regs[abi.ReturnRegister],notes,stackEffects,tailExit?"tail_call":"return");
    }
}

public static class Vc8Profile
{
    public const string Version="vc8-x86-thiscall-stores-tail-v2";
    public static RecoveryAbi Abi=>new(Version,0,[1],[0,1,2],[3,5,6,7]);
    public static string Emit(RecoveredFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        if(module.Length is <1 or >128 || module.Any(c=>!(char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-')))throw new ArgumentException("unsupported_module_annotation");
        if(ir.StackEffects.Any(e=>!e.WithinAllocatedFrame))throw new ArgumentException("caller_or_unallocated_stack_write_not_emittable");
        bool tail=ir.ExitKind=="tail_call";
        if(tail) {if(ir.Effects.Count==0||ir.Effects[^1].Kind!="tail_call"||ir.Effects.Count(e=>e.Kind=="tail_call")!=1)throw new ArgumentException("unsupported_tail_exit");}
        else if(ir.ExitKind!="return"||ir.Return!=new RegisterInput(1))throw new ArgumentException("unsupported_return_ABI");
        var decl=new List<string>();var statements=new List<string>();
        foreach(var e in ir.Effects)
        {
            if(e.Kind is "call" or "tail_call")
            {
                if(e.Inputs is not {Length:1} || e.Inputs[0]!=new RegisterInput(1)||e.Value is not Constant target||target.Value<imageBase||target.Value>=imageEnd)throw new ArgumentException("unsupported_call_ABI");
                var name=$"fn_{target.Value-imageBase:x8}";decl.Add($"    void {name}();");statements.Add($"    {name}();");continue;
            }
            if(e.Kind!="store")throw new ArgumentException("unsupported_emitted_effect");
            long offset=e.Address switch {RegisterInput {Index:1}=>0,AddValue {Left:RegisterInput {Index:1}} a=>a.Offset,_=>throw new ArgumentException("unsupported_store_address")};
            if(offset<0||offset>int.MaxValue||e.Value is not Constant c)throw new ArgumentException("unsupported_store_value");
            string expr;if(c.Value>=imageBase&&c.Value<imageEnd&&e.Bits==32){var name=$"g_{c.Value-imageBase:x8}";decl.Insert(0,$"GLOBAL:{name}");expr=$"&{name}";statements.Add($"    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + {offset}) = {expr};");}
            else {var type=e.Bits switch {8=>"unsigned char",16=>"unsigned short",32=>"unsigned int",_=>throw new ArgumentException("unsupported_store_width")};statements.Add($"    *reinterpret_cast<{type}*>(reinterpret_cast<char*>(this) + {offset}) = {c.Value}u;");}
        }
        var globals=decl.Where(d=>d.StartsWith("GLOBAL:")).Distinct().Select(d=>"extern unsigned char "+d[7..]+";");
        var returnType=tail?"void":"void*";
        return string.Join("\n",globals)+$"\nstruct Recovered {{\n"+string.Join("\n",decl.Where(d=>!d.StartsWith("GLOBAL:")).Distinct())+$"\n    {returnType} fn_{rva:x8}();\n}};\n// FUNCTION: {module} 0x{imageBase+rva:x8}\n{returnType} Recovered::fn_{rva:x8}() {{\n"+string.Join("\n",statements)+(tail?"":"\n    return this;")+"\n}\n";
    }
}
