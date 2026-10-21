using System.ComponentModel;
using System.Diagnostics;
using System.Reflection;
using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;

namespace Decompilation;

public static class Program
{
    public static async Task<int> Main(string[] args)
    {
        try
        {
            if(args.FirstOrDefault()=="recover-ir") {
                using var input=JsonDocument.Parse(await Console.In.ReadToEndAsync());var x=input.RootElement;
                try {
                    if(x.TryGetProperty("forward_cpp_regions",out var forward)){Console.WriteLine(Engine.Json(new{status="structured",lines=ForwardCppRegions.Structure(forward.EnumerateArray().Select(v=>v.GetString()!))}));return 0;}
                    if(x.TryGetProperty("ebp_lexical_topology",out var lexical)){Console.WriteLine(Engine.Json(new{status="recovered",topology=EbpLexicalTopology.Recover(lexical)}));return 0;}
                    if(x.TryGetProperty("ebp_region_dispatch",out var plan)){var regions=plan.Deserialize<EbpExceptionRegions>(Engine.Options)!;var state=x.GetProperty("state");Console.WriteLine(Engine.Json(regions.Dispatch(state.ValueKind==JsonValueKind.Null?null:state.GetInt32(),x.GetProperty("category").GetString()!,x.GetProperty("runtime_state_unchanged").GetBoolean())));return 0;}
                    if(x.TryGetProperty("ebp_try_source",out var ebp)&&ebp.GetBoolean()){var result=Vc8EbpTryProfile.Emit(x.GetProperty("lift"),x.GetProperty("frame").Deserialize<FlowFunction>(Engine.Options)!,x.GetProperty("eh"),x.GetProperty("callees"),x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.GetProperty("module").GetString()!,x.TryGetProperty("shared_tail",out var shared)&&shared.GetBoolean());Console.WriteLine(Engine.Json(new{status="generated",ir=result,source=result.Source,proof=false}));return 0;}
                    if(x.TryGetProperty("owned_ranges",out var selectedRanges)&&selectedRanges.GetBoolean()){var ranges=OwnedRangeRecovery.Inspect(x.GetProperty("lift"));Console.WriteLine(Engine.Json(new{status="inspected",ir=ranges,proof=false,source_emission="unsupported"}));return 0;}
                    var abi=x.TryGetProperty("abi",out var abiElement)?abiElement.Deserialize<RecoveryAbi>(Engine.Options)!:Vc8Profile.Abi;
                    if(x.TryGetProperty("normal_return_evidence",out var normalSelected)&&normalSelected.GetBoolean()) {var summary=X86StackArgumentRecovery.InspectNormalReturn(x.GetProperty("target").GetUInt64(),x.GetProperty("lift"),x.TryGetProperty("runtime_terminal_evidence",out var runtime)?runtime.Deserialize<RuntimeTerminalEvidence>(Engine.Options):null);Console.WriteLine(Engine.Json(new{status="recovered",ir=summary,proof=false,source_emission="not_selected"}));return 0;}
                    if(x.TryGetProperty("terminal_callee",out var terminalSelected)&&terminalSelected.GetBoolean()) {var runtime=x.GetProperty("runtime_terminal_evidence").Deserialize<RuntimeTerminalEvidence>(Engine.Options)!;var summary=Vc8TerminalCallProfile.Inspect(x.GetProperty("target").GetUInt64(),x.GetProperty("lift"),runtime);Console.WriteLine(Engine.Json(new{status="recovered",ir=summary,proof=false,source_emission="not_selected"}));return 0;}
                    if(x.TryGetProperty("structured_memory",out var memorySelected)&&memorySelected.GetBoolean()) {var deps=x.GetProperty("callee_lifts").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();if(x.TryGetProperty("recover_only",out var recoverOnly)&&recoverOnly.GetBoolean()){var flow=Vc8StructuredMemoryProfile.RecoverFlow(x.GetProperty("lift"),deps,x.TryGetProperty("runtime_terminal_evidence",out var runtimeOnly)?runtimeOnly.Deserialize<RuntimeTerminalEvidence>(Engine.Options):null);Console.WriteLine(Engine.Json(new{status="recovered",ir=x.TryGetProperty("layout_only",out var layoutOnly)&&layoutOnly.GetBoolean()?(object)ReceiverLayoutRecovery.Observe(flow):flow,proof=false}));return 0;}var memory=Vc8StructuredMemoryProfile.Raise(x.GetProperty("lift"),deps,x.TryGetProperty("runtime_terminal_evidence",out var terminalRuntime)?terminalRuntime.Deserialize<RuntimeTerminalEvidence>(Engine.Options):null);Console.WriteLine(Engine.Json(new{status="generated",ir=memory,source=Vc8StructuredMemoryProfile.Emit(memory,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var mod)?mod.GetString()!:"open.exe",x.GetProperty("lift"),x.TryGetProperty("typed_receiver",out var typedReceiver)&&typedReceiver.GetBoolean(),x.TryGetProperty("compact_scalars",out var compactScalars)&&compactScalars.GetBoolean(),x.TryGetProperty("incoming_value_identities",out var incomingValues)&&incomingValues.GetBoolean()),proof=false}));return 0;}
                    if(x.TryGetProperty("counted_loops",out var loopSelected)&&loopSelected.GetBoolean()) {var loop=Vc8LoopsProfile.Raise(x.GetProperty("lift"));Console.WriteLine(Engine.Json(new{status="generated",ir=loop,source=Vc8LoopsProfile.Emit(loop,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.TryGetProperty("module",out var mod)?mod.GetString()!:"open.exe"),proof=false}));return 0;}
                    if(x.TryGetProperty("graph_paths",out var graphSelected)&&graphSelected.GetBoolean()) {var graph=X86GraphRecovery.Raise(x.GetProperty("lift"));Console.WriteLine(Engine.Json(new{status="recovered",ir=graph,proof=false}));return 0;}
                    if(x.TryGetProperty("by_value_calls",out var byValueSelected)&&byValueSelected.GetBoolean()) {
                        var deps=x.GetProperty("callee_lifts").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();var recovered=Vc8ByValueCallsProfile.Raise(x.GetProperty("lift"),deps);var emittedByValue=Vc8ByValueCallsProfile.Emit(recovered,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var module)?module.GetString()!:"open.exe");Console.WriteLine(Engine.Json(new{status="generated",ir=recovered,source=emittedByValue,proof=false}));return 0;
                    }
                    if(x.TryGetProperty("eh_paths",out var ehSelected)&&ehSelected.GetBoolean()) {
                        var deps=x.GetProperty("callee_lifts").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();
                        var eh=Vc8EhProfile.Raise(x.GetProperty("lift"),deps,x.GetProperty("eh_evidence"));var emitted=x.TryGetProperty("emit",out var output)&&!output.GetBoolean()?"":Vc8EhProfile.Emit(eh,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var mod)?mod.GetString()!:"open.exe");
                        Console.WriteLine(Engine.Json(new{status=emitted.Length==0?"recovered":"generated",ir=eh,source=emitted,proof=false}));return 0;
                    }
                    if(x.TryGetProperty("flow_paths",out var flowSelected)&&flowSelected.GetBoolean()) {
                        var deps=x.GetProperty("callee_lifts").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();
                        var contract=x.TryGetProperty("flow_contract",out var flowContract)?flowContract.Deserialize<FlowCallContract>(Engine.Options)!:new(abi,true,true);
                        var flow=X86FlowRecovery.Raise(x.GetProperty("lift"),contract,deps);
                        Console.WriteLine(Engine.Json(new{status="recovered",ir=flow,proof=false,source_emission="not_selected"}));return 0;
                    }

                    if(x.TryGetProperty("leaf_returns",out var leafSelected)&&leafSelected.GetBoolean()) {var leaf=Vc8LeafReturnProfile.Raise(x.GetProperty("lift"));Console.WriteLine(Engine.Json(new{status="generated",ir=leaf,source=Vc8LeafReturnProfile.Emit(leaf,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.TryGetProperty("module",out var mod)?mod.GetString()!:"open.exe"),proof=false}));return 0;}
                    var adapters=x.TryGetProperty("call_adapters",out var adapterSelected)&&adapterSelected.GetBoolean();var conditional=adapters||(x.TryGetProperty("conditional_calls",out var conditionalSelected)&&conditionalSelected.GetBoolean());var stack=conditional||(x.TryGetProperty("stack_arguments",out var selected)&&selected.GetBoolean());if(conditional&&!x.TryGetProperty("abi",out _))abi=adapters?Vc8CallAdaptersProfile.Abi:Vc8ConditionalCallsProfile.Abi;object ir;string source;
                    try {var basic=X86Recovery.Raise(x.GetProperty("lift"),abi);ir=basic;source=x.TryGetProperty("emit",out var emit)&&!emit.GetBoolean()?"":Vc8Profile.Emit(basic,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var module)?module.GetString()!:"open_fixture");}
                    catch(ArgumentException) when(stack) {
                        var callees=x.GetProperty("callee_lifts").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();
                        try {if(Vc8LeafReturnProfile.TryRaise(x.GetProperty("lift"),out var leaf)){ir=leaf!;source=x.TryGetProperty("emit",out var leafEmit)&&!leafEmit.GetBoolean()?"":Vc8LeafReturnProfile.Emit(leaf!,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.TryGetProperty("module",out var leafModule)?leafModule.GetString()!:"open_fixture");}else{var recovered=X86StackArgumentRecovery.Raise(x.GetProperty("lift"),abi,callees);ir=recovered;source=x.TryGetProperty("emit",out var emit)&&!emit.GetBoolean()?"":Vc8StackArgsProfile.Emit(recovered,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var module)?module.GetString()!:"open_fixture");}}
                        catch(ArgumentException) when(conditional) {var recovered=X86ConditionalRecovery.Raise(x.GetProperty("lift"),abi,callees,true,adapters);ir=recovered;source=x.TryGetProperty("emit",out var emit)&&!emit.GetBoolean()?"":Vc8ConditionalCallsProfile.Emit(recovered,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var module)?module.GetString()!:"open_fixture");}
                    }
                    if(source.Length==0)Console.WriteLine(Engine.Json(new{status="recovered",ir,proof=false}));
                    else Console.WriteLine(Engine.Json(new{status="generated",ir,source,proof=false}));
                }
                catch(Exception e) when(e is ArgumentException or KeyNotFoundException or InvalidOperationException) {Console.WriteLine(Engine.Json(new{status="unsupported",blocker=e.Message,proof=false}));}
                return 0;
            }
            var configAt = Array.IndexOf(args, "--config");
            if (configAt < 0 || configAt + 1 >= args.Length) throw new ArgumentException("Use serve|project-list|worker --config /absolute/registry.json [--job ID]");
            var engine = new Engine(args[configAt + 1]);
            var command = args.FirstOrDefault() ?? "serve";
            if (command == "worker") { await engine.RunJob(args[Array.IndexOf(args, "--job") + 1]); return 0; }
            if (command == "project-list") { Console.WriteLine(Engine.Json(engine.ProjectList())); return 0; }
            if (command != "serve") throw new ArgumentException("Unknown command");
            var builder = Host.CreateApplicationBuilder();
            builder.Logging.ClearProviders();
            builder.Logging.AddConsole(o => o.LogToStandardErrorThreshold = LogLevel.Trace);
            builder.Services.AddSingleton(engine);
            builder.Services.AddMcpServer().WithStdioServerTransport().WithToolsFromAssembly();
            await builder.Build().RunAsync();
            return 0;
        }
        catch (Exception e) { Console.Error.WriteLine(e.Message); return 1; }
    }
}

