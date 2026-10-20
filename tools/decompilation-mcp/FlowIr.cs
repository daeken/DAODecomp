using System.Text.Json;
namespace Decompilation;

public sealed record FlowCallContract(RecoveryAbi Abi,bool FlatDataAndStackSegments,bool CallerFrameRetainedOnNormalReturn,RecoveredValue[]? RegisteredFrameAnchors=null,ulong ModuleImageStart=0,ulong ModuleImageEnd=0,bool PrivateSubwordStack=false,bool ObserveOutgoingPushRegion=false,int MaximumOutgoingBytes=16,bool AliasableMemoryStores=false);
public sealed record FlowCall(ulong Target,RecoveredValue Receiver,RecoveredValue[] Arguments,int CalleeCleanup,int CallerCleanup,ForwardedReturnEvidence Evidence,long EntrySp,Dictionary<int,RecoveredValue> EntryRegisters,Dictionary<long,RecoveredValue> EntryStack,bool MemoryEffectsUnknown=true,bool ThrowBehaviorUnknown=true,bool TerminationUnknown=true,bool FormalArityKnown=false,string ArgumentBasis="observed normal cleanup span; zero does not establish zero formal arity",int CallerPrivateCleanupBytes=0);
public sealed record FlowEffect(string Kind,ulong Pc,RecoveredValue? Address=null,RecoveredValue? Value=null,int Bits=0,FlowCall? Call=null);
public sealed record FlowPredicate(ulong Pc,RecoveredValue Value,bool Taken);
public sealed record FlowExit(ulong Pc,int ReturnCleanupBytes,long ExitSp,RecoveredValue Return,Dictionary<int,RecoveredValue> Registers,Dictionary<int,RecoveredValue> Flags,Dictionary<long,RecoveredValue> Stack,RecoveredValue? ReturnTarget=null,bool StackMemoryMayHaveChanged=false);
public sealed record FlowPath(FlowPredicate[] Predicates,FlowEffect[] Effects,FlowExit Exit);
public sealed record IncomingObservation(int RequiredReadBytes,bool ExactArityKnown,bool AddressEscapeObserved,string Basis);
public sealed record FlowFunction(FlowPath[] NormalPaths,IncomingObservation Incoming,int[] ReturnCleanupBytes,ulong[] InstructionOrigins,string NormalContinuationContract,bool ExceptionalSemanticsUnknown=true);

