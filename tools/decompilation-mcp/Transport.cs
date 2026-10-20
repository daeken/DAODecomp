using System.Diagnostics;
using System.Reflection;
using System.Text.Json;
namespace Decompilation;

public sealed partial class Engine
{
    void RequireSingleUnknownBarrier(Microsoft.Data.Sqlite.SqliteConnection db,Microsoft.Data.Sqlite.SqliteTransaction tx,string project,string target,string trackingKey)
    {
        using var query=db.CreateCommand();query.Transaction=tx;
        query.CommandText="SELECT input_key,status,job FROM replayable_frontier WHERE project=$p AND status IN ('running','external_outcome_unknown')";
        query.Parameters.AddWithValue("$p",project);using var reader=query.ExecuteReader();
        if(!reader.Read()||reader.GetString(0)!=trackingKey||reader.GetString(1)!="external_outcome_unknown"||reader.GetString(2)!=target||reader.Read())throw new ArgumentException("target_not_sole_completed_external_unknown");
    }
    static void VerifyTransportInputs(JsonElement inputs)
    {foreach(var item in inputs.EnumerateObject())if(Hash(File.ReadAllBytes(item.Name))!=item.Value.GetString())throw new ArgumentException("reconciliation_input_changed");}

    public object ReplayableAbandonUnknown(string projectId,string target,string token)
    {
        if(!Guid.TryParseExact(target,"N",out _)||token.Length<1||token.Length>128)throw new ArgumentException("invalid_reconciliation_identity_or_token");
        var p=Open(projectId);var cfg=p.Config.Replayable??throw new ArgumentException("replayable_not_registered");
        var profilePath=Safe(p.Config,cfg.TransportConfig??throw new ArgumentException("transport_profile_not_registered"));
        var profile=Read<JsonElement>(profilePath);if(profile.GetProperty("protocol").GetString()!="prlctl-sync-copy-v1")throw new ArgumentException("unsupported_transport_protocol");
        using var db=Db();using var tx=db.BeginTransaction();string originalRequest,originalResult;
        using(var get=db.CreateCommand())
        {
            get.Transaction=tx;get.CommandText="SELECT project,request,state,result FROM jobs WHERE id=$j";get.Parameters.AddWithValue("$j",target);using var reader=get.ExecuteReader();
            if(!reader.Read()||reader.GetString(0)!=projectId||reader.GetString(2)!="completed"||reader.IsDBNull(3))throw new ArgumentException("target_not_completed_transport_unknown");
            originalRequest=reader.GetString(1);originalResult=reader.GetString(3);
        }
        var request=JsonDocument.Parse(originalRequest).RootElement.Clone();var result=JsonDocument.Parse(originalResult).RootElement.Clone();
        if(!request.TryGetProperty("operation",out var operation)||operation.GetString()!="replayable"||!request.GetProperty("compile").GetBoolean()||result.GetProperty("status").GetString()!="external_outcome_unknown"||!result.TryGetProperty("blocker",out var blocker)||blocker.GetString()!="compiler_exit_marker_missing_no_automatic_retry")throw new ArgumentException("unsupported_unknown_attempt");
        var oldProject=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;
        if(oldProject.ModuleSha256!=p.Config.ModuleSha256||oldProject.Module!=p.Config.Module||oldProject.Original!=p.Config.Original||oldProject.Inventory!=p.Config.Inventory||oldProject.Compiler!=p.Config.Compiler||oldProject.CompilerSha256!=p.Config.CompilerSha256||Json(oldProject.CompilerFlags)!=Json(p.Config.CompilerFlags)||oldProject.Replayable!.VmBuildLock!=cfg.VmBuildLock)throw new ArgumentException("reconciliation_project_binding_changed");
        var identity=p.Functions.FirstOrDefault(f=>f.Rva==request.GetProperty("rva").GetUInt32())??throw new ArgumentException("unknown_inventory_identity");
        if(Json(identity.Entry)!=Json(request.GetProperty("entry")))throw new ArgumentException("reconciliation_inventory_entry_changed");
        var folder=Safe(p.Config,Path.Combine(oldProject.Replayable.OutputRoot,target));
        VerifyTransportInputs(request.GetProperty("inputs"));
        var inputs=request.GetProperty("inputs").Deserialize<Dictionary<string,string>>(Options)!;
        void Bind(string path){var digest=Hash(File.ReadAllBytes(path));if(inputs.TryGetValue(path,out var prior)&&prior!=digest)throw new ArgumentException("reconciliation_input_alias_changed");inputs[path]=digest;}
        if(inputs.GetValueOrDefault(p.Config.Original!)!=p.Config.ModuleSha256||inputs.GetValueOrDefault(p.Config.Inventory)!=p.InventorySha256||inputs.GetValueOrDefault(p.Config.Compiler!)!=p.Config.CompilerSha256)throw new ArgumentException("reconciliation_original_pins_changed");
        foreach(var path in new[]{profilePath,Assembly.GetExecutingAssembly().Location,Path.Combine(AppContext.BaseDirectory,"replayable_transport.py"),profile.GetProperty("executable").GetString()!,registry.Python})
        {if(!Path.IsPathFullyQualified(path))throw new ArgumentException("transport_executable_must_be_registered_absolute_path");Bind(path);}
        foreach(var name in new[]{"request.json","result.json","candidate.cpp","build/run.json","build/build.cmd","build/run.ps1","build/transport.stdout","build/transport.stderr"}){var path=Safe(p.Config,Path.Combine(folder,name));Bind(path);}
        if(HashText(File.ReadAllText(Path.Combine(folder,"request.json")))!=HashText(originalRequest)||HashText(File.ReadAllText(Path.Combine(folder,"result.json")))!=HashText(originalResult))throw new ArgumentException("unknown_history_artifact_changed");
        var requestHash=HashText(originalRequest);var resultHash=HashText(originalResult);var binding=HashText(Json(new{target,requestHash,resultHash,inputs,project=p.Config}));
        using(var old=db.CreateCommand())
        {
            old.Transaction=tx;old.CommandText="SELECT id,request FROM jobs WHERE project=$p AND token=$t";old.Parameters.AddWithValue("$p",projectId);old.Parameters.AddWithValue("$t",token);using var reader=old.ExecuteReader();
            if(reader.Read()){var historical=JsonDocument.Parse(reader.GetString(1)).RootElement;if(!historical.TryGetProperty("operation",out var op)||op.GetString()!="replayable_abandon_unknown"||historical.GetProperty("binding").GetString()!=binding)throw new ArgumentException("idempotency_request_changed");return new{job_id=reader.GetString(0),reused=true};}
        }
        var trackingKey=ReplayableTrackingKey(request);RequireSingleUnknownBarrier(db,tx,projectId,target,trackingKey);
        using(var active=db.CreateCommand())
        {
            active.Transaction=tx;active.CommandText="SELECT request FROM jobs WHERE project=$p AND state IN ('queued','running')";active.Parameters.AddWithValue("$p",projectId);using var reader=active.ExecuteReader();
            while(reader.Read()){var other=JsonDocument.Parse(reader.GetString(0)).RootElement;if(other.TryGetProperty("operation",out var op)&&op.GetString()=="replayable_abandon_unknown")throw new ArgumentException("reconciliation_already_active");}
        }
        var job=Guid.NewGuid().ToString("N");var submitted=Json(new{operation="replayable_abandon_unknown",project=p.Config,target_job=target,target_request=request,target_result=result,target_request_sha256=requestHash,target_result_sha256=resultHash,target_folder=folder,target_tracking_key=trackingKey,transport_config=profilePath,inputs,binding});
        using var insert=db.CreateCommand();insert.Transaction=tx;insert.CommandText="INSERT INTO jobs(id,project,token,request,state,created) VALUES($i,$p,$t,$r,'queued',$c)";
        foreach(var (name,value) in new[]{("$i",job),("$p",projectId),("$t",token),("$r",submitted),("$c",DateTimeOffset.UtcNow.ToString("O"))})insert.Parameters.AddWithValue(name,value);
        insert.ExecuteNonQuery();tx.Commit();StartWorker(job);return new{job_id=job,target_job_id=target,reused=false,match=false,original_compiler_outcome="unknown"};
    }

