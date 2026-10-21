using System.Diagnostics;
using System.Reflection;
using System.Text.Json;
namespace Decompilation;
public sealed record ReplayableConfig(string LifterConfig,string VmBuildLock,string OutputRoot,string? TransportConfig=null,string? EquivalenceSolverConfig=null);
public sealed record PipelineRecipe(int SchemaVersion,string Architecture,string Frontend,string CompilerProfile,string[] Steps)
{
    public static PipelineRecipe Default=>new(1,"x86-bits32-linear-tail-v2","sharpretro-typed-v1",Vc8Profile.Version,["raise-linear-effects-tail-v2","emit-thiscall-stores-tail-v2"]);
    public static PipelineRecipe StackArguments=>new(1,"x86-bits32-linear-tail-stack-v1","sharpretro-typed-v1",Vc8StackArgsProfile.Version,["raise-linear-effects-tail-v2","derive-original-normal-return-stack-v1","emit-vc8-composed-stack-v1"]);
    public static PipelineRecipe ConditionalCalls=>new(1,"x86-bits32-one-forward-conditional-v1","sharpretro-typed-v1",Vc8ConditionalCallsProfile.Version,["raise-linear-effects-tail-v2","derive-original-normal-return-stack-v1","resolve-pure-forwarding-normal-return-v1","raise-one-forward-conditional-v1","emit-vc8-composed-conditional-v1"]);
    public static PipelineRecipe EhTwoExit=>new(1,"x86-bits32-bounded-paths-EH-v1","sharpretro-typed-v1",Vc8EhProfile.Version,["raise-linear-effects-tail-v2","derive-original-normal-return-stack-v1","resolve-pure-forwarding-normal-return-v1","raise-one-forward-conditional-v1","raise-bounded-two-exit-effects-v1","derive-original-VC8-EH-frame-v1","emit-vc8-composed-EH-v1"]);
    public static PipelineRecipe CallAdapters=>new(1,"x86-bits32-composed-call-adapters-v1","sharpretro-typed-v1",Vc8CallAdaptersProfile.Version,["raise-linear-effects-tail-v2","derive-original-normal-return-stack-v1","resolve-pure-forwarding-normal-return-v1","resolve-transparent-effectful-tail-ABI-v1","raise-one-forward-conditional-v1","raise-bounded-two-exit-effects-v1","derive-original-VC8-EH-frame-v1","emit-vc8-composed-call-adapters-v1"]);
    public static PipelineRecipe ByValueCalls=>new(1,"x86-bits32-composed-byvalue-calls-v1","sharpretro-typed-v1",Vc8ByValueCallsProfile.Version,["raise-linear-effects-tail-v2","derive-original-normal-return-stack-v1","resolve-pure-forwarding-normal-return-v1","resolve-transparent-effectful-tail-ABI-v1","raise-one-forward-conditional-v1","raise-bounded-two-exit-effects-v1","derive-original-VC8-EH-frame-v1","raise-initialized-private-subword-copies-v1","observe-outgoing-push-and-private-cleanup-regions-v1","emit-vc8-composed-byvalue-calls-v1"]);
    public static PipelineRecipe IncomingSlotValues=>new(1,"x86-bits32-incoming-slot-value-identities-v1","sharpretro-typed-v1",Vc8TerminalCallProfile.Version,[..ScalarSource.Steps,IncomingSlotValueIdentityRecovery.Version,"compare-windows-x86-inherited-unwind-ordered-events-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesIncomingSlotValues=>Architecture==IncomingSlotValues.Architecture;
    public static PipelineRecipe BehavioralEvents=>new(1,"x86-bits32-scalar-behavioral-events-v1","sharpretro-typed-v1",Vc8TerminalCallProfile.Version,[..ScalarSource.Steps,"compare-windows-x86-inherited-unwind-ordered-events-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesBehavioralEvents=>Architecture==BehavioralEvents.Architecture||UsesIncomingSlotValues;
    public static PipelineRecipe ScalarSource=>new(1,"x86-bits32-terminal-aware-scalar-source-v1","sharpretro-typed-v1",Vc8TerminalCallProfile.Version,[..TypedReceiver.Steps,"compact-captured-instruction-local-unsigned-scalars-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesScalarSource=>Architecture==ScalarSource.Architecture||UsesBehavioralEvents;
    public static PipelineRecipe TypedReceiver=>new(1,"x86-bits32-terminal-aware-typed-receiver-v1","sharpretro-typed-v1",Vc8TerminalCallProfile.Version,[..TerminalMemory.Steps,"lower-vc8-packed-observed-receiver-word-fields-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesTypedReceiver=>Architecture==TypedReceiver.Architecture||UsesScalarSource;
    public static PipelineRecipe AbiEffects=>new(1,"x86-bits32-terminal-aware-abi-effects-v1","sharpretro-typed-v1",Vc8TerminalCallProfile.Version,[..TerminalMemory.Steps,"compare-complete-flat32-ABI-effects-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesAbiEffects=>Architecture==AbiEffects.Architecture;
    public static PipelineRecipe TerminalMemory=>new(1,"x86-bits32-terminal-aware-memory-encoding-v1","sharpretro-typed-v1",Vc8TerminalCallProfile.Version,[..OrderedMemory.Steps,"derive-original-noncontinuable-CRT-exits-v1","raise-terminal-calls-incoming-word-slots-v1","emit-vc8-terminal-aware-memory-control-v1","compare-complete-x86-encoding-equivalence-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesTerminalMemory=>Architecture==TerminalMemory.Architecture||UsesAbiEffects||UsesTypedReceiver;
    public static PipelineRecipe EncodingEquivalence=>new(1,"x86-bits32-composed-memory-encoding-equivalence-v1","sharpretro-typed-v1",Vc8StructuredMemoryProfile.Version,[..OrderedMemory.Steps,"compare-complete-x86-encoding-equivalence-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesEncodingEquivalence=>Architecture==EncodingEquivalence.Architecture||UsesTerminalMemory;
    public static PipelineRecipe OrderedMemory=>new(1,"x86-bits32-composed-ordered-memory-control-v1","sharpretro-typed-v1",Vc8StructuredMemoryProfile.Version,[..CountedLoops.Steps[..^1],"raise-aliasable-forward-memory-effects-v1","emit-vc8-composed-ordered-memory-control-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesOrderedMemory=>CompilerProfile is Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    public static PipelineRecipe CountedLoops=>new(1,"x86-bits32-composed-counted-loops-v1","sharpretro-typed-v1",Vc8LoopsProfile.Version,[..ByValueCalls.Steps[..^1],"raise-reducible-ordered-memory-graph-v1","raise-guarded-counted-loop-v1","emit-vc8-composed-counted-loops-v1"]);
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesCountedLoops=>CompilerProfile is Vc8LoopsProfile.Version or Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesByValueCalls=>CompilerProfile is Vc8ByValueCallsProfile.Version or Vc8LoopsProfile.Version or Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesCallAdapters=>CompilerProfile is Vc8CallAdaptersProfile.Version or Vc8ByValueCallsProfile.Version or Vc8LoopsProfile.Version or Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesEh=>CompilerProfile is Vc8EhProfile.Version or Vc8CallAdaptersProfile.Version or Vc8ByValueCallsProfile.Version or Vc8LoopsProfile.Version or Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesStackArguments=>CompilerProfile is Vc8StackArgsProfile.Version or Vc8ConditionalCallsProfile.Version or Vc8EhProfile.Version or Vc8CallAdaptersProfile.Version or Vc8ByValueCallsProfile.Version or Vc8LoopsProfile.Version or Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    [System.Text.Json.Serialization.JsonIgnore]
    public bool UsesConditionalCalls=>CompilerProfile is Vc8ConditionalCallsProfile.Version or Vc8EhProfile.Version or Vc8CallAdaptersProfile.Version or Vc8ByValueCallsProfile.Version or Vc8LoopsProfile.Version or Vc8StructuredMemoryProfile.Version or Vc8TerminalCallProfile.Version;
    public void Validate() { if(SchemaVersion!=1||Frontend!="sharpretro-typed-v1"||!(new[]{Default,StackArguments,ConditionalCalls,EhTwoExit,CallAdapters,ByValueCalls,CountedLoops,OrderedMemory,EncodingEquivalence,TerminalMemory,AbiEffects,TypedReceiver,ScalarSource,BehavioralEvents,IncomingSlotValues}.Any(r=>Architecture==r.Architecture&&CompilerProfile==r.CompilerProfile&&Steps.SequenceEqual(r.Steps))))throw new ArgumentException("unsupported_recipe_or_step_order"); }
}
public sealed partial class Engine
{
    Dictionary<string,string> PipelineInputs(Snapshot p,PipelineRecipe recipe)
    {
        recipe.Validate();var cfg=p.Config.Replayable??throw new ArgumentException("replayable_not_registered");
        var result=new Dictionary<string,string>();
        foreach(var path in new[]{p.Config.Inventory,p.Config.Original,p.Config.Compiler,cfg.LifterConfig,Assembly.GetExecutingAssembly().Location,Path.Combine(AppContext.BaseDirectory,"replayable_adapter.py"),Path.Combine(AppContext.BaseDirectory,"adapter.py"),Path.Combine(AppContext.BaseDirectory,"replayable_transport.py")}.Concat(new[]{cfg.TransportConfig}.OfType<string>()).Concat(new[]{p.Config.EhPolicy}.Concat(p.Config.Libraries?.Values??Enumerable.Empty<string>()).Where(path=>path!=null)))
        { if(path==null)throw new ArgumentException("missing_pipeline_input");result[path]=Hash(File.ReadAllBytes(path)); }
        if(recipe.UsesAbiEffects||recipe.UsesBehavioralEvents) {
            var config=cfg.EquivalenceSolverConfig??throw new ArgumentException("abi_effects_solver_not_registered");var path=Safe(p.Config,config);result[path]=Hash(File.ReadAllBytes(path));var solver=Read<JsonElement>(path);if(solver.EnumerateObject().Count()!=4||solver.EnumerateObject().Select(v=>v.Name).Distinct().Count()!=4||solver.GetProperty("schema_version").GetInt32()!=1||solver.GetProperty("observation_profile").GetString()!=(recipe.UsesBehavioralEvents?"windows-x86-inherited-unwind-ordered-events-v1":"abi-ordered-fault-events-v1"))throw new ArgumentException("unsupported_abi_effects_observation_profile");var executable=Safe(p.Config,solver.GetProperty("executable").GetString()!);var hash=Hash(File.ReadAllBytes(executable));if(hash!=solver.GetProperty("sha256").GetString())throw new ArgumentException("abi_effects_solver_changed");result[executable]=hash;
        }
        var lifter=Read<JsonElement>(Safe(p.Config,cfg.LifterConfig));
        foreach(var name in new[]{"build_manifest","adapter_dll"})
        {var path=lifter.GetProperty(name).GetString()!;path=Path.IsPathFullyQualified(path)?path:Path.Combine(Path.GetDirectoryName(cfg.LifterConfig)!,path);result[path]=Hash(File.ReadAllBytes(Safe(p.Config,path)));}
        var lifterConfigPath=cfg.LifterConfig;string ResolveLifter(string value)=>Path.IsPathFullyQualified(value)?value:Path.Combine(Path.GetDirectoryName(lifterConfigPath)!,value);
        var dllPath=ResolveLifter(lifter.GetProperty("adapter_dll").GetString()!);
        foreach(var path in Directory.EnumerateFiles(Path.GetDirectoryName(dllPath)!).Where(f=>f.EndsWith(".dll")||f.EndsWith(".json")))result[path]=Hash(File.ReadAllBytes(Safe(p.Config,path)));
        var manifest=Read<JsonElement>(ResolveLifter(lifter.GetProperty("build_manifest").GetString()!));var checkout=ResolveLifter(lifter.GetProperty("sharp_retro_checkout").GetString()!);
        foreach(var property in manifest.GetProperty("upstream_tracked_source_sha256").EnumerateObject()){var path=Safe(p.Config,Path.Combine(checkout,property.Name));var hash=Hash(File.ReadAllBytes(path));if(hash!=property.Value.GetString())throw new ArgumentException("lifter_source_changed");result[path]=hash;}
        foreach(var component in new[]{"rapid_object","rapid_native","rapid","workers","tools/replayable"})foreach(var path in Directory.EnumerateFiles(Path.Combine(registry.AdapterRoot,component),"*.py",SearchOption.AllDirectories))result[path]=Hash(File.ReadAllBytes(path));
        if(result[p.Config.Original!]!=p.Config.ModuleSha256||result[p.Config.Inventory]!=p.InventorySha256||result[p.Config.Compiler!]!=p.Config.CompilerSha256)throw new ArgumentException("pipeline_input_pin_changed");
        return result;
    }
    public object ReplayableNext(string projectId,string token,string? recipeJson,bool compile)
        => ReplayableSubmit(projectId,token,recipeJson,compile,null,null);
    public object ReplayableRegression(string projectId,string functionId,string token,string? recipeJson,bool compile,string? expectedSourceSha256)
        => ReplayableSubmit(projectId,token,recipeJson,compile,string.IsNullOrWhiteSpace(functionId)?throw new ArgumentException("invalid_function_identity"):functionId,expectedSourceSha256);
    static string ReplayablePurpose(JsonElement request) => request.TryGetProperty("purpose",out var purpose)?purpose.GetString()!:"recovery";
    static string ReplayableTrackingKey(JsonElement request) => (ReplayablePurpose(request)=="regression"?"regression:":"")+request.GetProperty("pipeline_key").GetString();
    const string ReplayableSchema = "CREATE TABLE IF NOT EXISTS replayable_frontier(project TEXT,input_key TEXT,rva INTEGER,status TEXT,job TEXT,PRIMARY KEY(project,input_key,rva));";
    object ReplayableSubmit(string projectId,string token,string? recipeJson,bool compile,string? functionId,string? expectedSourceSha256)
    {
        if(expectedSourceSha256!=null&&(expectedSourceSha256.Length!=64||expectedSourceSha256.Any(c=>!Uri.IsHexDigit(c))||expectedSourceSha256!=expectedSourceSha256.ToLowerInvariant()))throw new ArgumentException("invalid_expected_source_sha256");
        if(token.Length<1||token.Length>128)throw new ArgumentException("invalid_idempotency_key");
        var p=Open(projectId);var target=functionId==null?null:Find(p,functionId);var purpose=target==null?"recovery":"regression";var recipe=recipeJson==null?PipelineRecipe.Default:JsonSerializer.Deserialize<PipelineRecipe>(recipeJson,Options)!;var inputs=PipelineInputs(p,recipe);
        var key=HashText(Json(new{inputs,recipe,p.Config}));
        using var db=Db();using var tx=db.BeginTransaction();
        using var schema=db.CreateCommand();schema.Transaction=tx;schema.CommandText=ReplayableSchema;schema.ExecuteNonQuery();
        using var old=db.CreateCommand();old.Transaction=tx;old.CommandText="SELECT id,request FROM jobs WHERE project=$p AND token=$t";old.Parameters.AddWithValue("$p",projectId);old.Parameters.AddWithValue("$t",token);
        using(var r=old.ExecuteReader())if(r.Read()){var req=JsonDocument.Parse(r.GetString(1)).RootElement;if(!req.TryGetProperty("pipeline_key",out var k)||k.GetString()!=key||req.GetProperty("compile").GetBoolean()!=compile||ReplayablePurpose(req)!=purpose||(target!=null&&req.GetProperty("rva").GetUInt32()!=target.Rva)||(req.TryGetProperty("expected_source_sha256",out var expected)?expected.GetString():null)!=expectedSourceSha256)throw new ArgumentException("idempotency_request_changed");return new{job_id=r.GetString(0),reused=true};}
        // External uncertainty belongs to the project, not a cache/input key.
        // Regression uses a reserved key namespace in this same table, so older engines
        // also see its project-wide barrier. A changed compiler/lifter cannot clear uncertainty.
        using var barrier=db.CreateCommand();barrier.Transaction=tx;barrier.CommandText="SELECT job FROM replayable_frontier WHERE project=$p AND status IN ('running','external_outcome_unknown') ORDER BY rva,input_key LIMIT 1";barrier.Parameters.AddWithValue("$p",projectId);
        if(barrier.ExecuteScalar() is string unresolvedJob)throw new ArgumentException("frontier_job_active_or_unknown_reconciliation_required:"+unresolvedJob);
        var complete=new HashSet<uint>();int completeExact=0,completeEquivalent=0,completeAbi=0;using var q=db.CreateCommand();q.Transaction=tx;q.CommandText="SELECT rva,status,job FROM replayable_frontier WHERE project=$p AND input_key=$k";q.Parameters.AddWithValue("$p",projectId);q.Parameters.AddWithValue("$k",key);
        using(var r=q.ExecuteReader())while(r.Read()){if(AcceptedMatch(r.GetString(1)) && ValidPipelineMatch(p,r.GetString(2),r.GetString(1))){complete.Add((uint)r.GetInt64(0));if(r.GetString(1)=="full_match")completeExact++;else if(r.GetString(1)=="encoding_equivalent")completeEquivalent++;else completeAbi++;}}
        var f=target??p.Functions.FirstOrDefault(f=>!complete.Contains(f.Rva));if(f==null)return new{status="inventory_complete",new_pipeline_full_matches=completeExact,new_pipeline_encoding_equivalent_matches=completeEquivalent,new_pipeline_abi_trace_equivalent_matches=completeAbi,new_pipeline_accepted_matches=complete.Count};
        var job=Guid.NewGuid().ToString("N");var request=Json(new{operation="replayable",purpose,expected_source_sha256=expectedSourceSha256,project=p.Config,recipe,inputs,pipeline_key=key,rva=f.Rva,entry=f.Entry,compile});
        using var insert=db.CreateCommand();insert.Transaction=tx;insert.CommandText="INSERT INTO jobs(id,project,token,request,state,created) VALUES($i,$p,$t,$r,'queued',$c); INSERT INTO replayable_frontier(project,input_key,rva,status,job) VALUES($p,$k,$v,'running',$i) ON CONFLICT(project,input_key,rva) DO UPDATE SET status='running',job=$i";
        foreach(var (n,v) in new[]{("$i",job),("$p",projectId),("$t",token),("$r",request),("$c",DateTimeOffset.UtcNow.ToString("O")),("$k",target==null?key:"regression:"+key)})insert.Parameters.AddWithValue(n,v);insert.Parameters.AddWithValue("$v",(long)f.Rva);insert.ExecuteNonQuery();tx.Commit();StartWorker(job);
        return new{job_id=job,rva=f.Rva,pipeline_key=key,ascending_frontier=target==null,purpose,publication="draft_only",reused=false};
    }
    public object ReplayableStatus(string projectId,string? recipeJson=null)
    {
        var p=Open(projectId);var recipe=recipeJson==null?PipelineRecipe.Default:JsonSerializer.Deserialize<PipelineRecipe>(recipeJson,Options)!;var inputs=PipelineInputs(p,recipe);var key=HashText(Json(new{inputs,recipe,p.Config}));
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText=ReplayableSchema+" SELECT rva,status,job FROM replayable_frontier WHERE project=$p AND input_key=$k ORDER BY rva";cmd.Parameters.AddWithValue("$p",projectId);cmd.Parameters.AddWithValue("$k",key);
        var complete=new HashSet<uint>();var rows=new List<object>();int exact=0,equivalent=0,abi=0;
        using(var r=cmd.ExecuteReader())while(r.Read()){var rva=(uint)r.GetInt64(0);var status=r.GetString(1);var current=AcceptedMatch(status)&&ValidPipelineMatch(p,r.GetString(2),r.GetString(1));if(current){complete.Add(rva);if(status=="full_match")exact++;else if(status=="encoding_equivalent")equivalent++;else abi++;}rows.Add(new{rva,status,job_id=r.GetString(2),current_full_match=current&&status=="full_match",current_encoding_equivalent_match=current&&status=="encoding_equivalent",current_behaviorally_equivalent_match=current&&status=="behaviorally_equivalent",current_accepted_match=current});}
        var frontier=p.Functions.FirstOrDefault(f=>!complete.Contains(f.Rva))?.Rva;
        using var regression=db.CreateCommand();regression.CommandText="SELECT rva,status,job FROM replayable_frontier WHERE project=$p AND input_key=$k ORDER BY rva";regression.Parameters.AddWithValue("$p",projectId);regression.Parameters.AddWithValue("$k","regression:"+key);
        var regressions=new List<object>();int regressionExact=0,regressionEquivalent=0,regressionAbi=0,aheadExact=0,aheadEquivalent=0,aheadAbi=0;
        using(var r=regression.ExecuteReader())while(r.Read()){var rva=(uint)r.GetInt64(0);var status=r.GetString(1);var current=AcceptedMatch(status)&&ValidPipelineMatch(p,r.GetString(2),r.GetString(1));if(current){if(status=="full_match"){regressionExact++;if(frontier.HasValue&&rva>frontier.Value)aheadExact++;}else if(status=="encoding_equivalent"){regressionEquivalent++;if(frontier.HasValue&&rva>frontier.Value)aheadEquivalent++;}else{regressionAbi++;if(frontier.HasValue&&rva>frontier.Value)aheadAbi++;}}regressions.Add(new{rva,status,job_id=r.GetString(2),current_full_match=current&&status=="full_match",current_encoding_equivalent_match=current&&status=="encoding_equivalent",current_behaviorally_equivalent_match=current&&status=="behaviorally_equivalent",current_accepted_match=current});}
        return new{schema_version=1,pipeline_key=key,recipe,abi_effects_acceptance_enabled=false,behavioral_acceptance_enabled=recipe.UsesBehavioralEvents,observation_policy=recipe.UsesBehavioralEvents?"windows-x86-inherited-unwind-ordered-events-v1":null,source_publication=SourceExportSummary(p),inventory_identities=p.Functions.Length,new_pipeline_full_matches=exact,new_pipeline_encoding_equivalent_matches=equivalent,new_pipeline_abi_trace_equivalent_matches=0,new_pipeline_behaviorally_equivalent_matches=abi,new_pipeline_accepted_matches=complete.Count,first_unresolved_rva=frontier,regression_full_matches=regressionExact,regression_encoding_equivalent_matches=regressionEquivalent,regression_abi_trace_equivalent_matches=0,regression_behaviorally_equivalent_matches=regressionAbi,regression_accepted_matches=regressionExact+regressionEquivalent+regressionAbi,ahead_regression_full_matches=aheadExact,ahead_regression_encoding_equivalent_matches=aheadEquivalent,ahead_regression_abi_trace_equivalent_matches=0,ahead_regression_behaviorally_equivalent_matches=aheadAbi,regression_row_count=regressions.Count,regression_rows=regressions.Take(100),regression_rows_truncated=regressions.Count>100,attempted_frontiers=rows.Take(100),frontier_row_count=rows.Count,frontier_rows_truncated=rows.Count>100,provider_calls=0,publication="draft_only",proof=false};
    }
    static bool AcceptedMatch(string? status)=>status is "full_match" or "encoding_equivalent" or "behaviorally_equivalent";
    bool ValidPipelineMatch(Snapshot p,string job,string expectedStatus)
    {
        try {
            var folder=Path.Combine(Safe(p.Config,p.Config.Replayable!.OutputRoot),job);var result=Read<JsonElement>(Path.Combine(folder,"result.json"));
            // Batch classification is durable request state, never optional result metadata.
            var request=BatchChildRequest(job);var isBatch=request.TryGetProperty("group_parent",out var parent);
            var recipe=request.GetProperty("recipe").Deserialize<PipelineRecipe>(Options)!;recipe.Validate();
            var status=result.GetProperty("status").GetString();if(status!=expectedStatus||!AcceptedMatch(status)||(status=="encoding_equivalent"&&!recipe.UsesEncodingEquivalence)||(status=="behaviorally_equivalent"&&!recipe.UsesBehavioralEvents))return false;
            if(recipe.UsesEncodingEquivalence) {
                // The file cannot downgrade an equivalent result to an exact cache hit.
                using var durable=Db();using var stored=durable.CreateCommand();stored.CommandText="SELECT state,result FROM jobs WHERE id=$j";stored.Parameters.AddWithValue("$j",job);using var row=stored.ExecuteReader();
                if(!row.Read()||row.GetString(0)!="completed"||!JsonElement.DeepEquals(JsonDocument.Parse(row.GetString(1)).RootElement,result))return false;
                if(!result.TryGetProperty("retained_request_sha256",out var retainedRequest)||Hash(File.ReadAllBytes(Path.Combine(folder,"retained-check-request.json")))!=retainedRequest.GetString())return false;
                if(status is "encoding_equivalent" or "behaviorally_equivalent") {
                    var field=status=="encoding_equivalent"?"encoding_equivalence":"behavioral_equivalence";var file=status=="encoding_equivalent"?"encoding-equivalence.json":"behavioral-equivalence.json";
                    if(result.GetProperty("strict_status").GetString()!="mismatch"||result.GetProperty("match_kind").GetString()!=status||result.GetProperty("proof").ValueKind!=JsonValueKind.False)return false;
                    if(!result.TryGetProperty(field+"_sha256",out var proof)||Hash(File.ReadAllBytes(Path.Combine(folder,file)))!=proof.GetString())return false;
                    var gate=result.GetProperty("retained_check");if(gate.GetProperty("status").GetString()!=status||gate.GetProperty("strict_status").GetString()!="mismatch"||gate.GetProperty("proof").ValueKind!=JsonValueKind.False||!JsonElement.DeepEquals(gate.GetProperty(field),result.GetProperty(field)))return false;
                }
                var fresh=ReplayableAdapter(request,"verify_encoding_cache",folder).GetAwaiter().GetResult();
                if(fresh.GetProperty("status").GetString()!=status||!fresh.GetProperty("fresh_comparison").GetBoolean())return false;
            }
            if(isBatch) {
                if(!result.TryGetProperty("batch_provenance",out var provenance)||!Guid.TryParseExact(parent.GetString(),"N",out _)||request.GetProperty("job_id").GetString()!=job)return false;
                var allowed=new[]{"build/run.json","build/compiler.json","build/start.json","build/exit.json","build/build-exit.txt"};
                if(provenance.EnumerateObject().Count()!=allowed.Length)return false;
                foreach(var name in allowed)if(!provenance.TryGetProperty(name,out var digest)||Hash(File.ReadAllBytes(Path.Combine(folder,name)))!=digest.GetString())return false;
                var batch=result.GetProperty("build").GetProperty("batch");var group=batch.GetProperty("group_id").GetString()!;
                if(group!=parent.GetString()||result.GetProperty("group_job_id").GetString()!=group)return false;
                var batchFolder=Path.Combine(Safe(p.Config,p.Config.Replayable.OutputRoot),group,"batch");
                foreach(var(name,key)in new[]{("manifest.json","manifest_sha256"),("completed.json","envelope_sha256"),("dispatch-start.json","dispatch_sha256")})if(Hash(File.ReadAllBytes(Path.Combine(batchFolder,name)))!=batch.GetProperty(key).GetString())return false;
            }
            else if(result.TryGetProperty("batch_provenance",out _)||result.TryGetProperty("group_job_id",out _)||(result.TryGetProperty("build",out var ordinaryBuild)&&ordinaryBuild.TryGetProperty("batch",out _)))return false;
            return AcceptedMatch(result.GetProperty("status").GetString()) && Hash(File.ReadAllBytes(Path.Combine(folder,"candidate.cpp")))==result.GetProperty("source_sha256").GetString() && Hash(File.ReadAllBytes(Path.Combine(folder,"build/candidate.obj")))==result.GetProperty("object_sha256").GetString() && Hash(File.ReadAllBytes(Path.Combine(folder,"comparison.json")))==result.GetProperty("comparison_sha256").GetString() && (!result.TryGetProperty("retained_comparison_sha256",out var retained)||Hash(File.ReadAllBytes(Path.Combine(folder,"retained-comparison.json")))==retained.GetString()) && (!result.TryGetProperty("callee_lifts_sha256",out var dependencies)||Hash(File.ReadAllBytes(Path.Combine(folder,"callee-lifts.json")))==dependencies.GetString()) && (!result.TryGetProperty("eh_evidence_sha256",out var eh)||Hash(File.ReadAllBytes(Path.Combine(folder,"eh-evidence.json")))==eh.GetString());
        } catch(Exception e) when(e is IOException or JsonException or KeyNotFoundException or InvalidOperationException or FormatException or ArgumentException) {return false;}
    }
    public object ReplayableInspect(string id,int limit)
    {
        Limit(limit,12000);if(!Guid.TryParseExact(id,"N",out _))throw new ArgumentException("invalid_job_id");
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="SELECT request,state,result FROM jobs WHERE id=$i";cmd.Parameters.AddWithValue("$i",id);using var reader=cmd.ExecuteReader();if(!reader.Read())throw new ArgumentException("unknown_job");
        var request=JsonDocument.Parse(reader.GetString(0)).RootElement;if(!request.TryGetProperty("operation",out var op)||op.GetString()!="replayable")throw new ArgumentException("not_replayable_job");
        var p=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var folder=Path.Combine(Safe(p,p.Replayable!.OutputRoot),id);var path=Path.Combine(folder,"candidate.cpp");var source=File.Exists(path)?File.ReadAllText(path):null;
        var irPath=Path.Combine(folder,"recovered-ir.json");var ir=File.Exists(irPath)?File.ReadAllText(irPath):null;
        string? Artifact(string name){var artifact=Path.Combine(folder,name);if(!File.Exists(artifact))return null;var text=File.ReadAllText(artifact);return text[..Math.Min(limit,text.Length)];}
        return new{owned_range_ir=Artifact("owned-range-ir.json"),range_eh_inspection=Artifact("range-eh-inspection.json"),range_callee_inspection=Artifact("range-callee-inspection.json"),range_frame_ir=Artifact("range-frame-ir.json"),range_eh_comparison=Artifact("range-eh-comparison.json"),diagnostic_artifacts_may_be_truncated=true,job_id=id,rva=request.GetProperty("rva").GetUInt32(),state=reader.GetString(1),source=source?[..Math.Min(limit,source.Length)],source_sha256=source==null?null:HashText(source),source_truncated=source?.Length>limit,recovered_ir=ir==null?null:ir[..Math.Min(limit,ir.Length)],ir_truncated=ir?.Length>limit,publication="draft_only",proof=false};
    }
    async Task<JsonElement> ReplayableAdapter(JsonElement request,string action,string folder,string? source=null,object? members=null)
    {
        var pi=new ProcessStartInfo(registry.Python){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=registry.AdapterRoot};
        pi.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory,"replayable_adapter.py"));pi.ArgumentList.Add("--adapter-root");pi.ArgumentList.Add(registry.AdapterRoot);
        using var process=Process.Start(pi)??throw new IOException("pipeline_adapter_start");await process.StandardInput.WriteAsync(Json(new{request,action,folder,source,members}));process.StandardInput.Close();var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
        using var timeout=new CancellationTokenSource(TimeSpan.FromMinutes(6));try{await process.WaitForExitAsync(timeout.Token);}catch(OperationCanceledException){process.Kill(true);throw new IOException("external_pipeline_timeout_unknown");}
        var text=await output;await errors;if(process.ExitCode!=0||text.Length>2_000_000)throw new IOException("pipeline_adapter_failure");return JsonDocument.Parse(text).RootElement.Clone();
    }
    async Task<JsonElement> ReplayableRetainedCheck(JsonElement request,string folder,JsonElement built)
    {
        var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;
        var buildFolder=Path.Combine(folder,"build");var inputs=request.GetProperty("inputs").Deserialize<Dictionary<string,string>>(Options)!;
        foreach(var name in new[]{"candidate.cpp","candidate.obj","run.json","compiler.json"}){var path=Path.Combine(buildFolder,name);inputs[path]=Hash(File.ReadAllBytes(path));}
        var retained=new{project,build=new{config=new{folder=buildFolder,rva=request.GetProperty("rva").GetUInt32(),profile="ordinary",allow_encoding_equivalence=request.GetProperty("recipe").Deserialize<PipelineRecipe>(Options)!.UsesEncodingEquivalence,allow_abi_effects_equivalence=request.GetProperty("recipe").Deserialize<PipelineRecipe>(Options)!.UsesAbiEffects,allow_behavioral_equivalence=request.GetProperty("recipe").Deserialize<PipelineRecipe>(Options)!.UsesBehavioralEvents},expected_source_sha256=built.GetProperty("source_sha256").GetString()},inputs};
        File.WriteAllText(Path.Combine(folder,"retained-check-request.json"),Json(retained));
        var report=Path.Combine(folder,"retained-comparison.json");
        var pi=new ProcessStartInfo(registry.Python){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=registry.AdapterRoot};
        foreach(var arg in new[]{Path.Combine(AppContext.BaseDirectory,"adapter.py"),"--adapter-root",registry.AdapterRoot,"--report-path",report})pi.ArgumentList.Add(arg);
        using var process=Process.Start(pi)??throw new IOException("retained_adapter_start");await process.StandardInput.WriteAsync(Json(retained));process.StandardInput.Close();var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
        using var timeout=new CancellationTokenSource(TimeSpan.FromMinutes(3));try{await process.WaitForExitAsync(timeout.Token);}catch(OperationCanceledException){process.Kill(true);throw new IOException("retained_adapter_timeout_unknown");}
        var text=await output;await errors;if(process.ExitCode!=0||text.Length>64000)throw new IOException("retained_adapter_failure");
        var checkedResult=JsonDocument.Parse(text).RootElement;
        // Preserve the first full-range comparison and the existing adapter's independent
        // ordinary/EH gate report. Neither a generated source nor an unrun gate earns credit.
        var result=built.Deserialize<Dictionary<string,JsonElement>>(Options)!;
        var firstStatus=built.GetProperty("status").GetString();var secondStatus=checkedResult.GetProperty("status").GetString();
        var merged=AcceptedMatch(firstStatus)?(firstStatus==secondStatus?firstStatus:AcceptedMatch(secondStatus)?"inconclusive":secondStatus):firstStatus;
        if(merged is "encoding_equivalent" or "behaviorally_equivalent") {
            var field=merged=="encoding_equivalent"?"encoding_equivalence":"behavioral_equivalence";
            if(!built.TryGetProperty(field,out var firstProof)||!checkedResult.TryGetProperty(field,out var secondProof)||!JsonElement.DeepEquals(firstProof,secondProof)||built.GetProperty("strict_status").GetString()!="mismatch"||checkedResult.GetProperty("strict_status").GetString()!="mismatch"||built.GetProperty("proof").ValueKind!=JsonValueKind.False||checkedResult.GetProperty("proof").ValueKind!=JsonValueKind.False)merged="inconclusive";
        }

        result["status"]=JsonSerializer.SerializeToElement(merged);result["retained_check"]=checkedResult.Clone();
        result["retained_request_sha256"]=JsonSerializer.SerializeToElement(Hash(File.ReadAllBytes(Path.Combine(folder,"retained-check-request.json"))));
        result["retained_comparison_sha256"]=JsonSerializer.SerializeToElement(Hash(File.ReadAllBytes(report)));
        return JsonSerializer.SerializeToElement(result,Options);
    }
    async Task<string> GenerateReplayableSource(JsonElement request,string folder)
    {
        foreach(var pair in request.GetProperty("inputs").EnumerateObject())if(Hash(File.ReadAllBytes(pair.Name))!=pair.Value.GetString())throw new ArgumentException("submitted_pipeline_input_changed");
        var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;
            var lifted=await ReplayableAdapter(request,"lift",folder);if(lifted.TryGetProperty("error",out var error))throw new ArgumentException(error.GetString());
            File.WriteAllText(Path.Combine(folder,"lift.json"),lifted.GetRawText());
            if(lifted.GetProperty("lift").TryGetProperty("schema",out var rangeSchema)&&rangeSchema.GetString()=="sharpretro_owned_ranges_v1") {
                var owned=OwnedRangeRecovery.Inspect(lifted.GetProperty("lift"));File.WriteAllText(Path.Combine(folder,"owned-range-ir.json"),Json(owned));
                var rooted=await ReplayableAdapter(request,"inspect_range_eh",folder);File.WriteAllText(Path.Combine(folder,"range-eh-inspection.json"),rooted.GetRawText());
                if(rooted.TryGetProperty("error",out var rangeError))throw new ArgumentException("owned_ranges_EH_inspection: "+rangeError.GetString());
                var dependencies=await ReplayableAdapter(request,"inspect_range_callees",folder);File.WriteAllText(Path.Combine(folder,"range-callee-inspection.json"),dependencies.GetRawText());
                if(dependencies.TryGetProperty("error",out var depError))throw new ArgumentException("owned_range_callee_inspection: "+depError.GetString());
                if(dependencies.GetProperty("caller_slice_sha256").GetString()!=lifted.GetProperty("binary_slice_sha256").GetString())throw new ArgumentException("callee_caller_binding_changed");
                var blockers=dependencies.GetProperty("blockers").EnumerateArray().ToArray();
                if(blockers.Length>0)throw new ArgumentException("owned_range_callee_unsupported: "+string.Join("; ",blockers.Select(b=>$"0x{b.GetProperty("target").GetUInt64():x}:{b.GetProperty("blocker").GetString()}")));
                var callees=dependencies.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();
                // Architecture recovery retains unknown saved-frame values after
                // aliasable stores. This is not an EH/source/acceptance profile.
                var frame=X86FlowRecovery.Raise(lifted.GetProperty("lift"),new(Vc8EhProfile.Abi,true,true,[new SegmentedAddress(new SegmentInput(4),new Constant(0,64))],PrivateSubwordStack:true,MaximumOutgoingBytes:64,AliasableMemoryStores:true,MaximumPaths:128,IncomingWordStores:true,ExplicitOwnedRanges:true,SignedFrameDisplacements:true,DeferredUndefinedFlags:true,TrackFreshStackWords:true,NormalReturnTerminalRuntime:dependencies.TryGetProperty("runtime_terminal_evidence",out var terminalRuntime)?terminalRuntime.Deserialize<RuntimeTerminalEvidence>(Options):null,ConstantConditionEffects:true),callees);
                File.WriteAllText(Path.Combine(folder,"range-frame-ir.json"),Json(frame));
                if(rooted.GetProperty("typed_lift_errors").GetInt32()!=0||rooted.GetProperty("typed_opaque_instructions").GetInt32()!=0)throw new ArgumentException("owned_EH_required_effect_unsupported");
                var candidate=Vc8EbpTryProfile.Emit(lifted.GetProperty("lift"),frame,rooted,dependencies,request.GetProperty("rva").GetUInt32(),lifted.GetProperty("image_base").GetUInt32(),lifted.GetProperty("image_end").GetUInt32(),project.Module,sharedTail:true);
                File.WriteAllText(Path.Combine(folder,"recovered-ir.json"),Json(candidate));File.WriteAllText(Path.Combine(folder,"candidate.cpp"),candidate.Source);
                if(request.TryGetProperty("expected_source_sha256",out var expected)&&expected.ValueKind!=JsonValueKind.Null&&expected.GetString()!=HashText(candidate.Source))throw new ArgumentException("generated_source_hash_mismatch_no_compile");
                return candidate.Source;
            }
            var recipe=request.GetProperty("recipe").Deserialize<PipelineRecipe>(Options)!;recipe.Validate();
            var rva=request.GetProperty("rva").GetUInt32();var imageBase=lifted.GetProperty("image_base").GetUInt32();var imageEnd=lifted.GetProperty("image_end").GetUInt32();object ir;string source;
            try {var basic=X86Recovery.Raise(lifted.GetProperty("lift"),Vc8Profile.Abi);source=Vc8Profile.Emit(basic,rva,imageBase,imageEnd,project.Module);ir=basic;}
            catch(ArgumentException) when(recipe.UsesStackArguments) {
                var dependencies=await ReplayableAdapter(request,"lift_callees",folder);if(dependencies.TryGetProperty("error",out var dependencyError))throw new ArgumentException(dependencyError.GetString());
                File.WriteAllText(Path.Combine(folder,"callee-lifts.json"),dependencies.GetRawText());
                if(dependencies.GetProperty("caller_slice_sha256").GetString()!=lifted.GetProperty("binary_slice_sha256").GetString())throw new ArgumentException("callee_caller_binding_changed");
                var callees=dependencies.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();
                try {var stackIr=Vc8StackArgsProfile.Raise(lifted.GetProperty("lift"),callees);source=Vc8StackArgsProfile.Emit(stackIr,rva,imageBase,imageEnd,project.Module);ir=stackIr;}
                catch(ArgumentException) when(recipe.UsesConditionalCalls) {
                    try {var conditional=recipe.UsesCallAdapters?Vc8CallAdaptersProfile.Raise(lifted.GetProperty("lift"),callees):Vc8ConditionalCallsProfile.Raise(lifted.GetProperty("lift"),callees);source=Vc8ConditionalCallsProfile.Emit(conditional,rva,imageBase,imageEnd,project.Module);ir=conditional;}
                    catch(ArgumentException) when((recipe.UsesEh&&Vc8EhProfile.MayHaveFrame(lifted.GetProperty("lift")))||recipe.UsesByValueCalls) {
                        if(recipe.UsesEh&&Vc8EhProfile.MayHaveFrame(lifted.GetProperty("lift"))) {
                        var evidence=await ReplayableAdapter(request,"lift_eh",folder);if(evidence.TryGetProperty("error",out var ehError))throw new ArgumentException(ehError.GetString());File.WriteAllText(Path.Combine(folder,"eh-evidence.json"),evidence.GetRawText());
                        if(evidence.GetProperty("caller_slice_sha256").GetString()!=lifted.GetProperty("binary_slice_sha256").GetString())throw new ArgumentException("EH_caller_binding_changed");
                        var recovered=Vc8EhProfile.Raise(lifted.GetProperty("lift"),callees,evidence);ir=recovered;File.WriteAllText(Path.Combine(folder,"recovered-ir.json"),Json(ir));source=Vc8EhProfile.Emit(recovered,rva,imageBase,imageEnd,project.Module);
                        } else {
                            try {var recovered=Vc8ByValueCallsProfile.Raise(lifted.GetProperty("lift"),callees);ir=recovered;source=Vc8ByValueCallsProfile.Emit(recovered,rva,imageBase,imageEnd,project.Module);}
                            catch(ArgumentException) when(recipe.UsesCountedLoops) {
                                try {var recovered=Vc8LoopsProfile.Raise(lifted.GetProperty("lift"));ir=recovered;source=Vc8LoopsProfile.Emit(recovered,rva,imageBase,project.Module);}
                                catch(ArgumentException) when(recipe.UsesOrderedMemory) {
                                    StructuredMemoryFunction recovered;
                                    try {recovered=Vc8StructuredMemoryProfile.Raise(lifted.GetProperty("lift"),callees);}
                                    catch(ArgumentException) when(recipe.UsesTerminalMemory) {recovered=Vc8StructuredMemoryProfile.Raise(lifted.GetProperty("lift"),callees,dependencies.GetProperty("runtime_terminal_evidence").Deserialize<RuntimeTerminalEvidence>(Options));}
                                    ir=recovered;source=Vc8StructuredMemoryProfile.Emit(recovered,rva,imageBase,imageEnd,project.Module,lifted.GetProperty("lift"),recipe.UsesTypedReceiver,recipe.UsesScalarSource,recipe.UsesIncomingSlotValues);
                                }
                            }
                        }
                    }
                }
            }
            File.WriteAllText(Path.Combine(folder,"recovered-ir.json"),Json(ir));File.WriteAllText(Path.Combine(folder,"candidate.cpp"),source);
            if(request.TryGetProperty("expected_source_sha256",out var expectedSource)&&expectedSource.ValueKind!=JsonValueKind.Null&&expectedSource.GetString()!=HashText(source))throw new ArgumentException("generated_source_hash_mismatch_no_compile");
        return source;
    }
    async Task RunReplayable(string job,JsonElement request)
    {
        string status="inconclusive";object result;
        try
        {
            foreach(var pair in request.GetProperty("inputs").EnumerateObject())if(Hash(File.ReadAllBytes(pair.Name))!=pair.Value.GetString())throw new ArgumentException("submitted_pipeline_input_changed");
            var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var cfg=project.Replayable!;var folder=Path.Combine(Safe(project,cfg.OutputRoot),job);Directory.CreateDirectory(folder);File.WriteAllText(Path.Combine(folder,"request.json"),request.GetRawText());
            var source=await GenerateReplayableSource(request,folder);
            if(request.GetProperty("compile").GetBoolean()){var checkedResult=await ReplayableAdapter(request,"build",folder,source);if(checkedResult.TryGetProperty("source_sha256",out _)&&checkedResult.TryGetProperty("object_sha256",out _))checkedResult=await ReplayableRetainedCheck(request,folder,checkedResult);status=checkedResult.GetProperty("status").GetString()!;result=checkedResult;}
            else {status="generated";result=new{status,source,source_sha256=HashText(source),compiled=false,proof=false};}
            if(File.Exists(Path.Combine(folder,"callee-lifts.json"))) {
                var boundResult=JsonSerializer.SerializeToElement(result,Options).Deserialize<Dictionary<string,JsonElement>>(Options)!;
                boundResult["callee_lifts_sha256"]=JsonSerializer.SerializeToElement(Hash(File.ReadAllBytes(Path.Combine(folder,"callee-lifts.json"))));result=boundResult;
            }
            if(File.Exists(Path.Combine(folder,"eh-evidence.json"))) {var bound=JsonSerializer.SerializeToElement(result,Options).Deserialize<Dictionary<string,JsonElement>>(Options)!;bound["eh_evidence_sha256"]=JsonSerializer.SerializeToElement(Hash(File.ReadAllBytes(Path.Combine(folder,"eh-evidence.json"))));result=bound;}
            File.WriteAllText(Path.Combine(folder,"result.json"),Json(result));
        }
        catch(Exception e) when(e is IOException or ArgumentException or KeyNotFoundException or JsonException or InvalidOperationException){if(e is IOException && request.GetProperty("compile").GetBoolean())status="external_outcome_unknown";result=new{status,blocker=e.Message,proof=false};}
        var resultProject=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var resultFolder=Path.Combine(Safe(resultProject,resultProject.Replayable!.OutputRoot),job);Directory.CreateDirectory(resultFolder);File.WriteAllText(Path.Combine(resultFolder,"result.json"),Json(result));
        using(var db=Db()){using var cmd=db.CreateCommand();cmd.CommandText="UPDATE replayable_frontier SET status=$s WHERE project=$p AND input_key=$k AND job=$j";cmd.Parameters.AddWithValue("$s",status);cmd.Parameters.AddWithValue("$p",request.GetProperty("project").GetProperty("id").GetString());cmd.Parameters.AddWithValue("$k",ReplayableTrackingKey(request));cmd.Parameters.AddWithValue("$j",job);cmd.ExecuteNonQuery();}
        Finish(job,"completed",result);
    }
}
