using System.Security.Cryptography;
using System.Text.Json;
namespace Decompilation;

public sealed record TailAdapterReturnEvidence(ulong Target,RecoveredFunction Function,RecoveryAbi Abi,int StackPointerDelta,RecoveredValue[] ArgumentMap,bool MemoryEffectsUnknown=true,bool ThrowBehaviorUnknown=true,bool TerminationUnknown=true,bool CallerFrameRetainedOnlyOnNormalContinuation=true,bool ObjectFrameDisjointnessProven=false);
public sealed record ReturnEvidenceNode(ulong Target,string SliceSha256,int Bytes,TailAdapterReturnEvidence? TailAdapter=null);
public sealed record ForwardedReturnEvidence(ulong OriginalTarget,NormalReturnStackEvidence NormalReturn,ReturnEvidenceNode[] Chain,bool Proof=false);
public sealed record ConditionalEffect(string Kind,ulong Pc,RecoveredValue? Address=null,RecoveredValue? Value=null,int Bits=0,ConditionalCall? Call=null);
public sealed record ConditionalCall(ulong OriginalTarget,RecoveredValue Receiver,RecoveredValue[] Arguments,int CalleeCleanupBytes,int CallerCleanupBytes,ForwardedReturnEvidence Evidence,ConditionalState EntryState,bool MemoryEffectsUnknown=true,bool TerminationUnknown=true);
public sealed record ConditionalState(long Sp,Dictionary<int,RecoveredValue> Registers,Dictionary<long,RecoveredValue> Stack,Dictionary<int,RecoveredValue> Flags,int MemoryEpoch);
public sealed record StructuredConditional(RecoveredValue TakenCondition,ConditionalEffect[] FallthroughEffects,ulong BranchPc,ulong JoinPc,ConditionalState Join);
public sealed record ConditionalFunction(ConditionalEffect[] Prefix,StructuredConditional Conditional,ConditionalEffect[] Suffix,RecoveredValue Return,int ReturnCleanupBytes,ConditionalState Exit,string[] Hypotheses);

