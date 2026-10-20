using System.Text.Json;
namespace Decompilation;

// Instruction-local source compaction, never instruction scheduling. Captured
// values survive any intervening register write, memory event or control edge.
public static class ScalarUseRecovery
{
    static string Tag(JsonElement n)=>n.GetProperty("type").GetString()!.Split('+').Last().Split('.').Last();
    static IEnumerable<JsonElement> Expressions(JsonElement n) {
        if(n.ValueKind==JsonValueKind.Object){if(n.TryGetProperty("type",out _))yield return n;foreach(var p in n.EnumerateObject())foreach(var x in Expressions(p.Value))yield return x;}
        else if(n.ValueKind==JsonValueKind.Array)foreach(var v in n.EnumerateArray())foreach(var x in Expressions(v))yield return x;
    }
    public static HashSet<int> InlineTemps(JsonElement[] nodes,IReadOnlySet<int>? deferredCaptures=null)
    {
        if(nodes.Length>64)throw new ArgumentException("scalar_instruction_budget");
        var definitions=new Dictionary<int,int>();var uses=new Dictionary<int,List<int>>();
        for(int i=0;i<nodes.Length;i++){
            if(Tag(nodes[i])=="IlLet"&&!definitions.TryAdd(nodes[i].GetProperty("Id").GetInt32(),i))throw new ArgumentException("scalar_duplicate_temp");
            foreach(var tmp in Expressions(nodes[i]).Where(n=>Tag(n)=="IlTmp")){int id=tmp.GetProperty("Id").GetInt32();if(!uses.ContainsKey(id))uses[id]=[];uses[id].Add(i);}
        }
        bool Pure(JsonElement value,HashSet<(string,int)> reads,HashSet<int> seen) {
            string kind=Tag(value);if(value.TryGetProperty("Ty",out var type)&&type.GetProperty("Bits").GetInt32() is not (1 or 32 or 64))return false;
            if(kind=="IlTmp"){int id=value.GetProperty("Id").GetInt32();return seen.Add(id)&&definitions.TryGetValue(id,out var at)&&Pure(nodes[at].GetProperty("Val"),reads,seen);}
            if(kind=="IlReadReg"){string bank=value.GetProperty("Kind").GetProperty("name").GetString()!;if(bank is not ("X86" or "Eflags" or "X86Seg"))return false;reads.Add((bank,value.GetProperty("Idx").GetInt32()));return true;}
            if(kind=="IlConst")return true;
            if(kind=="IlCast")return value.GetProperty("Kind").GetProperty("name").GetString() is "Trunc" or "Zext"&&Pure(value.GetProperty("X"),reads,new(seen));
            if(kind=="IlBin")return value.GetProperty("Op").GetProperty("name").GetString() is "Add" or "Sub" or "And" or "Or" or "Xor" or "Eq" or "Ne" or "Ult"&&Pure(value.GetProperty("L"),reads,new(seen))&&Pure(value.GetProperty("R"),reads,new(seen));
            return false; // Loads, undefined values and unfamiliar effects stay captured/refused.
        }
        HashSet<int> ExpandedUses(int id,HashSet<int> seen) {
            if(!seen.Add(id))throw new ArgumentException("scalar_temp_cycle");var result=new HashSet<int>();
            foreach(int use in uses.GetValueOrDefault(id,[])){result.Add(use);if(Tag(nodes[use])=="IlLet")result.UnionWith(ExpandedUses(nodes[use].GetProperty("Id").GetInt32(),new(seen)));}return result;
        }
        var inline=new HashSet<int>();
        foreach(var (id,at) in definitions){if(deferredCaptures?.Contains(id)==true||uses.GetValueOrDefault(id,[]).Count!=1)continue;var reads=new HashSet<(string,int)>();if(!Pure(nodes[at].GetProperty("Val"),reads,[id]))continue;var endpoints=ExpandedUses(id,[]);bool safe=endpoints.All(end=>end>at);
            foreach(int end in endpoints)for(int k=at+1;k<end;k++){
                if(Expressions(nodes[k]).Any(n=>Tag(n) is "IlLoad" or "IlStore" or "IlBranch" or "IlUndefined"))safe=false;
                if(Tag(nodes[k])=="IlWriteReg"&&reads.Contains((nodes[k].GetProperty("Kind").GetProperty("name").GetString()!,nodes[k].GetProperty("Idx").GetInt32())))safe=false;
            }
            if(safe)inline.Add(id);
        }
        return inline;
    }
}
