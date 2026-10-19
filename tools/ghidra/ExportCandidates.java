// Read-only, bounded decompiler drafts and inferred types; never acceptance evidence.
// @category DAODecomp
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.data.*;
import ghidra.program.model.pcode.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.StringWriter;
import java.security.MessageDigest;
import java.util.*;

public class ExportCandidates extends GhidraScript {
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();
    private long base;
    private String digest(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }
    private void write(Path file, JsonObject value) throws Exception {
        Path tmp=file.resolveSibling(file.getFileName()+".tmp");
        Files.writeString(tmp,gson.toJson(value),StandardCharsets.UTF_8);
        Files.move(tmp,file,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
    }
    private JsonObject function(Function f) {
        JsonObject value=new JsonObject();
        value.addProperty("original_va",f.getEntryPoint().getOffset());
        value.addProperty("rva",f.getEntryPoint().getOffset()-base);
        value.addProperty("name",f.getName());
        value.addProperty("prototype_hypothesis",f.getPrototypeString(true,true));
        value.addProperty("calling_convention_hypothesis",f.getCallingConventionName());
        value.addProperty("signature_status","hypothesis");
        value.addProperty("external",f.isExternal());
        return value;
    }
    private JsonObject export(long rva, DecompInterface decompiler, int timeout) throws Exception {
        long started=System.nanoTime();JsonObject value=new JsonObject();
        value.addProperty("rva",rva);value.addProperty("original_va",base+rva);
        Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(base+rva));
        if(f==null){value.addProperty("status","missing_function");return value;}
        value.add("function",function(f));JsonArray ranges=new JsonArray();java.io.ByteArrayOutputStream whole=new java.io.ByteArrayOutputStream();
        for(AddressRange rr:f.getBody()) {
            byte[] bytes=new byte[(int)rr.getLength()];int read=currentProgram.getMemory().getBytes(rr.getMinAddress(),bytes);
            if(read!=bytes.length)throw new IllegalStateException("incomplete_original_range");
            whole.write(bytes);JsonObject range=new JsonObject();range.addProperty("start_rva",rr.getMinAddress().getOffset()-base);range.addProperty("end_rva_inclusive",rr.getMaxAddress().getOffset()-base);range.addProperty("bytes_sha256",digest(bytes));ranges.add(range);
        }
        value.add("ranges",ranges);value.addProperty("bytes_sha256",digest(whole.toByteArray()));
        DecompileResults result=decompiler.decompileFunction(f,timeout,monitor);
        value.addProperty("status",result.decompileCompleted()?"decompiled":"decompile_failed");value.addProperty("decompile_error",result.getErrorMessage());
        if(result.decompileCompleted()) {
            value.addProperty("draft",result.getDecompiledFunction().getC());value.addProperty("decompiled_signature_hypothesis",result.getDecompiledFunction().getSignature());
            HighFunction high=result.getHighFunction();JsonArray symbols=new JsonArray();List<DataType> types=new ArrayList<>();types.add(high.getFunctionPrototype().getReturnType());
            Iterator<HighSymbol> locals=high.getLocalSymbolMap().getSymbols();
            while(locals.hasNext())types.add(locals.next().getDataType());
            Iterator<ClangToken> tokens=result.getCCodeMarkup().tokenIterator(true);Set<String> seen=new HashSet<>();
            while(tokens.hasNext()) {
                ClangToken token=tokens.next();
                if(token instanceof ClangTypeToken)types.add(((ClangTypeToken)token).getDataType());
                if(token instanceof ClangFuncNameToken) {
                    PcodeOp op=token.getPcodeOp();Function target=null;
                    if(op==null)target=f;
                    else if(op.getOpcode()==PcodeOp.CALL)target=currentProgram.getFunctionManager().getFunctionAt(op.getInput(0).getAddress());
                    if(target!=null) {
                        JsonObject sym=function(target);sym.addProperty("kind","function");sym.addProperty("token",token.getText());String key=sym.toString();if(seen.add(key))symbols.add(sym);
                        types.add(target.getReturnType());for(Parameter p:target.getParameters())types.add(p.getDataType());
                    }
                } else if(token instanceof ClangVariableToken) {
                    HighSymbol sym=token.getHighSymbol(high);
                    if(sym!=null && sym.isGlobal() && sym.getStorage()!=null && sym.getStorage().getMinAddress()!=null && sym.getStorage().getMinAddress().isMemoryAddress()) {
                        JsonObject global=new JsonObject();global.addProperty("kind","global");global.addProperty("token",token.getText());global.addProperty("original_va",sym.getStorage().getMinAddress().getOffset());global.addProperty("type_hypothesis",sym.getDataType().getDisplayName());global.addProperty("size",sym.getSize());String key=global.toString();if(seen.add(key))symbols.add(global);types.add(sym.getDataType());
                    }
                }
            }
            value.add("symbols",symbols);
            try {
                StringWriter out=new StringWriter();DataTypeWriter writer=new DataTypeWriter(currentProgram.getDataTypeManager(),out);types.removeIf(Objects::isNull);writer.write(types,monitor);String text=out.toString();
                if(text.length()>262144)value.addProperty("type_error","type_export_size_limit");else value.addProperty("type_declarations_hypothesis",text);
            } catch(Exception e){value.addProperty("type_error",e.getClass().getSimpleName()+":"+e.getMessage());}
        }
        value.addProperty("elapsed_seconds",(System.nanoTime()-started)/1e9);return value;
    }
    public void run() throws Exception {
        String[] args=getScriptArgs();if(args.length!=2)throw new IllegalArgumentException("selection.json output-directory");
        JsonObject selection=JsonParser.parseString(Files.readString(Paths.get(args[0]))).getAsJsonObject();Path output=Paths.get(args[1]);Files.createDirectories(output);
        String pin=currentProgram.getExecutableSHA256();if(!pin.equalsIgnoreCase(selection.get("module_sha256").getAsString()))throw new IllegalStateException("module_pin");
        base=currentProgram.getImageBase().getOffset();int timeout=selection.get("timeout_seconds").getAsInt();if(timeout<1 || timeout>60 || selection.getAsJsonArray("rvas").size()>1000)throw new IllegalArgumentException("bounded_export_limits");
        JsonObject settings=selection.getAsJsonObject("settings");JsonObject revision=new JsonObject();revision.addProperty("saved_last_modified_ms",currentProgram.getDomainFile().getLastModifiedTime());revision.addProperty("saved_version",currentProgram.getDomainFile().getVersion());if(settings.has("project_store_sha256"))revision.add("project_store_sha256",settings.get("project_store_sha256"));String version=ghidra.framework.Application.getApplicationVersion();DecompInterface decompiler=new DecompInterface();int cached=0,exported=0;
        try {
            if(!decompiler.openProgram(currentProgram))throw new IllegalStateException(decompiler.getLastMessage());
            for(JsonElement item:selection.getAsJsonArray("rvas")) {
                monitor.checkCancelled();long rva=item.getAsLong();Path file=output.resolve(String.format("%08x.json",rva));
                if(Files.exists(file)) {JsonObject prior=JsonParser.parseString(Files.readString(file)).getAsJsonObject();if(prior.has("settings") && prior.get("settings").equals(settings) && prior.get("module_sha256").getAsString().equalsIgnoreCase(pin) && prior.get("ghidra_version").getAsString().equals(version) && prior.has("analysis_revision") && prior.get("analysis_revision").equals(revision) && prior.get("image_base").getAsLong()==base && prior.get("language").getAsString().equals(currentProgram.getLanguageID().toString()) && prior.get("compiler_spec").getAsString().equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString())){cached++;continue;}}
                JsonObject value;
                try{value=export(rva,decompiler,timeout);}catch(Exception e){value=new JsonObject();value.addProperty("rva",rva);value.addProperty("status","export_error");value.addProperty("error",e.getClass().getSimpleName()+":"+e.getMessage());}
                value.addProperty("module_sha256",pin.toLowerCase());value.addProperty("image_base",base);value.addProperty("ghidra_version",version);value.addProperty("language",currentProgram.getLanguageID().toString());value.addProperty("compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString());value.add("analysis_revision",revision);value.add("settings",settings);write(file,value);exported++;
            }
        } finally{decompiler.dispose();}
        println("ExportCandidates exported="+exported+" cached="+cached+" output="+output);
    }
}