public static class NormalReturnResolver
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static void Need(bool yes,string why){if(!yes)throw new ArgumentException(why);}
    public static ulong? PureForwardTarget(ulong target,JsonElement lift)
    {
        Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"incomplete_forwarding_evidence");
        var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length>0&&rows[0].GetProperty("pc").GetUInt64()==target,"forwarding_entry_mismatch");if(rows.Length!=1)return null;
        var row=rows[0];var body=row.GetProperty("tree");if(Tag(body)!="IlBlock")return null;var nodes=body.GetProperty("Body").EnumerateArray().ToArray();
        if(nodes.Length!=1||Tag(nodes[0])!="IlBranch"||nodes[0].GetProperty("Kind").GetProperty("name").GetString()!="Jmp")return null;
        var branch=nodes[0];Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null&&Tag(branch.GetProperty("Target"))=="IlConst","non_direct_forwarding_thunk");
        var prefix=row.GetProperty("decoded").GetProperty("P");Need(!prefix.GetProperty("Lock").GetBoolean()&&!prefix.GetProperty("Rep").GetBoolean()&&!prefix.GetProperty("RepNz").GetBoolean(),"prefixed_forwarding_thunk");
        var raw=Convert.FromHexString(row.GetProperty("raw_hex").GetString()!);Need(raw.Length==row.GetProperty("length").GetInt32()&&((raw.Length==2&&raw[0]==0xeb)||(raw.Length==5&&raw[0]==0xe9)),"unsupported_forwarding_encoding");
        long delta=raw.Length==2?(sbyte)raw[1]:System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(raw.AsSpan(1));
        var dest=branch.GetProperty("Target");Need(dest.GetProperty("Ty").GetProperty("Bits").GetInt32() is 32 or 64&&ulong.TryParse(dest.GetProperty("Bits").GetProperty("decimal").GetString(),out _),"unsupported_forwarding_target");
        ulong address=ulong.Parse(dest.GetProperty("Bits").GetProperty("decimal").GetString()!);Need(target<=uint.MaxValue&&address==unchecked((uint)((long)target+raw.Length+delta)),"forwarding_encoding_target_disagrees");return address;
    }
    static bool Contains(JsonElement node,string kind)
    {
        if(node.ValueKind==JsonValueKind.Object) {
            if(node.TryGetProperty("type",out var type)&&type.ValueKind==JsonValueKind.String&&Tag(node)==kind)return true;
            return node.EnumerateObject().Any(p=>Contains(p.Value,kind));
        }
        return node.ValueKind==JsonValueKind.Array&&node.EnumerateArray().Any(n=>Contains(n,kind));
    }
    public static TailAdapterReturnEvidence? TailAdapter(ulong target,JsonElement lift,RecoveryAbi abi)
    {
        var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();if(rows.Length<2)return null;
        var last=rows[^1];var tail=last.GetProperty("tree");if(Tag(tail)!="IlBlock")return null;
        var body=tail.GetProperty("Body").EnumerateArray().ToArray();
        if(body.Length!=1||Tag(body[0])!="IlBranch"||body[0].GetProperty("Kind").GetProperty("name").GetString()!="Jmp")return null;
        Need(abi.ArgumentRegisters.Length==1&&abi.ArgumentRegisters[0] is >=0 and <16&&abi.ArgumentRegisters[0]!=4,"tail_adapter_requires_explicit_receiver_ABI");
        // Reuse the original encoding/typed direct-target check on the final row.
        var single=lift.Deserialize<Dictionary<string,JsonElement>>()!;single["instructions"]=JsonSerializer.SerializeToElement(new[]{last});
        var destination=PureForwardTarget(last.GetProperty("pc").GetUInt64(),JsonSerializer.SerializeToElement(single));Need(destination!=null,"tail_adapter_direct_exit_required");
        ulong pc=target;
        foreach(var row in rows) {
            int size=row.GetProperty("length").GetInt32();var prefix=row.GetProperty("decoded").GetProperty("P");
            Need(row.GetProperty("pc").GetUInt64()==pc&&size is >0 and <=15&&row.GetProperty("raw_hex").GetString()!.Length==size*2&&!prefix.GetProperty("Lock").GetBoolean()&&!prefix.GetProperty("Rep").GetBoolean()&&!prefix.GetProperty("RepNz").GetBoolean(),"tail_adapter_range_or_prefix");pc+=(ulong)size;
        }
        foreach(var row in rows[..^1]) {
            var tree=row.GetProperty("tree");Need(Tag(tree)=="IlBlock"&&!Contains(tree,"IlLoad"),"tail_adapter_unknown_read");
            Need(tree.GetProperty("Body").EnumerateArray().All(n=>Tag(n) is "IlLet" or "IlStore"),"tail_adapter_register_stack_flag_or_control_effect");
        }
        var recovered=X86Recovery.Raise(lift,abi);var receiver=new RegisterInput(abi.ArgumentRegisters[0]);
        Need(recovered.ExitKind=="tail_call"&&recovered.StackEffects.Count==0&&recovered.Effects.Count is >=2 and <=9,"tail_adapter_complete_bounded_prefix_required");
        var exit=recovered.Effects[^1];Need(exit.Kind=="tail_call"&&exit.Value is Constant c&&c.Value==destination&&exit.Inputs is {Length:1}&&exit.Inputs[0]==receiver,"tail_adapter_argument_mapping_changed");
        foreach(var effect in recovered.Effects.Take(recovered.Effects.Count-1)) {
            long? offset=effect.Address==receiver?0:effect.Address is AddValue a&&a.Left==receiver?a.Offset:null;
            Need(effect.Kind=="store"&&effect.Bits is 8 or 16 or 32&&effect.Value is Constant value&&value.Bits==effect.Bits&&offset is >=0 and <=4096,"tail_adapter_requires_bounded_receiver_constant_stores");
        }
        return new(destination!.Value,recovered,abi,0,exit.Inputs!);
    }
    public static ForwardedReturnEvidence Resolve(ulong original,IEnumerable<CalleeStackLift> supplied,int maximumDepth=8,RecoveryAbi? adapterAbi=null)
    {
        Need(maximumDepth is >0 and <=16,"invalid_forwarding_budget");var map=new Dictionary<ulong,JsonElement>();foreach(var c in supplied)Need(map.TryAdd(c.Target,c.Lift),"duplicate_callee_evidence");var visited=new HashSet<ulong>();var chain=new List<ReturnEvidenceNode>();ulong target=original;
        for(int depth=0;depth<=maximumDepth;depth++) {
            Need(visited.Add(target),"forwarding_cycle");Need(map.TryGetValue(target,out var lift),"missing_forwarding_dependency");var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();
            var bytes=rows.SelectMany(r=>Convert.FromHexString(r.GetProperty("raw_hex").GetString()!)).ToArray();
            var next=PureForwardTarget(target,lift);var adapter=next==null&&adapterAbi!=null?TailAdapter(target,lift,adapterAbi):null;next??=adapter?.Target;
            chain.Add(new(target,Convert.ToHexStringLower(SHA256.HashData(bytes)),bytes.Length,adapter));
            if(next==null)return new(original,X86StackArgumentRecovery.InspectNormalReturn(target,lift),chain.ToArray());Need(depth<maximumDepth,"forwarding_depth_exhausted");target=next.Value;
        }
        throw new ArgumentException("forwarding_depth_exhausted");
    }
}

