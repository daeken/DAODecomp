"""Preferred-address linking for explicitly selected PE32 recovery projects."""
import base64
import copy
from pathlib import Path
from tools import recomp
from tools.daodecomp.pe import fingerprint


def reviewed_data_sections(state, result):
    """Expose only explicit, byte-pinned inline pools; never entire code pages."""
    regions = state.get("data_regions", [])
    if not regions:
        return []
    binary = recomp.checked_binary(state)
    image, pe = binary.read_bytes(), fingerprint(binary)
    if pe["sha256"] != state["binary_sha256"]:
        raise ValueError("inline data module identity changed")
    occupied = [(s["address"], s["size"]) for s in result["data_sections"]]
    occupied += [(result["image_base"] + i["rva"], len(bytes.fromhex(i["bytes"])))
                 for f in result["functions"] for i in f["instructions"]]
    sections = []
    for index, region in enumerate(regions):
        rva, size = region["rva"], region["size"]
        if (not isinstance(rva, int) or not isinstance(size, int) or rva < 0 or
                not 0 < size <= 1024 * 1024 or rva + size > result["pe_image_size"] or
                result["image_base"] + rva + size > 2**32 or not region.get("purpose") or
                not isinstance(region.get("provenance"), dict) or
                region["provenance"].get("module_sha256") != state["binary_sha256"]):
            raise ValueError("invalid reviewed inline data region")
        address = result["image_base"] + rva
        if any(address < start + length and start < address + size for start, length in occupied):
            raise ValueError("inline data overlaps mapped data or decoded instructions")
        candidates = [s for s in pe["sections"] if s["rva"] <= rva and rva + size <= s["rva"] + s["file_size"]]
        if len(candidates) != 1:
            raise ValueError("inline data is not uniquely file-backed")
        offset = candidates[0]["file_offset"] + rva - candidates[0]["rva"]
        content = image[offset:offset + size]
        if recomp.digest(content) != region["sha256"]:
            raise ValueError("reviewed inline data bytes changed")
        sections.append(dict(name=f".inline_{index}", address=address, size=size, readable=True, writable=False,
                             bytes=base64.b64encode(content).decode("ascii"), purpose=region["purpose"],
                             provenance=region["provenance"]))
        occupied.append((address, size))
    return sections


def module_key(name):
    return name.replace("\\", "/").rsplit("/", 1)[-1].lower()


def cpp_string(value):
    return "".join(f'"\\x{byte:02x}"' for byte in value.encode("ascii")) or '""'


def resolve_bindings(modules, functions, imports):
    providers = {module_key(m["module"]): m for m in modules}
    code = {f["image_base"] + i["rva"] for f in functions for i in f["instructions"]}
    bindings = []
    for imported in imports:
        provider = providers.get(module_key(imported["library"]))
        translated = provider is not None or imported["policy"] == "translate"
        imported["policy"] = "translate" if translated else "native"
        row = dict(imported, target=imported["address"], status="native", provider=None,
                   symbol_resolved=False, code_ready=False)
        if translated:
            row["status"] = "missing_module"
            if provider:
                row["provider"] = provider["id"]
                symbol = imported["symbol"]
                if symbol.startswith("@ordinal:"):
                    try:
                        ordinal = int(symbol.split(":", 1)[1])
                    except ValueError:
                        raise ValueError("invalid ordinal import") from None
                    matches = [e for e in provider["ordinal_exports"] if e["ordinal"] == ordinal]
                else:
                    matches = [e for e in provider["exports"] if e["name"] == symbol]
                row["status"] = "missing_export"
                if len(matches) > 1:
                    raise ValueError("ambiguous exported symbol")
                if matches:
                    exported = matches[0]
                    row["status"] = "unsupported_forwarder" if exported["forwarder"] else "invalid_export_address"
                    if not exported["forwarder"]:
                        target = exported["address"]
                        mapped_data = any(s["address"] <= target < s["address"] + s["size"] for s in provider["data_sections"])
                        if exported["executable"] and provider["image_base"] <= target < provider["image_base"] + provider["image_size"]:
                            row.update(target=target, symbol_resolved=True, code_ready=target in code,
                                       status="translated_code" if target in code else "untranslated_code")
                        elif not exported["executable"] and mapped_data:
                            row.update(target=target, symbol_resolved=True, status="translated_data")
        bindings.append(row)
    return bindings


