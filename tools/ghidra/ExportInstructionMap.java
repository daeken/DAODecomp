// Static instruction/flow hypotheses for whole-module coverage. Not acceptance.
// @category DAODecomp
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;
import java.util.zip.GZIPOutputStream;

public class ExportInstructionMap extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=2) throw new IllegalArgumentException("expected output.jsonl.gz and pinned module SHA-256");
        String sha=currentProgram.getExecutableSHA256();
        if(sha==null || !sha.equalsIgnoreCase(args[1])) throw new IllegalStateException("analysis module identity differs from pinned original");
        long base=currentProgram.getImageBase().getOffset();
        Path output=Paths.get(args[0]);Files.createDirectories(output.getParent());
        Gson gson=new Gson();long functions=0,instructionCount=0;
        try(BufferedWriter writer=new BufferedWriter(new OutputStreamWriter(
                new GZIPOutputStream(Files.newOutputStream(output)),StandardCharsets.UTF_8))) {
            JsonObject header=new JsonObject();header.addProperty("record","module");header.addProperty("schema_version",1);
            header.addProperty("module_sha256",sha.toLowerCase());header.addProperty("module",currentProgram.getName());
            header.addProperty("image_base",base);header.addProperty("ghidra_version",ghidra.framework.Application.getApplicationVersion());
            header.addProperty("evidence_kind","static instruction boundaries and references; original-byte validation required; no behavioral acceptance");
            writer.write(gson.toJson(header));writer.newLine();
            FunctionIterator iterator=currentProgram.getFunctionManager().getFunctions(true);
            while(iterator.hasNext()) {
                monitor.checkCancelled();Function function=iterator.next();JsonObject row=new JsonObject();
                row.addProperty("record","function");row.addProperty("rva",function.getEntryPoint().getOffset()-base);
                row.addProperty("name",function.getName());JsonArray ranges=new JsonArray();
                for(AddressRange range:function.getBody()) {
                    JsonObject item=new JsonObject();item.addProperty("rva",range.getMinAddress().getOffset()-base);
                    item.addProperty("size",range.getLength());ranges.add(item);
                }
                row.add("ranges",ranges);JsonArray instructions=new JsonArray();
                var listing=currentProgram.getListing().getInstructions(function.getBody(),true);
                while(listing.hasNext()) {
                    monitor.checkCancelled();var instruction=listing.next();JsonObject item=new JsonObject();
                    item.addProperty("rva",instruction.getAddress().getOffset()-base);
                    StringBuilder hex=new StringBuilder();
                    for(byte value:instruction.getBytes()) hex.append(String.format("%02x",value&255));
                    item.addProperty("bytes",hex.toString());item.addProperty("text",instruction.toString());
                    item.addProperty("flow_type",instruction.getFlowType().toString());
                    JsonArray targets=new JsonArray();
                    for(var address:instruction.getFlows()) targets.add(address.getOffset()-base);
                    item.add("flow_target_rvas",targets);
                    var fallthrough=instruction.getFallThrough();
                    if(fallthrough!=null)item.addProperty("fallthrough_rva",fallthrough.getOffset()-base);
                    instructions.add(item);instructionCount++;
                }
                row.add("instructions",instructions);writer.write(gson.toJson(row));writer.newLine();functions++;
            }
            JsonObject end=new JsonObject();end.addProperty("record","complete");end.addProperty("functions",functions);
            end.addProperty("instructions",instructionCount);end.addProperty("behavioral_acceptance",false);
            writer.write(gson.toJson(end));writer.newLine();
        }
        println("Exported "+functions+" function hypotheses and "+instructionCount+" instruction hypotheses to "+output);
    }
}
