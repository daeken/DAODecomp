using System.Text.Json;
namespace Decompilation;

public sealed record GraphEffect(string Kind,ulong Pc,RecoveredValue? Address,RecoveredValue Value,int Bits,int? Register=null);
public sealed record GraphEdge(ulong Target,bool? Taken=null);
public sealed record GraphBlock(ulong Pc,long EntrySp,GraphEffect[] Effects,Dictionary<int,RecoveredValue> Registers,Dictionary<int,RecoveredValue> Flags,RecoveredValue? Predicate,GraphEdge[] Edges,RecoveredValue? ReturnTarget,int? ReturnCleanup);
public sealed record NaturalLoop(ulong Header,ulong Latch,ulong[] Blocks,ulong[] Exits);
public sealed record GraphFunction(GraphBlock[] Blocks,NaturalLoop[] Loops,ulong[] InstructionOrigins,string MemoryModel);

// Block-local SSA: no memory forwarding, including stack loads after arbitrary
// stores. Edges retain simultaneous register joins and loops retain backedges.
// Register joins retain unknown architectural state; integer widths and casts
// remain explicit. Only SP is tracked as a wrapped Bits32 affine address.
public static class X86GraphRecovery
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static string Name(JsonElement n,string p)=>n.GetProperty(p).GetProperty("name").GetString()!;
    static void Need(bool p,string s){if(!p)throw new ArgumentException(s);}
    static int Bits(JsonElement n)=>FixedWidthInteger.Width(n);
    public static bool Same(RecoveredValue a,RecoveredValue b)=>JsonSerializer.Serialize<RecoveredValue>(a)==JsonSerializer.Serialize<RecoveredValue>(b);
    public static RecoveredValue Op(string op,RecoveredValue a,RecoveredValue b,int bits)
    {
        if(op=="Sar")return FixedWidthInteger.ArithmeticShift(a,b,bits);
        Need(op is "Add" or "Sub" or "And" or "Or" or "Xor" or "Shr" or "Shl" or "Eq" or "Ne" or "Ult" or "Mul","graph_binary");
        if(op=="Add"&&a is SegmentInput seg)return new SegmentedAddress(seg,b);
        if(Same(a,b)){if(op is "And" or "Or")return a;if(op is "Xor" or "Sub" or "Ne" or "Ult")return new Constant(0,bits);if(op=="Eq")return new Constant(1,1);}
        if(b is Constant{Value:0}) {if(op is "Add" or "Sub" or "Or" or "Xor")return a;if(op=="And")return new Constant(0,bits);if(a is BitValue{Operation:"Eq",Operands.Length:2} e&&op=="Eq")return new BitValue("Ne",e.Operands,1);}
        if(a is Constant{Value:0}&&op=="Or")return b;
        if(a is Constant l&&b is Constant r){ulong x=l.Value,y=r.Value;ulong z=op switch{"Add"=>unchecked(x+y),"Sub"=>unchecked(x-y),"Mul"=>unchecked(x*y),"And"=>x&y,"Or"=>x|y,"Xor"=>x^y,"Shr" when y<64=>x>>(int)y,"Shl" when y<64=>x<<(int)y,"Eq"=>x==y?1UL:0UL,"Ne"=>x!=y?1UL:0UL,"Ult"=>x<y?1UL:0UL,_=>throw new ArgumentException("graph_shift")};return new Constant(bits==64?z:z&((1UL<<bits)-1),bits);}
        return new BitValue(op,[a,b],bits);
    }
    static int Width(RecoveredValue x)=>x switch{Constant c=>c.Bits,BitValue b=>b.Bits,MemoryReadValue m=>m.Bits,WrappedStackAddress s=>s.Bits,_=>64};
    static RecoveredValue Cast(string op,RecoveredValue x,int width)
    {
        if(x is Constant c)return new Constant(width==64?c.Value:c.Value&((1UL<<width)-1),width);
        if(op=="Zext"&&Width(x)<=width)return x;
        if(op=="Trunc"&&Width(x)<=width)return x;
        if(op=="Trunc"&&x is BitValue b&&b.Operation is "Add" or "Sub" or "And" or "Or" or "Xor"&&b.Operands.Length==2)return Op(b.Operation,Cast("Trunc",b.Operands[0],width),Cast("Trunc",b.Operands[1],width),width);
        if(width is 32 or 64&&StackOffset(x)!=null)return x;
        return new BitValue(op,[x],width);
    }
    static JsonElement[] Nodes(JsonElement row)=>row.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();
    static JsonElement? Branch(JsonElement row){var n=Nodes(row);return n.Length>0&&Tag(n[^1])=="IlBranch"?n[^1]:null;}
    static long? StackOffset(RecoveredValue v)=>v switch{WrappedStackAddress s=>s.Offset,RegisterInput{Index:4}=>0,AddValue{Left:RegisterInput{Index:4}} a=>a.Offset,SegmentedAddress{Segment:{Index:2},Offset:var x}=>StackOffset(x),_=>null};
    public static GraphFunction Raise(JsonElement lift)
    {
        try{return Checked(lift);}catch(OverflowException){throw new ArgumentException("graph_numeric_budget");}
    }
    static GraphFunction Checked(JsonElement lift)
    {
        Need(lift.GetProperty("mode").GetString()=="Bits32"&&lift.GetProperty("decode_complete").GetBoolean()&&lift.GetProperty("lift_errors").GetInt32()==0&&lift.GetProperty("opaque_instructions").GetInt32()==0,"graph_incomplete_lift");var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length is >0 and <=256,"graph_instruction_budget");var index=new Dictionary<ulong,int>();ulong pc=rows[0].GetProperty("pc").GetUInt64();
        foreach(var row in rows){int len=row.GetProperty("length").GetInt32();var p=row.GetProperty("decoded").GetProperty("P");Need(row.GetProperty("pc").GetUInt64()==pc&&len is >0 and <=15&&row.GetProperty("raw_hex").GetString()!.Length==len*2&&Tag(row.GetProperty("tree"))=="IlBlock"&&!p.GetProperty("Lock").GetBoolean()&&!p.GetProperty("Rep").GetBoolean()&&!p.GetProperty("RepNz").GetBoolean(),"graph_boundary_or_prefix");index.Add(pc,index.Count);pc+=(ulong)len;}
        var starts=new SortedSet<int>{0};var branchTargets=new Dictionary<int,int>();
        for(int i=0;i<rows.Length;i++)if(Branch(rows[i]) is JsonElement br){string kind=Name(br,"Kind");Need(kind is "Jmp" or "CondJmp" or "Ret","graph_external_call_or_branch");if(kind!="Ret"){var target=br.GetProperty("Target");Need(Tag(target)=="IlConst"&&Bits(target) is 32 or 64&&ulong.TryParse(target.GetProperty("Bits").GetProperty("decimal").GetString(),out var dest)&&index.ContainsKey(dest),"graph_direct_internal_branch_required");int at=index[ulong.Parse(target.GetProperty("Bits").GetProperty("decimal").GetString()!)];starts.Add(at);branchTargets[i]=at;}if(i+1<rows.Length)starts.Add(i+1);}
        var ranges=starts.ToArray();var startPc=ranges.ToDictionary(i=>i,i=>rows[i].GetProperty("pc").GetUInt64());var incoming=new Dictionary<int,long>{{0,0}};var pending=new Queue<int>();pending.Enqueue(0);var blocks=new Dictionary<int,GraphBlock>();
        while(pending.TryDequeue(out int begin)) {
            if(blocks.ContainsKey(begin))continue;Need(blocks.Count<64,"graph_block_budget");int pos=Array.IndexOf(ranges,begin);int end=pos+1<ranges.Length?ranges[pos+1]:rows.Length;ulong blockPc=startPc[begin];long sp=incoming[begin];var regs=Enumerable.Range(0,16).Where(i=>i!=4).ToDictionary(i=>i,i=>(RecoveredValue)new BlockRegisterValue(blockPc,i));var flags=Enumerable.Range(0,32).ToDictionary(i=>i,i=>(RecoveredValue)new BlockFlagValue(blockPc,i));var effects=new List<GraphEffect>();RecoveredValue? condition=null,retTarget=null;int? cleanup=null;var edges=new List<GraphEdge>();int ordinal=0;
            for(int at=begin;at<end;at++) {
                var row=rows[at];ulong origin=row.GetProperty("pc").GetUInt64();var temp=new Dictionary<int,RecoveredValue>();var nodes=Nodes(row);string? branchKind=Branch(row) is JsonElement branch?Name(branch,"Kind"):null;
                RecoveredValue Eval(JsonElement n) {
                    switch(Tag(n)) {
                    case "IlConst":int bits=Bits(n);Need(ulong.TryParse(n.GetProperty("Bits").GetProperty("decimal").GetString(),out var c)&&(bits==64||c<(1UL<<bits)),"graph_constant");return new Constant(c,bits);
                    case "IlUndefined":throw new ArgumentException("graph_undefined_architectural_value:"+n.GetProperty("Reason").GetString());
                    case "IlReadReg":int i=n.GetProperty("Idx").GetInt32();string kind=Name(n,"Kind");if(kind=="X86Seg"){Need(i is >=0 and <6,"graph_segment");return new SegmentInput(i);}if(kind=="Eflags"){Need(flags.ContainsKey(i),"graph_flag");return flags[i];}Need(kind=="X86"&&i is >=0 and <16,"graph_register");return i==4?new WrappedStackAddress(sp):regs[i];
                    case "IlTmp":Need(temp.TryGetValue(n.GetProperty("Id").GetInt32(),out var t),"graph_temp_before_definition");return t!;
                    case "IlCast":var x=Eval(n.GetProperty("X"));int w=Bits(n);string cast=Name(n,"Kind");if(cast is "Sext" or "Bitcast")return FixedWidthInteger.Cast(cast,x,Bits(n.GetProperty("X")),w);Need(cast is "Trunc" or "Zext","graph_cast");return Cast(cast,x,w);
                    case "IlBin":FixedWidthInteger.ValidateSignedBinary(n);var left=Eval(n.GetProperty("L"));var right=Eval(n.GetProperty("R"));string op=Name(n,"Op");if(op is "Add" or "Sub"&&right is Constant delta&&StackOffset(left) is long offset){Need(delta.Value<=4096,"graph_stack_adjustment_budget");return new WrappedStackAddress(checked(offset+(op=="Sub"?-(long)delta.Value:(long)delta.Value)));}return Op(op,left,right,Bits(n));
                    case "IlLoad":var addr=Eval(n.GetProperty("Addr"));int b=Bits(n);Need(b is 8 or 16 or 32,"graph_memory_width");var memory=new MemoryReadValue(addr,b,origin,0,++ordinal);effects.Add(new("memory_read",origin,addr,memory,b));return memory;
                    default:throw new ArgumentException("graph_expression:"+Tag(n));
                    }
                }
                foreach(var n in nodes) {
                    if(Tag(n)=="IlLet"){Need(temp.TryAdd(n.GetProperty("Id").GetInt32(),Eval(n.GetProperty("Val"))),"graph_duplicate_temp");continue;}
                    if(Tag(n)=="IlWriteReg") {var value=Eval(n.GetProperty("Val"));int reg=n.GetProperty("Idx").GetInt32();string k=Name(n,"Kind");if(k=="Eflags"){Need(flags.ContainsKey(reg)&&Bits(n.GetProperty("Val"))==1,"graph_flag_write");flags[reg]=value;effects.Add(new("flag_write",origin,null,value,1,reg));}else{Need(k=="X86"&&reg is >=0 and <16,"graph_register_write");if(reg==4){Need(StackOffset(value) is long,"graph_nonrelative_SP");sp=StackOffset(value)!.Value;Need(sp%4==0&&sp>=-4096&&sp<=(branchKind=="Ret"?4096:0),"graph_SP_alignment_or_extent");}else regs[reg]=value;effects.Add(new("register_write",origin,null,value,Bits(n.GetProperty("Val")),reg));}continue;}
                    if(Tag(n)=="IlStore"){var address=Eval(n.GetProperty("Addr"));var value=Eval(n.GetProperty("Val"));int b=Bits(n.GetProperty("Val"));Need(b is 8 or 16 or 32,"graph_memory_width");effects.Add(new("memory_store",origin,address,value,b));continue;}
                    Need(Tag(n)=="IlBranch"&&n.Equals(nodes[^1])&&at==end-1,"graph_nonterminal_effect");if(branchKind=="Ret"){cleanup=X86StackArgumentRecovery.RetCleanup(row);X86StackArgumentRecovery.VerifyReturnTree(row,cleanup.Value);retTarget=Eval(n.GetProperty("Target"));Need(sp==4+cleanup,"graph_unbalanced_return");}else {Need(n.GetProperty("Cond").ValueKind==(branchKind=="Jmp"?JsonValueKind.Null:JsonValueKind.Object),"graph_branch_condition");if(branchKind=="CondJmp"){Need(Bits(n.GetProperty("Cond"))==1,"graph_condition_width");condition=Eval(n.GetProperty("Cond"));}edges.Add(new(startPc[branchTargets[at]],branchKind=="CondJmp"?true:null));if(branchKind=="CondJmp"){Need(end<rows.Length,"graph_fallthrough_outside");edges.Add(new(startPc[end],false));}}
                }
            }
            if(edges.Count==0&&cleanup==null){Need(end<rows.Length,"graph_fallthrough_outside");edges.Add(new(startPc[end]));}
            blocks[begin]=new(blockPc,incoming[begin],effects.ToArray(),regs,flags,condition,edges.ToArray(),retTarget,cleanup);
            foreach(var edge in edges){int next=index[edge.Target];if(incoming.TryGetValue(next,out long old))Need(old==sp,"graph_inconsistent_SP_join");else {incoming[next]=sp;pending.Enqueue(next);}}
        }
        Need(blocks.Count==ranges.Length,"graph_unreachable_instruction");var values=blocks.Values.OrderBy(b=>b.Pc).ToArray();var all=values.Select(b=>b.Pc).ToHashSet();var dom=values.ToDictionary(b=>b.Pc,b=>b.Pc==values[0].Pc?new HashSet<ulong>{b.Pc}:new HashSet<ulong>(all));bool changed;do{changed=false;foreach(var b in values.Skip(1)){var pred=values.Where(p=>p.Edges.Any(e=>e.Target==b.Pc)).ToArray();Need(pred.Length>0,"graph_missing_predecessor");var d=new HashSet<ulong>(dom[pred[0].Pc]);foreach(var p in pred.Skip(1))d.IntersectWith(dom[p.Pc]);d.Add(b.Pc);if(!d.SetEquals(dom[b.Pc])){dom[b.Pc]=d;changed=true;}}}while(changed);
        var loops=new List<NaturalLoop>();foreach(var latch in values)foreach(var edge in latch.Edges.Where(e=>dom[latch.Pc].Contains(e.Target))){ulong head=edge.Target;var members=new HashSet<ulong>{head,latch.Pc};var work=new Stack<ulong>();if(head!=latch.Pc)work.Push(latch.Pc);while(work.TryPop(out ulong item))foreach(var p in values.Where(p=>p.Edges.Any(e=>e.Target==item)))if(members.Add(p.Pc)&&p.Pc!=head)work.Push(p.Pc);Need(members.All(m=>dom[m].Contains(head)),"graph_irreducible_loop");loops.Add(new(head,latch.Pc,members.Order().ToArray(),values.Where(b=>members.Contains(b.Pc)).SelectMany(b=>b.Edges).Where(e=>!members.Contains(e.Target)).Select(e=>e.Target).Distinct().Order().ToArray()));}
        // Every nonforward edge must be a dominance backedge, never an ignored cycle.
        Need(values.All(b=>b.Edges.All(e=>e.Target>b.Pc||loops.Any(l=>l.Latch==b.Pc&&l.Header==e.Target))),"graph_unstructured_cycle");
        return new(values,loops.ToArray(),rows.Select(r=>r.GetProperty("pc").GetUInt64()).ToArray(),"ordered loads and stores; no forwarding or nonalias assumption, including entry return address and saved registers; flat32 segments remain explicit for profile interpretation");
    }
}
