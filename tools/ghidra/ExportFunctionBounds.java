// Bounds hypotheses for startup discovery, not signatures or acceptance evidence.
// @category DAODecomp
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

public class ExportFunctionBounds extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=1) throw new IllegalArgumentException("expected output JSON file");
        long base=currentProgram.getImageBase().getOffset();
        JsonObject root=new JsonObject();
        root.addProperty("schema_version",1);
        root.addProperty("evidence_kind","static_analysis_hypotheses; byte decoding and execution still required");
        root.addProperty("ghidra_version",ghidra.framework.Application.getApplicationVersion());
        root.addProperty("module_sha256",currentProgram.getExecutableSHA256());
        root.addProperty("image_base",base);
        JsonArray functions=new JsonArray();
        FunctionIterator iterator=currentProgram.getFunctionManager().getFunctions(true);
        while(iterator.hasNext()) {
            monitor.checkCancelled();
            Function function=iterator.next(); JsonObject row=new JsonObject();
            row.addProperty("rva",function.getEntryPoint().getOffset()-base);
            row.addProperty("name",function.getName());
            JsonArray ranges=new JsonArray();
            for(AddressRange range:function.getBody()) {
                JsonObject bounds=new JsonObject();
                bounds.addProperty("start_rva",range.getMinAddress().getOffset()-base);
                bounds.addProperty("end_rva_inclusive",range.getMaxAddress().getOffset()-base);
                ranges.add(bounds);
            }
            row.add("body_ranges",ranges); functions.add(row);
        }
        root.add("functions",functions);
        Path output=Paths.get(args[0]); Files.createDirectories(output.getParent());
        Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(root)+"\n",StandardCharsets.UTF_8);
    }
}