def generate_linked(project, linked_projects, dispatch=False, raw_memory=False, require_translated_code=False):
    paths = [project.resolve(), *(Path(p).resolve() for p in linked_projects)]
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate module project")
    snapshots = [recomp.state(path) for path in paths]
    names = [module_key(s["module"]) for s in snapshots]
    if len(set(names)) != len(names):
        raise ValueError("duplicate module name (Windows names are case-insensitive)")
    results, modules, functions, imports = [], [], [], []
    blobs, loader_lines, prefixes = {}, [], set()
    for index, (path, state) in enumerate(zip(paths, snapshots)):
        if module_key(Path(state["binary"]).name) != module_key(state["module"]):
            raise ValueError("module name does not match its pinned binary")
        identity = state["module"] + ":" + state["binary_sha256"]
        tag = "m_" + recomp.digest((module_key(state["module"]) + ":" + state["binary_sha256"]).encode())[:16] + "_"
        if tag in prefixes:
            raise ValueError("module symbol-prefix collision")
        prefixes.add(tag)
        result = recomp.export(state, dispatch, raw_memory, "" if index == 0 else tag, include_data=True)
        result["data_sections"].extend(reviewed_data_sections(state, result))
        if results and (result["runtime"] != results[0]["runtime"] or result["backend_artifacts"] != results[0]["backend_artifacts"] or
                        result["module_policy_sha256"] != results[0]["module_policy_sha256"]):
            raise ValueError("module runtime/backend/policy versions differ")
        rule = result["module_policy"]["modules"].get(module_key(state["module"]))
        if rule and rule["policy"] != "translate":
            raise ValueError("explicit module policy forbids translating this module")
        size, base = result["pe_image_size"], result["image_base"]
        if size <= 0 or base < 0 or base + size > 2**32:
            raise ValueError("linked modules require nonempty declared guest32 image ranges")
        if any(base < m["image_base"] + m["image_size"] and m["image_base"] < base + size for m in modules):
            raise ValueError("overlapping preferred module ranges; guest rebasing is not implemented")
        module = {"id": identity, "module": state["module"], "binary_sha256": state["binary_sha256"],
                  "project": str(path), "project_sha256": recomp.digest(recomp.encoded(state)),
                  "image_base": base, "image_size": size, "has_tls": result["pe_has_tls"],
                  "initialization": "PE data only; entry, TLS and CRT initializers not executed",
                  "code_prefix": "" if index == 0 else tag, "exports": result["exports"],
                  "ordinal_exports": result["ordinal_exports"], "data_sections": []}
        loader_lines.append(f"    memory.reserve_image(0x{base:08x}u,{size}u);")
        for section_index, section in enumerate(result.pop("data_sections")):
            section = dict(section)
            content = base64.b64decode(section.pop("bytes"), validate=True)
            if len(content) > section["size"] or section["size"] > 64 * 1024 * 1024:
                raise ValueError("invalid/oversized data section")
            filename = tag + f"section_{section_index}.bin"
            blobs[filename] = content
            section.update(file=filename, file_size=len(content), sha256=recomp.digest(content))
            module["data_sections"].append(section)
            loader_lines.append("    memory.map_file(" + cpp_string(state["module"] + ":" + section["name"]) +
                                f",0x{section['address']:08x}u,{section['size']}u," +
                                ("true" if section["readable"] else "false") + "," + ("true" if section["writable"] else "false") +
                                ",directory/" + cpp_string(filename) + f",{len(content)}u," + cpp_string(section["sha256"]) + ");")
        for function in result["functions"]:
            function.update(module=state["module"], module_sha256=state["binary_sha256"], module_id=identity,
                            image_base=base, owner_project=str(path))
        for imported in result["imports"]:
            imported.update(importing_module=state["module"], importing_module_id=identity)
            if not any(s["address"] <= imported["address"] and imported["address"] + 4 <= s["address"] + s["size"]
                       for s in module["data_sections"]):
                raise ValueError("IAT slot is outside mapped module data")
        functions.extend(result["functions"]); imports.extend(result["imports"]); modules.append(module); results.append(result)
    functions.sort(key=lambda f: f["image_base"] + f["rva"])
    if len({i["address"] for i in imports}) != len(imports):
        raise ValueError("duplicate IAT slot address")
    bindings = resolve_bindings(modules, functions, imports)
    incomplete = [b for b in bindings if b["policy"] == "translate" and b["status"] not in ("translated_code", "translated_data")]
    if require_translated_code and incomplete:
        raise ValueError(f"{len(incomplete)} translated imports lack executable code or data bindings")
    result = copy.copy(results[0])
    result.update(functions=functions, imports=imports, modules=modules, extra_sources=["image_loader.cpp"],
                  link={"bindings": bindings, "translated_imports": sum(b["policy"] == "translate" for b in bindings),
                        "symbols_resolved": sum(b["symbol_resolved"] for b in bindings),
                        "code_ready": sum(b["code_ready"] for b in bindings), "incomplete_translated": len(incomplete),
                        "preferred_bases_preserved": True, "module_initializers_executed": False},
                  linked_projects=[str(p) for p in paths[1:]],
                  module_backends={m["id"]: r["backend_artifacts"] for m, r in zip(modules, results)})
    files = recomp.render(snapshots[0], result)
    files.update(blobs)
    files["image_memory.hpp"] = (recomp.RUNTIME / "image_memory.hpp").read_text()
    files["process_memory.hpp"] = (recomp.RUNTIME / "process_memory.hpp").read_text()
    files["win32_memory.hpp"] = (recomp.RUNTIME / "win32_memory.hpp").read_text()
    files["image_tls.hpp"] = (recomp.RUNTIME / "image_tls.hpp").read_text()
    files["functions.hpp"] += ('\nnamespace recomp_generated {\n'
                               'struct LinkedImportBinding { std::uint32_t slot,target; const char* library; const char* symbol; const char* status; };\n'
                               'std::span<const LinkedImportBinding> linked_import_bindings();\n}\n')
    binding_rows = ",\n".join(f"    {{0x{b['address']:08x}u,0x{b['target']:08x}u,{cpp_string(b['library'])},{cpp_string(b['symbol'])},{cpp_string(b['status'])}}}"
                                for b in bindings)
    tls_modules=",\n".join(f"    {{0x{m['image_base']:08x}u,{m['image_size']}u}}" for m in modules)
    files["image_loader.cpp"] = ('#include "functions.hpp"\n#include "image_memory.hpp"\n#include "image_tls.hpp"\n#include <array>\n'
                                  'namespace recomp_generated {\n'
                                  f'static const std::array<ThreadTlsModule,{len(modules)}> tls_modules{{{{\n{tls_modules}\n}}}};\n'
                                  f'static const std::array<LinkedImportBinding,{len(bindings)}> bindings{{{{\n{binding_rows}\n}}}};\n'
                                  'std::span<const LinkedImportBinding> linked_import_bindings() { return bindings; }\n'
                                  'void reserve_linked_images(ImageMemory& memory) {\n' +
                                  "\n".join(f"    memory.reserve_image(0x{m['image_base']:08x}u,{m['image_size']}u);" for m in modules) + '\n}\n'
                                  'void initialize_linked_images(ImageMemory& memory,const std::filesystem::path& directory,const ThreadTlsLayout* tls) {\n' +
                                  "\n".join(loader_lines) + '\n'
                                  '    for(const auto& binding:bindings) memory.store(binding.slot,binding.target,32);\n'
                                  '    if(tls) initialize_image_tls(memory,tls_modules,*tls);\n'
                                  '    memory.seal();\n}\n}\n')
    files["image_main.cc"] = ('#include "functions.hpp"\n#include "image_memory.hpp"\n#include <cstdio>\n#include <cstring>\n'
                              'int main(int argc,char** argv) { try {\n'
                              '    if(argc==2 && !std::strcmp(argv[1],"--list")) {\n'
                              '        for(const auto& e:recomp_generated::compiled_functions()) std::printf("0x%08x\\n",unsigned(e.address)); return 0;\n    }\n'
                              '    if(argc==2 && !std::strcmp(argv[1],"--bindings")) {\n'
                              '        for(const auto& b:recomp_generated::linked_import_bindings()) std::printf("%s!%s -> 0x%08x [%s]\\n",b.library,b.symbol,unsigned(b.target),b.status); return 0;\n    }\n'
                              '    if(argc==3 && !std::strcmp(argv[1],"--check-images")) {\n'
                              '        recomp_generated::ImageMemory memory; recomp_generated::initialize_linked_images(memory,argv[2]);\n'
                              '        std::printf("Mapped %u data regions; module initialization not executed.\\n",unsigned(memory.region_count())); return 0;\n    }\n'
                              '    std::fputs("Use --list, --bindings or --check-images DIRECTORY. Game startup is not implemented.\\n",stderr); return 2;\n'
                              '} catch(const std::exception& e) { std::fprintf(stderr,"image: %s\\n",e.what()); return 3; } }\n')
    # Optimistic checks avoid holding mutually ordered project locks across roots.
    for path, snapshot in zip(paths, snapshots):
        if recomp.encoded(recomp.state(path)) != recomp.encoded(snapshot):
            raise ValueError("module project changed during linked generation")
        recomp.checked_binary(snapshot)
    if recomp.digest(recomp.MODULE_POLICY.read_bytes()) != result["module_policy_sha256"]:
        raise ValueError("module policy changed during linked generation")
    published = recomp.publish(project, snapshots[0], result, files)
    recomp.atomic_json(project / "link.json", {"schema_version": 1, "projects": [str(p) for p in paths[1:]]})
    return dict(published, modules=len(modules), translated_imports=result["link"]["translated_imports"],
                symbols_resolved=result["link"]["symbols_resolved"], code_ready=result["link"]["code_ready"],
                incomplete_translated=len(incomplete))