[McpServerToolType]
public sealed class DecompilationTools(Engine engine)
{
    [McpServerTool(Name = "project_list"), Description("List locally registered projects. No filesystem paths accepted and no paid work.")]
    public string ProjectList() => Engine.Json(engine.ProjectList());

    [McpServerTool(Name = "project_open"), Description("Open a registered immutable inventory/publication snapshot; return separate evidence states and implemented capabilities.")]
    public string ProjectOpen(string project_id) => Engine.Json(engine.ProjectOpen(project_id));

    [McpServerTool(Name = "function_query"), Description("Page inventory identities in RVA order. Publication is imported historical evidence, not a fresh validation. Cursor binds snapshot and filters.")]
    public string FunctionQuery(string project_id, string? cursor = null, int limit = 25, string publication = "all", string? name_contains = null) => Engine.Json(engine.Query(project_id, cursor, limit, publication, name_contains));

    [McpServerTool(Name = "function_inspect"), Description("Compact identity, range/signature hypotheses, bounded published C++ and retained build references. Never returns proprietary binary bytes.")]
    public string FunctionInspect(string project_id, string function_id, int source_limit = 2000) => Engine.Json(engine.Inspect(project_id, function_id, source_limit));

    [McpServerTool(Name = "corpus_find_related"), Description("Deterministic size/range/signature similarity over the entire inventory. Ranking is a search signal and grants no match credit.")]
    public string FindRelated(string project_id, string function_id, int limit = 10) => Engine.Json(engine.Related(project_id, function_id, limit));

