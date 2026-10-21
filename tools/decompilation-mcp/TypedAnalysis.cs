using System.Reflection;
using System.Text.Json;
namespace Decompilation;

public sealed partial class Engine
{
    const string TypedAnalysisSchema="CREATE TABLE IF NOT EXISTS replayable_typed_lifts(project TEXT,module_sha256 TEXT,rva INTEGER,record_id TEXT,record TEXT,first_origin TEXT,created TEXT,PRIMARY KEY(project,module_sha256,rva,record_id));";
    async Task SaveTypedAnalysis(JsonElement request,JsonElement lifted,string folder)
    {
        // This derived index is not an acceptance gate. An indexing failure is
        // recorded explicitly; ordinary source/comparison behavior is unchanged.
        object receipt;
        try {
            var packed=await ReplayableAdapter(request,"typed_cache_pack",folder,members:lifted);
            if(packed.TryGetProperty("error",out var error))throw new ArgumentException(error.GetString());
            var project=request.GetProperty("project");var recordId=packed.GetProperty("record_id").GetString();
            using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText=TypedAnalysisSchema+" INSERT OR IGNORE INTO replayable_typed_lifts(project,module_sha256,rva,record_id,record,first_origin,created) VALUES($p,$m,$r,$i,$v,$o,$c)";
            cmd.Parameters.AddWithValue("$p",project.GetProperty("id").GetString());cmd.Parameters.AddWithValue("$m",project.GetProperty("module_sha256").GetString());cmd.Parameters.AddWithValue("$r",request.GetProperty("rva").GetUInt32());cmd.Parameters.AddWithValue("$i",recordId);cmd.Parameters.AddWithValue("$v",packed.GetRawText());cmd.Parameters.AddWithValue("$o",folder);cmd.Parameters.AddWithValue("$c",DateTimeOffset.UtcNow.ToString("O"));cmd.ExecuteNonQuery();
            receipt=new{status="indexed",record_id=recordId,lift_status=packed.GetProperty("status").GetString(),payload_sha256=packed.GetProperty("payload_sha256").GetString(),acceptance_credit=false,proof=false};
        } catch(Exception e) when(e is IOException or ArgumentException or JsonException or KeyNotFoundException or InvalidOperationException or Microsoft.Data.Sqlite.SqliteException) {
            receipt=new{status="not_indexed",blocker=e.Message,acceptance_credit=false,proof=false};
        }
        File.WriteAllText(Path.Combine(folder,"typed-analysis-index.json"),Json(receipt));
    }
    static object ReplayLeafAnalysis(JsonElement payload,uint rva,string module)
    {
        var lift=payload.GetProperty("lift");
        if(lift.GetProperty("schema").GetString()!="sharpretro_instruction_lift_v1")throw new ArgumentException("cached_leaf_owned_ranges_unsupported");
        var count=lift.GetProperty("instructions").GetArrayLength();if(count is <1 or >2)throw new ArgumentException("cached_leaf_instruction_domain");
        var imageBase=payload.GetProperty("image_base").GetUInt32();
        if(Vc8LeafReturnProfile.TryRaise(lift,out var leaf)) {
            var source=Vc8LeafReturnProfile.Emit(leaf!,rva,imageBase,module);
            return new{status="source_proposal",ir=(object)leaf!,source,source_sha256=HashText(source),proof=false,acceptance_credit=false};
        }
        var basic=X86Recovery.Raise(lift,Vc8Profile.Abi);
        if(!basic.BareNearReturn)throw new ArgumentException("cached_leaf_profile_unsupported");
        var bare=Vc8Profile.Emit(basic,rva,imageBase,payload.GetProperty("image_end").GetUInt32(),module);
        return new{status="source_proposal",ir=(object)basic,source=bare,source_sha256=HashText(bare),proof=false,acceptance_credit=false};
    }
    public async Task<object> ReplayableAnalysisReplay(string projectId,string[] functionIds,string? recipeJson)
    {
        if(functionIds.Length is <1 or >16||functionIds.Distinct().Count()!=functionIds.Length)throw new ArgumentException("typed_analysis_identity_budget");
        var p=Open(projectId);var selected=functionIds.Select(id=>p.Functions.SingleOrDefault(f=>f.Id==id)??throw new ArgumentException("unknown_function_identity")).ToArray();
        var recipe=recipeJson==null?PipelineRecipe.StackArguments:JsonSerializer.Deserialize<PipelineRecipe>(recipeJson,Options)!;var inputs=PipelineInputs(p,recipe);
        var root=Safe(p.Config,p.Config.Replayable!.OutputRoot);var reportId=Guid.NewGuid().ToString("N");var folder=Path.Combine(root,"analysis-replay",reportId);Directory.CreateDirectory(folder);
        var reports=new List<object>();var summaries=new List<object>();
        foreach(var f in selected) {
            var request=JsonSerializer.SerializeToElement(new{project=p.Config,inputs,rva=f.Rva,entry=f.Entry,recipe,compile=false},Options);
            var records=new List<JsonElement>();
            using(var db=Db()){using var cmd=db.CreateCommand();cmd.CommandText=TypedAnalysisSchema+" SELECT record FROM replayable_typed_lifts WHERE project=$p AND module_sha256=$m AND rva=$r ORDER BY record_id LIMIT 17";cmd.Parameters.AddWithValue("$p",projectId);cmd.Parameters.AddWithValue("$m",p.Config.ModuleSha256);cmd.Parameters.AddWithValue("$r",f.Rva);using var row=cmd.ExecuteReader();while(row.Read())records.Add(JsonDocument.Parse(row.GetString(0)).RootElement.Clone());}
            var versions=new List<object>();var current=new List<JsonElement>();string status=records.Count==0?"missing":"unavailable";object? proposal=null;
            if(records.Count>16)status="version_budget_exceeded";
            else foreach(var record in records) {
                var checkedRecord=await ReplayableAdapter(request,"typed_cache_validate",folder,members:record);
                var outcome=checkedRecord.TryGetProperty("error",out var error)?"invalid":checkedRecord.GetProperty("status").GetString()!;
                versions.Add(new{record_id=record.TryGetProperty("record_id",out var id)?id.GetString():null,status=outcome,blocker=checkedRecord.TryGetProperty("error",out error)?error.GetString():null});
                if(outcome=="complete")current.Add(checkedRecord.GetProperty("payload").Clone());
            }
            if(current.Count>1)status="ambiguous_current_records";
            else if(current.Count==1) {
                try{proposal=ReplayLeafAnalysis(current[0],f.Rva,p.Config.Module);status="source_proposal";}
                catch(Exception e) when(e is ArgumentException or KeyNotFoundException or InvalidOperationException){status="unsupported";proposal=new{blocker=e.Message,proof=false};}
            }
            reports.Add(new{function_id=f.Id,rva=f.Rva,status,versions,proposal});
            summaries.Add(new{function_id=f.Id,rva=f.Rva,status,versions,source_sha256=proposal==null?null:JsonSerializer.SerializeToElement(proposal,Options).TryGetProperty("source_sha256",out var sourceHash)?sourceHash.GetString():null});
        }
        foreach(var pair in inputs)if(Hash(File.ReadAllBytes(pair.Key))!=pair.Value)throw new ArgumentException("typed_analysis_input_changed_during_replay");
        var report=new{schema="typed-analysis-leaf-replay-v1",project_id=projectId,recipe,inputs,runtime_sha256=Hash(File.ReadAllBytes(Assembly.GetExecutingAssembly().Location)),profile="bounded_leaf_source_proposal_v1",records=reports,new_lifts=0,compiler_invocations=0,acceptance_checks=0,acceptance_credit=false,proof=false};
        var path=Path.Combine(folder,"report.json");File.WriteAllText(path,Json(report));
        return new{status="source_only_analysis",report_id=reportId,report_sha256=Hash(File.ReadAllBytes(path)),records=summaries,new_lifts=0,compiler_invocations=0,acceptance_checks=0,acceptance_credit=false,proof=false};
    }
    public async Task<object> ReplayableAnalysisBatch(string projectId,string[] functionIds,bool populate,string? recipeJson,int seconds=300,long byteLimit=536870912)
    {
        var watch=System.Diagnostics.Stopwatch.StartNew();
        if(functionIds.Length is <1 or >128||functionIds.Distinct().Count()!=functionIds.Length)throw new ArgumentException("typed_analysis_identity_budget");
        if(seconds is <1 or >300||byteLimit is <1 or >536870912)throw new ArgumentException("typed_analysis_operation_budget");
        var p=Open(projectId);var selected=functionIds.Select(id=>p.Functions.SingleOrDefault(f=>f.Id==id)??throw new ArgumentException("unknown_function_identity")).ToArray();
        var recipe=recipeJson==null?PipelineRecipe.StackArguments:JsonSerializer.Deserialize<PipelineRecipe>(recipeJson,Options)!;var inputs=PipelineInputs(p,recipe);
        var contextSeconds=watch.Elapsed.TotalSeconds;
        var reportId=Guid.NewGuid().ToString("N");var folder=Path.Combine(Safe(p.Config,p.Config.Replayable!.OutputRoot),"analysis-replay",reportId);Directory.CreateDirectory(folder);
        var items=new List<object>();
        using(var db=Db()) foreach(var f in selected) {
            var records=new List<JsonElement>();
            if(!populate) {using var cmd=db.CreateCommand();cmd.CommandText=TypedAnalysisSchema+" SELECT record FROM replayable_typed_lifts WHERE project=$p AND module_sha256=$m AND rva=$r ORDER BY record_id LIMIT 17";cmd.Parameters.AddWithValue("$p",projectId);cmd.Parameters.AddWithValue("$m",p.Config.ModuleSha256);cmd.Parameters.AddWithValue("$r",f.Rva);using var dbRows=cmd.ExecuteReader();while(dbRows.Read())records.Add(JsonDocument.Parse(dbRows.GetString(0)).RootElement.Clone());}
            items.Add(new{rva=f.Rva,entry=f.Entry,records});
        }
        var request=JsonSerializer.SerializeToElement(new{project=p.Config,inputs,rva=selected[0].Rva,entry=selected[0].Entry,recipe,compile=false},Options);
        File.WriteAllText(Path.Combine(folder,"request.json"),Json(request));
        var backendStart=watch.Elapsed.TotalSeconds;
        var result=await ReplayableAdapter(request,"typed_analysis_batch",folder,members:new{items,populate,seconds,bytes=byteLimit});
        if(result.TryGetProperty("error",out var error))throw new ArgumentException(error.GetString());
        var path=Path.Combine(folder,"batch-data.json");var bytes=File.ReadAllBytes(path);
        if(Hash(bytes)!=result.GetProperty("data_sha256").GetString())throw new ArgumentException("typed_analysis_batch_changed");
        var data=JsonDocument.Parse(bytes).RootElement;var backendSeconds=watch.Elapsed.TotalSeconds-backendStart;
        var rowsOut=new List<object>();var summaries=new List<object>();double storageSeconds=0,recoverySeconds=0;long recordBytes=0;
        var rows=data.GetProperty("rows").EnumerateArray().ToArray();
        if(rows.Length!=selected.Length)throw new ArgumentException("typed_analysis_result_count");
        // Recheck before committing derived records, then again before returning.
        foreach(var pair in inputs)if(Hash(File.ReadAllBytes(pair.Key))!=pair.Value)throw new ArgumentException("typed_analysis_input_changed");
        using(var db=Db()) {using var tx=db.BeginTransaction();
            for(var i=0;i<rows.Length;i++) {
                var row=rows[i];var f=selected[i];if(row.GetProperty("rva").GetUInt32()!=f.Rva)throw new ArgumentException("typed_analysis_result_identity");
                var status=row.GetProperty("status").GetString()!;object? proposal=null;var current=new List<JsonElement>();
                if(row.TryGetProperty("versions",out var versions))foreach(var version in versions.EnumerateArray())if(version.GetProperty("status").GetString()=="complete")current.Add(version.GetProperty("payload").Clone());
                var stamp=watch.Elapsed.TotalSeconds;
                if(populate&&row.TryGetProperty("record",out var record)) {
                    var raw=record.GetRawText();recordBytes+=System.Text.Encoding.UTF8.GetByteCount(raw);
                    using var cmd=db.CreateCommand();cmd.Transaction=tx;cmd.CommandText=TypedAnalysisSchema+" INSERT OR IGNORE INTO replayable_typed_lifts VALUES($p,$m,$r,$i,$v,$o,$c)";
                    cmd.Parameters.AddWithValue("$p",projectId);cmd.Parameters.AddWithValue("$m",p.Config.ModuleSha256);cmd.Parameters.AddWithValue("$r",f.Rva);cmd.Parameters.AddWithValue("$i",record.GetProperty("record_id").GetString());cmd.Parameters.AddWithValue("$v",raw);cmd.Parameters.AddWithValue("$o",folder);cmd.Parameters.AddWithValue("$c",DateTimeOffset.UtcNow.ToString("O"));cmd.ExecuteNonQuery();
                }
                storageSeconds+=watch.Elapsed.TotalSeconds-stamp;stamp=watch.Elapsed.TotalSeconds;
                if(current.Count>1)status="ambiguous_current_records";
                else if(current.Count==1) {
                    var lift=current[0].GetProperty("lift");
                    if(lift.GetProperty("schema").GetString()!="sharpretro_instruction_lift_v1"||lift.GetProperty("instructions").GetArrayLength()>2)status="profile_not_implemented";
                    else try{proposal=ReplayLeafAnalysis(current[0],f.Rva,p.Config.Module);status="source_proposal";}
                    catch(Exception e) when(e is ArgumentException or KeyNotFoundException or InvalidOperationException){status="unsupported";proposal=new{blocker=e.Message,proof=false};}
                }
                else if(status=="validated")status="unavailable";
                recoverySeconds+=watch.Elapsed.TotalSeconds-stamp;
                rowsOut.Add(new{function_id=f.Id,rva=f.Rva,status,analysis=row,proposal});
                summaries.Add(new{function_id=f.Id,rva=f.Rva,status,source_sha256=proposal==null?null:JsonSerializer.SerializeToElement(proposal,Options).TryGetProperty("source_sha256",out var h)?h.GetString():null});
            }
            foreach(var pair in inputs)if(Hash(File.ReadAllBytes(pair.Key))!=pair.Value)throw new ArgumentException("typed_analysis_input_changed");
            tx.Commit();
        }
        var report=new{schema="typed-analysis-batch-report-v1",project_id=projectId,recipe,inputs,populate,runtime_sha256=Hash(File.ReadAllBytes(Assembly.GetExecutingAssembly().Location)),records=rowsOut,timing=new{context_seconds=contextSeconds,backend_process_and_operation_seconds=backendSeconds,backend=data.GetProperty("backend_seconds"),backend_context=data.GetProperty("context_seconds"),storage_seconds=storageSeconds,recovery_seconds=recoverySeconds,wall_seconds=watch.Elapsed.TotalSeconds},logical_index_bytes=recordBytes,fresh_attempts=data.GetProperty("fresh_attempts"),compiler_invocations=0,acceptance_checks=0,acceptance_credit=false,proof=false};
        var reportPath=Path.Combine(folder,"report.json");File.WriteAllText(reportPath,Json(report));
        return new{status="source_only_analysis",report_id=reportId,report_sha256=Hash(File.ReadAllBytes(reportPath)),records=summaries,fresh_attempts=data.GetProperty("fresh_attempts"),compiler_invocations=0,acceptance_checks=0,acceptance_credit=false,proof=false};
    }

}
