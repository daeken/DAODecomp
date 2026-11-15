using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using SharpRetro.Decompiler;

// Diagnostic only: each authenticated instruction is checked independently.
// This intentionally makes no function-boundary, compilation or behavior claim.
var json=new JsonSerializerOptions {PropertyNamingPolicy=JsonNamingPolicy.SnakeCaseLower,
    UnmappedMemberHandling=JsonUnmappedMemberHandling.Disallow};
try {
    var request=JsonSerializer.Deserialize<Request>(Console.In.ReadToEnd(),json) ?? throw new ArgumentException("Missing request");
    if(request.SchemaVersion!=1 || request.Instructions.Length==0 || request.Instructions.Length>500_000)
        throw new ArgumentException("Invalid instruction audit request/budget");
    var image=BinaryImage.Open(request.Binary);
    if(image.Format!=BinaryFormat.Pe || image.Architecture!=Architecture.X86 || image.Sha256!=request.BinarySha256)
        throw new InvalidDataException("Instruction audit requires the pinned PE32 x86 image");
    var results=new List<object>();
    foreach(var item in request.Instructions) {
        string stage="authenticate";
        try {
            byte[] bytes=Convert.FromHexString(item.Bytes);
            if(bytes.Length<1 || bytes.Length>15)throw new ArgumentException("Invalid instruction length");
            ulong pc=checked(image.ImageBase+item.Rva);
            if(!image.ReadExecutable(pc,bytes.Length).SequenceEqual(bytes))throw new InvalidDataException("Instruction bytes differ from pinned image");
            stage="recover";
            var program=ControlFlow.Recover(image,pc,[new CodeRange(pc,(ulong)bytes.Length)],allowCalls:true,externalDispatch:true);
            if(program.Instructions.Count!=1 || !program.Instructions[0].Bytes.SequenceEqual(bytes))
                throw new NotSupportedException("Independent decoder boundary differs from instruction candidate");
            stage="structures";var objects=Pe32ObjectRecovery.Analyze(program);
            stage="emit";var emitter=new CppEmitter();
            string source=emitter.Emit(program with {AllowsCalls=true},ControlFlowStyle.Dispatch,
                new("support_audit","runtime.hpp",Objects:objects,ExternalDispatch:true));
            results.Add(new {item.Rva,item.Bytes,Status="instruction_emission_available",Stage=stage,
                SourceSha256=Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(source)))});
        } catch(Exception error) when(error is ArgumentException or NotSupportedException or InvalidOperationException or OverflowException or StructuringException) {
            results.Add(new {item.Rva,item.Bytes,Status="instruction_support_unresolved",Stage=stage,ErrorType=error.GetType().Name,Error=error.Message});
        }
    }
    Console.WriteLine(JsonSerializer.Serialize(new {SchemaVersion=1,BinarySha256=image.Sha256,Results=results,
        Scope="Independent original-instruction diagnostics; not a complete function, compilable build or behavioral acceptance",
        GameAcceptance=false},json));return 0;
} catch(Exception error) when(error is ArgumentException or IOException or InvalidOperationException or NotSupportedException or OverflowException or JsonException) {
    Console.Error.WriteLine("instruction support audit: "+error.Message);return 1;
}
sealed record Instruction(ulong Rva,string Bytes);
sealed record Request(int SchemaVersion,string Binary,string BinarySha256,Instruction[] Instructions);