    [McpServerTool(Name = "candidate_check"), Description("Freshly recheck a registered retained source/object build using actual original, inventory ranges, compiler inputs and strict symbol binder. Returns a durable job promptly; registered ABI-effect diagnostics are nonaccepting while observation policy is pending. No compilation/publication. Same idempotency key returns the same historical job.")]
    public string CandidateCheck(string project_id, string build_id, string idempotency_key) => Engine.Json(engine.SubmitCheck(project_id, build_id, idempotency_key));

    [McpServerTool(Name = "replayable_run_next"), Description("Generate and optionally compile/check the lowest inventory RVA without a current accepted pipeline match. Unsupported frontiers remain active. Versioned JSON recipes are bounded; no provider calls or source publication.")]
    public string ReplayableRunNext(string project_id,string idempotency_key,string? recipe_json=null,bool compile=true) => Engine.Json(engine.ReplayableNext(project_id,idempotency_key,recipe_json,compile));

    [McpServerTool(Name = "replayable_regression_check"), Description("Generate and optionally compile/check one explicit registered inventory identity through the durable replayable worker. Separate regression results never advance the ascending recovery frontier. Optional source hash is checked before compilation; no source injection.")]
    public string ReplayableRegressionCheck(string project_id,string function_id,string idempotency_key,string? expected_source_sha256=null,string? recipe_json=null,bool compile=true) => Engine.Json(engine.ReplayableRegression(project_id,function_id,idempotency_key,recipe_json,compile,expected_source_sha256));

