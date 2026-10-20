using System.Text.Json;
namespace Decompilation;

// Reuse verified forward paths, but preserve architectural operand provenance
// from the actual typed nodes. Mutable scalar joins avoid duplicating a shared
// suffix merely because its reaching register values differ on two edges.
public static class Vc8MutableMemoryEmitter
{
    sealed record Effect(ulong Pc,string Source);
    sealed record Predicate(ulong Pc,string Source,bool Taken,string? Inverse=null);
    sealed record Path(Predicate[] Predicates,Effect[] Effects,bool Terminal);
    static void Need(bool x,string reason){if(!x)throw new ArgumentException(reason);}
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static string Name(JsonElement n,string p)=>n.GetProperty(p).GetProperty("name").GetString()!;
    static int Bits(JsonElement n)=>n.GetProperty("Ty").GetProperty("Bits").GetInt32();
    static JsonElement[] Nodes(JsonElement row)=>row.GetProperty("tree").GetProperty("Body").EnumerateArray().ToArray();
    static void Dependencies(JsonElement n,HashSet<int> temps,HashSet<int> flags,bool incomingLoad=false)
    {
        if(n.ValueKind==JsonValueKind.Object){if(n.TryGetProperty("type",out _)){if(incomingLoad&&Tag(n)=="IlLoad")return;if(Tag(n)=="IlTmp")temps.Add(n.GetProperty("Id").GetInt32());if(Tag(n)=="IlReadReg"&&Name(n,"Kind")=="Eflags")flags.Add(n.GetProperty("Idx").GetInt32());}foreach(var p in n.EnumerateObject())Dependencies(p.Value,temps,flags,incomingLoad);}
        else if(n.ValueKind==JsonValueKind.Array)foreach(var x in n.EnumerateArray())Dependencies(x,temps,flags,incomingLoad);
    }
    static bool HasLoad(JsonElement n)=>n.ValueKind==JsonValueKind.Object&&(n.TryGetProperty("type",out _)&&Tag(n)=="IlLoad"||n.EnumerateObject().Any(p=>HasLoad(p.Value)))||n.ValueKind==JsonValueKind.Array&&n.EnumerateArray().Any(HasLoad);
    static long? Slot(RecoveredValue v)=>v switch{AddValue{Left:RegisterInput{Index:4}} a=>a.Offset,SegmentedAddress{Segment:{Index:2},Offset:var x}=>Slot(x),_=>null};
    public static string Emit(StructuredMemoryFunction ir,JsonElement lift,uint rva,uint imageBase,uint imageEnd,string module,bool typedReceiver=false)
    {
        Need(ir.TerminalAware,"mutable_requires_explicit_profile");var rows=lift.GetProperty("instructions").EnumerateArray().ToDictionary(r=>r.GetProperty("pc").GetUInt64());var f=ir.Flow;
        var allEffects=f.NormalPaths.SelectMany(p=>p.Effects).Concat((f.TerminalPaths??[]).SelectMany(p=>p.Effects)).ToArray();
        var inputs=allEffects.Where(e=>e.Kind=="incoming_read").Select(e=>(IncomingStackRead)e.Value!).GroupBy(i=>i.Offset).ToDictionary(g=>g.Key,g=>g.Select(i=>i.Bits).Distinct().Single());int argumentCount=f.ReturnCleanupBytes.Single()/4;
        // A byte parameter is not storage for a later full incoming-word write.
        // Refuse mixed-width mutation until separate fullword slot storage exists.
        Need(!allEffects.Where(e=>e.Kind=="incoming_store").Any(e=>inputs.Any(i=>i.Key==Slot(e.Address!)&&i.Value!=32)),"mutable_mixed_width_incoming_store");
        Need(allEffects.Where(e=>e.Kind=="incoming_read").All(e=>e.Value is IncomingStackRead{Bits:8 or 32,MemoryEpoch:0,Offset:>=4} v&&v.Offset%4==0),"mutable_incoming_byte_or_word_precall_slots");
        Need(allEffects.Where(e=>e.Kind=="external_call").All(e=>e.Call!.CalleeCleanup==0&&e.Call.CallerPrivateCleanupBytes==0&&e.Call.CallerCleanup==e.Call.Arguments.Length*4&&e.Call.Arguments.Length is >0 and <=8),"mutable_cdecl_observed_words");
        var typedSlots=typedReceiver&&ir.ReceiverLayout!=null?ReceiverLayoutRecovery.TypedWordSlots(ir.ReceiverLayout):[];
        string? Member(ulong pc,int bits) {
            if(bits!=32||ir.ReceiverLayout==null)return null;
            var accesses=ir.ReceiverLayout.Accesses.Where(a=>a.Pc==pc).ToArray();
            if(accesses.Length==0||accesses.Any(a=>a.Index!=null||a.WidthBits!=32)||accesses.Select(a=>a.FixedOffset).Distinct().Count()!=1)return null;
            var slot=typedSlots.FirstOrDefault(s=>s.Offset==accesses[0].FixedOffset);
            return slot==null?null:$"this->field_{slot.Offset:x4}";
        }
        var declarations=new SortedDictionary<string,string>();var paths=new List<Path>();
        string Temp(ulong pc,int id)=>$"t_{pc:x}_{id}";
        string Type(int bits)=>bits==1?"bool":bits<=32?"unsigned int":bits==64?"unsigned __int64":throw new ArgumentException("mutable_integer_width");
        var allPaths=f.NormalPaths.Select(p=>(p.Predicates,p.Effects,Terminal:false)).Concat((f.TerminalPaths??[]).Select(p=>(p.Predicates,p.Effects,Terminal:true)));
        foreach(var path in allPaths) {
            var effects=path.Effects.GroupBy(e=>e.Pc).ToDictionary(g=>g.Key,g=>g.ToArray());var decisions=path.Predicates.ToDictionary(p=>p.Pc);var sequence=new List<JsonElement>();ulong at=rows.Keys.Min();var visited=new HashSet<ulong>();
            while(true){Need(visited.Add(at)&&rows.TryGetValue(at,out _),"mutable_path_cycle_or_range");var row=rows[at];sequence.Add(row);var body=Nodes(row);var branch=body.LastOrDefault();string? kind=branch.ValueKind==JsonValueKind.Object&&Tag(branch)=="IlBranch"?Name(branch,"Kind"):null;
                if(kind=="Ret"||effects.GetValueOrDefault(at,[]).Any(e=>e.Kind=="terminal_call"))break;
                ulong next=at+(ulong)row.GetProperty("length").GetInt32();if(kind is "Jmp" or "CondJmp"){Need(Tag(branch.GetProperty("Target"))=="IlConst","mutable_direct_branch");if(kind=="Jmp"||decisions[at].Taken)next=ulong.Parse(branch.GetProperty("Target").GetProperty("Bits").GetProperty("decimal").GetString()!);}at=next;
            }
            // Which original pushes are actually observed at an outgoing call?
            // Saved-register words are compiler-owned ABI details, not zeroed data.
            var neededPush=new HashSet<ulong>();var stackOwners=new Dictionary<long,ulong>();
            foreach(var e in path.Effects){if(e.Kind=="stack_store"&&e.Bits==32&&Slot(e.Address!) is long slot)stackOwners[slot]=e.Pc;if(e.Kind=="external_call")for(int i=0;i<e.Call!.Arguments.Length;i++){Need(stackOwners.TryGetValue(e.Call.EntrySp+4+i*4,out var owner),"mutable_outgoing_stack_owner");neededPush.Add(owner);}}
            var liveFlags=new HashSet<int>();var keeps=new Dictionary<ulong,HashSet<int>>();var flagWrites=new Dictionary<ulong,HashSet<int>>();
            foreach(var row in sequence.AsEnumerable().Reverse()){
                ulong pc=row.GetProperty("pc").GetUInt64();var es=effects.GetValueOrDefault(pc,[]);var ns=Nodes(row);var temps=new HashSet<int>();var writes=new HashSet<int>();bool incomingLoad=es.Any(e=>e.Kind is "incoming_read" or "incoming_slot_read");void Mark(JsonElement value)=>Dependencies(value,temps,liveFlags,incomingLoad);
                if(es.Any(e=>e.Kind is "external_call" or "terminal_call")){liveFlags.Clear();keeps[pc]=temps;flagWrites[pc]=writes;continue;}
                bool privatePop=es.Any(e=>e.Kind=="stack_read")&&ns.Any(n=>Tag(n)=="IlWriteReg"&&Name(n,"Kind")=="X86"&&n.GetProperty("Idx").GetInt32()==4);
                foreach(var n in ns.Reverse()){
                    string tag=Tag(n);
                    if(tag=="IlBranch"){if(Name(n,"Kind")=="CondJmp")Mark(n.GetProperty("Cond"));continue;}
                    if(tag=="IlWriteReg") {string kind=Name(n,"Kind");int i=n.GetProperty("Idx").GetInt32();if(kind=="Eflags"){if(liveFlags.Remove(i)){writes.Add(i);Mark(n.GetProperty("Val"));}}else if(i!=4&&!privatePop)Mark(n.GetProperty("Val"));continue;}
                    if(tag=="IlStore") {if(es.Any(e=>e.Kind is "memory_store" or "incoming_store")){if(es.Any(e=>e.Kind=="memory_store"))Mark(n.GetProperty("Addr"));Mark(n.GetProperty("Val"));}continue;}
                    if(tag=="IlLet"){int id=n.GetProperty("Id").GetInt32();Need(!HasLoad(n.GetProperty("Val"))||temps.Contains(id)||!es.Any(e=>e.Kind=="memory_read"),"mutable_unused_memory_effect_requires_observable_read");if(temps.Contains(id))Mark(n.GetProperty("Val"));}
                }
                if(neededPush.Contains(pc)){Need(ns.Length==3&&Tag(ns[0])=="IlLet","mutable_outgoing_push_shape");Mark(ns[0].GetProperty("Val"));}
                keeps[pc]=temps;flagWrites[pc]=writes;
            }
            Need(liveFlags.Count==0,"mutable_unknown_entry_flags");var definedRegs=new HashSet<int>{1};var definedFlags=new HashSet<int>();var flagFacts=new Dictionary<int,(ulong Pc,bool False,string? ZeroOperand)>();var sourceEffects=new List<Effect>();var sourcePredicates=new List<Predicate>();var stackSources=new Dictionary<long,string>();
            foreach(var row in sequence){ulong pc=row.GetProperty("pc").GetUInt64();var es=effects.GetValueOrDefault(pc,[]);var ns=Nodes(row);var tmp=new Dictionary<int,string>();var statements=new List<string>();
                string Value(JsonElement n,bool addressContext=false){int bits=n.TryGetProperty("Ty",out _)?Bits(n):0;switch(Tag(n)){
                    case "IlConst":Need(ulong.TryParse(n.GetProperty("Bits").GetProperty("decimal").GetString(),out var c)&&bits is 1 or 8 or 16 or 32 or 64,"mutable_constant");if(addressContext&&ir.ReceiverLayout!=null&&ir.ReceiverLayout.Slots.Any(s=>!s.OverlapAmbiguous&&s.Offset==c)&&ir.ReceiverLayout.Accesses.Any(a=>a.Pc==pc&&a.Index==null&&a.FixedOffset==c))return $"static_cast<{Type(bits)}>(receiver_access_{c:x4})";return c.ToString()+(bits==64?"ULL":"u");
                    case "IlTmp":Need(tmp.ContainsKey(n.GetProperty("Id").GetInt32()),"mutable_temp_before_definition");return tmp[n.GetProperty("Id").GetInt32()];
                    case "IlReadReg":int i=n.GetProperty("Idx").GetInt32();string k=Name(n,"Kind");if(k=="Eflags"){Need(definedFlags.Contains(i),"mutable_unknown_flag");return "f_"+i;}if(k=="X86Seg"){Need(i is 2 or 3,"mutable_nonflat_segment");return "0u";}Need(k=="X86"&&i!=4&&definedRegs.Contains(i),"mutable_unknown_register");return bits==64?$"static_cast<unsigned __int64>(r_{i})":$"r_{i}";
                    case "IlCast":Need(Name(n,"Kind") is "Trunc" or "Zext","mutable_cast");var operand=n.GetProperty("X");string val=Value(operand,addressContext);return bits switch{1=>$"({val} != 0u)",8=>$"static_cast<unsigned char>({val})",16=>$"static_cast<unsigned short>({val})",32=>$"static_cast<unsigned int>({val})",64=>$"static_cast<unsigned __int64>({val})",_=>throw new ArgumentException("mutable_cast_width")};
                    case "IlBin":string op=Name(n,"Op");Need(op is "Add" or "Sub" or "And" or "Or" or "Xor" or "Shr" or "Shl" or "Eq" or "Ne" or "Ult","mutable_binary");string sign=op switch{"Add"=>"+","Sub"=>"-","And"=>"&","Or"=>"|","Xor"=>"^","Shr"=>">>","Shl"=>"<<","Eq"=>"==","Ne"=>"!=",_=>"<"};return $"({Value(n.GetProperty("L"),addressContext)} {sign} {Value(n.GetProperty("R"),addressContext)})";
                    case "IlLoad":var incoming=es.FirstOrDefault(e=>e.Kind is "incoming_read" or "incoming_slot_read");if(incoming!=null){var offset=Slot(incoming.Address!);Need(offset>=4&&offset%4==0,"mutable_incoming_slot");return $"arg_{offset/4-1}";}Need(es.Any(e=>e.Kind=="memory_read"),"mutable_private_load_not_observed");Need(bits==32,"mutable_memory_width");return Member(pc,bits)??$"read_word(static_cast<unsigned int>({Value(n.GetProperty("Addr"),true)}))";
                    default:throw new ArgumentException("mutable_unknown_expression:"+Tag(n));}}
                if(es.Any(e=>e.Kind=="terminal_call")){var call=es.Single(e=>e.Kind=="terminal_call").TerminalCall!;statements.Add($"fn_{call.Target-imageBase:x8}();");}
                else if(es.Any(e=>e.Kind=="external_call")){var call=es.Single(e=>e.Kind=="external_call").Call!;var args=Enumerable.Range(0,call.Arguments.Length).Select(i=>stackSources.TryGetValue(call.EntrySp+4+i*4,out var value)?value:throw new ArgumentException("mutable_outgoing_value_missing")).ToArray();statements.Add($"fn_{call.Target-imageBase:x8}({string.Join(", ",args)});");foreach(int i in new[]{0,1,2})definedRegs.Remove(i);definedFlags.Clear();flagFacts.Clear();}
                else if(neededPush.Contains(pc)){string name=$"push_{pc:x}";declarations[name]="unsigned int";statements.Add($"{name} = static_cast<unsigned int>({Value(ns[0].GetProperty("Val"))});");var store=es.Single(e=>e.Kind=="stack_store");stackSources[Slot(store.Address!)!.Value]=name;}
                else if(es.Any(e=>e.Kind=="stack_store")&&!es.Any(e=>e.Kind=="incoming_store")){// A private save/allocation remains in IR; no unknown value is materialized.
                    Need(!es.Any(e=>e.Kind is "memory_read" or "incoming_read" or "incoming_slot_read"),"mutable_private_copy_read_not_emittable");
                }
                else {
                    bool pop=es.Any(e=>e.Kind=="stack_read")&&ns.Any(n=>Tag(n)=="IlWriteReg"&&Name(n,"Kind")=="X86"&&n.GetProperty("Idx").GetInt32()==4);
                    foreach(var n in ns){string tag=Tag(n);if(tag=="IlLet"){int id=n.GetProperty("Id").GetInt32();if(keeps[pc].Contains(id)&&!pop){string name=Temp(pc,id);declarations[name]=Type(Bits(n.GetProperty("Val")));statements.Add($"{name} = {Value(n.GetProperty("Val"),Bits(n.GetProperty("Val"))==64&&es.Any(e=>e.Kind is "memory_read" or "memory_store"))};");tmp.Add(id,name);}continue;}
                        if(tag=="IlWriteReg"){int i=n.GetProperty("Idx").GetInt32();string kind=Name(n,"Kind");if(kind=="Eflags"){if(flagWrites[pc].Contains(i)){statements.Add($"f_{i} = {Value(n.GetProperty("Val"))};");declarations["f_"+i]="bool";definedFlags.Add(i);var value=n.GetProperty("Val");bool falseFlag=Tag(value)=="IlConst"&&Bits(value)==1&&value.GetProperty("Bits").GetProperty("decimal").GetString()=="0";string? zeroOperand=null;if(i==6&&Tag(value)=="IlBin"&&Name(value,"Op")=="Eq"&&Tag(value.GetProperty("L"))=="IlTmp"&&Bits(value.GetProperty("L"))==32&&Tag(value.GetProperty("R"))=="IlConst"&&value.GetProperty("R").GetProperty("Bits").GetProperty("decimal").GetString()=="0")zeroOperand=Value(value.GetProperty("L"));flagFacts[i]=(pc,falseFlag,zeroOperand);}}else if(i!=4){if(pop){definedRegs.Remove(i);continue;}statements.Add($"r_{i} = static_cast<unsigned int>({Value(n.GetProperty("Val"))});");declarations["r_"+i]="unsigned int";definedRegs.Add(i);}continue;}
                        if(tag=="IlStore"){var slot=es.FirstOrDefault(e=>e.Kind=="incoming_store");if(slot!=null){Need(Slot(slot.Address!) is >=4,"mutable_incoming_store");statements.Add($"arg_{Slot(slot.Address!)/4-1} = static_cast<unsigned int>({Value(n.GetProperty("Val"))});");}else if(es.Any(e=>e.Kind=="memory_store")){int width=Bits(n.GetProperty("Val"));Need(width is 8 or 32,"mutable_store_width");string address=$"static_cast<unsigned int>({Value(n.GetProperty("Addr"),true)})";var member=Member(pc,width);statements.Add(member!=null?$"{member} = static_cast<unsigned int>({Value(n.GetProperty("Val"))});":width==32?$"write_word({address}, static_cast<unsigned int>({Value(n.GetProperty("Val"))}));":$"*reinterpret_cast<unsigned char *>({address}) = static_cast<unsigned char>({Value(n.GetProperty("Val"))});");}continue;}
                        if(tag=="IlBranch"&&Name(n,"Kind")=="CondJmp"){var cond=n.GetProperty("Cond");string condition=Value(cond);string? inverse=null;bool Flag(JsonElement x,int i)=>Tag(x)=="IlReadReg"&&Name(x,"Kind")=="Eflags"&&x.GetProperty("Idx").GetInt32()==i;if(Tag(cond)=="IlBin"&&Name(cond,"Op")=="Or"&&((Flag(cond.GetProperty("L"),0)&&Flag(cond.GetProperty("R"),6))||(Flag(cond.GetProperty("R"),0)&&Flag(cond.GetProperty("L"),6)))&&flagFacts.TryGetValue(0,out var cf)&&cf.False&&flagFacts.TryGetValue(6,out var zf)&&cf.Pc==zf.Pc&&zf.ZeroOperand!=null){condition=$"({zf.ZeroOperand} <= 0u)";inverse=$"({zf.ZeroOperand} > 0u)";}sourcePredicates.Add(new(pc,condition,decisions[pc].Taken,inverse));}
                    }
                }
                if(statements.Count>0)sourceEffects.Add(new(pc,string.Join("\n",statements)));
            }
            paths.Add(new(sourcePredicates.ToArray(),sourceEffects.ToArray(),path.Terminal));
        }
        var lines=new List<string>{"extern \"C\" void * __cdecl memcpy(void *, const void *, unsigned int);","#pragma intrinsic(memcpy)","static __forceinline unsigned int read_word(unsigned int address) { unsigned int value; memcpy(&value, reinterpret_cast<const void *>(address), 4); return value; }","static __forceinline void write_word(unsigned int address, unsigned int value) { memcpy(reinterpret_cast<void *>(address), &value, 4); }"};
        if(ir.ReceiverLayout!=null)lines.AddRange(ReceiverLayoutRecovery.AccessView(ir.ReceiverLayout));
        foreach(var calls in allEffects.Where(e=>e.Kind=="external_call").GroupBy(e=>e.Call!.Target)){Need(calls.Key>=imageBase&&calls.Key<imageEnd&&calls.Select(e=>e.Call!.Arguments.Length).Distinct().Count()==1,"mutable_call_signature_conflict");lines.Add($"extern \"C\" void __cdecl fn_{calls.Key-imageBase:x8}({string.Join(", ",Enumerable.Repeat("unsigned int",calls.First().Call!.Arguments.Length))});");}
        foreach(var t in (f.TerminalPaths??[]).Select(p=>p.Call.Target).Distinct())lines.Add($"extern \"C\" void __cdecl fn_{t-imageBase:x8}();");
        string parameters=string.Join(", ",Enumerable.Range(0,argumentCount).Select(i=>$"{(inputs.GetValueOrDefault(4+i*4,32)==8?"unsigned char":"unsigned int")} arg_{i}"));if(typedSlots.Length>0){lines.Add("// VC8 compile-time offsetof idiom; no header or runtime null dereference.");lines.Add("#define DAO_ACCESS_OFFSETOF(type, member) ((unsigned int)&(((type *)0)->member))");lines.Add("// Packed access-carrier hypothesis; field widths are observations, object extent/type remain unknown.");lines.Add("#pragma pack(push, 1)");lines.Add("struct Recovered {");lines.AddRange(ReceiverLayoutRecovery.TypedMembers(typedSlots));lines.Add($"    void * fn_{rva:x8}({parameters});");lines.Add("};");lines.Add("#pragma pack(pop)");foreach(var slot in typedSlots)lines.Add($"typedef char checked_field_{slot.Offset:x4}[(DAO_ACCESS_OFFSETOF(Recovered, field_{slot.Offset:x4}) == {slot.Offset}u) ? 1 : -1];");}else lines.Add($"struct Recovered {{ void * fn_{rva:x8}({parameters}); }};");lines.Add($"// FUNCTION: {module} 0x{imageBase+rva:x8}");lines.Add($"void * Recovered::fn_{rva:x8}({parameters}) {{");lines.Add("    unsigned int r_1 = reinterpret_cast<unsigned int>(this);");foreach(var d in declarations.Where(d=>d.Key!="r_1"))lines.Add($"    {d.Value} {d.Key};");
        void Effect(Effect e,int depth){string pad=new(' ',depth*4);foreach(var line in e.Source.Split('\n'))lines.Add(pad+line);}
        void Tree(Path[] group,int depth){Need(group.Length>0,"mutable_empty_tree");int prefix=0;while(group.All(p=>p.Effects.Length>prefix)&&group.All(p=>p.Effects[prefix]==group[0].Effects[prefix]))prefix++;ulong branch=group.Where(p=>p.Predicates.Length>0).Select(p=>p.Predicates[0].Pc).DefaultIfEmpty(ulong.MaxValue).Min();while(prefix>0&&group[0].Effects[prefix-1].Pc>branch)prefix--;foreach(var e in group[0].Effects.Take(prefix))Effect(e,depth);group=group.Select(p=>p with{Effects=p.Effects[prefix..]}).ToArray();if(group.All(p=>p.Predicates.Length==0)){Need(group.All(p=>p.Effects.Length==0),"mutable_unmerged_leaf");return;}Need(group.All(p=>p.Predicates.Length>0&&p.Predicates[0].Pc==branch&&p.Predicates[0].Source==group[0].Predicates[0].Source),"mutable_predicate_join");var common=new HashSet<ulong>(group[0].Effects.Select(e=>e.Pc).Concat(group[0].Predicates.Select(p=>p.Pc)));foreach(var p in group.Skip(1))common.IntersectWith(p.Effects.Select(e=>e.Pc).Concat(p.Predicates.Select(p=>p.Pc)));ulong? join=common.Where(pc=>pc>branch&&group.Select(p=>string.Join("\n",p.Effects.Where(e=>e.Pc==pc).Select(e=>e.Source))+"|"+string.Join("\n",p.Predicates.Where(p=>p.Pc==pc).Select(p=>p.Source))).Distinct().Count()==1).Order().Cast<ulong?>().FirstOrDefault();
            if(join is ulong commonPc){var before=group.Select(p=>p with{Effects=p.Effects.Where(e=>e.Pc<commonPc).ToArray(),Predicates=p.Predicates.Where(q=>q.Pc<commonPc).ToArray(),Terminal=false}).DistinctBy(p=>JsonSerializer.Serialize(p)).ToArray();var after=group.Select(p=>p with{Effects=p.Effects.Where(e=>e.Pc>=commonPc).ToArray(),Predicates=p.Predicates.Where(q=>q.Pc>=commonPc).ToArray()}).DistinctBy(p=>JsonSerializer.Serialize(p)).ToArray();Tree(before,depth);Tree(after,depth);return;}
            int suffix=0;while(group.All(p=>p.Effects.Length>suffix)&&group.All(p=>p.Effects[^(suffix+1)]==group[0].Effects[^(suffix+1)]))suffix++;var tail=group[0].Effects.Skip(group[0].Effects.Length-suffix).ToArray();var yes=group.Where(p=>p.Predicates[0].Taken).Select(p=>p with{Predicates=p.Predicates[1..],Effects=p.Effects[..(p.Effects.Length-suffix)]}).ToArray();var no=group.Where(p=>!p.Predicates[0].Taken).Select(p=>p with{Predicates=p.Predicates[1..],Effects=p.Effects[..(p.Effects.Length-suffix)]}).ToArray();Need(yes.Length>0&&no.Length>0,"mutable_missing_branch");string pad=new(' ',depth*4),condition=group[0].Predicates[0].Source;string Test(bool invert)=>invert?group[0].Predicates[0].Inverse??$"!({condition})":$"({condition})";
            bool yesTerminal=yes.All(p=>p.Terminal),noTerminal=no.All(p=>p.Terminal);if(yesTerminal!=noTerminal){lines.Add($"{pad}if ({Test(!yesTerminal)}) {{");Tree(yesTerminal?yes:no,depth+1);lines.Add(pad+"}");Tree(yesTerminal?no:yes,depth);}else{bool emptyYes=yes.All(p=>p.Predicates.Length==0&&p.Effects.Length==0),emptyNo=no.All(p=>p.Predicates.Length==0&&p.Effects.Length==0);if(!emptyYes||!emptyNo){bool fallthroughFirst=emptyYes||(!emptyYes&&!emptyNo);lines.Add($"{pad}if ({Test(fallthroughFirst)}) {{");Tree(fallthroughFirst?no:yes,depth+1);if(!emptyYes&&!emptyNo){lines.Add(pad+"} else {");Tree(yes,depth+1);}lines.Add(pad+"}");}}foreach(var e in tail)Effect(e,depth);
        }
        Tree(paths.ToArray(),1);lines.Add("    return this;");lines.Add("}");return string.Join("\n",lines)+"\n";
    }
}
