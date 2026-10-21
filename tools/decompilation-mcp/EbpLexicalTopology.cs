using System.Text.Json;
namespace Decompilation;

// EH intervals constrain lexical ownership; an unchanged writable machine state
// after a source scope exits does not extend that scope's exception-object life.
public sealed record EbpLexicalScope(int TryLow,int TryHigh,int CatchHigh,int CatchEntry,int? ParentTryLow,string ParentRegion,int ParentState);
public sealed record EbpLexicalTopology(EbpLexicalScope[] Scopes,string Interpretation,bool Proof=false)
{
    public static EbpLexicalTopology Recover(JsonElement graph)
    {
        void Need(bool ok,string why){if(!ok)throw new ArgumentException("EBP_lexical_"+why);}
        var entries=graph.GetProperty("try_map").GetProperty("entries").EnumerateArray()
            .Select(t=>(Low:t.GetProperty("try_low").GetInt32(),High:t.GetProperty("try_high").GetInt32(),End:t.GetProperty("catch_high").GetInt32())).OrderBy(t=>t.Low).ToArray();
        var unwind=graph.GetProperty("unwind_map").GetProperty("transitions").EnumerateArray().ToArray();
        Need(entries.Length is >0 and <=16&&unwind.Length==graph.GetProperty("FuncInfo").GetProperty("states").GetInt32(),"complete_tables");
        Need(entries.Select(t=>t.Low).Distinct().Count()==entries.Length,"unique_try_entries");
        for(int i=0;i<unwind.Length;i++)Need(unwind[i].GetProperty("action_va").GetUInt64()==0&&unwind[i].GetProperty("to_state").GetInt32()>=-1&&unwind[i].GetProperty("to_state").GetInt32()<i,"bounded_unwind");
        foreach(var t in entries)Need(0<=t.Low&&t.Low<=t.High&&t.High<t.End&&t.End<unwind.Length,"ordered_intervals");
        var scopes=new List<EbpLexicalScope>();
        foreach(var child in entries){
            var parents=new List<(int Low,string Region,int State,int Width)>();
            foreach(var parent in entries.Where(t=>t.Low!=child.Low)){
                bool disjoint=child.End<parent.Low||parent.End<child.Low;
                bool insideTry=parent.Low<child.Low&&child.End<=parent.High;
                bool insideCatch=parent.High<child.Low&&child.End<=parent.End;
                bool containsChild=insideTry||insideCatch;
                bool childContains=child.Low<parent.Low&&parent.End<=child.End;
                Need(disjoint||containsChild||childContains,"crossing_intervals");
                if(containsChild)parents.Add((parent.Low,insideCatch?"catch":"try",insideCatch?parent.High+1:parent.Low,parent.End-parent.Low));
            }
            var nearest=parents.OrderBy(p=>p.Width).ToArray();Need(nearest.Length<2||nearest[0].Width<nearest[1].Width,"ambiguous_parent");
            int expected=nearest.Length==0?-1:nearest[0].State;
            Need(unwind[child.Low].GetProperty("to_state").GetInt32()==expected&&unwind[child.High+1].GetProperty("to_state").GetInt32()==expected,"scope_exit_disagrees_with_unwind");
            scopes.Add(new(child.Low,child.High,child.End,child.High+1,nearest.Length==0?null:nearest[0].Low,nearest.Length==0?"function":nearest[0].Region,expected));
        }
        return new(scopes.ToArray(),"Zero-action VC8 try/catch interval containment corroborated by unwind exits; lexical ownership is distinct from residual machine state and does not prove dynamic runtime behavior");
    }
}