// Bounded single forward diamond. All IL effects are visited; only its two paths
// may be joined, with exact live stack/preserved registers and explicit unknowns.
public static class X86ConditionalRecovery
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static string Name(JsonElement n,string property)=>n.GetProperty(property).GetProperty("name").GetString()!;
    static void Need(bool yes,string why){if(!yes)throw new ArgumentException(why);}
    static int Bits(JsonElement n){var t=n.GetProperty("Ty");Need(Tag(t)=="I"&&!t.GetProperty("Signed").GetBoolean(),"unsupported_conditional_type");int bits=t.GetProperty("Bits").GetInt32();Need(bits is 1 or 8 or 16 or 32 or 64,"unsupported_conditional_width");return bits;}
    sealed class State
    {
        public long Sp;public int Epoch;public Dictionary<int,RecoveredValue> Regs=Enumerable.Range(0,16).ToDictionary(i=>i,i=>(RecoveredValue)new RegisterInput(i));
        public Dictionary<long,RecoveredValue> Stack=new(){{0,new UnknownValue("entry_return_address")}};public Dictionary<int,RecoveredValue> Flags=Enumerable.Range(0,32).ToDictionary(i=>i,i=>(RecoveredValue)new UnknownValue("entry_flag_"+i));
        public State Copy()=>new(){Sp=Sp,Epoch=Epoch,Regs=new(Regs),Stack=new(Stack),Flags=new(Flags)};
        public ConditionalState Snapshot()=>new(Sp,new(Regs),new(Stack),new(Flags),Epoch);
        public void Prune(){foreach(var key in Stack.Keys.Where(k=>k<Sp).ToArray())Stack.Remove(key);}
    }
    static bool Same(RecoveredValue a,RecoveredValue b)=>JsonSerializer.Serialize<RecoveredValue>(a)==JsonSerializer.Serialize<RecoveredValue>(b);
    static RecoveredValue Operation(string op,RecoveredValue l,RecoveredValue r,int bits)
    {
        if((op is "Add" or "Sub")&&r is Constant c&&c.Value<=long.MaxValue&&(l is RegisterInput or AddValue)) {
            long amount=checked((long)c.Value*(op=="Sub"?-1:1));return l is AddValue a?new AddValue(a.Left,checked(a.Offset+amount)):new AddValue(l,amount);
        }
        Need(op is "Add" or "Sub" or "And" or "Or" or "Xor" or "Shr" or "Shl" or "Eq" or "Ne" or "Ult","unsupported_conditional_binary");return new BitValue(op,[l,r],bits);
    }
    static bool FramePointer(RecoveredValue value)=>value switch{RegisterInput{Index:4}=>true,AddValue a=>FramePointer(a.Left),SegmentedAddress a=>FramePointer(a.Offset),BitValue b=>b.Operands.Any(FramePointer),_=>false};
    static long? Offset(RecoveredValue v,bool flat)=>v switch {SegmentedAddress{Segment:{Index:2},Offset:AddValue{Left:RegisterInput{Index:4}} a}=>a.Offset,AddValue{Left:RegisterInput{Index:4}} a when flat=>a.Offset,_=>null};
    static RecoveredValue Eval(JsonElement n,State s,Dictionary<int,RecoveredValue> temp,ulong pc,int cleanup,bool flat)
    {
        switch(Tag(n)) {
            case "IlUndefined":throw new ArgumentException("conditional_undefined_architectural_value:"+n.GetProperty("Reason").GetString());
            case "IlConst":int bits=Bits(n);Need(ulong.TryParse(n.GetProperty("Bits").GetProperty("decimal").GetString(),out var number)&&(bits==64||number<(1UL<<bits)),"conditional_constant_width");return new Constant(number,bits);
            case "IlTmp":Need(temp.ContainsKey(n.GetProperty("Id").GetInt32()),"missing_conditional_temporary");return temp[n.GetProperty("Id").GetInt32()];
            case "IlReadReg":int i=n.GetProperty("Idx").GetInt32();var kind=Name(n,"Kind");if(kind=="X86Seg")return new SegmentInput(i);if(kind=="Eflags"){Need(s.Flags.ContainsKey(i),"unsupported_flag_index");return s.Flags[i];}Need(kind=="X86"&&s.Regs.ContainsKey(i),"unsupported_conditional_register");return i==4?new AddValue(new RegisterInput(4),s.Sp):s.Regs[i];
            case "IlCast":var value=Eval(n.GetProperty("X"),s,temp,pc,cleanup,flat);var cast=Name(n,"Kind");int width=Bits(n);Need(cast is "Trunc" or "Zext","unsupported_conditional_cast");
                if(value is Constant constant)return new Constant(width==64?constant.Value:constant.Value&((1UL<<width)-1),width);
                if(width is 32 or 64&&value is RegisterInput or AddValue or SegmentedAddress)return value;
                return new BitValue(cast,[value],width);
            case "IlBin":var left=Eval(n.GetProperty("L"),s,temp,pc,cleanup,flat);var right=Eval(n.GetProperty("R"),s,temp,pc,cleanup,flat);var op=Name(n,"Op");if(op=="Add"&&left is SegmentInput seg)return new SegmentedAddress(seg,right);return Operation(op,left,right,Bits(n));
            case "IlLoad":var address=Eval(n.GetProperty("Addr"),s,temp,pc,cleanup,flat);var offset=Offset(address,flat);int loadBits=Bits(n);Need(offset!=null,"unsupported_conditional_memory_load");long slot=offset!.Value;
                if(slot>=4) {Need(slot+loadBits/8<=4+cleanup&&loadBits is 8 or 16 or 32&&slot%(loadBits/8)==0,"incoming_stack_read_outside_extent");return new IncomingStackRead((int)slot,loadBits,pc,s.Epoch);}
                Need(loadBits==32&&s.Stack.TryGetValue(slot,out _),"unsupported_conditional_stack_load");return s.Stack[slot];
            default:throw new ArgumentException("unsupported_conditional_expression:"+Tag(n));
        }
    }
    static void Simple(JsonElement row,State s,List<ConditionalEffect> effects,int cleanup,bool flat)
    {
        ulong pc=row.GetProperty("pc").GetUInt64();var temp=new Dictionary<int,RecoveredValue>();
        foreach(var node in row.GetProperty("tree").GetProperty("Body").EnumerateArray()) {
            if(Tag(node)=="IlLet"){Need(temp.TryAdd(node.GetProperty("Id").GetInt32(),Eval(node.GetProperty("Val"),s,temp,pc,cleanup,flat)),"duplicate_conditional_temporary");continue;}
            if(Tag(node)=="IlWriteReg") {
                var value=Eval(node.GetProperty("Val"),s,temp,pc,cleanup,flat);int index=node.GetProperty("Idx").GetInt32();var kind=Name(node,"Kind");
                if(kind=="Eflags") {Need(index is 0 or 2 or 4 or 6 or 7 or 11&&Bits(node.GetProperty("Val"))==1,"unsupported_flag_write");s.Flags[index]=value;effects.Add(new("flag_write",pc,Value:value,Bits:1,Address:new Constant((ulong)index,8)));continue;}
                Need(kind=="X86"&&s.Regs.ContainsKey(index),"unsupported_conditional_write");if(index==4){Need(value is AddValue{Left:RegisterInput{Index:4}} adjusted&&adjusted.Offset<=0&&adjusted.Offset%4==0,"unsupported_conditional_SP");effects.Add(new("stack_adjust",pc,new AddValue(new RegisterInput(4),s.Sp),value,32));s.Sp=((AddValue)value).Offset;s.Prune();}else s.Regs[index]=value;continue;
            }
            if(Tag(node)=="IlStore") {
                var address=Eval(node.GetProperty("Addr"),s,temp,pc,cleanup,flat);var value=Eval(node.GetProperty("Val"),s,temp,pc,cleanup,flat);int bits=Bits(node.GetProperty("Val"));var offset=Offset(address,flat);
                if(offset!=null){Need(bits==32&&offset>=s.Sp&&offset%4==0&&offset<=-4,"unsupported_conditional_stack_store");s.Stack[offset.Value]=value;effects.Add(new("stack_store",pc,address,value,bits));}
                else {effects.Add(new("store",pc,address,value,bits));s.Epoch++;}continue;
            }
            throw new ArgumentException("unsupported_conditional_effect:"+Tag(node));
        }
    }
    static int CallerCleanup(JsonElement? next,State state,int cleanup,bool flat)
    {
        if(next==null)return 0;var nodes=next.Value.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();
        if(!nodes.Any(n=>Tag(n)=="IlWriteReg"&&Name(n,"Kind")=="X86"&&n.GetProperty("Idx").GetInt32()==4))return 0;
        Need(nodes.All(n=>Tag(n)=="IlLet"||(Tag(n)=="IlWriteReg"&&(Name(n,"Kind")=="Eflags"||(Name(n,"Kind")=="X86"&&n.GetProperty("Idx").GetInt32()==4)))),"ambiguous_caller_cleanup");
        var copy=state.Copy();Simple(next.Value,copy,[],cleanup,flat);long delta=copy.Sp-state.Sp;Need(delta is >0 and <=16&&delta%4==0,"unsupported_caller_cleanup");return (int)delta;
    }
    static JsonElement[] Nodes(JsonElement row)=>row.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();
    static string? BranchKind(JsonElement row){var nodes=Nodes(row);return nodes.Length>0&&Tag(nodes[^1])=="IlBranch"?Name(nodes[^1],"Kind"):null;}
    static void Call(JsonElement row,JsonElement? next,State s,List<ConditionalEffect> effects,int cleanup,bool flat,RecoveryAbi abi,IEnumerable<CalleeStackLift> callees,bool tailAdapters)
    {
        ulong pc=row.GetProperty("pc").GetUInt64();var nodes=Nodes(row);Need(nodes.Length is 4 or 5,"unsupported_conditional_call_tree");var temp=new Dictionary<int,RecoveredValue>();int cursor=0;
        while(cursor<nodes.Length&&Tag(nodes[cursor])=="IlLet"){var node=nodes[cursor++];Need(temp.TryAdd(node.GetProperty("Id").GetInt32(),Eval(node.GetProperty("Val"),s,temp,pc,cleanup,flat)),"duplicate_conditional_call_temporary");}
        Need(cursor==nodes.Length-3&&Tag(nodes[cursor])=="IlWriteReg"&&Name(nodes[cursor],"Kind")=="X86"&&nodes[cursor].GetProperty("Idx").GetInt32()==4&&Tag(nodes[cursor+1])=="IlStore","unsupported_conditional_call_tree");
        var branch=nodes[^1];Need(branch.GetProperty("Cond").ValueKind==JsonValueKind.Null,"conditional_call_node");var targetNode=branch.GetProperty("Target");
        var capture=Tag(targetNode)=="IlTmp"?nodes.Take(cursor).FirstOrDefault(n=>n.GetProperty("Id").GetInt32()==targetNode.GetProperty("Id").GetInt32()).GetProperty("Val"):targetNode;
        Need(Tag(capture)=="IlConst"&&Eval(capture,s,temp,pc,cleanup,flat) is Constant,"indirect_conditional_call");var target=(Constant)Eval(capture,s,temp,pc,cleanup,flat);
        var before=s.Sp;Need(Eval(nodes[cursor].GetProperty("Val"),s,temp,pc,cleanup,flat)==new AddValue(new RegisterInput(4),before-4),"incorrect_Bits32_call_stack_width");s.Sp-=4;
        var store=nodes[cursor+1];Need(Offset(Eval(store.GetProperty("Addr"),s,temp,pc,cleanup,flat),flat)==s.Sp&&Bits(store.GetProperty("Val"))==32&&Eval(store.GetProperty("Val"),s,temp,pc,cleanup,flat) is Constant{Bits:32} ret&&ret.Value==pc+(ulong)row.GetProperty("length").GetInt32(),"conditional_call_return_address_mismatch");s.Sp=before;
        var evidence=NormalReturnResolver.Resolve(target.Value,callees,adapterAbi:tailAdapters?abi:null);int callee=evidence.NormalReturn.CleanupBytes;Need(callee is >=0 and <=16&&callee%4==0,"unsupported_conditional_callee_cleanup");int caller=CallerCleanup(next,s,cleanup,flat);int extent=checked(callee+caller);Need(extent<=16&&before+extent<=0,"outgoing_arguments_cross_return_slot");var args=new List<RecoveredValue>();
        for(int n=0;n<extent;n+=4){Need(s.Stack.TryGetValue(before+n,out var v),"missing_conditional_outgoing_argument");Need(!FramePointer(v!),"conditional_stack_address_escape");args.Add(v!);}
        Need(!FramePointer(s.Regs[abi.ArgumentRegisters.Single()]),"conditional_stack_address_escape");
        var entry=s.Copy();entry.Sp=before-4;entry.Stack[entry.Sp]=new Constant(pc+(ulong)row.GetProperty("length").GetInt32(),32);
        effects.Add(new("call",pc,Call:new(target.Value,s.Regs[abi.ArgumentRegisters.Single()],args.ToArray(),callee,caller,evidence,entry.Snapshot())));
        s.Sp+=callee;s.Prune();s.Epoch++;foreach(var r in abi.VolatileRegisters)s.Regs[r]=new UnknownValue("external_call_"+pc+"_reg_"+r);foreach(var r in s.Flags.Keys.ToArray())s.Flags[r]=new UnknownValue("external_call_"+pc+"_flag_"+r);
    }
    static void Linear(JsonElement[] rows,int start,int end,State s,List<ConditionalEffect> effects,int cleanup,bool flat,RecoveryAbi abi,IEnumerable<CalleeStackLift> callees,bool allowReturn,bool tailAdapters)
    {
        for(int i=start;i<end;i++) {
            var row=rows[i];var kind=BranchKind(row);
            if(kind=="Call"){Call(row,i+1<end?rows[i+1]:null,s,effects,cleanup,flat,abi,callees,tailAdapters);continue;}
            if(kind=="Ret") {
                Need(allowReturn&&i==end-1,"conditional_path_early_return");X86StackArgumentRecovery.VerifyReturnTree(row,cleanup);var n=Nodes(row);var temp=new Dictionary<int,RecoveredValue>();ulong pc=row.GetProperty("pc").GetUInt64();RecoveredValue? target=null;
                foreach(var node in n) {
                    if(Tag(node)=="IlBranch"){Need(Name(node,"Kind")=="Ret"&&node.GetProperty("Cond").ValueKind==JsonValueKind.Null,"unsupported_conditional_return");target=Eval(node.GetProperty("Target"),s,temp,pc,cleanup,flat);}
                    else if(Tag(node)=="IlLet")temp[node.GetProperty("Id").GetInt32()]=Eval(node.GetProperty("Val"),s,temp,pc,cleanup,flat);
                    else {Need(Tag(node)=="IlWriteReg"&&Name(node,"Kind")=="X86"&&node.GetProperty("Idx").GetInt32()==4,"unsupported_conditional_return_tree");var v=Eval(node.GetProperty("Val"),s,temp,pc,cleanup,flat);Need(v is AddValue{Left:RegisterInput{Index:4}},"unsupported_conditional_return_SP");s.Sp=((AddValue)v).Offset;}
                }
                Need(s.Sp==4+cleanup&&target==new UnknownValue("entry_return_address"),"unbalanced_conditional_return");s.Prune();continue;
            }
            Need(kind==null,"unsupported_nested_or_unconditional_control_flow");Simple(row,s,effects,cleanup,flat);
        }
    }
    public static ConditionalFunction Raise(JsonElement lift,RecoveryAbi abi,IEnumerable<CalleeStackLift> supplied,bool flat32StackRelation,bool tailAdapters=false)
    {
        try{return RaiseChecked(lift,abi,supplied.ToArray(),flat32StackRelation,tailAdapters);}catch(OverflowException){throw new ArgumentException("conditional_symbolic_offset_out_of_range");}
    }
    static ConditionalFunction RaiseChecked(JsonElement lift,RecoveryAbi abi,CalleeStackLift[] callees,bool flat,bool tailAdapters)
    {
        Need(flat&&abi.ArgumentRegisters.Length==1&&abi.ArgumentRegisters[0]!=4&&abi.ReturnRegister is >=0 and <16&&abi.ReturnRegister!=4&&new[]{abi.ArgumentRegisters,abi.VolatileRegisters,abi.PreservedRegisters}.All(a=>a!=null&&a.Distinct().Count()==a.Length&&a.All(r=>r is >=0 and <16&&r!=4)),"conditional_profile_requires_explicit_flat32_ABI");Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"incomplete_conditional_lift");var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length is >0 and <=128,"conditional_instruction_budget");ulong expected=rows[0].GetProperty("pc").GetUInt64();
        foreach(var row in rows){var p=row.GetProperty("decoded").GetProperty("P");Need(!p.GetProperty("Lock").GetBoolean()&&!p.GetProperty("Rep").GetBoolean()&&!p.GetProperty("RepNz").GetBoolean(),"unsupported_conditional_prefix");int len=row.GetProperty("length").GetInt32();Need(row.GetProperty("pc").GetUInt64()==expected&&len is >0 and <=15&&row.GetProperty("raw_hex").GetString()!.Length==2*len&&Tag(row.GetProperty("tree"))=="IlBlock","incomplete_conditional_range");expected+=(ulong)len;}
        var branches=Enumerable.Range(0,rows.Length).Where(i=>BranchKind(rows[i])=="CondJmp").ToArray();Need(branches.Length==1,"requires_one_forward_conditional");int at=branches.Single();var node=Nodes(rows[at]);Need(node.Length==1&&Tag(node[0].GetProperty("Target"))=="IlConst","unsupported_conditional_branch_tree");ulong destination=ulong.Parse(node[0].GetProperty("Target").GetProperty("Bits").GetProperty("decimal").GetString()!);int join=Array.FindIndex(rows,r=>r.GetProperty("pc").GetUInt64()==destination);Need(join>at+1&&join<rows.Length-1,"unsupported_backward_or_nonboundary_join");Need(BranchKind(rows[^1])=="Ret","conditional_requires_final_return");int cleanup=X86StackArgumentRecovery.RetCleanup(rows[^1]);Need(cleanup is >0 and <=16,"unsupported_conditional_input_extent");
        var state=new State();var prefix=new List<ConditionalEffect>();Linear(rows,0,at,state,prefix,cleanup,flat,abi,callees,false,tailAdapters);var condition=Eval(node[0].GetProperty("Cond"),state,[],rows[at].GetProperty("pc").GetUInt64(),cleanup,flat);Need(Bits(node[0].GetProperty("Cond"))==1&&condition is not UnknownValue,"unknown_conditional_predicate");var fall=state.Copy();var body=new List<ConditionalEffect>();Linear(rows,at+1,join,fall,body,cleanup,flat,abi,callees,false,tailAdapters);
        state.Prune();fall.Prune();Need(state.Sp==fall.Sp&&state.Stack.Count==fall.Stack.Count&&state.Stack.All(k=>fall.Stack.TryGetValue(k.Key,out var v)&&Same(k.Value,v)),"incompatible_live_stack_join");
        foreach(var r in state.Regs.Keys.ToArray())if(!Same(state.Regs[r],fall.Regs[r])){Need(abi.VolatileRegisters.Contains(r),"incompatible_preserved_register_join");state.Regs[r]=new UnknownValue("conditional_join_reg_"+r);}
        foreach(var r in state.Flags.Keys.ToArray())if(!Same(state.Flags[r],fall.Flags[r]))state.Flags[r]=new UnknownValue("conditional_join_flag_"+r);state.Epoch=Math.Max(state.Epoch,fall.Epoch)+1;
        var joined=state.Snapshot();var suffix=new List<ConditionalEffect>();Linear(rows,join,rows.Length,state,suffix,cleanup,flat,abi,callees,true,tailAdapters);foreach(var r in abi.PreservedRegisters)Need(state.Regs[r]==new RegisterInput(r),"conditional_preserved_register_not_restored");
        return new(prefix.ToArray(),new(condition,body.ToArray(),rows[at].GetProperty("pc").GetUInt64(),destination,joined),suffix.ToArray(),state.Regs[abi.ReturnRegister],cleanup,state.Snapshot(),["Explicit flat32 profile relates SS stack addresses to ordinary ESP-based incoming loads; segment state is not replaced by a guessed zero.","All typed flag writes and external calls are retained; unknown calls clobber volatile registers/flags and memory epochs. Normal-return evidence does not prove callee effects or termination.","Incoming loads refer to current stack storage at their recorded PC/memory epoch, not a cached pre-call value. Conditional live stacks/preserved registers join exactly; differing volatile state remains unknown."]);
    }
}

