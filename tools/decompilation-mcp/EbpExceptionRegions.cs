using System.Text.Json;
namespace Decompilation;

// A source-region hypothesis under the named VC8 normal-completion convention.
// This is deliberately not a runtime-equivalence certificate: external calls can
// mutate the writable registration node and exception delivery remains unproved.
public sealed record EbpProtectedRegion(string Role,int State,ulong? Handler,ulong[] Origins,bool AfterCatchCompletion=false);
public sealed record EbpExceptionRoute(string Status,ulong? Handler,string Reason);
public sealed record EbpExceptionRegions(int RegistrationParentOffset,int SavedEspParentOffset,int StateParentOffset,
    int InitialState,int CatchPreparationState,int RetryState,int CleanupState,
    EbpProtectedRegion[] Regions,string RuntimeConvention,string[] Obligations,bool Proof=false)
{
    public EbpExceptionRoute Dispatch(int? state,string category,bool runtimeStateUnchanged)
    {
        if(!runtimeStateUnchanged||state==null)return new("unknown",null,"writable_state_or_callback_mutation");
        // FuncInfo EHs is not a promise that every machine fault is a C++ throw.
        if(category!="eligible_cpp")return new("unknown",null,"exception_category_or_runtime_dispatch_unproved");
        if(state==InitialState)return new("local_handler",Regions.Single(r=>r.Role=="initial_suffix").Handler,"try_interval");
        if(state==RetryState)return new("local_handler",Regions.Single(r=>r.Role=="resumed_suffix").Handler,"try_interval");
        if(state is -1||state==CatchPreparationState||state==CleanupState)return new("propagate",null,"outside_local_try_intervals");
        return new("unknown",null,"state_outside_supported_topology");
    }
    public static EbpExceptionRegions Recover(JsonElement graph,long savedSp,long stateOffset,JsonElement[] catchRows,JsonElement[] resumeRows,JsonElement[] suffixRows,int retryMarker)
    {
        void Need(bool yes,string why){if(!yes)throw new ArgumentException("EBP_regions_"+why);}
        var info=graph.GetProperty("FuncInfo");
        Need(info.TryGetProperty("flags",out var flags)&&flags.GetInt32()==1&&info.TryGetProperty("bytes_hex",out var raw)&&raw.GetString() is string bytes&&bytes.Length==72&&bytes.StartsWith("22059319",StringComparison.Ordinal)&&bytes.EndsWith("01000000",StringComparison.Ordinal),"exception_category_profile");
        Need(savedSp==-16&&stateOffset==-4&&savedSp+4<=stateOffset,"distinct_saved_ESP_and_state");
        var tries=graph.GetProperty("try_map").GetProperty("entries").EnumerateArray().OrderBy(t=>t.GetProperty("try_low").GetInt32()).ToArray();
        Need(tries.Length==2&&retryMarker>=0&&retryMarker<catchRows.Length,"complete_regions");
        int initial=tries[0].GetProperty("try_low").GetInt32(),retry=tries[1].GetProperty("try_low").GetInt32();
        Need(initial==0&&retry==2&&tries.All(t=>t.GetProperty("try_high").GetInt32()==t.GetProperty("try_low").GetInt32()&&t.GetProperty("catch_high").GetInt32()==3),"try_intervals");
        ulong Handler(JsonElement t)=>t.GetProperty("handlers").GetProperty("entries")[0].GetProperty("entry_va").GetUInt64();
        ulong[] Origins(IEnumerable<JsonElement> rows)=>rows.Select(r=>r.GetProperty("pc").GetUInt64()).ToArray();
        return new(-12,(int)savedSp,(int)stateOffset,initial,initial+1,retry,retry+1,
            [new("initial_suffix",initial,Handler(tries[0]),Origins(suffixRows)),
             new("catch_preparation",initial+1,null,Origins(catchRows.Take(retryMarker))),
             new("retry_allocation",retry,Handler(tries[1]),Origins(catchRows.Skip(retryMarker))),
             new("catch_completion",retry,Handler(tries[1]),[]),
             new("literal_continuation",retry,Handler(tries[1]),Origins(resumeRows),true),
             new("resumed_suffix",retry,Handler(tries[1]),Origins(suffixRows),true),
             new("cleanup",retry+1,null,[])],
            "vc8_ebp_catch_normal_completion_restores_saved_esp_not_state_v1",
            ["State intervals are conditional on no intervening runtime-state alias or callback mutation; arbitrary writes remain unknown",
             "CatchIt stores try_high+1 at registration+8; catch state marker overrides it; normal completion restores registration-4 only",
             "Guarded caught-object destruction precedes literal continuation loads and remains in the retry-state interval if a C++ exception reaches the parent",
             "State1 preparation and state3 cleanup failures do not reenter cleanup; source guard/rethrow adds unproved runtime effects",
             "Ordinary access faults are not converted into host C++ exceptions; FuncInfo magic/flags and runtime category dispatch remain bound obligations",
             "Native frame/alias, unwind, exception ownership, saved registers, return-PC and trap/resumption correspondence require independent complete checking"]);
    }
}
