using System.Diagnostics;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Data.Sqlite;

namespace Decompilation;

public sealed record Registry(string StateRoot, string Python, string AdapterRoot, ProjectConfig[] Projects);
public sealed record BuildConfig(string Name, string Folder, uint Rva, string Profile = "ordinary");
public sealed record ProjectConfig(string Id, string Module, string ModuleSha256, string Inventory, string[] AllowedRoots,
    string? PublishedIndex = null, string? Original = null, string? Compiler = null, string? CompilerSha256 = null,
    string[]? CompilerFlags = null, BuildConfig[]? Builds = null, string? RetainedDatabase = null,
    string? EhPolicy = null, Dictionary<string,string>? Libraries = null, ReplayableConfig? Replayable = null);
public sealed record BuildRef(string Id, BuildConfig Config, string? ExpectedSourceSha256 = null);
public sealed record Identity(string Id, uint Rva, JsonElement Entry);
public sealed record CheckRequest(ProjectConfig Project, BuildRef Build, Dictionary<string,string> Inputs, string Revision);

public sealed partial class Engine
{
    public static readonly JsonSerializerOptions Options = new() { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower, PropertyNameCaseInsensitive = true };
    public static string Json(object? value) => JsonSerializer.Serialize(value, Options);
    public static string Hash(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    public static string HashText(string text) => Hash(Encoding.UTF8.GetBytes(text));
    public static T Read<T>(string path) => JsonSerializer.Deserialize<T>(File.ReadAllText(path), Options) ?? throw new ArgumentException("Invalid JSON");
    readonly Registry registry;
    readonly string configPath;
    readonly string state;
    readonly Dictionary<string, Snapshot> snapshots = new();
    readonly object gate = new();
    public Engine(string config)
    {
        configPath = Path.GetFullPath(config);
        registry = Read<Registry>(configPath);
        if (registry.Projects.Select(p => p.Id).Distinct().Count() != registry.Projects.Length) throw new ArgumentException("Duplicate project id");
        state = Path.GetFullPath(registry.StateRoot);
        NoSymlinks(state);
        Directory.CreateDirectory(state);
        if (registry.Projects.Any(p => p.AllowedRoots.Any(r => Path.GetFullPath(r) == Path.GetPathRoot(r)))) throw new ArgumentException("Filesystem root cannot be an allowed root");
        using var db = Db();
        using var cmd = db.CreateCommand();
        cmd.CommandText = "PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, project TEXT NOT NULL, token TEXT NOT NULL, request TEXT NOT NULL, state TEXT NOT NULL, created TEXT NOT NULL, started TEXT, finished TEXT, result TEXT, UNIQUE(project,token));";
        cmd.ExecuteNonQuery();
    }
    SqliteConnection Db()
    {
        var db = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = Path.Combine(state,"jobs.sqlite3"), DefaultTimeout = 30 }.ToString());
        db.Open(); return db;
    }
    public static void NoSymlinks(string path)
    {
        var full = Path.GetFullPath(path);
        for (var p = full; !string.IsNullOrEmpty(p); p = Path.GetDirectoryName(p))
        {
            var info = Directory.Exists(p) ? (FileSystemInfo)new DirectoryInfo(p) : new FileInfo(p);
            if (info.LinkTarget != null || (info.Exists && info.Attributes.HasFlag(FileAttributes.ReparsePoint))) throw new ArgumentException("Symlink paths are unsupported");
        }
    }
    public static string Safe(ProjectConfig p, string path)
    {
        if (!Path.IsPathFullyQualified(path)) throw new ArgumentException("Registered paths must be absolute");
        var full = Path.GetFullPath(path); NoSymlinks(full);
        if (!p.AllowedRoots.Any(root => full.StartsWith(Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.Ordinal))) throw new ArgumentException("Path outside registered roots");
        return full;
    }
    Snapshot Open(string id)
    {
        lock(gate)
        {
            if (snapshots.TryGetValue(id, out var snapshot)) return snapshot;
            var config = registry.Projects.SingleOrDefault(p => p.Id == id) ?? throw new ArgumentException("Unknown registered project");
            snapshot = new Snapshot(config); snapshots.Add(id,snapshot); return snapshot;
        }
    }
    public object ProjectList() => new { schema_version = 1, projects = registry.Projects.Select(p => new { project_id = p.Id, module = p.Module }), paid_provider_calls = 0 };
    object JobCounts(string id)
    {
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="SELECT state,count(*) FROM jobs WHERE project=$p GROUP BY state";cmd.Parameters.AddWithValue("$p",id);
        using var reader=cmd.ExecuteReader();var counts=new Dictionary<string,long>();while(reader.Read())counts[reader.GetString(0)]=reader.GetInt64(1);return counts;
    }
    public object ProjectOpen(string id)
    {
        var p = Open(id);
        return new { schema_version=1, project_id=id, revision=p.Revision, module=p.Config.Module, module_sha256=p.Config.ModuleSha256,
            inventory_identities=p.Functions.Length, published_identities=p.Published.Count, retained_builds=p.Builds.Count, jobs=JobCounts(id),
            capabilities=new[]{"inventory_query","published_source_inspect","structural_similarity_v1","retained_object_check","durable_local_jobs"},
            comparison="unchecked; publication index is historical evidence", compilation=p.Config.Replayable==null?"unsupported":"bounded_replayable_profile", publication="read_only", proof=false };
    }
    static void Limit(int limit, int max) { if (limit < 1 || limit > max) throw new ArgumentException($"Limit must be 1..{max}"); }
    object Row(Snapshot p, Identity f) => new { function_id=f.Id, rva=$"0x{f.Rva:x8}", name=f.Entry.GetProperty("name").GetString(), body_bytes=f.Entry.GetProperty("body_bytes").GetInt32(), publication=p.Published.ContainsKey(f.Rva)?"published_historical":"unpublished", comparison="unchecked", retained_build_count=p.Builds.Values.Count(b=>b.Config.Rva==f.Rva) };
    public object Query(string id,string? cursor,int limit,string publication,string? name)
    {
        Limit(limit,100); if (publication is not ("all" or "published" or "unpublished")) throw new ArgumentException("Invalid publication filter");
        if(name?.Length>128) throw new ArgumentException("Name filter too long");
        var p=Open(id); var filter=HashText(Json(new { p.Revision, publication, name })); uint? after=null;
        if(cursor!=null)
        {
            if(cursor.Length>300) throw new ArgumentException("Invalid cursor");
            try { var c=JsonDocument.Parse(Convert.FromBase64String(cursor)).RootElement; if(c.GetProperty("filter").GetString()!=filter) throw new ArgumentException("Cursor snapshot/filter mismatch"); after=c.GetProperty("after").GetUInt32(); }
            catch(Exception e) when(e is FormatException or JsonException or KeyNotFoundException) { throw new ArgumentException("Invalid cursor"); }
        }
        var matches=p.Functions.Where(f=>(after==null||f.Rva>after) && (name==null||(f.Entry.GetProperty("name").GetString()??"").Contains(name,StringComparison.OrdinalIgnoreCase)) && (publication=="all"||p.Published.ContainsKey(f.Rva)==(publication=="published"))).Take(limit+1).ToArray();
        var items=matches.Take(limit).ToArray();
        return new { schema_version=1, revision=p.Revision, total_inventory=p.Functions.Length, items=items.Select(f=>Row(p,f)), next_cursor=matches.Length>limit?Convert.ToBase64String(Encoding.UTF8.GetBytes(Json(new {filter,after=items.Last().Rva}))):null };
    }
    static Identity Find(Snapshot p,string id) => p.FunctionsById.GetValueOrDefault(id) ?? throw new ArgumentException("Unknown function identity");
    public object Inspect(string id,string functionId,int sourceLimit)
    {
        if(sourceLimit<0||sourceLimit>12000) throw new ArgumentException("Source limit must be 0..12000");
        var p=Open(id); var f=Find(p,functionId); string? source=null; bool truncated=false; string? sourceHash=null; string? sourceError=null;
        if(p.Published.TryGetValue(f.Rva,out var pub))
        {
            sourceHash=pub.GetProperty("source_sha256").GetString();
            try
            {
                var path=Safe(p.Config,Path.Combine(Path.GetDirectoryName(p.Config.PublishedIndex!)!,pub.GetProperty("source").GetString()!));
                var raw=File.ReadAllBytes(path); if(Hash(raw)!=sourceHash) throw new ArgumentException("Published source hash changed");
                var text=Encoding.UTF8.GetString(raw); truncated=text.Length>sourceLimit; source=text[..Math.Min(sourceLimit,text.Length)];
            }
            catch(Exception e) when(e is IOException or ArgumentException or UnauthorizedAccessException) { sourceError="published_source_unavailable_or_changed"; }
        }
        object? retainedSource=null;
        var retained=p.Builds.Values.FirstOrDefault(b=>b.Config.Rva==f.Rva);
        if(retained!=null)
        {
            try
            {
                var sourcePath=Safe(p.Config,Path.Combine(retained.Config.Folder,"candidate.cpp"));
                var raw=File.ReadAllBytes(sourcePath);var receipt=Read<JsonElement>(Safe(p.Config,Path.Combine(retained.Config.Folder,"run.json")));var hash=Hash(raw);
                if(hash!=receipt.GetProperty("source_sha256").GetString()||(retained.ExpectedSourceSha256!=null&&hash!=retained.ExpectedSourceSha256))throw new ArgumentException("Retained source changed");
                var text=Encoding.UTF8.GetString(raw);retainedSource=new {build_id=retained.Id,source_sha256=hash,source=text[..Math.Min(sourceLimit,text.Length)],source_truncated=text.Length>sourceLimit,comparison="unchecked"};
            }
            catch(Exception e) when(e is IOException or ArgumentException or UnauthorizedAccessException or JsonException or KeyNotFoundException) {retainedSource=new {build_id=retained.Id,source_error="retained_source_unavailable_or_changed"};}
        }
        var ranges=f.Entry.GetProperty("body_ranges").EnumerateArray().ToArray();
        return new { schema_version=1, revision=p.Revision, identity=Row(p,f), module_sha256=p.Config.ModuleSha256, boundary_provenance="inventory_hypothesis", ranges=ranges.Take(32), ranges_truncated=ranges.Length>32,
            signature_hypothesis=f.Entry.GetProperty("signature_hypothesis"), calling_convention_hypothesis=f.Entry.GetProperty("calling_convention_hypothesis"),
            incoming_callsite_rvas=f.Entry.TryGetProperty("incoming_callsite_rvas",out var calls)?calls.EnumerateArray().Take(32).ToArray():[],
            source, source_sha256=sourceHash, source_truncated=truncated, source_error=sourceError, retained_source=retainedSource,
            builds=p.Builds.Values.Where(b=>b.Config.Rva==f.Rva).Take(50).Select(b=>new {build_id=b.Id, profile=b.Config.Profile, comparison="unchecked", provenance="registered_retained_artifact"}), proof=false };
    }
    public object Related(string id,string functionId,int limit)
    {
        Limit(limit,50);var p=Open(id);var f=Find(p,functionId);int size=f.Entry.GetProperty("body_bytes").GetInt32();int ranges=f.Entry.GetProperty("body_ranges").GetArrayLength();string signature=f.Entry.GetProperty("calling_convention_hypothesis").GetRawText();
        var rows=p.Functions.Where(x=>x.Id!=f.Id).Select(x=>new { identity=x, distance=Math.Abs((long)x.Entry.GetProperty("body_bytes").GetInt32()-size), same_range_count=x.Entry.GetProperty("body_ranges").GetArrayLength()==ranges, same_calling_convention_hypothesis=x.Entry.GetProperty("calling_convention_hypothesis").GetRawText()==signature }).OrderBy(x=>x.distance).ThenByDescending(x=>x.same_range_count).ThenByDescending(x=>x.same_calling_convention_hypothesis).ThenBy(x=>x.identity.Rva).Take(limit);
        return new { schema_version=1, index_version="size_range_signature_v1", revision=p.Revision, coverage=p.Functions.Length, acceptance_evidence=false, items=rows.Select(x=>new { identity=Row(p,x.identity), size_distance=x.distance, x.same_range_count, x.same_calling_convention_hypothesis }) };
    }
    public object SubmitCheck(string projectId,string buildId,string token)
    {
        if(token.Length<1||token.Length>128||token.Any(char.IsControl)) throw new ArgumentException("Idempotency key must be 1..128 non-control characters");
        var p=Open(projectId); if(!p.Builds.TryGetValue(buildId,out var build)) throw new ArgumentException("Unknown retained build");
        using var db=Db(); using var tx=db.BeginTransaction();
        using var find=db.CreateCommand();find.Transaction=tx;find.CommandText="SELECT id,request FROM jobs WHERE project=$p AND token=$t";find.Parameters.AddWithValue("$p",projectId);find.Parameters.AddWithValue("$t",token);
        string job;
        using(var reader=find.ExecuteReader())
        {
            if(reader.Read()) { job=reader.GetString(0);var old=JsonSerializer.Deserialize<CheckRequest>(reader.GetString(1),Options)!; if(old.Build.Id!=buildId||old.Revision!=p.Revision) throw new ArgumentException("Idempotency key already bound to a different request"); tx.Commit();return new{job_id=job,reused=true,fresh_comparison=false}; }
        }
        var inputs=new Dictionary<string,string>();
        var inventoryPath=Safe(p.Config,p.Config.Inventory);
        foreach(var path in p.InputPaths(build).Distinct())
        {
            var safe=Safe(p.Config,path);
            if(File.Exists(safe))
            {
                var bytes=File.ReadAllBytes(safe);var hash=Hash(bytes);
                if(safe==inventoryPath && hash!=p.InventorySha256) throw new ArgumentException("Inventory changed since project open; restart server to refresh snapshot");
                inputs[safe]=hash;
                var blobs=Path.Combine(state,"artifacts");Directory.CreateDirectory(blobs);var blob=Path.Combine(blobs,hash);
                try { using var immutable=new FileStream(blob,FileMode.CreateNew,FileAccess.Write,FileShare.Read);immutable.Write(bytes); }
                catch(IOException) when(File.Exists(blob)) { if(Hash(File.ReadAllBytes(blob))!=hash)throw new IOException("Immutable input artifact changed"); }
            }
            else
            {
                if(safe==inventoryPath) throw new ArgumentException("Inventory missing since project open; restart server to refresh snapshot");
                inputs[safe]="missing";
            }
        }
        // Bind adapter/comparator implementations too; an update cannot silently reuse old work.
        foreach(var file in Directory.EnumerateFiles(Path.Combine(registry.AdapterRoot,"rapid_object"),"*.py").Append(Path.Combine(AppContext.BaseDirectory,"adapter.py")).Append(Assembly.GetExecutingAssembly().Location)) inputs[file]=Hash(File.ReadAllBytes(file));
        job=Guid.NewGuid().ToString("N"); var request=new CheckRequest(p.Config,build,inputs,p.Revision);
        using var insert=db.CreateCommand();insert.Transaction=tx;insert.CommandText="INSERT INTO jobs(id,project,token,request,state,created) VALUES($i,$p,$t,$r,'queued',$c)";
        insert.Parameters.AddWithValue("$i",job);insert.Parameters.AddWithValue("$p",projectId);insert.Parameters.AddWithValue("$t",token);insert.Parameters.AddWithValue("$r",Json(request));insert.Parameters.AddWithValue("$c",DateTimeOffset.UtcNow.ToString("O"));insert.ExecuteNonQuery();tx.Commit();
        StartWorker(job);return new{job_id=job,reused=false,fresh_comparison=false};
    }
    void StartWorker(string job)
    {
        var pi=new ProcessStartInfo(Environment.ProcessPath!) {UseShellExecute=false};
        if (Path.GetFileNameWithoutExtension(Environment.ProcessPath)=="dotnet") pi.ArgumentList.Add(Assembly.GetExecutingAssembly().Location); pi.ArgumentList.Add("worker");pi.ArgumentList.Add("--config");pi.ArgumentList.Add(configPath);pi.ArgumentList.Add("--job");pi.ArgumentList.Add(job);
        // Worker must not inherit the MCP stdout pipe.
        pi.RedirectStandardOutput=true;pi.RedirectStandardError=true;
        var child=Process.Start(pi) ?? throw new IOException("Worker start failed");child.OutputDataReceived+=(_,_)=>{};child.ErrorDataReceived+=(_,_)=>{};child.BeginOutputReadLine();child.BeginErrorReadLine();
    }
    public object JobGet(string id)
    {
        if(!Guid.TryParseExact(id,"N",out _)) throw new ArgumentException("Invalid job id");
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="SELECT project,state,created,started,finished,result FROM jobs WHERE id=$i";cmd.Parameters.AddWithValue("$i",id);
        using var reader=cmd.ExecuteReader();if(!reader.Read()) throw new ArgumentException("Unknown job");
        string status=reader.GetString(1);string? started=reader.IsDBNull(3)?null:reader.GetString(3);
        // A running job with no lock holder is a crashed attempt. Never replay it.
        if(status=="running")
        {
            try { using var probe=new FileStream(Path.Combine(state,id+".lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None); Finish(id,"interrupted_unknown",new{status="inconclusive",reason="worker_interrupted; external outcome unknown",proof=false});return JobGet(id); }
            catch(IOException) { }
        }
        if(status=="queued" && DateTimeOffset.UtcNow-DateTimeOffset.Parse(reader.GetString(2))>TimeSpan.FromSeconds(5)) StartWorker(id);
        return new {schema_version=1,job_id=id,project_id=reader.GetString(0),state=status,created_at=reader.GetString(2),started_at=started,finished_at=reader.IsDBNull(4)?null:reader.GetString(4),result=reader.IsDBNull(5)?(JsonElement?)null:JsonDocument.Parse(reader.GetString(5)).RootElement, historical_result=true, reading_revalidates=false};
    }
    void Finish(string id,string status,object result)
    {
        using var db=Db();using var cmd=db.CreateCommand();cmd.CommandText="UPDATE jobs SET state=$s,finished=$f,result=$r WHERE id=$i AND state='running'";cmd.Parameters.AddWithValue("$i",id);cmd.Parameters.AddWithValue("$s",status);cmd.Parameters.AddWithValue("$f",DateTimeOffset.UtcNow.ToString("O"));cmd.Parameters.AddWithValue("$r",Json(result));cmd.ExecuteNonQuery();
    }
    public async Task RunJob(string id)
    {
        if(!Guid.TryParseExact(id,"N",out _)) throw new ArgumentException("Invalid job id");
        FileStream claim;
        try { claim=new FileStream(Path.Combine(state,id+".lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None); }
        catch(IOException) { return; }
        using(claim)
        {
            string request;
            using(var db=Db())
            {
                using var update=db.CreateCommand();update.CommandText="UPDATE jobs SET state='running',started=$s WHERE id=$i AND state='queued'";update.Parameters.AddWithValue("$s",DateTimeOffset.UtcNow.ToString("O"));update.Parameters.AddWithValue("$i",id);if(update.ExecuteNonQuery()!=1)return;
                using var get=db.CreateCommand();get.CommandText="SELECT request FROM jobs WHERE id=$i";get.Parameters.AddWithValue("$i",id);request=(string)get.ExecuteScalar()!;
            }
            if(JsonDocument.Parse(request).RootElement.TryGetProperty("operation",out var operation) && operation.GetString()=="replayable") { await RunReplayable(id,JsonDocument.Parse(request).RootElement);return; }
            try
            {
                var pi=new ProcessStartInfo(registry.Python){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=registry.AdapterRoot};
                pi.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory,"adapter.py")); pi.ArgumentList.Add("--adapter-root");pi.ArgumentList.Add(registry.AdapterRoot); pi.ArgumentList.Add("--report-path"); pi.ArgumentList.Add(Path.Combine(state,id+".report.json"));
                using var process=Process.Start(pi)??throw new IOException("Adapter start failed");
                await process.StandardInput.WriteAsync(request);process.StandardInput.Close();
                var output=process.StandardOutput.ReadToEndAsync(); var errors=process.StandardError.ReadToEndAsync();
                using var timeout=new CancellationTokenSource(TimeSpan.FromMinutes(3));
                try { await process.WaitForExitAsync(timeout.Token); }
                catch(OperationCanceledException) { process.Kill(true);await process.WaitForExitAsync();throw new IOException("adapter_timeout"); }
                var text=await output;await errors;
                if(process.ExitCode!=0||text.Length>64000) throw new IOException("adapter_failed_or_output_limit");
                var result=JsonDocument.Parse(text).RootElement;Finish(id,"completed",result);
            }
            catch(Exception e) when(e is IOException or JsonException or UnauthorizedAccessException or System.ComponentModel.Win32Exception) { Finish(id,"interrupted_unknown",new{status="inconclusive",reason=e is JsonException?"invalid_adapter_result":e.Message,proof=false}); }
        }
    }
}

public sealed class Snapshot
{
    public ProjectConfig Config {get;}
    public string Revision {get;}
    public string InventorySha256 {get;}
    public Identity[] Functions {get;}
    public Dictionary<string,Identity> FunctionsById {get;}
    public Dictionary<uint,JsonElement> Published {get;} = new();
    public Dictionary<string,BuildRef> Builds {get;} = new();
    public Snapshot(ProjectConfig config)
    {
        Config=config;if(config.ModuleSha256.Length!=64||config.ModuleSha256.Any(c=>!char.IsAsciiHexDigitLower(c)))throw new ArgumentException("Invalid module hash");
        var inventory=File.ReadAllBytes(Engine.Safe(config,config.Inventory)); InventorySha256=Engine.Hash(inventory); var doc=JsonDocument.Parse(inventory).RootElement;
        if(doc.GetProperty("module_sha256").GetString()!=config.ModuleSha256)throw new ArgumentException("Inventory module mismatch");
        Functions=doc.GetProperty("functions").EnumerateArray().Select(e=>new Identity(Engine.HashText(config.ModuleSha256+":"+e.GetProperty("rva").GetUInt32()),e.GetProperty("rva").GetUInt32(),e.Clone())).OrderBy(x=>x.Rva).ToArray();
        if(Functions.Select(f=>f.Rva).Distinct().Count()!=Functions.Length)throw new ArgumentException("Duplicate inventory identity");
        FunctionsById=Functions.ToDictionary(x=>x.Id);
        string publishedHash="none";
        if(config.PublishedIndex!=null)
        {
            var bytes=File.ReadAllBytes(Engine.Safe(config,config.PublishedIndex));publishedHash=Engine.Hash(bytes);var index=JsonDocument.Parse(bytes).RootElement;
            if(index.GetProperty("module_sha256").GetString()!=config.ModuleSha256)throw new ArgumentException("Publication module mismatch");
            foreach(var f in index.GetProperty("functions").EnumerateArray()) { var rva=Convert.ToUInt32(f.GetProperty("rva").GetString()![2..],16);if(!Functions.Any(x=>x.Rva==rva)||!Published.TryAdd(rva,f.Clone()))throw new ArgumentException("Unknown/duplicate published identity"); }
        }
        foreach(var build in config.Builds??[]) AddBuild(build);
        if(config.RetainedDatabase!=null)
        {
            using var db=new SqliteConnection(new SqliteConnectionStringBuilder {DataSource=Engine.Safe(config,config.RetainedDatabase),Mode=SqliteOpenMode.ReadOnly}.ToString());db.Open();using var cmd=db.CreateCommand();
            cmd.CommandText="SELECT DISTINCT c.rva,c.sha,c.profile,b.folder FROM candidates c JOIN builds b ON c.sha=b.source_sha AND c.profile=b.profile ORDER BY c.rva,c.sha,b.folder";
            using var reader=cmd.ExecuteReader();while(reader.Read())AddBuild(new BuildConfig("imported",reader.GetString(3),checked((uint)reader.GetInt64(0)),reader.GetString(2)),reader.GetString(1));
        }
        Revision=Engine.HashText(InventorySha256+publishedHash+Engine.Json(Builds.Keys.Order())+Engine.Json(config));
    }
    void AddBuild(BuildConfig build,string? sha=null)
    {
        if(!Functions.Any(f=>f.Rva==build.Rva))throw new ArgumentException("Retained build identity outside inventory");
        if(build.Profile is not ("ordinary" or "eh")) throw new ArgumentException("Unknown check profile");
        Engine.Safe(Config,build.Folder);var id=Engine.HashText(Engine.Json(new{Config.ModuleSha256,build.Folder,build.Rva,build.Profile,sha}));Builds.TryAdd(id,new BuildRef(id,build,sha));
    }
    public IEnumerable<string> InputPaths(BuildRef b)
    {
        yield return Config.Inventory;
        if(Config.Original!=null)yield return Config.Original;
        if(Config.Compiler!=null)yield return Config.Compiler;
        foreach(var file in new[]{"candidate.cpp","candidate.obj","run.json","compiler.json"}) yield return Path.Combine(b.Config.Folder,file);
        if(Config.EhPolicy!=null)yield return Config.EhPolicy;
        foreach(var file in (Config.Libraries??new()).Values)yield return file;
    }
}
