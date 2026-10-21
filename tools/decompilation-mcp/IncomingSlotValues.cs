namespace Decompilation;

// Source-emission hypothesis only. Architectural incoming-memory versions stay
// in FlowFunction; a fresh C++ carrier does not prove a store/alias unobservable.
// The compiled candidate still requires the unchanged complete native gates.
public static class IncomingSlotValueIdentityRecovery
{
    public const string Version="emit-vc8-incoming-word-value-identities-v1";
    static void Need(bool p,string reason){if(!p)throw new ArgumentException(reason);}
    static long? Slot(RecoveredValue? v)=>v switch{AddValue{Left:RegisterInput{Index:4}} a=>a.Offset,SegmentedAddress{Segment:{Index:2},Offset:var x}=>Slot(x),_=>null};
    public static Dictionary<long,string> Plan(FlowFunction f)
    {
        var paths=f.NormalPaths.Select(p=>p.Effects).Concat((f.TerminalPaths??[]).Select(p=>p.Effects)).ToArray();
        var effects=paths.SelectMany(p=>p).ToArray();var stores=effects.Where(e=>e.Kind=="incoming_store").ToArray();
        if(stores.Length==0)return [];
        Need(!f.Incoming.AddressEscapeObserved,"incoming_identity_frame_escape");
        var slots=stores.Select(e=>Slot(e.Address)).ToArray();
        Need(stores.All(e=>e.Bits==32)&&slots.All(s=>s is >=4&&s%4==0&&s+4<=4+f.Incoming.RequiredReadBytes),"incoming_identity_complete_word_extent");
        var selected=slots.Select(s=>s!.Value).Distinct().Where(s=>effects.Any(e=>e.Kind=="incoming_slot_read"&&Slot(e.Address)==s)).Order().ToDictionary(s=>s,s=>$"slot_value_{s:x4}");
        foreach(var path in paths){var defined=new HashSet<long>();foreach(var e in path){
            if(e.Kind is "external_call" or "terminal_call" or "memory_store")defined.Clear();
            if(e.Kind=="incoming_store"&&Slot(e.Address) is long store&&selected.ContainsKey(store))defined.Add(store);
            if(e.Kind=="incoming_slot_read"&&Slot(e.Address) is long read&&selected.ContainsKey(read))Need(e.Bits==32&&defined.Contains(read),"incoming_identity_unknown_reaching_word");
        }}
        return selected;
    }
}
