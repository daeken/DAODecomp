using System.Security.Cryptography;
using System.Text;
using System.IO.Compression;
using System.Text.Json;
using System.Text.Json.Serialization;
using SharpRetro.Decompiler;

var json=new JsonSerializerOptions {
    PropertyNamingPolicy=JsonNamingPolicy.SnakeCaseLower,
    UnmappedMemberHandling=JsonUnmappedMemberHandling.Disallow,
    WriteIndented=true
};
try {
    var request=JsonSerializer.Deserialize<Request>(Console.In.ReadToEnd(),json)
        ?? throw new ArgumentException("Missing request");
    if(request.SchemaVersion!=1 || request.Functions.Length==0 && !request.IncludeData)
        throw new ArgumentException("Expected schema 1 and nonempty function selection");
    var image=BinaryImage.Open(request.Binary);
    if(image.Format!=BinaryFormat.Pe || image.Architecture!=Architecture.X86)
        throw new NotSupportedException("Initial recomp profile requires PE32 x86");
    if(image.Sha256!=request.BinarySha256) throw new InvalidDataException("Binary identity changed");
    if(request.IsolateFailures && request.ArtifactDirectory==null)
        throw new ArgumentException("Failure isolation requires artifact output");
    if(request.ArtifactDirectory!=null) Directory.CreateDirectory(request.ArtifactDirectory);
    var functions=new List<object>();
    foreach(var selection in request.Functions) {
        if(request.ArtifactDirectory!=null && (selection.ArtifactKey==null ||
            !System.Text.RegularExpressions.Regex.IsMatch(selection.ArtifactKey,@"\A[0-9a-f]{64}\z")))
            throw new ArgumentException("Artifact key must be a complete SHA-256");
        var generationStage="recover";
        try {
        ulong entry=checked(image.ImageBase+selection.Rva);
        var ranges=selection.Ranges?.Select(r=>new CodeRange(checked(image.ImageBase+r.Rva),r.Size)).ToArray()
            ?? [new CodeRange(entry,selection.Size)];
        if(ranges.Any(r=>r.Address<entry || r.End>checked(entry+selection.Size)))
            throw new ArgumentException("Selection subranges exceed their traversal envelope");
        var program=ControlFlow.Recover(image,entry,ranges,allowCalls:true,externalDispatch:true,
            extraEntries:selection.ExtraEntries?.Select(rva=>checked(image.ImageBase+rva)).ToArray());
        generationStage="blocks";
        var graph=BasicBlocks.Build(program,includeCalls:true,allowDynamicTargets:true);
        bool hasCalls=graph.Blocks.Values.Any(b=>b.Kind==TerminatorKind.Call);
        program=program with { AllowsCalls=hasCalls };
        if(graph.Blocks.Values.Any(b=>b.Branch==null && b.FlowSuccessors.Any(s=>!graph.Blocks.ContainsKey(s))))
            throw new NotSupportedException("Function reaches an untranslated boundary");
        // Static discovery often omits the continuation after a presumed
        // nonreturning call. Keep it unresolved rather than guessing ownership
        // or claiming the call cannot return. If reached, dispatch still fails.
        var unselectedContinuations=graph.Blocks.Values.Where(b=>b.Kind==TerminatorKind.Call && !graph.Blocks.ContainsKey(b.Alternative))
            .Select(b=>b.Alternative-image.ImageBase).Distinct().Order().ToArray();
        if(request.ModulePrefix!="" && !System.Text.RegularExpressions.Regex.IsMatch(request.ModulePrefix,@"\Am_[0-9a-f]{16}_\z"))
            throw new ArgumentException("Invalid module symbol prefix");
        string function=request.ModulePrefix+$"fn_{selection.Rva:x8}";
        var emitter=new CppEmitter();
        var annotations=selection.Annotations.ToDictionary(a=>a.Key,a=>new CppVariableAnnotation(a.Value.Name,a.Value.Type));
        generationStage="structures";
        var objects=Pe32ObjectRecovery.Analyze(program,selection.Structures);
        generationStage="emit";
        string source=emitter.Emit(program,request.Dispatch ? ControlFlowStyle.Dispatch : ControlFlowStyle.Auto,
            new($"recomp_generated::{function}_detail","runtime.hpp",annotations,request.RawMemory ? null : objects,ExternalDispatch:true));
        source+=$"\nnamespace recomp_generated {{\n"+
            $"sharp_retro::Exit {function}(sharp_retro::State& s, sharp_retro::Memory& memory, std::uint64_t budget) {{\n"+
            $"    return {function}_detail::run(s,memory,budget);\n}}\n"+
            $"sharp_retro::Exit {function}_step(sharp_retro::State& s, sharp_retro::Memory& memory, std::uint64_t& budget) {{\n"+
            $"    return {function}_detail::run(s,memory,budget);\n}}\n}}\n";
        generationStage="origins";
        var variables=CppVariableOrigins.Collect(program).Select(v=>new {
            v.Origin,v.InstructionRva,v.TemporaryId,v.Width,
            Name=annotations.GetValueOrDefault(v.Origin)?.Name ?? v.Name,
            Type=annotations.GetValueOrDefault(v.Origin)?.Type ?? "bits",v.Definition
        }).ToArray();
        string slices=string.Join("\n",program.Instructions.Select(i=>$"{i.Address-image.ImageBase:x8}:{Convert.ToHexStringLower(i.Bytes)}"));
        var generated=new {selection.Rva,selection.Size,Ranges=ranges.Select(r=>new {Rva=r.Address-image.ImageBase,r.Size}).ToArray(),Name=function,Source=source,Variables=variables,
            ExtraEntries=selection.ExtraEntries ?? [],UnselectedCallContinuations=unselectedContinuations,
            ExportNames=image.Exports.Where(e=>e.Value.Address==entry).Select(e=>e.Key).Order().ToArray(),
            CodeSha256=Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(slices))),
            Structures=objects.Objects,UnrecoveredAccesses=objects.UnrecoveredAccesses,
            Abi=Pe32AbiFacts.Analyze(program,objects),
            StructureLowering=!request.RawMemory,
            StructureEvidence="observed constant-offset accesses from traced base values; source classes/allocation bounds unknown",
            ControlFlow=emitter.ControlFlowSummary,Instructions=program.Instructions.Select(i=>new {
                Rva=i.Address-image.ImageBase,Bytes=Convert.ToHexStringLower(i.Bytes),i.Text
            }).ToArray()};
        if(request.ArtifactDirectory==null) functions.Add(generated);
        else {
            generationStage="artifact";
            functions.Add(WriteShard(request,selection,generated,source,null,null,null,json));
        }
        } catch(Exception exception) when(request.IsolateFailures && generationStage!="artifact" &&
            exception is ArgumentException or NotSupportedException or InvalidOperationException or OverflowException or StructuringException) {
            functions.Add(WriteShard(request,selection,null,null,generationStage,exception.GetType().Name,exception.Message,json));
        }
    }
    string runtime=File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"CppRuntime.hpp"))
        .Replace("#include \"IntegerRuntime.hpp\"",File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"IntegerRuntime.hpp")));
    Console.WriteLine(JsonSerializer.Serialize(new {SchemaVersion=1,BinarySha256=image.Sha256,image.ImageBase,image.PeImageSize,image.PeHasTls,
        ArtifactMode=request.ArtifactDirectory!=null,FailureIsolation=request.IsolateFailures,
        Representation="instruction-local machine values; explicit guest state and memory",Runtime=runtime,Functions=functions,
        Exports=image.Exports.Select(e=>new {Name=e.Key,e.Value.Address,e.Value.Ordinal,e.Value.Forwarder,
            Executable=image.Regions.Any(r=>r.Executable && e.Value.Address>=r.Address && e.Value.Address-r.Address<r.Size)}).ToArray(),
        OrdinalExports=image.PeOrdinalExports.Values.Select(e=>new {e.Address,e.Ordinal,e.Forwarder,
            Executable=image.Regions.Any(r=>r.Executable && e.Address>=r.Address && e.Address-r.Address<r.Size)}).ToArray(),
        DataSections=request.IncludeData ? new[] { new {
            Name=".headers",Address=image.ImageBase,Size=(ulong)image.ReadPeHeaders().Length,Writable=false,Readable=true,
            Bytes=Convert.ToBase64String(image.ReadPeHeaders())} }.Concat(image.Regions.Where(r=>!r.Executable && r.Size!=0).Select(r=>new {
            r.Name,r.Address,r.Size,r.Writable,Readable=image.IsPeReadable(r),
            Bytes=Convert.ToBase64String(image.ReadRegion(r))})).ToArray() : null,
        Imports=image.PeImportSlots.Select(p=>new {Address=p.Key,Library=image.ImportLibraries[p.Key],Symbol=p.Value,
            Policy=request.ImportPolicy?.GetValueOrDefault(image.ImportLibraries[p.Key].ToLowerInvariant()) ?? "native",
            Contract=image.ImportLibraries[p.Key].Equals("kernel32.dll",StringComparison.OrdinalIgnoreCase) ? p.Value switch {
                "MulDiv" => "win32-stdcall-i32-i32-i32-to-eax-i32; cleanup12; ECX/EDX/flags unknown",
                "GetCommandLineA" or "GetCommandLineW" => "win32-stdcall-to-readonly-process-command-line-guest-pointer32; cleanup0; configured logical game arguments, never host diagnostic arguments",
                "GetModuleFileNameA" => "win32-stdcall-module32-checked-byte-output-capacity32-to-DWORD32-length; cleanup12; configured main identity for NULL/0x400000, registered native modules otherwise; native measured truncation/last-error; truncated non-ASCII paths and translated DLL identity unsupported",
                "GetModuleFileNameW" => "win32-stdcall-module32-checked-UTF16-output-capacity-in-WCHAR32-to-DWORD32-length; cleanup12; configured main identity for NULL/0x400000, registered native modules otherwise; native measured truncation/last-error; translated DLL identity unsupported",
                "SetCurrentDirectoryW" => "win32-stdcall-optional-known-UTF16-path-to-BOOL32; cleanup4; actual process directory change and native failure/last-error, NULL forwarded unchanged",
                "CreateDirectoryW" => "win32-stdcall-known-nonnull-UTF16-path-optional-SECURITY_ATTRIBUTES12-default-descriptor-to-BOOL32; cleanup8; actual native directory creation, failure and last-error; nondefault security descriptors unsupported",
                "GetPrivateProfileStringW" => "win32-stdcall-known-UTF16-section-key-optional-default-checked-WCHAR16-output-capacity32-optional-filename-to-DWORD32-length; cleanup24; native INI lookup/default/truncation/error; known input uses original checked backing; returned string and terminator defined, tail unchanged; NULL section/key enumeration unsupported",
                "GetStdHandle" => "win32-stdcall-DWORD32-kind-to-native-HANDLE32; cleanup4; actual inherited process standard handle",
                "GetACP" or "GetOEMCP" => "win32-stdcall-to-UINT32-codepage; cleanup0; actual process Windows code page",
                "IsValidCodePage" => "win32-stdcall-UINT32-codepage-to-BOOL32; cleanup4; actual OS code-page availability",
                "GetCPInfo" => "win32-stdcall-UINT32-codepage-checked-CPINFO20-output-to-BOOL32; cleanup8; failure output unknown and stops exploration",
                "GetStringTypeW" => "win32-stdcall-DWORD32-kind-checked-UTF16-count32-checked-WORD16-per-character-output-to-BOOL32; cleanup16; negative count includes terminator; actual OS classification; failure output unknown",
                "LCMapStringW" => "win32-stdcall-LCID32-flags32-checked-UTF16-count32-checked-output-capacity32-to-int32; cleanup24; sort-key capacity counts bytes, otherwise UTF16 units; actual OS mapping; failure output unknown",
                "MultiByteToWideChar" => "win32-stdcall-codepage32-flags32-checked-byte-input-count32-checked-UTF16-output-capacity32-to-int32; cleanup24; minus-one count includes terminator; actual OS conversion; failure output unknown",
                "SetHandleCount" => "win32-stdcall-UINT32-count-to-UINT32; cleanup4; actual legacy OS API result",
                "GetEnvironmentStringsW" => "win32-stdcall-to-registered-readonly-UTF16-double-null-environment32; cleanup0; actual host process environment; lifetime tracked",
                "WideCharToMultiByte" => "win32-stdcall-codepage32-flags32-checked-UTF16-count32-checked-byte-output-capacity32-null-default-optional-BOOL32-output-to-int32; cleanup32; actual OS conversion; custom default characters unsupported",
                "FreeEnvironmentStringsW" => "win32-stdcall-owned-native-environment-block32-to-BOOL32; cleanup4; unregister on actual successful release",
                "GetFileType" => "win32-stdcall-native-HANDLE32-to-DWORD32; cleanup4; actual OS handle type/error",
                "InterlockedIncrement" or "InterlockedDecrement" => "win32-stdcall-checked-aligned-LONG32-inout-to-eax-LONG32; cleanup4; actual native atomic operation",
                "GetLastError" => "win32-stdcall-to-eax-DWORD32; cleanup0; actual guest-thread last-error state preserved across bridge bookkeeping",
                "SetLastError" => "win32-stdcall-DWORD32-to-void; cleanup4; set guest-thread native last-error state",
                "SetUnhandledExceptionFilter" => "win32-stdcall-guest-filter32-or-owned-native-filter32-to-previous-filter32; cleanup4; actual native registration, own-thunk identity translated; native callback invocation explicitly stops until context transport exists",
                "InitializeCriticalSectionAndSpinCount" => "win32-stdcall-checked-CRITICAL_SECTION24-inout-spin32-to-BOOL32; cleanup8; actual Windows x86 layout",
                "InitializeCriticalSectionEx" => "win32-stdcall-checked-CRITICAL_SECTION24-inout-spin32-flags32-to-BOOL32; cleanup12; actual Windows x86 layout",
                "InitializeCriticalSection" or "DeleteCriticalSection" or "EnterCriticalSection" or "LeaveCriticalSection" => "win32-stdcall-checked-CRITICAL_SECTION24-inout-to-void; cleanup4; actual native synchronization",
                "TryEnterCriticalSection" => "win32-stdcall-checked-CRITICAL_SECTION24-inout-to-BOOL32; cleanup4; actual native synchronization",
                "CreateMutexW" => "win32-stdcall-optional-checked-SECURITY_ATTRIBUTES12-initial-BOOL32-optional-known-UTF16-name-to-owned-HANDLE32; cleanup12; actual OS creation/opening and last-error, nonnull security descriptors unsupported",
                "CreateEventW" => "win32-stdcall-optional-checked-SECURITY_ATTRIBUTES12-manual-BOOL32-initial-BOOL32-optional-known-UTF16-name-to-owned-event-HANDLE32; cleanup16; actual OS creation/opening, reset/state and last-error; nonnull security descriptors unsupported",
                "CreateSemaphoreW" => "win32-stdcall-optional-checked-SECURITY_ATTRIBUTES12-initial-LONG32-maximum-LONG32-optional-known-UTF16-name-to-owned-semaphore-HANDLE32; cleanup16; actual signed count validation/state, named reuse and native error; nonnull security descriptors unsupported",
                "WaitForSingleObject" => "win32-stdcall-live-owned-kernel-HANDLE32-timeout32-to-DWORD32; cleanup8; actual native wait including timeout/abandonment/failure",
                "WaitForSingleObjectEx" => "win32-stdcall-live-owned-kernel-HANDLE32-timeout32-alertable-BOOL32-to-DWORD32; cleanup12; actual native wait/APC/timeout/abandonment/failure and last-error; guest APC registration/transport not implemented",
                "ReleaseMutex" => "win32-stdcall-live-owned-kernel-HANDLE32-to-BOOL32; cleanup4; actual native ownership release/error",
                "CloseHandle" => "win32-stdcall-live-owned-kernel-HANDLE32-to-BOOL32; cleanup4; retire only on real successful close; registry/module/heap handles have separate lifetimes",
                "GetCurrentProcessId" or "GetCurrentThreadId" or "GetTickCount" => "win32-stdcall-no-arguments-to-eax-u32; cleanup0; ECX/EDX/flags unknown",
                "IsProcessorFeaturePresent" => "win32-stdcall-DWORD32-feature-to-BOOL32; cleanup4; actual Windows feature report, no inferred host-CPU substitution",
                "GetSystemTimeAsFileTime" => "win32-stdcall-guest32-out-FILETIME8-to-void; cleanup4; EAX/ECX/EDX/flags unknown",
                "GetSystemInfo" => "win32-stdcall-checked-SYSTEM_INFO36-output-to-void; cleanup4; actual Windows x86 fields, reserved WORD unknown except reviewed exact-provider native write (file hashes, procedure RVAs, live thunk target and complete-output guard); address limits are numeric bounds, never registered allocations; EAX/ECX/EDX/flags unknown",
                "QueryPerformanceCounter" => "win32-stdcall-guest32-out-LARGE_INTEGER8-to-eax-BOOL32; cleanup4; failure output unknown; ECX/EDX/flags unknown",
                "QueryPerformanceFrequency" => "win32-stdcall-checked-LARGE_INTEGER8-output-to-BOOL32; cleanup4; actual native frequency/result/last-error, failure output unknown; ECX/EDX/flags unknown",
                "GetStartupInfoA" => "win32-stdcall-guest32-out-STARTUPINFOA68-to-void; cleanup4; native strings registered read-only; x86 process backing required",
                "GetProcessHeap" => "win32-stdcall-to-native-heap-handle32; cleanup0; x86 process backing required",
                "HeapCreate" => "win32-stdcall-flags32-size32-size32-to-native-heap-handle32; cleanup12; exceptions unsupported",
                "GetModuleHandleA" => "win32-stdcall-guest-ANSI-name-to-native-module32; cleanup4; translated/null module identity unsupported",
                "GetProcAddress" => "win32-stdcall-registered-native-module32-guest-ANSI-or-ordinal-to-dynamic-native-target32; cleanup8; calls still require explicit signatures",
                "TlsAlloc" => "win32-stdcall-to-native-TLS-index32; cleanup0; register index ownership",
                "TlsGetValue" or "FlsGetValue" => "win32-stdcall-owned-slot32-to-opaque-value32; cleanup4; native TLS/FLS semantics",
                "TlsSetValue" or "FlsSetValue" => "win32-stdcall-owned-slot32-opaque-value32-to-BOOL32; cleanup8; no pointer dereference",
                "TlsFree" or "FlsFree" => "win32-stdcall-owned-slot32-to-BOOL32; cleanup4; FLS callbacks execute before release",
                "FlsAlloc" => "win32-stdcall-guest-callback32-to-native-FLS-index32; cleanup4; actual native-to-translated callback thunk required",
                "EncodePointer" or "DecodePointer" => "win32-stdcall-opaque-pointer-bits32-to-opaque-pointer-bits32; cleanup4; actual native process cookie",
                "HeapAlloc" => "win32-stdcall-native-heap-handle32-flags32-size32-to-registered-native-memory32; cleanup12; exceptions unsupported",
                "HeapSize" => "win32-stdcall-native-heap-handle32-flags32-registered-memory32-to-SIZE_T32; cleanup12; actual Windows heap size; memory contents need not be defined",
                "HeapFree" => "win32-stdcall-native-heap-handle32-flags32-registered-native-pointer32-to-BOOL32; cleanup12; unregister on success",
                "GetVersionExA" => "win32-stdcall-registered-native-OSVERSIONINFOA-or-EXA-to-BOOL32; cleanup4; actual host manifest/version behavior",
                _ => "unknown; explicit bridge required"
            } : image.ImportLibraries[p.Key].Equals("advapi32.dll",StringComparison.OrdinalIgnoreCase) ? p.Value switch {
                "RegOpenKeyExW" => "win32-stdcall-live-or-predefined-HKEY32-optional-UTF16-name-options32-rights32-checked-HKEY32-output-to-LSTATUS32; cleanup20; real native status, failed out-key unknown; successful non-predefined keys tracked",
                "RegCloseKey" => "win32-stdcall-live-or-predefined-HKEY32-to-LSTATUS32; cleanup4; native release, retire owned identity only on success",
                _ => "unknown; explicit bridge required"
            } : image.ImportLibraries[p.Key].Equals("winmm.dll",StringComparison.OrdinalIgnoreCase) ? p.Value switch {
                "timeGetTime" => "win32-stdcall-no-arguments-to-DWORD32-system-milliseconds; cleanup0; actual native modulo32 result and last-error; ECX/EDX/flags unknown",
                _ => "unknown; explicit bridge required"
            } : image.ImportLibraries[p.Key].Equals("user32.dll",StringComparison.OrdinalIgnoreCase) ? p.Value switch {
                "LoadIconW" or "LoadCursorW" => "win32-stdcall-checked-resource-module32-UTF16-name-or-ordinal16-to-shared-USER-handle32; cleanup8; real native resource result/last-error; translated PE headers/resource data require known readable flat backing, original code remains inaccessible",
                _ => "unknown; explicit bridge required"
            } : image.ImportLibraries[p.Key].Equals("shell32.dll",StringComparison.OrdinalIgnoreCase) ? p.Value switch {
                "SHGetFolderPathW" => "win32-stdcall-NULL-reserved-owner-int32-CSIDL-NULL-or-default-user-token32-flags32-checked-WCHAR16-MAX_PATH260-output-to-HRESULT32; cleanup20; actual native profile lookup/result/last-error; only returned string including terminator defined, tail knownness preserved; other user tokens unsupported",
                _ => "unknown; explicit bridge required"
            } : "unknown; explicit bridge required"}).ToArray()},json));
    return 0;
} catch(Exception exception) when(exception is ArgumentException or IOException or NotSupportedException or
    InvalidOperationException or OverflowException or JsonException or StructuringException) {
    Console.Error.WriteLine("recomp bridge: "+exception.Message);
    return 1;
}

