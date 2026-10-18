"""Automatically derived context and provisional declarations; no ABI acceptance gate."""
from workers.deepseek_packet import encode
from rapid.packets import PIN
from .catalog import entry

INSTRUCTIONS='''Emit only JSON {"source":"one self-contained C++98 translation unit", "uncertainties":[optional strings]}. C++ is the only authored per-function artifact. Define every currently requested fn_RVA with its exact // FUNCTION: DAO 0xORIGINAL_VA annotation in increasing VA order, at the emitting out-of-line definition. Use real x86 native calling conventions inferred from bytes, unsigned wrapping and precise memory/FP behavior. Small inferred class declarations with OUT-OF-LINE __thiscall methods are permitted. No Context, inline assembly, naked functions, encoded opcode arrays, test artifacts, wrappers or successful unknown stubs. Unknown ABI/signature remains a hypothesis, never evidence of zero arguments. Refine provisional declarations locally as required. All declarations stay in this source. Compile with VC8 /c /O2 /Ob1 /Oy /Gy /Z7 /Zl /GS- /GR- /EHsc, no headers/libraries or link. Unresolved functions, globals, imports and indirect calls ARE permitted: use extern declarations and stable fn_XXXXXXXX / g_XXXXXXXX RVA identities. Do not define fake globals or stub callees. Preserve actual call target, import slot, displacement, reads/writes, TLS, FP and control flow; unresolved compiler helpers or comparison support remain inconclusive. Byte-backed context is evidence; pseudotypes are guesses. Do not replace calls with successful constants. Return only currently requested unmatched definitions; prior matched functions may be declared extern. Up to six repairs use actual compiler/object differences. For paged original context, incorporate this page with the prior retained source; partial source/declarations are explicitly provisional until the last page. Never claim a match. No mandatory functions list or per-function notes.'''


def packet(store,rvas,page=0,feedback=None,prior_source=None):
    functions=[];context=[];seen=set()
    for rva in sorted(rvas):
        f=entry(store,rva);pages=f.pop('context_pages');f['context_page']=page;f['context_pages_total']=len(pages);f['instructions']=pages[min(page,len(pages)-1)];functions.append(f)
        neighbors=list(f['direct_calls'])[:12]+f.get('incoming_calls',[])[:4]+[r[0] for r in store.db.execute('SELECT rva FROM catalog WHERE rva BETWEEN ? AND ? ORDER BY abs(rva-?) LIMIT 2',(rva-64,rva+64,rva))]
        # Byte-backed callers are inferred from the already decoded catalog, not invented signatures.
        for n in neighbors:
            if n in seen or n in rvas:continue
            row=store.db.execute('SELECT details_json FROM catalog WHERE rva=?',(n,)).fetchone()
            if row:
                import json
                other=json.loads(row[0]);units=other.pop('context_pages');other['instructions_preview']=units[0][:12];context.append(other);seen.add(n)
        for address in f['address_references'][:32]:
            row=store.db.execute('SELECT details_json FROM object_symbols WHERE original_va=?',(address,)).fetchone()
            if row:
                import json
                context.append(json.loads(row[0]))
    value={'schema_version':1,'profile':'all-inventory-coff','module':'DAOrigins.exe','module_sha256':PIN,'compiler_hypothesis':'VC8 SP1 candidate, exact original patch unknown','instructions_to_author':INSTRUCTIONS,'functions':functions,'related_context':context,'context_complete':all(page+1>=f['context_pages_total'] for f in functions)}
    # Related context is useful but never displaces requested byte-backed pages.
    while len(encode(value))>100000 and value['related_context']:value['related_context'].pop()
    if feedback:value['repair_feedback']=feedback
    if prior_source:value['prior_context_source']=prior_source
    return value
