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
                try { var abi=x.TryGetProperty("abi",out var abiElement)?abiElement.Deserialize<RecoveryAbi>(Engine.Options)!:Vc8Profile.Abi;var ir=X86Recovery.Raise(x.GetProperty("lift"),abi);if(x.TryGetProperty("emit",out var emit)&&!emit.GetBoolean()){Console.WriteLine(Engine.Json(new{status="recovered",ir,proof=false}));return 0;}var source=Vc8Profile.Emit(ir,x.GetProperty("rva").GetUInt32(),x.GetProperty("image_base").GetUInt32(),x.GetProperty("image_end").GetUInt32(),x.TryGetProperty("module",out var module)?module.GetString()!:"open_fixture");Console.WriteLine(Engine.Json(new{status="generated",ir,source,proof=false})); }
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

    [McpServerTool(Name = "candidate_check"), Description("Freshly recheck a registered retained source/object build using actual original, inventory ranges, compiler inputs and strict symbol binder. Returns a durable job promptly; no compilation/publication. Same idempotency key returns the same historical job.")]
    public string CandidateCheck(string project_id, string build_id, string idempotency_key) => Engine.Json(engine.SubmitCheck(project_id, build_id, idempotency_key));

    [McpServerTool(Name = "replayable_run_next"), Description("Generate and optionally compile/check the lowest inventory RVA without a current pipeline full match. Unsupported frontiers remain active. Versioned JSON recipes are bounded; no provider calls or source publication.")]
    public string ReplayableRunNext(string project_id,string idempotency_key,string? recipe_json=null,bool compile=true) => Engine.Json(engine.ReplayableNext(project_id,idempotency_key,recipe_json,compile));

    [McpServerTool(Name = "replayable_status"), Description("Inspect the current exact pipeline key, ascending unresolved frontier, inventory denominator and current artifact-bound match count. Historical imported sources do not count.")]
    public string ReplayableStatus(string project_id) => Engine.Json(engine.ReplayableStatus(project_id));

    [McpServerTool(Name = "replayable_inspect"), Description("Read bounded generated source and typed recovered IR from a replayable job. Identity and acceptance remain separate from source spelling.")]
    public string ReplayableInspect(string job_id,int source_limit=4000) => Engine.Json(engine.ReplayableInspect(job_id,source_limit));

    [McpServerTool(Name = "job_get"), Description("Read compact persisted job result. Reading a completed result never revalidates it. An interrupted worker is conservatively interrupted_unknown.")]
    public string JobGet(string job_id) => Engine.Json(engine.JobGet(job_id));
}