// Architecture-only bounded path recovery. Calls retain their actual target and
// unknown result/effects; the supplied profile explicitly owns normal ABI facts.
public static class X86FlowRecovery
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static string Name(JsonElement n,string p)=>n.GetProperty(p).GetProperty("name").GetString()!;
    static void Need(bool ok,string reason){if(!ok)throw new ArgumentException(reason);}
    static int Bits(JsonElement n){var t=n.GetProperty("Ty");Need(Tag(t)=="I"&&!t.GetProperty("Signed").GetBoolean(),"flow_unsigned_integer_required");int b=t.GetProperty("Bits").GetInt32();Need(b is 1 or 8 or 16 or 32 or 64,"flow_unsupported_width");return b;}
    static bool Same(RecoveredValue a,RecoveredValue b)=>JsonSerializer.Serialize<RecoveredValue>(a)==JsonSerializer.Serialize<RecoveredValue>(b);
    sealed class State
    {
        public long Sp;public int Epoch;public int ReadOrdinal;public int Incoming;public bool Escaped;public bool UnrestrictedFrameEscape;public bool StackMemoryMayHaveChanged;
        public Dictionary<int,RecoveredValue> Regs=Enumerable.Range(0,16).ToDictionary(i=>i,i=>(RecoveredValue)new RegisterInput(i));
        public Dictionary<int,RecoveredValue> Flags=Enumerable.Range(0,32).ToDictionary(i=>i,i=>(RecoveredValue)new UnknownValue("entry_flag_"+i));
        public Dictionary<long,RecoveredValue> Stack=new(){{0,new UnknownValue("entry_return_address")}};
        public HashSet<long> PushWords=[];public HashSet<long> PrivateWords=[];
        public List<FlowEffect> Effects=[];public List<FlowPredicate> Predicates=[];
        public State Copy()=>new(){Sp=Sp,Epoch=Epoch,ReadOrdinal=ReadOrdinal,Incoming=Incoming,Escaped=Escaped,UnrestrictedFrameEscape=UnrestrictedFrameEscape,StackMemoryMayHaveChanged=StackMemoryMayHaveChanged,Regs=new(Regs),Flags=new(Flags),Stack=new(Stack),PushWords=new(PushWords),PrivateWords=new(PrivateWords),Effects=new(Effects),Predicates=new(Predicates)};
        public Dictionary<int,RecoveredValue> SnapshotRegisters(){var r=new Dictionary<int,RecoveredValue>(Regs);r[4]=new AddValue(new RegisterInput(4),Sp);return r;}
        public void Prune(){foreach(var k in Stack.Keys.Where(k=>k<Sp).ToArray())Stack.Remove(k);PushWords.RemoveWhere(k=>k<Sp);PrivateWords.RemoveWhere(k=>k<Sp);}
    }
    static bool Frame(RecoveredValue v)=>v switch{RegisterInput{Index:4}=>true,AddValue a=>Frame(a.Left),BitValue b=>b.Operands.Any(Frame),SegmentedAddress a=>Frame(a.Offset),_=>false};
    static long? Offset(RecoveredValue v,bool flat)=>v switch{SegmentedAddress{Segment:{Index:2},Offset:AddValue{Left:RegisterInput{Index:4}} a}=>a.Offset,AddValue{Left:RegisterInput{Index:4}} a when flat=>a.Offset,_=>null};
    static RecoveredValue Bin(string op,RecoveredValue l,RecoveredValue r,int bits)
    {
        Need(op is "Add" or "Sub" or "And" or "Or" or "Xor" or "Shr" or "Shl" or "Eq" or "Ne" or "Ult","flow_unsupported_binary");
        if(op=="Add"&&l is SegmentInput seg)return new SegmentedAddress(seg,r);
        if((op is "Add" or "Sub")&&r is Constant c&&(l is RegisterInput{Index:4} or AddValue{Left:RegisterInput{Index:4}})) {
            Need(c.Value<=4096,"flow_stack_adjustment_budget");long delta=(long)c.Value*(op=="Sub"?-1:1);return l is AddValue a?new AddValue(a.Left,checked(a.Offset+delta)):new AddValue(l,delta);
        }
        if(op=="Xor"&&Same(l,r))return new Constant(0,bits);
        if(l is Constant a0&&r is Constant b0) {
            ulong a=a0.Value,b=b0.Value;ulong v=op switch{"Add"=>unchecked(a+b),"Sub"=>unchecked(a-b),"And"=>a&b,"Or"=>a|b,"Xor"=>a^b,"Shr" when b<64=>a>>(int)b,"Shl" when b<64=>a<<(int)b,"Eq"=>a==b?1UL:0UL,"Ne"=>a!=b?1UL:0UL,"Ult"=>a<b?1UL:0UL,_=>throw new ArgumentException("flow_shift_budget")};return new Constant(bits==64?v:v&((1UL<<bits)-1),bits);
        }
        return new BitValue(op,[l,r],bits);
    }
    static RecoveredValue Eval(JsonElement n,State s,Dictionary<int,RecoveredValue> temp,ulong pc,FlowCallContract contract)
    {
        switch(Tag(n)) {
            case "IlUndefined":throw new ArgumentException("flow_undefined_architectural_value:"+n.GetProperty("Reason").GetString());
            case "IlConst":int b=Bits(n);Need(ulong.TryParse(n.GetProperty("Bits").GetProperty("decimal").GetString(),out var c)&&(b==64||c<(1UL<<b)),"flow_constant_width");return new Constant(c,b);
            case "IlReadReg":int i=n.GetProperty("Idx").GetInt32();string k=Name(n,"Kind");if(k=="X86Seg"){Need(i is >=0 and <6,"flow_segment");return new SegmentInput(i);}if(k=="Eflags"){Need(s.Flags.ContainsKey(i),"flow_flag");return s.Flags[i];}Need(k=="X86"&&s.Regs.ContainsKey(i),"flow_register");return i==4?new AddValue(new RegisterInput(4),s.Sp):s.Regs[i];
            case "IlTmp":Need(temp.TryGetValue(n.GetProperty("Id").GetInt32(),out var t),"flow_temporary_before_definition");return t!;
            case "IlCast":var x=Eval(n.GetProperty("X"),s,temp,pc,contract);int w=Bits(n);string cast=Name(n,"Kind");Need(cast is "Zext" or "Trunc","flow_cast");if(x is Constant cv)return new Constant(w==64?cv.Value:cv.Value&((1UL<<w)-1),w);if(w is 32 or 64&&x is RegisterInput or AddValue or SegmentedAddress or ExternalRegisterValue)return x;return new BitValue(cast,[x],w);
            case "IlBin":return Bin(Name(n,"Op"),Eval(n.GetProperty("L"),s,temp,pc,contract),Eval(n.GetProperty("R"),s,temp,pc,contract),Bits(n));
            case "IlLoad":var addr=Eval(n.GetProperty("Addr"),s,temp,pc,contract);int width=Bits(n);long? slot=Offset(addr,contract.FlatDataAndStackSegments);
                if(slot!=null){Need(slot>=-4096&&slot<=4096,"flow_stack_extent_budget");if(slot>=4){Need(width is 8 or 16 or 32&&slot%(width/8)==0,"flow_incoming_alignment");s.Incoming=Math.Max(s.Incoming,checked((int)slot.Value+width/8-4));var incomingRead=new IncomingStackRead((int)slot.Value,width,pc,s.Epoch);s.Effects.Add(new("incoming_read",pc,addr,incomingRead,width));return incomingRead;}Need(width==32&&slot%4==0&&s.Stack.ContainsKey(slot.Value),"flow_unknown_or_overlapping_stack_read");if(s.StackMemoryMayHaveChanged){var uncertain=new MemoryReadValue(addr,width,pc,s.Epoch,++s.ReadOrdinal);s.Effects.Add(new("stack_read",pc,addr,uncertain,width));return uncertain;}var read=s.Stack[slot.Value];s.Effects.Add(new("stack_read",pc,addr,read,width));return read;}
                var memory=new MemoryReadValue(addr,width,pc,s.Epoch,++s.ReadOrdinal);s.Effects.Add(new("memory_read",pc,addr,memory,width));return memory;
            default:throw new ArgumentException("flow_expression:"+Tag(n));
        }
    }
    static JsonElement[] Nodes(JsonElement row)=>row.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();
    static JsonElement? Branch(JsonElement row){var n=Nodes(row);return n.Length>0&&Tag(n[^1])=="IlBranch"?n[^1]:null;}
    static int CallerCleanup(JsonElement? row,State state,FlowCallContract contract)
    {
        if(row==null)return 0;var nodes=Nodes(row.Value);if(!nodes.Any(n=>Tag(n)=="IlWriteReg"&&Name(n,"Kind")=="X86"&&n.GetProperty("Idx").GetInt32()==4))return 0;
        var temp=new Dictionary<int,RecoveredValue>();RecoveredValue? adjusted=null;ulong pc=row.Value.GetProperty("pc").GetUInt64();
        foreach(var n in nodes){if(Tag(n)=="IlLet"){Need(temp.TryAdd(n.GetProperty("Id").GetInt32(),Eval(n.GetProperty("Val"),state,temp,pc,contract)),"flow_duplicate_temporary");continue;}Need(Tag(n)=="IlWriteReg"&&(Name(n,"Kind")=="Eflags"||(Name(n,"Kind")=="X86"&&n.GetProperty("Idx").GetInt32()==4)),"flow_ambiguous_caller_cleanup");if(Name(n,"Kind")=="X86"){Need(adjusted==null,"flow_ambiguous_caller_cleanup");adjusted=Eval(n.GetProperty("Val"),state,temp,pc,contract);}}
        Need(adjusted is AddValue{Left:RegisterInput{Index:4}},"flow_ambiguous_caller_cleanup");long amount=((AddValue)adjusted!).Offset-state.Sp;Need(amount>0&&amount<=contract.MaximumOutgoingBytes&&amount%4==0,"flow_caller_cleanup_budget");return (int)amount;
    }
    public static FlowFunction Raise(JsonElement lift,FlowCallContract contract,IEnumerable<CalleeStackLift> supplied)
    {
        try{return RaiseChecked(lift,contract,supplied.ToArray());}catch(OverflowException){throw new ArgumentException("flow_numeric_budget");}
    }
    static FlowFunction RaiseChecked(JsonElement lift,FlowCallContract contract,CalleeStackLift[] callees)
    {
        Need(contract.CallerFrameRetainedOnNormalReturn,"flow_requires_explicit_normal_frame_contract");var abi=contract.Abi;Need(abi.ArgumentRegisters.Length<=1&&abi.ArgumentRegisters.All(i=>i!=4)&&contract.MaximumOutgoingBytes is >=4 and <=64&&contract.MaximumOutgoingBytes%4==0&&abi.ReturnRegister is >=0 and <16&&abi.ReturnRegister!=4&&new[]{abi.ArgumentRegisters,abi.VolatileRegisters,abi.PreservedRegisters}.All(a=>a.Distinct().Count()==a.Length&&a.All(i=>i is >=0 and <16&&i!=4)),"flow_ABI_contract");
        Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"flow_incomplete_lift");var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length is >0 and <=128,"flow_instruction_budget");var indexes=new Dictionary<ulong,int>();ulong expected=rows[0].GetProperty("pc").GetUInt64();
        for(int i=0;i<rows.Length;i++){var r=rows[i];int len=r.GetProperty("length").GetInt32();var p=r.GetProperty("decoded").GetProperty("P");Need(r.GetProperty("pc").GetUInt64()==expected&&len is >0 and <=15&&r.GetProperty("raw_hex").GetString()!.Length==2*len&&Tag(r.GetProperty("tree"))=="IlBlock"&&!p.GetProperty("Lock").GetBoolean()&&!p.GetProperty("Rep").GetBoolean()&&!p.GetProperty("RepNz").GetBoolean(),"flow_instruction_boundary_or_prefix");indexes.Add(expected,i);expected+=(ulong)len;}
        var visited=new HashSet<int>();var paths=new List<FlowPath>();var queue=new Queue<(int,State)>();queue.Enqueue((0,new State()));int incoming=0;bool escaped=false;
        while(queue.TryDequeue(out var item)) {
            Need(paths.Count+queue.Count<8,"flow_path_budget");int at=item.Item1;var s=item.Item2;
            for(;at<rows.Length;at++) {
                visited.Add(at);var row=rows[at];ulong pc=row.GetProperty("pc").GetUInt64();var nodes=Nodes(row);var temp=new Dictionary<int,RecoveredValue>();long beforeSp=s.Sp;var branch=Branch(row);string? kind=branch==null?null:Name(branch.Value,"Kind");
                foreach(var node in nodes) {
                    if(Tag(node)=="IlLet"){Need(temp.TryAdd(node.GetProperty("Id").GetInt32(),Eval(node.GetProperty("Val"),s,temp,pc,contract)),"flow_duplicate_temporary");continue;}
                    if(Tag(node)=="IlWriteReg") {
                        var v=Eval(node.GetProperty("Val"),s,temp,pc,contract);int reg=node.GetProperty("Idx").GetInt32();string k=Name(node,"Kind");
                        if(k=="Eflags"){Need(s.Flags.ContainsKey(reg)&&Bits(node.GetProperty("Val"))==1,"flow_flag_write");s.Flags[reg]=v;s.Effects.Add(new("flag_write",pc,new Constant((ulong)reg,8),v,1));}
                        else {Need(k=="X86"&&s.Regs.ContainsKey(reg),"flow_register_write");if(reg==4){Need(v is AddValue{Left:RegisterInput{Index:4}},"flow_nonrelative_SP");long sp=((AddValue)v).Offset;Need(sp%4==0&&sp>=-4096&&sp<=(kind=="Ret"?4096:0),"flow_SP_budget_or_alignment");s.Sp=sp;}else s.Regs[reg]=v;s.Effects.Add(new("register_write",pc,new RegisterInput(reg),v,Bits(node.GetProperty("Val"))));}continue;
                    }
                    if(Tag(node)=="IlStore") {
                        var a=Eval(node.GetProperty("Addr"),s,temp,pc,contract);var v=Eval(node.GetProperty("Val"),s,temp,pc,contract);int b=Bits(node.GetProperty("Val"));var slot=Offset(a,contract.FlatDataAndStackSegments);
                        if(slot!=null){
                            Need(slot>=s.Sp&&slot+b/8<=0&&slot%Math.Max(1,b/8)==0,"flow_stack_store_outside_allocated_word");
                            bool push=kind==null&&nodes.Length==3&&Tag(nodes[0])=="IlLet"&&Tag(nodes[1])=="IlWriteReg"&&Name(nodes[1],"Kind")=="X86"&&nodes[1].GetProperty("Idx").GetInt32()==4&&b==32&&s.Sp==beforeSp-4&&slot==s.Sp;
                            if(b==32){Need(slot%4==0,"flow_stack_store_outside_allocated_word");s.Stack[slot.Value]=v;}
                            else {
                                Need(contract.PrivateSubwordStack&&b is 8 or 16,"flow_stack_store_outside_allocated_word");long word=slot.Value&~3L;Need(word>=s.Sp&&word+4<=0&&slot+b/8<=word+4&&s.Stack.ContainsKey(word),"flow_private_subword_without_initialized_word");
                                int shift=checked((int)(slot-word)*8);ulong mask=((1UL<<b)-1)<<shift;var low=new BitValue("Zext",[v],32);RecoveredValue inserted=shift==0?low:new BitValue("Shl",[low,new Constant((ulong)shift,32)],32);s.Stack[word]=new BitValue("Or",[new BitValue("And",[s.Stack[word],new Constant(uint.MaxValue^mask,32)],32),inserted],32);s.PrivateWords.Add(word);s.PushWords.Remove(word);
                            }
                            if(push)s.PushWords.Add(slot.Value);else if(b==32){s.PrivateWords.Add(slot.Value);s.PushWords.Remove(slot.Value);}
                        }else{Need(contract.AliasableMemoryStores||(contract.RegisteredFrameAnchors??[]).Any(anchor=>Same(anchor,a))||(a is SegmentedAddress{Segment:{Index:3},Offset:Constant absolute}&&absolute.Value>=contract.ModuleImageStart&&absolute.Value<contract.ModuleImageEnd&&absolute.Value+(ulong)(b/8)<=contract.ModuleImageEnd),"flow_unknown_store_frame_alias");if(contract.AliasableMemoryStores)s.StackMemoryMayHaveChanged=true;s.Epoch++;if(Frame(v)){s.Escaped=true;if(!(contract.RegisteredFrameAnchors??[]).Any(anchor=>Same(anchor,a)))s.UnrestrictedFrameEscape=true;}}
                        s.Effects.Add(new(slot==null?"memory_store":"stack_store",pc,a,v,b));continue;
                    }
                    Need(Tag(node)=="IlBranch"&&node.Equals(nodes[^1]),"flow_unknown_or_nonterminal_effect");var target=Eval(node.GetProperty("Target"),s,temp,pc,contract);
                    if(kind=="Call") {
                        Need(!s.StackMemoryMayHaveChanged,"flow_call_after_aliasable_store_requires_fresh_argument_state");
                        var capture=node.GetProperty("Target");if(Tag(capture)=="IlTmp"){int id=capture.GetProperty("Id").GetInt32();capture=nodes.Single(n=>Tag(n)=="IlLet"&&n.GetProperty("Id").GetInt32()==id).GetProperty("Val");}Need(Tag(capture)=="IlConst"&&node.GetProperty("Cond").ValueKind==JsonValueKind.Null&&target is Constant,"flow_direct_call_required");Need(s.Sp==beforeSp-4&&s.Stack.TryGetValue(s.Sp,out var ra)&&ra==new Constant(pc+(ulong)row.GetProperty("length").GetInt32(),32),"flow_call_stack_or_return_address");
                        Need(!s.UnrestrictedFrameEscape&&(abi.ArgumentRegisters.Length==0||!Frame(s.Regs[abi.ArgumentRegisters[0]])),"flow_unknown_call_frame_alias");ulong dest=((Constant)target).Value;var evidence=NormalReturnResolver.Resolve(dest,callees);int callee=evidence.NormalReturn.CleanupBytes;Need(callee>=0&&callee<=contract.MaximumOutgoingBytes&&callee%4==0,"flow_callee_cleanup_budget");var continuation=s.Copy();continuation.Sp=beforeSp;int caller=CallerCleanup(at+1<rows.Length?rows[at+1]:null,continuation,contract);int extent=checked(callee+caller);Need(extent<=contract.MaximumOutgoingBytes&&beforeSp+extent<=0,"flow_arguments_cross_return_address");int privateCleanup=0;
                        if(contract.ObserveOutgoingPushRegion&&extent>0){int pushed=0;while(pushed<extent&&s.PushWords.Contains(beforeSp+pushed))pushed+=4;Need(pushed>=callee,"flow_callee_cleanup_crosses_private_frame");for(int off=pushed;off<extent;off+=4)Need(s.PrivateWords.Contains(beforeSp+off),"flow_cleanup_region_not_outgoing_or_private");privateCleanup=extent-pushed;extent=pushed;}
                        var args=new List<RecoveredValue>();for(int off=0;off<extent;off+=4){Need(s.Stack.TryGetValue(beforeSp+off,out var av),"flow_outgoing_argument_missing");Need(!Frame(av!),"flow_unknown_call_frame_alias");args.Add(av!);}
                        s.Effects.Add(new("external_call",pc,Call:new(dest,abi.ArgumentRegisters.Length==0?new UnknownValue("profile_has_no_register_arguments"):s.Regs[abi.ArgumentRegisters[0]],args.ToArray(),callee,caller,evidence,s.Sp,s.SnapshotRegisters(),new(s.Stack),ArgumentBasis:contract.ObserveOutgoingPushRegion?"contiguous observed push region; remaining explicit private-word cleanup is separate; formal arity unknown":"observed normal cleanup span; zero does not establish zero formal arity",CallerPrivateCleanupBytes:privateCleanup)));s.Stack.Remove(beforeSp-4);s.Sp=beforeSp+callee;s.Prune();s.Epoch++;foreach(int reg in abi.VolatileRegisters)s.Regs[reg]=new ExternalRegisterValue(pc,reg,32);foreach(int f in s.Flags.Keys.ToArray())s.Flags[f]=new UnknownValue("external_flag_"+pc+"_"+f);
                    } else if(kind=="Ret") {
                        int cleanup=X86StackArgumentRecovery.RetCleanup(row);X86StackArgumentRecovery.VerifyReturnTree(row,cleanup);Need((target==new UnknownValue("entry_return_address")||contract.AliasableMemoryStores&&target is MemoryReadValue)&&s.Sp==4+cleanup,"flow_unbalanced_return");if(!s.StackMemoryMayHaveChanged)foreach(int reg in abi.PreservedRegisters)Need(s.Regs[reg]==new RegisterInput(reg),"flow_preserved_register");incoming=Math.Max(incoming,s.Incoming);escaped|=s.Escaped;paths.Add(new(s.Predicates.ToArray(),s.Effects.ToArray(),new(pc,cleanup,s.Sp,s.Regs[abi.ReturnRegister] is Constant retval?new Constant(retval.Value&uint.MaxValue,32):s.Regs[abi.ReturnRegister],s.SnapshotRegisters(),new(s.Flags),new(s.Stack),target,s.StackMemoryMayHaveChanged)));goto PathDone;
                    } else if(kind is "CondJmp" or "Jmp") {
                        Need(target is Constant&&indexes.TryGetValue(((Constant)target).Value,out _),"flow_external_or_misaligned_branch");int next=indexes[((Constant)target).Value];Need(next>at,"flow_backward_branch");if(kind=="Jmp"){Need(node.GetProperty("Cond").ValueKind==JsonValueKind.Null,"flow_conditional_jump_kind");at=next-1;}
                        else {Need(node.GetProperty("Cond").ValueKind!=JsonValueKind.Null&&Bits(node.GetProperty("Cond"))==1,"flow_branch_predicate_width");var cond=Eval(node.GetProperty("Cond"),s,temp,pc,contract);Need(cond is not UnknownValue,"flow_unknown_predicate");var taken=s.Copy();taken.Predicates.Add(new(pc,cond,true));queue.Enqueue((next,taken));s.Predicates.Add(new(pc,cond,false));} 
                    } else throw new ArgumentException("flow_branch_kind");
                }
            }
            throw new ArgumentException("flow_fallthrough_outside_range");
            PathDone:;
        }
        Need(visited.Count==rows.Length&&paths.Count>0,"flow_unreached_instruction_or_no_return");return new(paths.ToArray(),new(incoming,false,escaped,"minimum directly observed incoming reads; return cleanup never determines arity"),paths.Select(p=>p.Exit.ReturnCleanupBytes).Distinct().Order().ToArray(),rows.Select(r=>r.GetProperty("pc").GetUInt64()).ToArray(),abi.Id+"; explicit caller-frame retention only on normal continuation");
    }
}
