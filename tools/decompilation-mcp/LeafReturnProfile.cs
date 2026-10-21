using System.Text.Json;
namespace Decompilation;

// A bounded source proposal, not an ABI or flag-observation equivalence rule.
// Keep the complete FlowFunction, including every flag/register/return effect.
public sealed record LeafReturnFunction(FlowFunction Flow,string ReturnType,ulong? ConstantValue,int ProposedWordParameters,string? ReceiverOperation=null,int ReceiverOffset=0);
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
    // Only discard 32/64-bit casts for a low32 source proposal. The original
    // expression stays in FlowIR, so wrapping/context checks are not erased.
    static RecoveredValue LowWord(RecoveredValue value)
    {
        for(int i=0;i<8&&value is BitValue{Operation:"Zext" or "Trunc",Bits:32 or 64,Operands:var operands}&&operands.Length==1;i++)value=operands[0];
        return value;
    }
    static bool ReceiverOffset(RecoveredValue value,out int offset)
    {
        value=LowWord(value);offset=0;if(value==new RegisterInput(1))return true;
        if(value is AddValue{Left:RegisterInput{Index:1},Offset:>=0 and <=4096} add){offset=(int)add.Offset;return true;}
        if(value is BitValue{Operation:"Add",Bits:32 or 64,Operands:var terms}&&terms.Length==2&&LowWord(terms[0])==new RegisterInput(1)&&terms[1] is Constant{Bits:32 or 64,Value:<=4096} c){offset=(int)c.Value;return true;}
        return false;
    }
    static bool LowByteRead(RecoveredValue value,MemoryReadValue read)
    {
        if(value is not BitValue{Operation:"Or",Bits:64,Operands:var terms}||terms.Length!=2)return false;
        if(terms[0] is not BitValue{Operation:"And",Bits:64,Operands:var mask}||mask.Length!=2||mask[0]!=new RegisterInput(0)||mask[1]!=new Constant(ulong.MaxValue-255,64))return false;
        return terms[1] is BitValue{Operation:"Zext",Bits:64,Operands:var bytes}&&bytes.Length==1&&bytes[0]==read;
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
        foreach(var pair in exit.Registers)if(pair.Key is not 0 and not 4)Need(pair.Value==new RegisterInput(pair.Key),"leaf_return_changed_register");
        var writes=pre.Where(e=>e.Kind=="register_write").ToArray();
        if(rows.Length==1) {
            Need(cleanup>0&&pre.Length==0&&exit.Return==new RegisterInput(0),"leaf_return_cleanup_only");
            return new(flow,"void",null,cleanup/4);
        }
        Need(writes.Length==1&&writes[0].Address==new RegisterInput(0)&&writes[0].Bits is 32 or 64,"leaf_return_one_result_write");
        if(pre.Length==2&&pre[0].Kind=="memory_read"&&pre[1]==writes[0]&&pre[0].Pc==writes[0].Pc&&pre[0].Value is MemoryReadValue{Epoch:0,ReadOrdinal:1} read&&pre[0].Bits==read.Bits&&pre[0].Address==read.Address&&ReceiverOffset(read.Address,out var loadOffset)) {
            if(read.Bits==32&&LowWord(exit.Return)==read&&LowWord(writes[0].Value!)==read)return new(flow,"unsigned int",null,cleanup/4,"load_word",loadOffset);
            if(read.Bits==8&&LowByteRead(exit.Return,read)&&LowByteRead(writes[0].Value!,read))return new(flow,"unsigned char",null,cleanup/4,"load_byte",loadOffset);
        }
        if(pre.Length==1&&ReceiverOffset(exit.Return,out var addressOffset)&&ReceiverOffset(writes[0].Value!,out var writeOffset)&&addressOffset==writeOffset)
            return new(flow,"unsigned int",null,cleanup/4,"address",addressOffset);
        Need(pre.All(e=>e.Kind=="flag_write"&&e.Bits==1&&e.Value is Constant{Bits:1}||e.Kind=="register_write"&&e.Address==new RegisterInput(0)),"leaf_return_extra_effect");
        if(exit.Return is Constant{Bits:32,Value:<=uint.MaxValue} result&&writes[0].Value is Constant{Value:<=uint.MaxValue})return new(flow,"unsigned int",result.Value,cleanup/4);
        Need(LowByteConstant(exit.Return,out var low)&&LowByteConstant(writes[0].Value!,out var written)&&low==written,"leaf_return_constant_low_byte");
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
        var receiver=$"(reinterpret_cast<unsigned int>(this) + {ir.ReceiverOffset}u)";
        var statement=ir.ReceiverOperation switch {
            "load_byte"=>$"    return *reinterpret_cast<unsigned char*>({receiver});\n",
            "load_word"=>$"    return *reinterpret_cast<unsigned int*>({receiver});\n",
            "address"=>$"    return {receiver};\n",
            null=>ir.ConstantValue is ulong value?$"    return {value}u;\n":"",
            _=>throw new ArgumentException("leaf_receiver_operation")
        };
        return $"struct Recovered {{\n    {ir.ReturnType} fn_{rva:x8}({parameters});\n}};\n// FUNCTION: {module} 0x{imageBase+rva:x8}\n{ir.ReturnType} Recovered::fn_{rva:x8}({parameters}) {{\n{statement}}}\n";
    }
}
