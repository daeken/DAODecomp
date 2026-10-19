using System.Collections;
using System.Reflection;
using System.Text.Json;
using LiftIl;
using XFusionCpu;

// Reflection preserves every public record property/decoder field, including type tags.
// New non-data types fail closed rather than falling back to a display string.
static class Wire {
 public static object? Encode(object? v) {
  if(v is null || v is string || v is bool) return v;
  var t=v.GetType();
  if(t.IsEnum) return new Dictionary<string,object?>{{"type",t.FullName},{"name",v.ToString()},{"value",Convert.ToInt64(v)}};
  if(v is UInt128 u) return new Dictionary<string,object?>{{"type","System.UInt128"},{"decimal",u.ToString(System.Globalization.CultureInfo.InvariantCulture)}};
  if(t.IsPrimitive || v is decimal) return v;
  if(v is IEnumerable seq) return seq.Cast<object?>().Select(Encode).ToArray();
  if(!(v is Il || v is IlType || t.Namespace=="XFusionCpu")) throw new InvalidOperationException("unsupported_wire_type:"+t.FullName);
  var d=new SortedDictionary<string,object?>{{"type",t.FullName}};
  foreach(var p in t.GetProperties(BindingFlags.Instance|BindingFlags.Public)) {
   if(p.GetIndexParameters().Length!=0) throw new InvalidOperationException("indexed_wire_property");
   d.Add(p.Name,Encode(p.GetValue(v)));
  }
  foreach(var f in t.GetFields(BindingFlags.Instance|BindingFlags.Public)) d.Add(f.Name,Encode(f.GetValue(v)));
  return d;
 }
 public static IEnumerable<Il> Nodes(Il node) {
  yield return node;
  foreach(var p in node.GetType().GetProperties(BindingFlags.Instance|BindingFlags.Public)) {
   var v=p.GetValue(node);
   if(v is Il il) foreach(var n in Nodes(il)) yield return n;
   else if(v is IEnumerable seq && v is not string) foreach(var item in seq) if(item is Il x) foreach(var n in Nodes(x)) yield return n;
  }
 }
 public static object Lift(JsonElement req) {
  var bytes=Convert.FromHexString(req.GetProperty("hex").GetString()!);
  if(bytes.Length>1048576) throw new InvalidOperationException("range_too_large");
  var pc=req.GetProperty("pc").GetUInt64();
  if(pc>uint.MaxValue || pc+(ulong)bytes.Length>0x100000000UL) throw new InvalidOperationException("not_32bit_range");
  var rows=new List<object>(); var off=0; var liftErrors=0; var opaque=0; string? stop=null;
  while(off<bytes.Length) {
   DecodedInsn d;
   try { if(!Disassembler.DecodeInsn(bytes.AsSpan(off),XMode.Bits32,out d)) {stop="decode_failed";break;} }
   catch(Exception e) {stop="decode_exception:"+e.GetType().Name+":"+e.Message;break;}
   if(d.Len<=0 || d.Len>15 || off+d.Len>bytes.Length) {stop="invalid_decode_length:"+d.Len;break;}
   object? tree=null; string? error=null; string[] markers=[];
   try {
    var block=X86Lifter.Lift(in d,pc+(ulong)off,XMode.Bits32);
    if(block is null) throw new InvalidOperationException("null_lift");
    tree=Encode(block);
    markers=Nodes(block).Where(n=>n is IlIntrin || n is IlUnimpl || n is IlNote).Select(n=>n.GetType().Name+":"+(n is IlIntrin i ? i.Name : n is IlUnimpl x ? x.SourceOp+":"+x.Why : ((IlNote)n).Text)).ToArray();
    if(markers.Length>0) opaque++;
   } catch(Exception e) {error=e.GetType().Name+":"+e.Message;liftErrors++;}
   rows.Add(new {offset=off,pc=pc+(ulong)off,length=d.Len,raw_hex=Convert.ToHexString(bytes.AsSpan(off,d.Len)).ToLowerInvariant(),def_name=Disassembler.DefNames[d.DefId],decoded=Encode(d),tree,opaque_markers=markers,lift_error=error});
   off+=d.Len;
  }
  return new {schema="sharpretro_instruction_lift_v1",id=req.GetProperty("id").GetString(),mode="Bits32",pc,byte_length=bytes.Length,decoded_bytes=off,decode_complete=off==bytes.Length,range_stop=stop,unprocessed_hex=Convert.ToHexString(bytes.AsSpan(off)).ToLowerInvariant(),lift_errors=liftErrors,opaque_instructions=opaque,instructions=rows};
 }
 public static void Main() {
  string? line;
  while((line=Console.ReadLine())!=null) {
   try {using var req=JsonDocument.Parse(line);Console.WriteLine(JsonSerializer.Serialize(Lift(req.RootElement)));}
   catch(Exception e) {Console.WriteLine(JsonSerializer.Serialize(new {adapter_error=e.GetType().Name+":"+e.Message}));}
  }
 }
}
