using System.Text.Json;
using Microsoft.Data.Sqlite;
namespace Decompilation;

public sealed partial class Engine
{
    const string BatchSchema="CREATE TABLE IF NOT EXISTS replayable_batches(job TEXT PRIMARY KEY,phase TEXT,decision TEXT);";
    sealed record BatchMember(string JobId,string FunctionId,uint Rva,string? ExpectedSourceSha256=null);
    public object ReplayableRegressionBatch(string projectId,string[] functionIds,string token,string? recipeJson,string? expectedSourcesJson)
    {
        if(token.Length is <1 or >128)throw new ArgumentException("invalid_idempotency_key");
        if(functionIds==null||functionIds.Length is <1 or >16||functionIds.Distinct().Count()!=functionIds.Length)throw new ArgumentException("batch_requires_1_to_16_unique_inventory_identities");
        var p=Open(projectId);var functions=functionIds.Select(id=>Find(p,id)).ToArray();
        var expected=new Dictionary<string,string>();
        if(expectedSourcesJson!=null) {
            using var parsed=JsonDocument.Parse(expectedSourcesJson);if(parsed.RootElement.ValueKind!=JsonValueKind.Object)throw new ArgumentException("invalid_expected_sources");
            foreach(var pair in parsed.RootElement.EnumerateObject()) {
                var value=pair.Value.GetString();if(!functionIds.Contains(pair.Name)||value==null||value.Length!=64||value.Any(c=>!Uri.IsHexDigit(c))||value!=value.ToLowerInvariant()||!expected.TryAdd(pair.Name,value))throw new ArgumentException("invalid_expected_sources");
            }
        }
        var recipe=recipeJson==null?PipelineRecipe.Default:JsonSerializer.Deserialize<PipelineRecipe>(recipeJson,Options)!;var inputs=PipelineInputs(p,recipe);
        if(p.Config.Replayable?.TransportConfig==null)throw new ArgumentException("batch_requires_registered_transport");
        var flags=p.Config.CompilerFlags;var supported=new[]{"/c","/O2","/Ob1","/Oy","/Gy","/Z7","/Zl","/GS","/GR-","/EHsc"};
        if(flags==null||!(flags.SequenceEqual(supported)||flags.SequenceEqual(supported.Select(x=>x=="/GS"?"/GS-":x))))throw new ArgumentException("unsupported_batch_compiler_flags");
        if(Read<JsonElement>(Safe(p.Config,p.Config.Replayable.TransportConfig)).GetProperty("protocol").GetString()!="prlctl-sync-copy-v1")throw new ArgumentException("unsupported_batch_transport_protocol");
        var key=HashText(Json(new{inputs,recipe,p.Config}));var fingerprint=HashText(Json(new{key,functionIds,expected=expected.OrderBy(x=>x.Key).ToArray()}));
        using var db=Db();using var tx=db.BeginTransaction();
        using(var schema=db.CreateCommand()){schema.Transaction=tx;schema.CommandText=ReplayableSchema+BatchSchema;schema.ExecuteNonQuery();}
        using(var old=db.CreateCommand()) {
            old.Transaction=tx;old.CommandText="SELECT id,request FROM jobs WHERE project=$p AND token=$t";old.Parameters.AddWithValue("$p",projectId);old.Parameters.AddWithValue("$t",token);using var reader=old.ExecuteReader();
            if(reader.Read()){var previous=JsonDocument.Parse(reader.GetString(1)).RootElement;if(!previous.TryGetProperty("batch_request_key",out var hash)||hash.GetString()!=fingerprint)throw new ArgumentException("idempotency_request_changed");return new{job_id=reader.GetString(0),reused=true};}
        }
        using(var barrier=db.CreateCommand()) {
            barrier.Transaction=tx;barrier.CommandText="SELECT job FROM replayable_frontier WHERE project=$p AND status IN ('running','external_outcome_unknown') ORDER BY rva,input_key LIMIT 1";barrier.Parameters.AddWithValue("$p",projectId);
            if(barrier.ExecuteScalar() is string active)throw new ArgumentException("frontier_job_active_or_unknown_reconciliation_required:"+active);
        }
        var group=Guid.NewGuid().ToString("N");var members=functions.Select(f=>new BatchMember(Guid.NewGuid().ToString("N"),f.Id,f.Rva,expected.GetValueOrDefault(f.Id))).ToArray();var created=DateTimeOffset.UtcNow.ToString("O");
        string parent=Json(new{operation="replayable_batch",group_id=group,purpose="regression",project=p.Config,recipe,inputs,pipeline_key=key,batch_request_key=fingerprint,compile=true,members});
        InsertBatchJob(db,tx,group,projectId,token,parent,"queued",created,null);
        using(var phase=db.CreateCommand()){phase.Transaction=tx;phase.CommandText="INSERT INTO replayable_batches(job,phase) VALUES($j,'claimed')";phase.Parameters.AddWithValue("$j",group);phase.ExecuteNonQuery();}
        foreach(var (member,function) in members.Zip(functions)) {
            var child=Json(new{operation="replayable",purpose="regression",group_parent=group,job_id=member.JobId,expected_source_sha256=expected.GetValueOrDefault(function.Id),project=p.Config,recipe,inputs,pipeline_key=key,rva=function.Rva,entry=function.Entry,compile=true});
            InsertBatchJob(db,tx,member.JobId,projectId,"group-member:"+member.JobId,child,"group_member",created,Json(new{status="waiting_for_group",group_job_id=group,proof=false}));
            using var claim=db.CreateCommand();claim.Transaction=tx;claim.CommandText="INSERT INTO replayable_frontier(project,input_key,rva,status,job) VALUES($p,$k,$v,'running',$j) ON CONFLICT(project,input_key,rva) DO UPDATE SET status='running',job=$j";
            claim.Parameters.AddWithValue("$p",projectId);claim.Parameters.AddWithValue("$k","regression:"+key);claim.Parameters.AddWithValue("$v",(long)member.Rva);claim.Parameters.AddWithValue("$j",member.JobId);claim.ExecuteNonQuery();
        }
        tx.Commit();StartWorker(group);return new{job_id=group,members,purpose="regression_batch",ascending_frontier=false,reused=false,publication="draft_only"};
    }
    static void InsertBatchJob(SqliteConnection db,SqliteTransaction tx,string id,string project,string token,string request,string state,string created,string? result)
    {
        using var cmd=db.CreateCommand();cmd.Transaction=tx;cmd.CommandText="INSERT INTO jobs(id,project,token,request,state,created,result) VALUES($i,$p,$t,$r,$s,$c,$v)";
        foreach(var(n,v)in new[]{("$i",id),("$p",project),("$t",token),("$r",request),("$s",state),("$c",created)})cmd.Parameters.AddWithValue(n,v);cmd.Parameters.AddWithValue("$v",(object?)result??DBNull.Value);cmd.ExecuteNonQuery();
    }
    JsonElement BatchChildRequest(string id)
    {
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="SELECT request FROM jobs WHERE id=$i";cmd.Parameters.AddWithValue("$i",id);return JsonDocument.Parse((string)cmd.ExecuteScalar()!).RootElement.Clone();
    }
    void CompleteReplayableBatchMember(string id,JsonElement request,string status,object result)
    {
        var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var folder=Path.Combine(Safe(project,project.Replayable!.OutputRoot),id);
        Directory.CreateDirectory(folder);var fields=JsonSerializer.SerializeToElement(result,Options).Deserialize<Dictionary<string,JsonElement>>(Options)!;
        foreach(var(name,key)in new[]{("callee-lifts.json","callee_lifts_sha256"),("eh-evidence.json","eh_evidence_sha256")})if(File.Exists(Path.Combine(folder,name)))fields[key]=JsonSerializer.SerializeToElement(Hash(File.ReadAllBytes(Path.Combine(folder,name))));
        File.WriteAllText(Path.Combine(folder,"result.json"),Json(fields));
        using var db=Db();using var tx=db.BeginTransaction();using var cmd=db.CreateCommand();cmd.Transaction=tx;cmd.CommandText="UPDATE replayable_frontier SET status=$s WHERE project=$p AND input_key=$k AND job=$j; UPDATE jobs SET state='completed',finished=$f,result=$r WHERE id=$j AND state='running'";
        cmd.Parameters.AddWithValue("$s",status);cmd.Parameters.AddWithValue("$p",project.Id);cmd.Parameters.AddWithValue("$k",ReplayableTrackingKey(request));cmd.Parameters.AddWithValue("$j",id);cmd.Parameters.AddWithValue("$f",DateTimeOffset.UtcNow.ToString("O"));cmd.Parameters.AddWithValue("$r",Json(fields));cmd.ExecuteNonQuery();tx.Commit();
    }
    bool InterruptReplayableBatch(string id,string reason,bool preserveParent=false)
    {
        using var db=Db();using var get=db.CreateCommand();get.CommandText="SELECT request FROM jobs WHERE id=$j";get.Parameters.AddWithValue("$j",id);var text=get.ExecuteScalar() as string;if(text==null)return false;
        var request=JsonDocument.Parse(text).RootElement;if(!request.TryGetProperty("operation",out var operation)||operation.GetString()!="replayable_batch")return false;
        var members=request.GetProperty("members").Deserialize<BatchMember[]>(Options)!;var now=DateTimeOffset.UtcNow.ToString("O");using var tx=db.BeginTransaction();
        foreach(var member in members) {
            using var child=db.CreateCommand();child.Transaction=tx;child.CommandText="UPDATE jobs SET state='interrupted_unknown',finished=$f,result=$r WHERE id=$j AND state IN ('group_member','running'); UPDATE replayable_frontier SET status='external_outcome_unknown' WHERE job=$j AND status='running'";
            child.Parameters.AddWithValue("$j",member.JobId);child.Parameters.AddWithValue("$f",now);child.Parameters.AddWithValue("$r",Json(new{status="external_outcome_unknown",group_job_id=id,blocker=reason,automatic_retry=false,proof=false}));child.ExecuteNonQuery();
        }
        using var parent=db.CreateCommand();parent.Transaction=tx;parent.CommandText="UPDATE replayable_batches SET phase='unknown' WHERE job=$j;"+(preserveParent?"":" UPDATE jobs SET state='interrupted_unknown',finished=$f,result=$r WHERE id=$j AND state='running'");parent.Parameters.AddWithValue("$j",id);
        if(!preserveParent){parent.Parameters.AddWithValue("$f",now);parent.Parameters.AddWithValue("$r",Json(new{status="external_outcome_unknown",reason,members,automatic_retry=false,proof=false}));}parent.ExecuteNonQuery();tx.Commit();return true;
    }
    void EnsureTerminalBatchMembers(string id,string stateName)
    {
        if(stateName is "queued" or "running" or "group_member")return;
        using var db=Db();using var table=db.CreateCommand();table.CommandText="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='replayable_batches'";if((long)table.ExecuteScalar()! ==0)return;
        using var phase=db.CreateCommand();phase.CommandText="SELECT phase FROM replayable_batches WHERE job=$j";phase.Parameters.AddWithValue("$j",id);var value=phase.ExecuteScalar() as string;
        // An older engine may have terminalized an unknown new operation. Its
        // group claims still block execution; never reinterpret that as completion.
        if(value is "claimed" or "dispatching")InterruptReplayableBatch(id,"group_parent_terminal_without_confirmed_group_completion",true);
    }
    async Task RunReplayableBatch(string id,JsonElement request)
    {
        var project=request.GetProperty("project").Deserialize<ProjectConfig>(Options)!;var folder=Path.Combine(Safe(project,project.Replayable!.OutputRoot),id);Directory.CreateDirectory(folder);File.WriteAllText(Path.Combine(folder,"request.json"),request.GetRawText());
        var members=request.GetProperty("members").Deserialize<BatchMember[]>(Options)!;var locks=new List<FileStream>();var prepared=new List<(BatchMember Member,JsonElement Request,string Folder,string Source)>();
        try {
            if(request.GetProperty("group_id").GetString()!=id||members.Length is <1 or >16||members.Any(m=>!Guid.TryParseExact(m.JobId,"N",out _))||members.Select(m=>m.JobId).Distinct().Count()!=members.Length||members.Select(m=>m.FunctionId).Distinct().Count()!=members.Length)throw new ArgumentException("batch_membership_changed");
            var snapshot=new Snapshot(project);
            foreach(var member in members) {
                locks.Add(new FileStream(Path.Combine(state,member.JobId+".lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None));
                using(var db=Db()){using var start=db.CreateCommand();start.CommandText="UPDATE jobs SET state='running',started=$s WHERE id=$j AND state='group_member'";start.Parameters.AddWithValue("$s",DateTimeOffset.UtcNow.ToString("O"));start.Parameters.AddWithValue("$j",member.JobId);if(start.ExecuteNonQuery()!=1)throw new InvalidOperationException("batch_member_claim_changed");}
                var child=BatchChildRequest(member.JobId);
                if(!snapshot.FunctionsById.TryGetValue(member.FunctionId,out var original)||original.Rva!=member.Rva||child.GetProperty("rva").GetUInt32()!=member.Rva||child.GetProperty("job_id").GetString()!=member.JobId||child.GetProperty("group_parent").GetString()!=id||child.GetProperty("expected_source_sha256").GetString()!=member.ExpectedSourceSha256||Json(child.GetProperty("entry"))!=Json(original.Entry)||Json(child.GetProperty("project"))!=Json(request.GetProperty("project"))||Json(child.GetProperty("inputs"))!=Json(request.GetProperty("inputs"))||Json(child.GetProperty("recipe"))!=Json(request.GetProperty("recipe"))||child.GetProperty("pipeline_key").GetString()!=request.GetProperty("pipeline_key").GetString())throw new ArgumentException("batch_member_original_binding_changed");
                var childFolder=Path.Combine(Safe(project,project.Replayable.OutputRoot),member.JobId);Directory.CreateDirectory(childFolder);File.WriteAllText(Path.Combine(childFolder,"request.json"),child.GetRawText());
                try {var source=await GenerateReplayableSource(child,childFolder);prepared.Add((member,child,childFolder,source));}
                catch(Exception e) when(e is IOException or ArgumentException or KeyNotFoundException or JsonException or InvalidOperationException) {CompleteReplayableBatchMember(member.JobId,child,"inconclusive",new{status="inconclusive",blocker=e.Message,compiler_dispatched=false,proof=false});}
            }
            if(prepared.Count>0) {
                var decisionMembers=prepared.Select(x=>new{request=x.Request,folder=x.Folder,source_sha256=HashText(x.Source)}).ToArray();var decision=Json(new{group_id=id,members=decisionMembers});
                using(var db=Db()){using var persist=db.CreateCommand();persist.CommandText="UPDATE replayable_batches SET phase='dispatching',decision=$d WHERE job=$j AND phase='claimed'";persist.Parameters.AddWithValue("$d",decision);persist.Parameters.AddWithValue("$j",id);if(persist.ExecuteNonQuery()!=1)throw new InvalidOperationException("batch_dispatch_already_consumed");}
                using(var file=new FileStream(Path.Combine(folder,"dispatch-decision.json"),FileMode.CreateNew,FileAccess.Write,FileShare.None,4096,FileOptions.WriteThrough)){var bytes=System.Text.Encoding.UTF8.GetBytes(decision);file.Write(bytes);file.Flush(true);}
                var batch=await ReplayableAdapter(request,"build_batch",folder,members:decisionMembers);File.WriteAllText(Path.Combine(folder,"batch-build-result.json"),Json(batch));
                if(batch.GetProperty("status").GetString()!="batch_completed") {
                    var uncertain=batch.GetProperty("status").GetString()=="external_outcome_unknown";
                    foreach(var child in prepared)CompleteReplayableBatchMember(child.Member.JobId,child.Request,uncertain?"external_outcome_unknown":"inconclusive",new{status=uncertain?"external_outcome_unknown":"inconclusive",group_job_id=id,blocker="batch_dispatch_not_confirmed",batch,automatic_retry=false,proof=false});
                } else {
                    if(batch.GetProperty("members").GetArrayLength()!=prepared.Count||!batch.GetProperty("members").EnumerateArray().Select(x=>x.GetProperty("job_id").GetString()).SequenceEqual(prepared.Select(x=>x.Member.JobId)))throw new ArgumentException("batch_returned_member_bindings_changed");
                    foreach(var child in prepared) {
                        try {
                            var built=await ReplayableAdapter(child.Request,"check_build",child.Folder,child.Source);
                            if(built.TryGetProperty("source_sha256",out _)&&built.TryGetProperty("object_sha256",out _))built=await ReplayableRetainedCheck(child.Request,child.Folder,built);
                            var fields=built.Deserialize<Dictionary<string,JsonElement>>(Options)!;var provenance=new Dictionary<string,string>();
                            foreach(var name in new[]{"run.json","compiler.json","start.json","exit.json","build-exit.txt"})provenance["build/"+name]=Hash(File.ReadAllBytes(Path.Combine(child.Folder,"build",name)));
                            fields["batch_provenance"]=JsonSerializer.SerializeToElement(provenance,Options);fields["group_job_id"]=JsonSerializer.SerializeToElement(id);
                            CompleteReplayableBatchMember(child.Member.JobId,child.Request,built.GetProperty("status").GetString()!,fields);
                        } catch(Exception e) when(e is IOException or ArgumentException or KeyNotFoundException or JsonException or InvalidOperationException) {CompleteReplayableBatchMember(child.Member.JobId,child.Request,e is IOException?"external_outcome_unknown":"inconclusive",new{status=e is IOException?"external_outcome_unknown":"inconclusive",group_job_id=id,blocker=e.Message,proof=false});}
                    }
                }
            }
            FinishReplayableBatch(id,request,folder);
        } catch(Exception e) when(e is IOException or ArgumentException or KeyNotFoundException or JsonException or InvalidOperationException) {InterruptReplayableBatch(id,"batch_interrupted_no_automatic_retry:"+e.Message);}
        finally {foreach(var held in locks)held.Dispose();}
    }
    void FinishReplayableBatch(string id,JsonElement request,string folder)
    {
        var members=request.GetProperty("members").Deserialize<BatchMember[]>(Options)!;var rows=new List<object>();var counts=new Dictionary<string,int>();using var db=Db();
        foreach(var member in members) {using var get=db.CreateCommand();get.CommandText="SELECT state,result FROM jobs WHERE id=$j";get.Parameters.AddWithValue("$j",member.JobId);using var reader=get.ExecuteReader();if(!reader.Read()||reader.GetString(0)!="completed")throw new InvalidOperationException("batch_member_not_terminal");var result=JsonDocument.Parse(reader.GetString(1)).RootElement;var status=result.GetProperty("status").GetString()!;counts[status]=counts.GetValueOrDefault(status)+1;rows.Add(new{job_id=member.JobId,function_id=member.FunctionId,rva=member.Rva,status});}
        var uncertain=counts.ContainsKey("external_outcome_unknown");var summary=Json(new{status=uncertain?"external_outcome_unknown":"batch_completed",group_job_id=id,members=rows,outcomes=counts,ascending_frontier=false,automatic_retry=false,proof=false});File.WriteAllText(Path.Combine(folder,"result.json"),summary);
        using var tx=db.BeginTransaction();using var finish=db.CreateCommand();finish.Transaction=tx;finish.CommandText="UPDATE replayable_batches SET phase=$p WHERE job=$j; UPDATE jobs SET state='completed',finished=$f,result=$r WHERE id=$j AND state='running'";finish.Parameters.AddWithValue("$p",uncertain?"unknown":"completed");finish.Parameters.AddWithValue("$j",id);finish.Parameters.AddWithValue("$f",DateTimeOffset.UtcNow.ToString("O"));finish.Parameters.AddWithValue("$r",summary);finish.ExecuteNonQuery();tx.Commit();
    }
}