    async Task RunReplayableAbandonUnknown(string job,JsonElement request)
    {
        var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var target=request.GetProperty("target_job").GetString()!;
        var folder=Path.Combine(Safe(project,project.Replayable!.OutputRoot),job);Directory.CreateDirectory(folder);File.WriteAllText(Path.Combine(folder,"request.json"),request.GetRawText());
        try
        {
            // A completed target can still be exiting. Its exclusive claim must be gone;
            // hold it through the durable release so no target worker can run concurrently.
            using var targetClaim=new FileStream(Path.Combine(state,target+".lock"),FileMode.Open,FileAccess.ReadWrite,FileShare.None);
            VerifyTransportInputs(request.GetProperty("inputs"));
            var pi=new ProcessStartInfo(registry.Python){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=registry.AdapterRoot};
            pi.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory,"replayable_transport.py"));
            using var process=Process.Start(pi)??throw new IOException("transport_probe_start");await process.StandardInput.WriteAsync(Json(new{request,folder}));process.StandardInput.Close();var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
            using var timeout=new CancellationTokenSource(TimeSpan.FromSeconds(75));try{await process.WaitForExitAsync(timeout.Token);}catch(OperationCanceledException){process.Kill(true);throw new IOException("read_only_transport_probe_timeout");}
            var text=await output;await errors;if(process.ExitCode!=0||text.Length>64000)throw new IOException("read_only_transport_probe_failed");
            var witness=JsonDocument.Parse(text).RootElement.Clone();File.WriteAllText(Path.Combine(folder,"witness.json"),Json(witness));
            if(witness.GetProperty("status").GetString()!="quiescent_absent_synchronous_prefix")throw new ArgumentException(witness.TryGetProperty("blocker",out var reason)?reason.GetString():"transport_not_quiescent");
            VerifyTransportInputs(request.GetProperty("inputs"));
            var resolved=new{status="abandoned_nonaccepting",target_job_id=target,original_compiler_outcome="unknown",original_result_preserved=true,match=false,proof=false,automatic_retry=false,witness_sha256=Hash(File.ReadAllBytes(Path.Combine(folder,"witness.json"))),binding=request.GetProperty("binding").GetString()};
            File.WriteAllText(Path.Combine(folder,"result.json"),Json(resolved));
            using var db=Db();using var tx=db.BeginTransaction();RequireSingleUnknownBarrier(db,tx,project.Id,target,request.GetProperty("target_tracking_key").GetString()!);
            using(var old=db.CreateCommand())
            {
                old.Transaction=tx;old.CommandText="SELECT request,result,state FROM jobs WHERE id=$t";old.Parameters.AddWithValue("$t",target);using var reader=old.ExecuteReader();
                if(!reader.Read()||reader.GetString(2)!="completed"||HashText(reader.GetString(0))!=request.GetProperty("target_request_sha256").GetString()||HashText(reader.GetString(1))!=request.GetProperty("target_result_sha256").GetString())throw new ArgumentException("unknown_history_changed");
            }
            // The nonaccepting observation and barrier release commit atomically.
            // The original job/request/result are never rewritten and receive no match.
            using var update=db.CreateCommand();update.Transaction=tx;update.CommandText="UPDATE replayable_frontier SET status='abandoned_nonaccepting' WHERE project=$p AND job=$t AND status='external_outcome_unknown'; UPDATE jobs SET state='completed',finished=$f,result=$r WHERE id=$j AND state='running'";
            foreach(var (name,value) in new[]{("$p",project.Id),("$t",target),("$j",job),("$f",DateTimeOffset.UtcNow.ToString("O")),("$r",Json(resolved))})update.Parameters.AddWithValue(name,value);
            if(update.ExecuteNonQuery()!=2)throw new ArgumentException("reconciliation_state_changed");tx.Commit();
        }
        catch(Exception e) when(e is IOException or ArgumentException or KeyNotFoundException or JsonException or InvalidOperationException or UnauthorizedAccessException or System.ComponentModel.Win32Exception)
        {
            var result=new{status="inconclusive",target_job_id=target,blocker=e.Message,original_compiler_outcome="unknown",barrier_retained=true,match=false,proof=false};File.WriteAllText(Path.Combine(folder,"result.json"),Json(result));Finish(job,"completed",result);
        }
    }
}
