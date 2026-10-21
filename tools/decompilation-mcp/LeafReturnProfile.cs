using System.Text.Json;
namespace Decompilation;

// A bounded source proposal, not an ABI or flag-observation equivalence rule.
// Keep the complete FlowFunction, including every flag/register/return effect.
public sealed record LeafReturnFunction(FlowFunction Flow,string ReturnType,ulong? ConstantValue,int ProposedWordParameters);
public static class Vc8LeafReturnProfile
{
    static void Need(bool ok,string reason){if(!ok)throw new ArgumentException(reason);}
    static bool LowByteConstant(RecoveredValue value,out ulong constant)
    {
        constant=0;
        if(value is not BitValue{Operation:"Or",Bits:64,Operands:var terms}||terms.Length!=2||terms[1] is not Constant{Bits:64,Value:<=255} c)return false;
        if(terms[0] is not BitValue{Operation:"And",Bits:64,Operands:var mask}||mask.Length!=2||mask[0]!=new RegisterInput(0)||mask[1]!=new Constant(ulong.MaxValue-255,64))return false;
        constant=c.Value;return true;
    }
    public static LeafReturnFunction Raise(JsonElement lift)
    {
        var rows=lift.GetProperty("instructions").EnumerateArray().ToArray();Need(rows.Length is 1 or 2,"leaf_return_instruction_domain");
        var flow=X86FlowRecovery.Raise(lift,new(Vc8Profile.Abi,true,true),[]);
        Need(flow.NormalPaths.Length==1&&(flow.TerminalPaths??[]).Length==0&&(flow.FaultPaths??[]).Length==0&&!flow.Incoming.AddressEscapeObserved&&flow.Incoming.RequiredReadBytes==0,"leaf_return_single_no_input_path");
        var path=flow.NormalPaths[0];var exit=path.Exit;int cleanup=exit.ReturnCleanupBytes;
        Need(path.Predicates.Length==0&&cleanup is >=0 and <=32&&cleanup%4==0&&!exit.StackMemoryMayHaveChanged&&exit.ReturnTarget==new UnknownValue("entry_return_address"),"leaf_return_exit_domain");
        Need(exit.Pc==rows[^1].GetProperty("pc").GetUInt64(),"leaf_return_final_instruction");
        var pre=path.Effects.Where(e=>e.Pc!=exit.Pc).ToArray();
        // The existing full return-tree verifier forbids any non-return effect
        // in the last instruction. No other memory, call, register or SP effect
        // may disappear behind the source proposal.
        Need(pre.All(e=>e.Kind=="flag_write"&&e.Bits==1&&e.Value is Constant{Bits:1}||e.Kind=="register_write"&&e.Address==new RegisterInput(0)),"leaf_return_extra_effect");
        foreach(var pair in exit.Registers)if(pair.Key is not 0 and not 4)Need(pair.Value==new RegisterInput(pair.Key),"leaf_return_changed_register");
        var writes=pre.Where(e=>e.Kind=="register_write").ToArray();
        if(rows.Length==1) {
            Need(cleanup>0&&pre.Length==0&&exit.Return==new RegisterInput(0),"leaf_return_cleanup_only");
            return new(flow,"void",null,cleanup/4);
        }
        Need(writes.Length==1&&writes[0].Bits is 32 or 64,"leaf_return_one_result_write");
        if(exit.Return is Constant{Bits:32,Value:<=uint.MaxValue} result&&writes[0].Value is Constant{Value:<=uint.MaxValue})return new(flow,"unsigned int",result.Value,cleanup/4);
        Need(LowByteConstant(exit.Return,out var low)&&LowByteConstant(writes[0].Value!,out var written)&&low==written&&pre.Length==1,"leaf_return_constant_low_byte");
        return new(flow,"unsigned char",low,cleanup/4);
    }
    public static bool TryRaise(JsonElement lift,out LeafReturnFunction? result)
    {
        try{result=Raise(lift);return true;}catch(ArgumentException){result=null;return false;}
    }
    public static string Emit(LeafReturnFunction ir,uint rva,uint imageBase,string module)
    {
        Need(module.Length is >0 and <=128&&module.All(c=>char.IsAsciiLetterOrDigit(c)||c is '.' or '_' or '-'),"unsupported_module_annotation");
        var parameters=string.Join(", ",Enumerable.Range(0,ir.ProposedWordParameters).Select(i=>$"unsigned int arg_{i}"));
        var statement=ir.ConstantValue is ulong value?$"    return {value}u;\n":"";
        return $"struct Recovered {{\n    {ir.ReturnType} fn_{rva:x8}({parameters});\n}};\n// FUNCTION: {module} 0x{imageBase+rva:x8}\n{ir.ReturnType} Recovered::fn_{rva:x8}({parameters}) {{\n{statement}}}\n";
    }
}
