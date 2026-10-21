using System.Text.Json;
namespace Decompilation;

public sealed record ScalarPathsFunction(FlowFunction Flow,string[] Hypotheses);
public static class Vc8ScalarPathsProfile
{
    public const string Version="vc8-closed-readonly-scalar-paths-v1";
    static void Need(bool p,string s){if(!p)throw new ArgumentException(s);}
    static bool Same(object a,object b)=>JsonSerializer.Serialize(a)==JsonSerializer.Serialize(b);
    public static ScalarPathsFunction Raise(JsonElement lift) {
        Need(Engine.IsCompleteCallFree(lift),"scalar_closed_control_required");
        var f=X86FlowRecovery.Raise(lift,new(new(Version,0,[1],[0,1,2],[3,5,6,7]),true,true,MaximumPaths:16,DeferredUndefinedFlags:true,ConstantConditionEffects:true),[]);
        Need(f.ReturnCleanupBytes.Length==1&&f.ReturnCleanupBytes[0] is >=0 and <=16&&f.ReturnCleanupBytes[0]%4==0&&!f.Incoming.AddressEscapeObserved&&f.Incoming.RequiredReadBytes<=f.ReturnCleanupBytes[0],"scalar_incoming_extent");
        Need(f.NormalPaths.Length is >=1 and <=12&&(f.FaultPaths??[]).Length==0&&(f.TerminalPaths??[]).Length==0,"scalar_path_domain");
        Need(f.NormalPaths.All(p=>!p.Exit.StackMemoryMayHaveChanged&&p.Effects.All(e=>e.Kind is "register_write" or "flag_write" or "incoming_read" or "stack_read" or "stack_store" or "memory_read")),"scalar_readonly_effect_domain");
        Need(f.NormalPaths.SelectMany(p=>p.Effects).Where(e=>e.Kind=="incoming_read").All(e=>e.Value is IncomingStackRead{Bits:32,MemoryEpoch:0} input&&input.Offset>=4&&input.Offset%4==0),"scalar_word_inputs_required");
        return new(f,["flat32 thiscall word parameters and word result are compiler hypotheses; full native comparison required","ordered faulting reads and exact modular typed arithmetic; no object extent, nonalias or valid-pointer assertion","original stack/register/flag effects remain in FlowIR; source proposal alone does not discharge physical/fault-context obligations"]);
    }
    sealed record Path(FlowPredicate[] Predicates,FlowEffect[] Effects,RecoveredValue Return);
    public static string Emit(ScalarPathsFunction ir,uint rva,uint imageBase,string module) {
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"scalar_module_annotation");
        var f=ir.Flow;int argc=f.ReturnCleanupBytes[0]/4;var lines=new List<string>{"extern \"C\" void * __cdecl memcpy(void *, const void *, unsigned int);","#pragma intrinsic(memcpy)","typedef unsigned __int64 bits64;","static __forceinline unsigned int read32(unsigned int a) { unsigned int v; memcpy(&v, reinterpret_cast<const void *>(a), 4); return v; }","static __forceinline unsigned int read8(unsigned int a) { return *reinterpret_cast<const unsigned char *>(a); }"};
        string Cast(string text,int bits)=>bits==64?$"static_cast<bits64>({text})":bits==32?$"static_cast<unsigned int>({text})":bits is 1 or 8 or 16?$"(static_cast<unsigned int>({text}) & {FixedWidthInteger.Mask(bits)}u)":throw new ArgumentException("scalar_value_width");
        string Value(RecoveredValue v)=>v switch {
            Constant c=>c.Bits==64?$"{c.Value}ui64":$"{c.Value}u",
            RegisterInput{Index:1}=>"reinterpret_cast<unsigned int>(this)",
            IncomingStackRead{Bits:32,MemoryEpoch:0} i when i.Offset>=4&&i.Offset/4-1<argc=>$"arg_{i.Offset/4-1}",
            MemoryReadValue m=>$"read_{m.Pc:x}_{m.ReadOrdinal}",
            SegmentedAddress{Segment:{Index:3},Offset:var x}=>Value(x),
            AddValue a=>$"({Value(a.Left)} + {unchecked((uint)a.Offset)}u)",
            BitValue b=>Bit(b),
            _=>throw new ArgumentException("scalar_value_unsupported:"+v.GetType().Name)
        };
        string Bit(BitValue b) {
            string V(int i)=>Value(b.Operands[i]);
            if(b.Operation is "Trunc" or "Zext"&&b.Operands.Length==1)return Cast(V(0),b.Bits);
            if(b.Operation=="Sext"&&b.Operands is [var x,Constant from]) {
                int w=checked((int)from.Value);Need(w is 8 or 16 or 32&&b.Bits>w&&b.Bits<=64,"scalar_sign_extension_width");ulong sign=1UL<<(w-1);
                // XOR/subtract in the destination unsigned ring extends the sign.
                return Cast($"({Cast($"({Cast(Value(x),w)} ^ {sign}u)",b.Bits)} - {sign}u)",b.Bits);
            }
            if(b.Operation=="Sar"&&b.Operands is [var input,Constant shift]) {
                Need(shift.Value<(ulong)b.Bits&&b.Bits is 8 or 16 or 32 or 64,"scalar_shift_domain");int n=(int)shift.Value;if(n==0)return Cast(Value(input),b.Bits);string shifted=Cast(Value(input),b.Bits),zero=b.Bits==64?"0ui64":"0u";
                return Cast($"(({shifted} >> {n}) | (({zero} - ({shifted} >> {b.Bits-1})) << {b.Bits-n}))",b.Bits);
            }
            Need(b.Operands.Length==2,"scalar_operator_arity");string op=b.Operation switch{"Add"=>"+","Sub"=>"-","Mul"=>"*","And"=>"&","Or"=>"|","Xor"=>"^","Eq"=>"==","Ne"=>"!=","Ult"=>"<","Ule"=>"<=","Ugt"=>">","Uge"=>">=","Shr"=>">>","Shl"=>"<<",_=>throw new ArgumentException("scalar_operator_unsupported:"+b.Operation)};
            if(b.Operation is "Shr" or "Shl")Need(b.Operands[1] is Constant c&&c.Value<(ulong)b.Bits,"scalar_shift_count_unproven");
            // Result width alone cannot control C++ usual arithmetic conversions.
            // Widen/truncate arithmetic operands first; comparison result width is
            // one bit and must never be used as the operands' interpretation.
            bool comparison=b.Operation is "Eq" or "Ne" or "Ult" or "Ule" or "Ugt" or "Uge";
            string left=comparison?V(0):Cast(V(0),b.Bits);
            string right=comparison||b.Operation is "Shr" or "Shl"?V(1):Cast(V(1),b.Bits);
            return Cast($"({left} {op} {right})",b.Bits);
        }
        string args=string.Join(", ",Enumerable.Range(0,argc).Select(i=>$"unsigned int arg_{i}"));lines.Add($"struct Recovered {{ unsigned int fn_{rva:x8}({args}); }};");lines.Add($"// FUNCTION: {module} 0x{imageBase+rva:x8}");lines.Add($"unsigned int Recovered::fn_{rva:x8}({args}) {{");
        void Tree(Path[] paths,int depth) {
            Need(paths.Length>0,"scalar_empty_tree");string pad=new(' ',depth*4);ulong branch=paths.Where(p=>p.Predicates.Length>0).Select(p=>p.Predicates[0].Pc).DefaultIfEmpty(ulong.MaxValue).Min();int prefix=0;
            while(paths.All(p=>p.Effects.Length>prefix)&&paths.All(p=>Same(p.Effects[prefix],paths[0].Effects[prefix]))&&paths[0].Effects[prefix].Pc<branch)prefix++;
            foreach(var e in paths[0].Effects.Take(prefix)){Need(e.Value is MemoryReadValue&&e.Bits is 8 or 32,"scalar_memory_width");lines.Add($"{pad}unsigned int {Value(e.Value!)} = read{e.Bits}({Cast(Value(e.Address!),32)});");}
            paths=paths.Select(p=>p with{Effects=p.Effects[prefix..]}).ToArray();
            if(paths.All(p=>p.Predicates.Length==0)){Need(paths.All(p=>p.Effects.Length==0&&Same(p.Return,paths[0].Return)),"scalar_unmerged_return");lines.Add($"{pad}return {Cast(Value(paths[0].Return),32)};");return;}
            Need(paths.All(p=>p.Predicates.Length>0&&p.Predicates[0].Pc==branch&&Same(p.Predicates[0].Value,paths[0].Predicates[0].Value)),"scalar_predicate_join");
            var yes=paths.Where(p=>p.Predicates[0].Taken).Select(p=>p with{Predicates=p.Predicates[1..]}).ToArray();var no=paths.Where(p=>!p.Predicates[0].Taken).Select(p=>p with{Predicates=p.Predicates[1..]}).ToArray();Need(yes.Length>0&&no.Length>0,"scalar_missing_branch");lines.Add($"{pad}if ({Value(paths[0].Predicates[0].Value)}) {{");Tree(yes,depth+1);lines.Add(pad+"} else {");Tree(no,depth+1);lines.Add(pad+"}");
        }
        Tree(f.NormalPaths.Select(p=>new Path(p.Predicates,p.Effects.Where(e=>e.Kind=="memory_read").ToArray(),p.Exit.Return)).ToArray(),1);lines.Add("}");return string.Join("\n",lines)+"\n";
    }
}
