// Export analysis hypotheses and selected decompilations; never acceptance proof.
// @category DAODecomp
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.Reference;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class ExportInventory extends GhidraScript {
    private long base;

    private JsonObject describe(Function f) throws Exception {
        JsonObject item = new JsonObject();
        item.addProperty("rva", f.getEntryPoint().getOffset() - base);
        item.addProperty("name", f.getName());
        item.addProperty("signature_hypothesis", f.getSignature().toString());
        item.addProperty("calling_convention_hypothesis", f.getCallingConventionName());
        item.addProperty("thunk", f.isThunk());
        item.addProperty("body_bytes", f.getBody().getNumAddresses());
        JsonArray ranges = new JsonArray();
        for (AddressRange range : f.getBody()) {
            JsonObject entry = new JsonObject();
            entry.addProperty("start_rva", range.getMinAddress().getOffset() - base);
            entry.addProperty("end_rva_inclusive", range.getMaxAddress().getOffset() - base);
            ranges.add(entry);
        }
        item.add("body_ranges", ranges);
        JsonArray calls = new JsonArray();
        for (Reference ref : getReferencesTo(f.getEntryPoint())) {
            if (ref.getReferenceType().isCall()) {
                calls.add(ref.getFromAddress().getOffset() - base);
            }
        }
        item.add("incoming_callsite_rvas", calls);
        return item;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("expected output directory");
        Path output = Paths.get(args[0]);
        Files.createDirectories(output);
        base = currentProgram.getImageBase().getOffset();
        JsonObject root = new JsonObject();
        root.addProperty("schema_version", 1);
        root.addProperty("evidence_kind", "static_analysis_hypotheses");
        root.addProperty("ghidra_version", ghidra.framework.Application.getApplicationVersion());
        root.addProperty("module_sha256", currentProgram.getExecutableSHA256());
        root.addProperty("language", currentProgram.getLanguageID().toString());
        root.addProperty("compiler_spec", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        root.addProperty("image_base", base);
        JsonArray functions = new JsonArray();
        FunctionIterator iter = currentProgram.getFunctionManager().getFunctions(true);
        while (iter.hasNext()) {
            monitor.checkCancelled();
            functions.add(describe(iter.next()));
        }
        root.add("functions", functions);
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        Files.writeString(output.resolve("functions.json"), gson.toJson(root), StandardCharsets.UTF_8);

        DecompInterface decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException(decompiler.getLastMessage());
            for (long rva : new long[]{0x4a3f0L, 0x518a0L}) {
                Function f = currentProgram.getFunctionManager().getFunctionAt(toAddr(base + rva));
                if (f == null) throw new IllegalStateException("missing selected function " + Long.toHexString(rva));
                JsonObject item = describe(f);
                DecompileResults result = decompiler.decompileFunction(f, 30, monitor);
                item.addProperty("decompile_completed", result.decompileCompleted());
                item.addProperty("decompile_error", result.getErrorMessage());
                if (result.decompileCompleted()) {
                    item.addProperty("pseudocode_hypothesis", result.getDecompiledFunction().getC());
                }
                JsonArray disassembly = new JsonArray();
                var instructions = currentProgram.getListing().getInstructions(f.getBody(), true);
                while (instructions.hasNext()) {
                    var instruction = instructions.next();
                    disassembly.add(instruction.getAddress() + "  " + instruction.toString());
                }
                item.add("disassembly", disassembly);
                Files.writeString(output.resolve(String.format("leaf-%08x.json", rva)), gson.toJson(item), StandardCharsets.UTF_8);
            }
        } finally {
            decompiler.dispose();
        }
        println("Exported " + functions.size() + " function hypotheses to " + output);
    }
}
