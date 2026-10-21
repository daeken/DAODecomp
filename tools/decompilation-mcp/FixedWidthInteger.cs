using System.Text.Json;
namespace Decompilation;

// Values remain bit patterns. Signedness is interpreted only by an explicit
// extension, comparison or arithmetic shift; arithmetic never acquires C++ UB.
public static class FixedWidthInteger
{
    static void Need(bool p,string s){if(!p)throw new ArgumentException(s);}
    public static int Width(JsonElement n) {
        var t=n.GetProperty("Ty");Need(t.GetProperty("type").GetString()=="LiftIl.IlType+I","integer_type_required");int w=t.GetProperty("Bits").GetInt32();Need(w is 1 or 8 or 16 or 32 or 64,"integer_width");Need(w!=1||!t.GetProperty("Signed").GetBoolean(),"signed_boolean_unsupported");return w;
    }
    public static void ValidateSignedBinary(JsonElement n) {
        var left=n.GetProperty("L");var right=n.GetProperty("R");string op=n.GetProperty("Op").GetProperty("name").GetString()!;
        bool signed=n.GetProperty("Ty").GetProperty("Signed").GetBoolean()||left.GetProperty("Ty").GetProperty("Signed").GetBoolean()||right.GetProperty("Ty").GetProperty("Signed").GetBoolean();
        if(!signed&&op!="Sar")return;
        int l=Width(left),r=Width(right),w=Width(n);
        if(op is "Eq" or "Ne" or "Ult" or "Ule" or "Ugt" or "Uge")Need(w==1&&l==r,"signed_comparison_width");
        else if(op is "Sar" or "Shr" or "Shl")Need(l==w,"signed_shift_width");
        else Need(op is "Add" or "Sub" or "Mul" or "And" or "Or" or "Xor"&&l==r&&r==w,"signed_binary_width_or_operation");
    }
    public static int ValueWidth(RecoveredValue x)=>x switch {Constant c=>c.Bits,BitValue b=>b.Bits,MemoryReadValue m=>m.Bits,IncomingStackRead i=>i.Bits,_=>64};
    public static RecoveredValue? SimplifyUnsignedCast(string op,RecoveredValue x,int width) {
        if(x is not BitValue b||b.Operands.Length!=1||b.Operation is not ("Trunc" or "Zext"))return null;
        if(op=="Trunc"&&width==b.Bits)return x;
        if(op=="Trunc"&&b.Operation=="Zext"&&ValueWidth(b.Operands[0])==width)return b.Operands[0];
        if(op=="Zext"&&b.Operation=="Zext"&&width>=b.Bits)return new BitValue("Zext",b.Operands,width);
        return null;
    }
    public static ulong Mask(int w)=>w==64?ulong.MaxValue:(1UL<<w)-1;
    public static RecoveredValue Cast(string op,RecoveredValue value,int from,int to) {
        Need(op=="Bitcast"?from==to:op=="Sext"&&from is 8 or 16 or 32&&to>from&&to<=64,"signed_cast_width");
        if(op=="Bitcast")return new BitValue("Trunc",[value],to);
        if(value is Constant c){ulong x=c.Value&Mask(from);return new Constant(((x&(1UL<<(from-1)))!=0?x|~Mask(from):x)&Mask(to),to);}
        return new BitValue("Sext",[value,new Constant((ulong)from,32)],to);
    }
    public static RecoveredValue ArithmeticShift(RecoveredValue value,RecoveredValue count,int width) {
        Need(width is 8 or 16 or 32 or 64,"arithmetic_shift_width");Need(count is Constant c&&c.Value<(ulong)width,"arithmetic_shift_count_unproven");int n=(int)((Constant)count).Value;
        if(value is Constant v){ulong x=v.Value&Mask(width);ulong result=n==0?x:(x>>n)|((x&(1UL<<(width-1)))==0?0:Mask(width)^(Mask(width)>>n));return new Constant(result,width);}
        return new BitValue("Sar",[value,count],width);
    }
}
