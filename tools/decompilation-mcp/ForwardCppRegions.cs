using System.Text.RegularExpressions;
namespace Decompilation;

// Structure only the labels/branches emitted by the typed effect lowerer. Every
// statement stays on its original path and in order; calls/loads/stores are not
// folded, moved or treated as pure. Non-laminar entry edges refuse the spelling.
public static class ForwardCppRegions
{
    static readonly Regex Label=new(@"^L_[a-z_]+_[0-9a-f]+:;$");
    static readonly Regex Jump=new(@"^(?:if \((.*)\) )?goto (L_[a-z_]+_[0-9a-f]+);$");
    public static string[] Structure(IEnumerable<string> source)
    {
        var lines=source.ToArray();var labels=new Dictionary<string,int>();var edges=new Dictionary<int,(string? Condition,int Target)>();
        for(int i=0;i<lines.Length;i++)if(Label.IsMatch(lines[i].Trim()))labels.Add(lines[i].Trim()[..^2],i);
        for(int i=0;i<lines.Length;i++){
            var m=Jump.Match(lines[i].Trim());if(!m.Success)continue;
            if(!labels.TryGetValue(m.Groups[2].Value,out int target)||target<=i)throw new ArgumentException("EBP_forward_nonforward_target");
            edges.Add(i,(m.Groups[1].Success?m.Groups[1].Value:null,target));
        }
        void SingleEntry(int start,int end,int? allowedEntry){if(edges.Any(e=>(e.Key<start||e.Key>=end)&&e.Value.Target>=start&&e.Value.Target<end&&!(e.Value.Target==start&&e.Key==allowedEntry)))throw new ArgumentException("EBP_forward_cross_entry");}
        List<string> Emit(int start,int end,int indent,int? allowedEntry=null){
            var result=new List<string>();SingleEntry(start,end,allowedEntry);
            for(int i=start;i<end;i++){
                var line=lines[i];if(Label.IsMatch(line.Trim()))continue;
                if(!edges.TryGetValue(i,out var edge)){result.Add(new string(' ',indent)+line);continue;}
                if(edge.Target>end)throw new ArgumentException("EBP_forward_cross_exit");
                if(edge.Condition==null){if(edge.Target!=end)throw new ArgumentException("EBP_forward_unconditional_region");break;}
                int alternative=edge.Target,join=alternative,skip=alternative-1;
                while(skip>i&&Label.IsMatch(lines[skip].Trim()))skip--;
                bool hasElse=edges.TryGetValue(skip,out var exit)&&exit.Condition==null&&exit.Target>alternative;
                if(hasElse){join=exit.Target;if(join>end)throw new ArgumentException("EBP_forward_cross_exit");}
                string pad=new string(' ',indent+line.Length-line.TrimStart().Length);
                result.Add(pad+"if (!("+edge.Condition+")) {");
                result.AddRange(Emit(i+1,hasElse?skip:alternative,indent+2));
                if(hasElse){result.Add(pad+"} else {");result.AddRange(Emit(alternative,join,indent+2,i));}
                result.Add(pad+"}");i=join-1;
            }
            return result;
        }
        return Emit(0,lines.Length,0).ToArray();
    }
}