    [McpServerTool(Name = "replayable_regression_batch"), Description("Durably claim 1..16 unique inventory identities for one serial guest compiler envelope and independent complete per-function comparisons. Does not advance the ascending recovery selector. Partial/unknown execution blocks all project compilation and is never automatically retried. Optional expected source hashes are a JSON identity-to-SHA256 object.")]
    public string ReplayableRegressionBatch(string project_id,string[] function_ids,string idempotency_key,string? recipe_json=null,string? expected_sources_json=null) => Engine.Json(engine.ReplayableRegressionBatch(project_id,function_ids,idempotency_key,recipe_json,expected_sources_json));

    [McpServerTool(Name = "replayable_abandon_unknown"), Description("Durably abandon one completed missing-exit-marker attempt without accepting it or retrying. Requires a registered synchronous transport profile, exact retained bindings, absent launch prefix/workspace and quiescent isolated compiler host. Original unknown result remains unchanged; unsafe or unsupported observations retain the project barrier.")]
    public string ReplayableAbandonUnknown(string project_id,string unknown_job_id,string idempotency_key) => Engine.Json(engine.ReplayableAbandonUnknown(project_id,unknown_job_id,idempotency_key));

    [McpServerTool(Name = "replayable_status"), Description("Inspect the current exact pipeline key, ascending unresolved frontier, inventory denominator and current artifact-bound match count. Historical imported sources do not count.")]
    public string ReplayableStatus(string project_id,string? recipe_json=null) => Engine.Json(engine.ReplayableStatus(project_id,recipe_json));

    [McpServerTool(Name = "replayable_analysis_replay"), Description("Replay the bounded leaf source-proposal profile for 1..16 explicit inventory identities using indexed bound typed lifts only. Ordinary selected generation populates the existing job database. Reports missing, stale, legacy, failed, incomplete or unsupported records. No lifting, compiler, acceptance, export or frontier update; produces a bound local report.")]
    public async Task<string> ReplayableAnalysisReplay(string project_id,string[] function_ids,string? recipe_json=null) => Engine.Json(await engine.ReplayableAnalysisReplay(project_id,function_ids,recipe_json));

    [McpServerTool(Name = "replayable_inspect"), Description("Read bounded generated source and typed recovered IR from a replayable job. Identity and acceptance remain separate from source spelling.")]
    public string ReplayableInspect(string job_id,int source_limit=4000) => Engine.Json(engine.ReplayableInspect(job_id,source_limit));

    [McpServerTool(Name = "source_export"), Description("Durably export 1..16 explicit accepted replayable jobs to a registered independent source namespace after current source regeneration and fresh complete ordinary/SIB/EH artifact checks. Expected project and publication revisions prevent stale writes. No compilation, ABI-diagnostic acceptance, linking or match-credit transfer; same token returns historical job.")]
    public string SourceExport(string project_id,string[] job_ids,string expected_revision,string expected_publication_revision,string idempotency_key) => Engine.Json(engine.SourceExport(project_id,job_ids,expected_revision,expected_publication_revision,idempotency_key));

    [McpServerTool(Name = "job_get"), Description("Read compact persisted job result. Reading a completed result never revalidates it. An interrupted worker is conservatively interrupted_unknown.")]
    public string JobGet(string job_id) => Engine.Json(engine.JobGet(job_id));
}
