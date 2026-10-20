using System.Diagnostics;
using System.Reflection;
using System.Text.Json;
namespace Decompilation;
public sealed record ReplayableConfig(string LifterConfig,string VmBuildLock,string OutputRoot);
public sealed record PipelineRecipe(int SchemaVersion,string Architecture,string Frontend,string CompilerProfile,string[] Steps)
{
    public static PipelineRecipe Default=>new(1,"x86-bits32-linear-v1","sharpretro-typed-v1",Vc8Profile.Version,["raise-linear-effects-v1","emit-thiscall-stores-v1"]);
    public void Validate() { if(SchemaVersion!=1||Architecture!="x86-bits32-linear-v1"||Frontend!="sharpretro-typed-v1"||CompilerProfile!=Vc8Profile.Version||!Steps.SequenceEqual(Default.Steps))throw new ArgumentException("unsupported_recipe_or_step_order"); }
}
public sealed partial class Engine
{
    Dictionary<string,string> PipelineInputs(Snapshot p,PipelineRecipe recipe)
    {
        recipe.Validate();var cfg=p.Config.Replayable??throw new ArgumentException("replayable_not_registered");
        var result=new Dictionary<string,string>();
        foreach(var path in new[]{p.Config.Inventory,p.Config.Original,p.Config.Compiler,cfg.LifterConfig,Assembly.GetExecutingAssembly().Location,Path.Combine(AppContext.BaseDirectory,"replayable_adapter.py")})
        { if(path==null)throw new ArgumentException("missing_pipeline_input");result[path]=Hash(File.ReadAllBytes(path)); }
        var lifter=Read<JsonElement>(Safe(p.Config,cfg.LifterConfig));
        foreach(var name in new[]{"build_manifest","adapter_dll"})
        {var path=lifter.GetProperty(name).GetString()!;path=Path.IsPathFullyQualified(path)?path:Path.Combine(Path.GetDirectoryName(cfg.LifterConfig)!,path);result[path]=Hash(File.ReadAllBytes(Safe(p.Config,path)));}
        var lifterConfigPath=cfg.LifterConfig;string ResolveLifter(string value)=>Path.IsPathFullyQualified(value)?value:Path.Combine(Path.GetDirectoryName(lifterConfigPath)!,value);
        var dllPath=ResolveLifter(lifter.GetProperty("adapter_dll").GetString()!);
        foreach(var path in Directory.EnumerateFiles(Path.GetDirectoryName(dllPath)!).Where(f=>f.EndsWith(".dll")||f.EndsWith(".json")))result[path]=Hash(File.ReadAllBytes(Safe(p.Config,path)));
        var manifest=Read<JsonElement>(ResolveLifter(lifter.GetProperty("build_manifest").GetString()!));var checkout=ResolveLifter(lifter.GetProperty("sharp_retro_checkout").GetString()!);
        foreach(var property in manifest.GetProperty("upstream_tracked_source_sha256").EnumerateObject()){var path=Safe(p.Config,Path.Combine(checkout,property.Name));var hash=Hash(File.ReadAllBytes(path));if(hash!=property.Value.GetString())throw new ArgumentException("lifter_source_changed");result[path]=hash;}
        foreach(var component in new[]{"rapid_object","rapid_native","rapid","workers"})foreach(var path in Directory.EnumerateFiles(Path.Combine(registry.AdapterRoot,component),"*.py",SearchOption.AllDirectories))result[path]=Hash(File.ReadAllBytes(path));
        if(result[p.Config.Original!]!=p.Config.ModuleSha256||result[p.Config.Inventory]!=p.InventorySha256||result[p.Config.Compiler!]!=p.Config.CompilerSha256)throw new ArgumentException("pipeline_input_pin_changed");
        return result;
    }
    public object ReplayableNext(string projectId,string token,string? recipeJson,bool compile)
    {
        if(token.Length<1||token.Length>128)throw new ArgumentException("invalid_idempotency_key");
        var p=Open(projectId);var recipe=recipeJson==null?PipelineRecipe.Default:JsonSerializer.Deserialize<PipelineRecipe>(recipeJson,Options)!;var inputs=PipelineInputs(p,recipe);
        var key=HashText(Json(new{inputs,recipe,p.Config}));
        using var db=Db();using var tx=db.BeginTransaction();
        using var schema=db.CreateCommand();schema.Transaction=tx;schema.CommandText="CREATE TABLE IF NOT EXISTS replayable_frontier(project TEXT,input_key TEXT,rva INTEGER,status TEXT,job TEXT,PRIMARY KEY(project,input_key,rva));";schema.ExecuteNonQuery();
        using var old=db.CreateCommand();old.Transaction=tx;old.CommandText="SELECT id,request FROM jobs WHERE project=$p AND token=$t";old.Parameters.AddWithValue("$p",projectId);old.Parameters.AddWithValue("$t",token);
        using(var r=old.ExecuteReader())if(r.Read()){var req=JsonDocument.Parse(r.GetString(1)).RootElement;if(!req.TryGetProperty("pipeline_key",out var k)||k.GetString()!=key||req.GetProperty("compile").GetBoolean()!=compile)throw new ArgumentException("idempotency_request_changed");return new{job_id=r.GetString(0),reused=true};}
        // External uncertainty belongs to the project, not a cache/input key.
        // A changed compiler, lifter or engine cannot authorize replay of an old attempt.
        using var barrier=db.CreateCommand();barrier.Transaction=tx;barrier.CommandText="SELECT job FROM replayable_frontier WHERE project=$p AND status IN ('running','external_outcome_unknown') ORDER BY rva,input_key LIMIT 1";barrier.Parameters.AddWithValue("$p",projectId);
        if(barrier.ExecuteScalar() is string unresolvedJob)throw new ArgumentException("frontier_job_active_or_unknown_reconciliation_required:"+unresolvedJob);
        var complete=new HashSet<uint>();using var q=db.CreateCommand();q.Transaction=tx;q.CommandText="SELECT rva,status,job FROM replayable_frontier WHERE project=$p AND input_key=$k";q.Parameters.AddWithValue("$p",projectId);q.Parameters.AddWithValue("$k",key);
        using(var r=q.ExecuteReader())while(r.Read()){if(r.GetString(1)=="full_match" && ValidPipelineMatch(p,r.GetString(2)))complete.Add((uint)r.GetInt64(0));}
        var f=p.Functions.FirstOrDefault(f=>!complete.Contains(f.Rva));if(f==null)return new{status="inventory_complete",new_pipeline_full_matches=complete.Count};
        var job=Guid.NewGuid().ToString("N");var request=Json(new{operation="replayable",project=p.Config,recipe,inputs,pipeline_key=key,rva=f.Rva,entry=f.Entry,compile});
        using var insert=db.CreateCommand();insert.Transaction=tx;insert.CommandText="INSERT INTO jobs(id,project,token,request,state,created) VALUES($i,$p,$t,$r,'queued',$c); INSERT INTO replayable_frontier(project,input_key,rva,status,job) VALUES($p,$k,$v,'running',$i) ON CONFLICT(project,input_key,rva) DO UPDATE SET status='running',job=$i";
        foreach(var (n,v) in new[]{("$i",job),("$p",projectId),("$t",token),("$r",request),("$c",DateTimeOffset.UtcNow.ToString("O")),("$k",key)})insert.Parameters.AddWithValue(n,v);insert.Parameters.AddWithValue("$v",(long)f.Rva);insert.ExecuteNonQuery();tx.Commit();StartWorker(job);
        return new{job_id=job,rva=f.Rva,pipeline_key=key,ascending_frontier=true,publication="draft_only",reused=false};
    }
    public object ReplayableStatus(string projectId)
    {
        var p=Open(projectId);var recipe=PipelineRecipe.Default;var inputs=PipelineInputs(p,recipe);var key=HashText(Json(new{inputs,recipe,p.Config}));
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="CREATE TABLE IF NOT EXISTS replayable_frontier(project TEXT,input_key TEXT,rva INTEGER,status TEXT,job TEXT,PRIMARY KEY(project,input_key,rva)); SELECT rva,status,job FROM replayable_frontier WHERE project=$p AND input_key=$k ORDER BY rva";cmd.Parameters.AddWithValue("$p",projectId);cmd.Parameters.AddWithValue("$k",key);
        var complete=new HashSet<uint>();var rows=new List<object>();using(var r=cmd.ExecuteReader())while(r.Read()){var rva=(uint)r.GetInt64(0);var status=r.GetString(1);var current=status=="full_match"&&ValidPipelineMatch(p,r.GetString(2));if(current)complete.Add(rva);rows.Add(new{rva,status,job_id=r.GetString(2),current_full_match=current});}
        return new{schema_version=1,pipeline_key=key,recipe,inventory_identities=p.Functions.Length,new_pipeline_full_matches=complete.Count,first_unresolved_rva=p.Functions.FirstOrDefault(f=>!complete.Contains(f.Rva))?.Rva,attempted_frontiers=rows.Take(100),frontier_row_count=rows.Count,frontier_rows_truncated=rows.Count>100,provider_calls=0,publication="draft_only",proof=false};
    }
    bool ValidPipelineMatch(Snapshot p,string job)
    {
        try {
            var folder=Path.Combine(Safe(p.Config,p.Config.Replayable!.OutputRoot),job);var result=Read<JsonElement>(Path.Combine(folder,"result.json"));
            return result.GetProperty("status").GetString()=="full_match" && Hash(File.ReadAllBytes(Path.Combine(folder,"candidate.cpp")))==result.GetProperty("source_sha256").GetString() && Hash(File.ReadAllBytes(Path.Combine(folder,"build/candidate.obj")))==result.GetProperty("object_sha256").GetString() && Hash(File.ReadAllBytes(Path.Combine(folder,"comparison.json")))==result.GetProperty("comparison_sha256").GetString();
        } catch(Exception e) when(e is IOException or JsonException or KeyNotFoundException) {return false;}
    }
    public object ReplayableInspect(string id,int limit)
    {
        Limit(limit,12000);if(!Guid.TryParseExact(id,"N",out _))throw new ArgumentException("invalid_job_id");
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="SELECT request,state,result FROM jobs WHERE id=$i";cmd.Parameters.AddWithValue("$i",id);using var reader=cmd.ExecuteReader();if(!reader.Read())throw new ArgumentException("unknown_job");
        var request=JsonDocument.Parse(reader.GetString(0)).RootElement;if(!request.TryGetProperty("operation",out var op)||op.GetString()!="replayable")throw new ArgumentException("not_replayable_job");
        var p=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var folder=Path.Combine(Safe(p,p.Replayable!.OutputRoot),id);var path=Path.Combine(folder,"candidate.cpp");var source=File.Exists(path)?File.ReadAllText(path):null;
        var irPath=Path.Combine(folder,"recovered-ir.json");var ir=File.Exists(irPath)?File.ReadAllText(irPath):null;
        return new{job_id=id,rva=request.GetProperty("rva").GetUInt32(),state=reader.GetString(1),source=source?[..Math.Min(limit,source.Length)],source_sha256=source==null?null:HashText(source),source_truncated=source?.Length>limit,recovered_ir=ir==null?null:ir[..Math.Min(limit,ir.Length)],ir_truncated=ir?.Length>limit,publication="draft_only",proof=false};
    }
    async Task<JsonElement> ReplayableAdapter(JsonElement request,string action,string folder,string? source=null)
    {
        var pi=new ProcessStartInfo(registry.Python){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=registry.AdapterRoot};
        pi.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory,"replayable_adapter.py"));pi.ArgumentList.Add("--adapter-root");pi.ArgumentList.Add(registry.AdapterRoot);
        using var process=Process.Start(pi)??throw new IOException("pipeline_adapter_start");await process.StandardInput.WriteAsync(Json(new{request,action,folder,source}));process.StandardInput.Close();var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
        using var timeout=new CancellationTokenSource(TimeSpan.FromMinutes(6));try{await process.WaitForExitAsync(timeout.Token);}catch(OperationCanceledException){process.Kill(true);throw new IOException("external_pipeline_timeout_unknown");}
        var text=await output;await errors;if(process.ExitCode!=0||text.Length>2_000_000)throw new IOException("pipeline_adapter_failure");return JsonDocument.Parse(text).RootElement.Clone();
    }
    async Task RunReplayable(string job,JsonElement request)
    {
        string status="inconclusive";object result;
        try
        {
            foreach(var pair in request.GetProperty("inputs").EnumerateObject())if(Hash(File.ReadAllBytes(pair.Name))!=pair.Value.GetString())throw new ArgumentException("submitted_pipeline_input_changed");
            var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var cfg=project.Replayable!;var folder=Path.Combine(Safe(project,cfg.OutputRoot),job);Directory.CreateDirectory(folder);File.WriteAllText(Path.Combine(folder,"request.json"),request.GetRawText());
            var lifted=await ReplayableAdapter(request,"lift",folder);if(lifted.TryGetProperty("error",out var error))throw new ArgumentException(error.GetString());
            File.WriteAllText(Path.Combine(folder,"lift.json"),lifted.GetRawText());var ir=X86Recovery.Raise(lifted.GetProperty("lift"),Vc8Profile.Abi);File.WriteAllText(Path.Combine(folder,"recovered-ir.json"),Json(ir));
            var source=Vc8Profile.Emit(ir,request.GetProperty("rva").GetUInt32(),lifted.GetProperty("image_base").GetUInt32(),lifted.GetProperty("image_end").GetUInt32(),project.Module);File.WriteAllText(Path.Combine(folder,"candidate.cpp"),source);
            if(request.GetProperty("compile").GetBoolean()){var checkedResult=await ReplayableAdapter(request,"build",folder,source);status=checkedResult.GetProperty("status").GetString()!;result=checkedResult;}
            else {status="generated";result=new{status,source,source_sha256=HashText(source),compiled=false,proof=false};}
            File.WriteAllText(Path.Combine(folder,"result.json"),Json(result));
        }
        catch(Exception e) when(e is IOException or ArgumentException or KeyNotFoundException or JsonException or InvalidOperationException){if(e is IOException && request.GetProperty("compile").GetBoolean())status="external_outcome_unknown";result=new{status,blocker=e.Message,proof=false};}
        var resultProject=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var resultFolder=Path.Combine(Safe(resultProject,resultProject.Replayable!.OutputRoot),job);Directory.CreateDirectory(resultFolder);File.WriteAllText(Path.Combine(resultFolder,"result.json"),Json(result));
        using(var db=Db()){using var cmd=db.CreateCommand();cmd.CommandText="UPDATE replayable_frontier SET status=$s WHERE project=$p AND input_key=$k AND job=$j";cmd.Parameters.AddWithValue("$s",status);cmd.Parameters.AddWithValue("$p",request.GetProperty("project").GetProperty("id").GetString());cmd.Parameters.AddWithValue("$k",request.GetProperty("pipeline_key").GetString());cmd.Parameters.AddWithValue("$j",job);cmd.ExecuteNonQuery();}
        Finish(job,"completed",result);
    }
}