public static class Vc8ConditionalCallsProfile
{
    public const string Version="vc8-x86-flat32-conditional-calls-v1";
    public static RecoveryAbi Abi=>new(Version,0,[1],[0,1,2],[3,5,6,7]);
    public static ConditionalFunction Raise(JsonElement lift,IEnumerable<CalleeStackLift> callees)=>X86ConditionalRecovery.Raise(lift,Abi,callees,true);
    public static string Emit(ConditionalFunction ir,uint rva,uint imageBase,uint imageEnd,string module)
    {
        void Need(bool yes,string why){if(!yes)throw new ArgumentException(why);}
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"unsupported_module_annotation");
        Need(ir.ReturnCleanupBytes==4&&ir.Return==new RegisterInput(1),"unsupported_conditional_return_ABI");
        var condition=ir.Conditional.TakenCondition as BitValue;Need(condition is {Operation:"Eq" or "Ne",Bits:1,Operands.Length:2},"unsupported_conditional_predicate_ABI");
        Need(condition!.Operands[0] is BitValue{Operation:"And",Bits:8,Operands.Length:2}&&condition.Operands[1] is Constant{Value:0,Bits:8},"unsupported_conditional_predicate_ABI");
        var test=(BitValue)condition.Operands[0];Need(test.Operands[0] is IncomingStackRead{Offset:4,Bits:8}&&test.Operands[1] is Constant{Value:>0 and <=255,Bits:8},"unsupported_conditional_stack_test_ABI");
        var mask=(Constant)test.Operands[1];var globals=new List<string>();var members=new List<string>();var functions=new List<string>();
        List<string> EmitEffects(ConditionalEffect[] effects) {
            var lines=new List<string>();foreach(var effect in effects) {
                if(effect.Kind is "flag_write" or "stack_adjust" or "stack_store")continue; // Typed flags and validated native frame operations remain in IR. The compiler lowers the ABI frame; complete native comparison is mandatory.
                if(effect.Kind=="call") {
                    var c=effect.Call!;Need(c.Evidence.OriginalTarget==c.OriginalTarget&&c.OriginalTarget>=imageBase&&c.OriginalTarget<imageEnd,"conditional_call_identity_or_bounds");string name=$"fn_{c.OriginalTarget-imageBase:x8}";
                    if(c.Arguments.Length==0&&c.CalleeCleanupBytes==0&&c.CallerCleanupBytes==0&&c.Receiver==new RegisterInput(1)){members.Add($"    void {name}();");lines.Add($"    {name}();");}
                    else if(c.Arguments.Length==1&&c.CalleeCleanupBytes==0&&c.CallerCleanupBytes==4&&c.Arguments[0]==new RegisterInput(1)){functions.Add($"extern \"C\" void __cdecl {name}(void*);");lines.Add($"    {name}(this);");}
                    else throw new ArgumentException("unsupported_conditional_call_ABI");continue;
                }
                Need(effect.Kind=="store"&&effect.Value is Constant,"unsupported_conditional_source_effect");var value=(Constant)effect.Value!;long offset=effect.Address switch{RegisterInput{Index:1}=>0,AddValue{Left:RegisterInput{Index:1}} a=>a.Offset,_=>throw new ArgumentException("unsupported_conditional_store_address")};Need(offset is >=0 and <=int.MaxValue,"unsupported_conditional_store_offset");
                if(effect.Bits==32&&value.Value>=imageBase&&value.Value<imageEnd){var name=$"g_{value.Value-imageBase:x8}";globals.Add($"extern unsigned char {name};");lines.Add($"    *reinterpret_cast<void**>(reinterpret_cast<char*>(this) + {offset}) = &{name};");}
                else {var type=effect.Bits switch{8=>"unsigned char",16=>"unsigned short",32=>"unsigned int",_=>throw new ArgumentException("unsupported_conditional_store_width")};lines.Add($"    *reinterpret_cast<{type}*>(reinterpret_cast<char*>(this) + {offset}) = {value.Value}u;");}
            }
            return lines;
        }
        Need(ir.Conditional.FallthroughEffects.Count(e=>e.Kind=="call")==1,"unsupported_conditional_body_shape");var prefix=EmitEffects(ir.Prefix);var body=EmitEffects(ir.Conditional.FallthroughEffects);var suffix=EmitEffects(ir.Suffix);
        var declarations=globals.Distinct().Concat(functions.Distinct());string comparison=condition.Operation=="Eq"?"!=":"==";
        return string.Join("\n",declarations)+"\nstruct Recovered {\n"+string.Join("\n",members.Distinct())+$"\n    void* fn_{rva:x8}(unsigned int arg_0);\n}};\n// FUNCTION: {module} 0x{imageBase+rva:x8}\nvoid* Recovered::fn_{rva:x8}(unsigned int arg_0) {{\n"+string.Join("\n",prefix)+$"\n    if ((arg_0 & {mask.Value}u) {comparison} 0u) {{\n"+string.Join("\n",body.Select(l=>"    "+l))+"\n    }\n"+string.Join("\n",suffix)+"\n    return this;\n}\n";
    }
}

public static class Vc8CallAdaptersProfile
{
    public const string Version="vc8-x86-flat32-call-adapters-v1";
    public static RecoveryAbi Abi=>Vc8ConditionalCallsProfile.Abi with {Id=Version};
    public static ConditionalFunction Raise(JsonElement lift,IEnumerable<CalleeStackLift> callees)=>X86ConditionalRecovery.Raise(lift,Abi,callees,true,true);
    public static string Emit(ConditionalFunction ir,uint rva,uint imageBase,uint imageEnd,string module)=>Vc8ConditionalCallsProfile.Emit(ir,rva,imageBase,imageEnd,module);
}
