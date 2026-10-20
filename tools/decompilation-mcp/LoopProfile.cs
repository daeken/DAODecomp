using System.Text.Json;
namespace Decompilation;

public sealed record OrderedWordTransfer(int SourceOffset,int DestinationOffset,ulong ReadPc,ulong StorePc);
public sealed record CountedMemoryLoop(GraphFunction Graph,int CountArgument,int SourceArgument,int DestinationArgument,uint DestinationStride,int[] PointerInputOrder,OrderedWordTransfer[] Transfers,string[] Hypotheses);

// Compiler spelling for a bounded reducible count-down loop. Recognition uses
// SSA effects/edges, never opcode bytes, function identity or expected output.
public static class Vc8LoopsProfile
{
    public const string Version="vc8-x86-flat32-ordered-counted-loops-v1";
    static void Need(bool p,string s){if(!p)throw new ArgumentException(s);}
    static RecoveredValue Low(RecoveredValue v)=>v is BitValue{Operation:"Trunc",Bits:32,Operands.Length:1} t?Low(t.Operands[0]):v;
    static int? Reg(RecoveredValue v,ulong block)=>Low(v) is BlockRegisterValue r&&r.Block==block?r.Register:null;
    static long? Stack(RecoveredValue v)=>v switch{WrappedStackAddress w=>w.Offset,AddValue{Left:RegisterInput{Index:4}} a=>a.Offset,SegmentedAddress{Segment:{Index:2},Offset:var x}=>Stack(x),_=>null};
    static (int Register,int Offset)? Address(RecoveredValue v,ulong block)
    {
        v=Low(v);if(v is SegmentedAddress a){Need(a.Segment.Index==3,"loop_nonflat_data_segment");v=Low(a.Offset);}
        if(Reg(v,block) is int reg)return (reg,0);
        if(v is BitValue{Operation:"Add",Operands.Length:2} b&&Reg(b.Operands[0],block) is int r&&b.Operands[1] is Constant{Value:<=4096} c)return (r,(int)c.Value);
        return null;
    }
    static bool Unchanged(GraphBlock block,int reg)=>Reg(block.Registers[reg],block.Pc)==reg;
    static int Argument(MemoryReadValue read){Need(read.Bits==32&&Stack(read.Address) is >=4 and <=64&&Stack(read.Address)%4==0,"loop_incoming_word");return checked((int)Stack(read.Address)!.Value/4-1);}
    static bool Zero(RecoveredValue? v,string operation,out RecoveredValue tested)
    {
        if(v is BitValue{Operation:var op,Operands.Length:2} b&&op==operation&&b.Operands[1] is Constant{Value:0}){tested=b.Operands[0];return true;}tested=new UnknownValue("not_zero_test");return false;
    }
    public static CountedMemoryLoop Raise(JsonElement lift)
    {
        var graph=X86GraphRecovery.Raise(lift);Need(graph.Loops.Length==1,"loop_one_natural_loop_required");var loop=graph.Loops[0];Need(loop.Blocks.Length==3&&loop.Exits.Length==1,"loop_guarded_body_latch_domain");var map=graph.Blocks.ToDictionary(b=>b.Pc);var head=map[loop.Header];var latch=map[loop.Latch];Need(head.Pc!=latch.Pc&&head.Edges.Length==2&&latch.Edges.Length==2,"loop_conditional_header_and_latch");
        Need(Zero(latch.Predicate,"Ne",out var decremented)&&decremented is BitValue{Operation:"Sub",Operands.Length:2} sub&&sub.Operands[1] is Constant{Value:1}&&Reg(sub.Operands[0],latch.Pc)!=null,"loop_count_down_one_required");int count=Reg(((BitValue)decremented).Operands[0],latch.Pc)!.Value;
        Need(X86GraphRecovery.Same(latch.Registers[count],decremented)&&latch.Edges.Any(e=>e.Taken==true&&e.Target==head.Pc)&&latch.Edges.Any(e=>e.Taken==false&&e.Target==loop.Exits[0]),"loop_count_backedge");
        Need(Zero(head.Predicate,"Eq",out var pointer)&&Reg(pointer,head.Pc)!=null,"loop_null_destination_guard");int dst=Reg(pointer,head.Pc)!.Value;Need(dst!=count&&head.Edges.Any(e=>e.Taken==true&&e.Target==latch.Pc),"loop_null_guard_must_reach_latch");ulong bodyPc=head.Edges.Single(e=>e.Taken==false).Target;Need(loop.Blocks.Contains(bodyPc)&&bodyPc!=head.Pc&&bodyPc!=latch.Pc,"loop_body_domain");var body=map[bodyPc];Need(body.Edges.Length==1&&body.Edges[0].Target==latch.Pc&&body.Predicate==null,"loop_body_single_latch");
        Need(latch.Registers[dst] is BitValue{Operation:"Add",Operands.Length:2} increment&&Reg(increment.Operands[0],latch.Pc)==dst&&increment.Operands[1] is Constant{Value:>0 and <=4096},"loop_destination_constant_stride");uint stride=(uint)((Constant)((BitValue)latch.Registers[dst]).Operands[1]).Value;
        Need(head.Effects.All(e=>e.Kind=="flag_write")&&latch.Effects.All(e=>e.Kind=="flag_write"||(e.Kind=="register_write"&&e.Register is int r&&(r==dst||r==count))),"loop_extra_header_or_latch_effect");
        var memory=body.Effects.Where(e=>e.Kind is "memory_read" or "memory_store").ToArray();Need(memory.Length is >=2 and <=32&&memory.Length%2==0&&body.Effects.All(e=>e.Kind is "memory_read" or "memory_store" or "register_write"),"loop_ordered_transfer_domain");int? source=null;var transfers=new List<OrderedWordTransfer>();var scratch=new HashSet<int>();
        for(int i=0;i<memory.Length;i+=2){var read=memory[i];var store=memory[i+1];Need(read.Kind=="memory_read"&&store.Kind=="memory_store"&&read.Bits==32&&store.Bits==32&&X86GraphRecovery.Same(read.Value,store.Value),"loop_alternating_word_read_store_required");var from=Address(read.Address!,body.Pc);var to=Address(store.Address!,body.Pc);Need(from!=null&&to!=null&&to.Value.Register==dst&&from.Value.Register!=dst&&from.Value.Register!=count,"loop_transfer_address");source??=from!.Value.Register;Need(source==from!.Value.Register,"loop_single_invariant_source");transfers.Add(new(from.Value.Offset,to!.Value.Offset,read.Pc,store.Pc));}
        foreach(var e in body.Effects.Where(e=>e.Kind=="register_write")){Need(e.Register is int r&&r!=source&&r!=dst&&r!=count&&memory.Any(m=>m.Kind=="memory_read"&&X86GraphRecovery.Same(m.Value,e.Value)),"loop_body_non_scratch_register_write");scratch.Add(e.Register!.Value);}
        Need(source!=null&&new[]{head,latch,body}.All(b=>Unchanged(b,source!.Value))&&Enumerable.Range(0,16).Where(r=>r!=4&&r!=count&&r!=dst&&!scratch.Contains(r)).All(r=>new[]{head,latch,body}.All(b=>Unchanged(b,r))),"loop_unmodeled_register_update");
        // Require the sole loop entry to have a zero-count bypass. All outside
        // blocks must be this entry, one preparation, one restoration and RET.
        var entry=graph.Blocks[0];Need(Zero(entry.Predicate,"Eq",out var initialCount)&&initialCount is MemoryReadValue,"loop_initial_zero_count_guard");int countArg=Argument((MemoryReadValue)initialCount);Need(entry.Registers[count] is MemoryReadValue cm&&X86GraphRecovery.Same(cm,initialCount),"loop_count_input_binding");var pre=map[entry.Edges.Single(e=>e.Taken==false).Target];var done=map[entry.Edges.Single(e=>e.Taken==true).Target];var restore=map[loop.Exits[0]];
        Need(pre.Pc!=head.Pc&&pre.Edges.Length==1&&pre.Edges[0].Target==head.Pc&&pre.Predicate==null&&restore.Edges.Length==1&&restore.Edges[0].Target==done.Pc&&done.Edges.Length==0&&done.ReturnCleanup==0&&graph.Blocks.Length==7,"loop_entry_exit_structure");
        Need(pre.Registers[dst] is MemoryReadValue&&pre.Registers[source!.Value] is MemoryReadValue,"loop_pointer_input_bindings");int dstArg=Argument((MemoryReadValue)pre.Registers[dst]),srcArg=Argument((MemoryReadValue)pre.Registers[source!.Value]);Need(new[]{countArg,dstArg,srcArg}.Distinct().Count()==3,"loop_distinct_input_slots");
        Need(entry.Effects.Where(e=>e.Kind!="flag_write").All(e=>e.Kind=="memory_read"&&X86GraphRecovery.Same(e.Value,initialCount)||e.Kind=="register_write"&&e.Register==count&&X86GraphRecovery.Same(e.Value,initialCount)),"loop_extra_entry_effect");
        var saves=pre.Effects.Where(e=>e.Kind=="memory_store").ToArray();var restores=restore.Effects.Where(e=>e.Kind=="memory_read").ToArray();Need(saves.Length==scratch.Count&&restores.Length==scratch.Count&&scratch.Count is >0 and <=4&&pre.EntrySp==0&&head.EntrySp==-4*scratch.Count&&restore.EntrySp==head.EntrySp&&done.EntrySp==0,"loop_private_save_extent");
        foreach(int reg in scratch){var save=saves.SingleOrDefault(e=>Reg(e.Value,pre.Pc)==reg);Need(save!=null&&save.Bits==32&&Stack(save.Address!) is long slot&&slot>=head.EntrySp&&slot<0&&slot%4==0,"loop_saved_register_word");var read=restores.SingleOrDefault(e=>e.Bits==32&&Stack(e.Address!)==Stack(save!.Address!));Need(read!=null&&X86GraphRecovery.Same(restore.Registers[reg],read.Value),"loop_restored_register_load");}
        Need(pre.Effects.All(e=>e.Kind=="memory_store"||e.Kind=="register_write"&&(e.Register==4||e.Register==dst||e.Register==source)||e.Kind=="memory_read"&&(X86GraphRecovery.Same(e.Value,pre.Registers[dst])||X86GraphRecovery.Same(e.Value,pre.Registers[source!.Value])))&&restore.Effects.All(e=>e.Kind=="memory_read"||e.Kind=="register_write"&&(e.Register==4||scratch.Contains(e.Register!.Value))),"loop_extra_preparation_or_restore_effect");
        Need(done.ReturnTarget is MemoryReadValue ret&&Stack(ret.Address)==0&&ret.Bits==32&&done.Effects.Count(e=>e.Kind=="memory_read")==1&&done.Effects.All(e=>e.Kind=="memory_read"||e.Kind=="register_write"&&e.Register==4),"loop_return_target_must_remain_memory_read");
        var preparation=pre.Effects.Where(e=>e.Kind=="memory_read").Select(e=>Argument((MemoryReadValue)e.Value)).ToArray();Need(preparation.Length==2&&preparation.Distinct().Count()==2,"loop_pointer_preparation_order");
        return new(graph,countArg,srcArg,dstArg,stride,preparation,transfers.ToArray(),["flat32 cdecl void source spelling is a compiler hypothesis; architectural EAX/flags/return target remain in the graph","memory operations stay sequential, may alias source/destination/incoming stack/saved words/return address; no copied-block or disjointness claim","saved-register restoration and RET remain memory reads, not an assumed untouched private frame","count and guest address arithmetic wrap modulo32; zero guard precedes pointer inputs; pointer null guard repeats after each stride","volatile parameter access constrains original pointer-input observation order in this compiler profile, not a caller storage qualification fact"]);
    }
    public static string Emit(CountedMemoryLoop ir,uint rva,uint imageBase,string module)
    {
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"unsupported_module_annotation");int arguments=new[]{ir.CountArgument,ir.SourceArgument,ir.DestinationArgument}.Max()+1;
        var lines=new List<string>{"extern \"C\" void * __cdecl memcpy(void *, const void *, unsigned int);","#pragma intrinsic(memcpy)","typedef unsigned int guest_address;","static __forceinline unsigned int read_word(guest_address address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }","static __forceinline void write_word(guest_address address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }",$"// FUNCTION: {module} 0x{imageBase+rva:x8}",$"extern \"C\" void __cdecl fn_{rva:x8}({string.Join(", ",Enumerable.Range(0,arguments).Select(i=>$"{(ir.PointerInputOrder.Contains(i)?"volatile ":"")}unsigned int arg_{i}"))}) {{",$"    unsigned int remaining = arg_{ir.CountArgument};","    if (remaining > 0u) {",};
        foreach(int input in ir.PointerInputOrder)lines.Add($"        guest_address {(input==ir.SourceArgument?"source":"destination")} = arg_{input};");
        lines.AddRange(["        do {","        if (destination != 0u) {"]);
        foreach(var item in ir.Transfers.Select((transfer,index)=>(transfer,index))){var t=item.transfer;lines.Add($"            unsigned int word_{item.index} = read_word(source + {t.SourceOffset}u);");lines.Add($"            write_word(destination + {t.DestinationOffset}u, word_{item.index});");}
        lines.AddRange(["        }","        --remaining;",$"        destination += {ir.DestinationStride}u;","        } while (remaining > 0u);","    }","}"]);return string.Join("\n",lines)+"\n";
    }
}
