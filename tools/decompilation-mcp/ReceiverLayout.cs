using System.Text.Json;
namespace Decompilation;
public sealed record ReceiverGuard(ulong Pc,bool Taken);
public sealed record ReceiverGuardPath(int FlowPathIndex,ReceiverGuard[] Conditions);
public sealed record ReceiverAccess(ulong Pc,string Kind,int WidthBits,uint? FixedOffset,RecoveredValue? Index,ReceiverGuardPath[] PathGuards,string Basis);
public sealed record ReceiverSlot(uint Offset,int ObservedBytes,int[] AccessWidths,ulong[] Origins,bool OverlapAmbiguous,bool IndexedOverlapPossible,bool DeclaredFieldSizeKnown=false,string DeclaredType="unknown");
public sealed record ReceiverLayout(string ReceiverIdentity,ReceiverAccess[] Accesses,ReceiverSlot[] Slots,int UnclassifiedMemorySites,uint MinimumFixedAccessSpan,bool AllocatedObjectExtentKnown=false,bool CrossMethodTypeMerge=false,string[]? Limitations=null);
public static class ReceiverLayoutRecovery
{
    static RecoveredValue Low(RecoveredValue v)=>v is BitValue{Operation:"Trunc" or "Zext",Bits:32 or 64,Operands.Length:1} b?Low(b.Operands[0]):v;
    static bool Receiver(RecoveredValue raw)=>Low(raw) switch{RegisterInput{Index:1}=>true,AddValue a=>Receiver(a.Left),BitValue b=>b.Operands.Any(Receiver),SegmentedAddress s=>Receiver(s.Offset),_=>false};
    static (uint Offset,RecoveredValue? Index)? Address(RecoveredValue raw)
    {
        var v=Low(raw);if(v is RegisterInput{Index:1})return (0,null);if(v is SegmentedAddress{Segment:{Index:3},Offset:var x})return Address(x);
        if(v is AddValue a&&Address(a.Left) is var p&&p!=null)return (unchecked(p.Value.Offset+(uint)a.Offset),p.Value.Index);
        if(v is BitValue{Operation:"Add",Operands.Length:2} sum){var left=Address(sum.Operands[0]);var right=Address(sum.Operands[1]);if(left!=null&&right!=null)return null;var known=left??right;var other=Low(left!=null?sum.Operands[1]:sum.Operands[0]);if(known==null||Receiver(other))return null;if(other is Constant c)return (unchecked(known.Value.Offset+(uint)c.Value),known.Value.Index);return (known.Value.Offset,known.Value.Index==null?other:new BitValue("Add",[known.Value.Index,other],32));}
        return null;
    }
    public static ReceiverLayout Observe(FlowFunction flow)
    {
        var paths=flow.NormalPaths.Select(p=>(p.Predicates,p.Effects)).Concat((flow.TerminalPaths??[]).Select(p=>(p.Predicates,p.Effects))).ToArray();var accesses=new List<(FlowEffect Effect,ReceiverGuardPath Guards,(uint Offset,RecoveredValue? Index)? Address)>();
        for(int pathIndex=0;pathIndex<paths.Length;pathIndex++){var path=paths[pathIndex];foreach(var effect in path.Effects.Where(e=>e.Kind is "memory_read" or "memory_store"))accesses.Add((effect,new ReceiverGuardPath(pathIndex,path.Predicates.Select(p=>new ReceiverGuard(p.Pc,p.Taken)).ToArray()),Address(effect.Address!)));}
        var sites=accesses.Where(a=>a.Address!=null).GroupBy(a=>JsonSerializer.Serialize(new{a.Effect.Pc,a.Effect.Kind,a.Effect.Bits,offset=a.Address!.Value.Offset,index=a.Address.Value.Index})).Select(g=>{var a=g.First();return new ReceiverAccess(a.Effect.Pc,a.Effect.Kind,a.Effect.Bits,a.Address!.Value.Offset,a.Address.Value.Index,g.Select(x=>x.Guards).ToArray(),"entry GPR1 receiver lineage; explicit unsigned32 address adjustment; access width is not declared field size");}).ToArray();
        var fixedSites=sites.Where(a=>a.Index==null&&a.FixedOffset<=4096&&a.WidthBits is 8 or 16 or 32&&a.FixedOffset+(uint)(a.WidthBits/8)<=4096).ToArray();var intervals=fixedSites.Select(a=>(Offset:a.FixedOffset!.Value,Size:a.WidthBits/8)).Distinct().ToArray();bool indexed=sites.Any(a=>a.Index!=null);
        var slots=intervals.Select(i=>new ReceiverSlot(i.Offset,i.Size,fixedSites.Where(a=>a.FixedOffset==i.Offset&&a.WidthBits/8==i.Size).Select(a=>a.WidthBits).Distinct().Order().ToArray(),fixedSites.Where(a=>a.FixedOffset==i.Offset&&a.WidthBits/8==i.Size).Select(a=>a.Pc).Distinct().Order().ToArray(),intervals.Any(j=>j!=i&&i.Offset<j.Offset+j.Size&&j.Offset<i.Offset+i.Size),indexed)).OrderBy(s=>s.Offset).ThenBy(s=>s.ObservedBytes).ToArray();
        return new("entry-x86-GPR1; type identity unknown",sites,slots,accesses.Where(a=>a.Address==null).Select(a=>a.Effect.Pc).Distinct().Count(),slots.Select(s=>s.Offset+(uint)s.ObservedBytes).DefaultIfEmpty(0u).Max(),Limitations:["minimum span is a fixed-access observation, never an allocation extent or array bound","overlaps retain union ambiguity; indexed accesses may overlap every slot","no type merging across methods without receiver/type evidence","raw byte access views preserve unknown padding and field types"]);
    }
    // Neutral unsigned access carriers, not recovered original declarations.
    // Pack1 avoids adding an unproved receiver-alignment premise on x86.
    // Dynamic byte accesses and memcpy fallbacks may alias these fields.
    public static ReceiverSlot[] TypedWordSlots(ReceiverLayout layout)=>layout.Slots.Where(s=>!s.OverlapAmbiguous&&s.ObservedBytes==4&&s.AccessWidths.SequenceEqual(new[]{32})&&s.Offset%4==0&&s.Offset<=4092).ToArray();
    public static string[] TypedMembers(ReceiverSlot[] slots)
    {
        var lines=new List<string>();uint cursor=0;
        foreach(var s in slots){if(s.Offset>cursor)lines.Add($"    unsigned char unknown_{cursor:x4}[{s.Offset-cursor}];");lines.Add($"    unsigned int field_{s.Offset:x4};");cursor=s.Offset+4;}
        return lines.ToArray();
    }
    public static string[] AccessView(ReceiverLayout layout)
    {
        var slots=layout.Slots.Where(s=>!s.OverlapAmbiguous).ToArray();if(slots.Length==0)return [];var lines=new List<string>{"// Observed access-slot view; actual field types, sizes and object extent remain unknown.","struct ReceiverAccessView {"};uint cursor=0;
        foreach(var slot in slots){if(slot.Offset>cursor)lines.Add($"    unsigned char unknown_{cursor:x4}[{slot.Offset-cursor}];");lines.Add($"    unsigned char access_{slot.Offset:x4}[{slot.ObservedBytes}];");cursor=slot.Offset+(uint)slot.ObservedBytes;}
        lines.Add("};");lines.Add($"typedef char checked_receiver_access_view[(sizeof(ReceiverAccessView) == {cursor}u) ? 1 : -1];");lines.Add("enum ReceiverAccessOffsets {");foreach(var slot in slots)lines.Add($"    receiver_access_{slot.Offset:x4} = {slot.Offset}u,");lines.Add("};");return lines.ToArray();
    }
}