static ShardSummary WriteShard(Request request,Selection selection,object? generated,string? source,
    string? stage,string? errorType,string? error,JsonSerializerOptions json)
{
    var output=Path.GetFullPath(request.ArtifactDirectory!);
    var target=Path.Combine(output,selection.ArtifactKey!);
    if(Directory.Exists(target)) throw new IOException("Immutable function shard already exists: "+selection.ArtifactKey);
    var temporary=Path.Combine(output,".function-"+Guid.NewGuid().ToString("N"));
    Directory.CreateDirectory(temporary);
    var files=new SortedDictionary<string,string>();
    string status=generated!=null ? "generated_only":"generation_failed";
    if(generated!=null) {
        File.WriteAllText(Path.Combine(temporary,"function.cpp"),source!,new UTF8Encoding(false));
        using(var file=File.Create(Path.Combine(temporary,"function.json.gz")))
        using(var zip=new GZipStream(file,CompressionLevel.Fastest)) JsonSerializer.Serialize(zip,generated,json);
        foreach(var name in new[]{"function.cpp","function.json.gz"}) {
            using var file=File.OpenRead(Path.Combine(temporary,name));
            files[name]=Convert.ToHexStringLower(SHA256.HashData(file));
        }
    } else {
        var failure=new {selection.Rva,selection.Size,Stage=stage,ErrorType=errorType,Error=error,
            Status=status,BehavioralAcceptance=false};
        var path=Path.Combine(temporary,"failure.json");
        File.WriteAllText(path,JsonSerializer.Serialize(failure,json),new UTF8Encoding(false));
        using var file=File.OpenRead(path);files["failure.json"]=Convert.ToHexStringLower(SHA256.HashData(file));
    }
    var marker=new {SchemaVersion=1,request.BinarySha256,selection.Rva,selection.ArtifactKey,Selection=selection,Status=status,
        BehavioralAcceptance=false,Files=files,Stage=stage,ErrorType=errorType,Error=error};
    File.WriteAllText(Path.Combine(temporary,"complete.json"),JsonSerializer.Serialize(marker,json),new UTF8Encoding(false));
    Directory.Move(temporary,target);
    return new(selection.Rva,selection.ArtifactKey!,status,files,stage,errorType,error);
}

sealed record ShardSummary(ulong Rva,string ArtifactKey,string Status,SortedDictionary<string,string> Files,
    string? Stage,string? ErrorType,string? Error);

sealed record Annotation(string Name,string? Type);
sealed record Selection(ulong Rva,ulong Size,Dictionary<string,Annotation> Annotations,
    Dictionary<string,Pe32StructureAnnotation>? Structures=null,SelectionRange[]? Ranges=null,ulong[]? ExtraEntries=null,string? ArtifactKey=null);
sealed record SelectionRange(ulong Rva,ulong Size);
sealed record Request(int SchemaVersion,string Binary,string BinarySha256,Selection[] Functions,bool Dispatch=false,bool RawMemory=false,
    Dictionary<string,string>? ImportPolicy=null,string ModulePrefix="",bool IncludeData=false,
    bool IsolateFailures=false,string? ArtifactDirectory=null);
