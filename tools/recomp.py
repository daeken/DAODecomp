"""Iterative binary-to-C++ workspace. Run with python3 -m tools.recomp.

Human edits live in project.json; immutable generated views resolve display names
to backend-provided origins. This does not promote the recovery registry.
"""
import argparse
from contextlib import contextmanager
import hashlib
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "recompiler/Bridge/Recomp.Bridge.csproj"
DLL = BRIDGE.parent / "bin/Release/net10.0/Recomp.Bridge.dll"
RUNTIME = ROOT / "recompiler/runtime"
MODULE_POLICY = ROOT / "recompiler/modules.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".recomp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(project):
    # Supported controller hosts are POSIX. Windows runners are separate tools.
    import fcntl
    project.mkdir(parents=True, exist_ok=True)
    with (project / ".lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def state(project):
    result = load(project / "project.json")
    if result["schema_version"] != 1:
        raise ValueError("unsupported project schema")
    return result


def checked_binary(project_state):
    binary = Path(project_state["binary"])
    if digest(binary.read_bytes()) != project_state["binary_sha256"]:
        raise ValueError("reference binary hash changed")
    return binary


def export(project_state, dispatch=False, raw_memory=False, module_prefix="", include_data=False):
    with locked(ROOT / "local/recomp/bridge-build"):
        return _export(project_state, dispatch, raw_memory, module_prefix, include_data)


def _export(project_state, dispatch=False, raw_memory=False, module_prefix="", include_data=False):
    checked_binary(project_state)
    policy = load(MODULE_POLICY)
    if policy["schema_version"] != 1 or policy["default_import_policy"] != "native":
        raise ValueError("unsupported module policy")
    if any(spec.get("policy") not in ("translate", "native") for spec in policy["modules"].values()):
        raise ValueError("unknown module policy; refusing implicit native fallback")
    own_policy = policy["modules"].get(project_state["module"].lower())
    if own_policy and own_policy["sha256"] != project_state["binary_sha256"]:
        raise ValueError("module differs from the pinned translation policy")
    build = subprocess.run(["dotnet", "build", str(BRIDGE), "-c", "Release", "--nologo",
                            f"-p:SharpRetroRoot={project_state['sharp_retro']}"],
                           capture_output=True, text=True, timeout=180)
    if build.returncode:
        raise ValueError(build.stdout + build.stderr)
    request = {"schema_version": 1, "binary": project_state["binary"],
               "module_prefix": module_prefix, "include_data": include_data,
               "binary_sha256": project_state["binary_sha256"], "dispatch": dispatch, "raw_memory": raw_memory,
               "import_policy": {name: spec["policy"] for name, spec in policy["modules"].items()},
               "functions": [{"rva": f["rva"], "size": f["size"],
                              "ranges": f.get("ranges"), "extra_entries": f.get("extra_entries"),
                              "annotations": f["annotations"], "structures": f.get("structures", {})}
                             for f in project_state["functions"]]}
    run = subprocess.run(["dotnet", str(DLL)], input=json.dumps(request),
                         capture_output=True, text=True, timeout=180)
    if run.returncode:
        raise ValueError(run.stderr)
    checked_binary(project_state)
    result = json.loads(run.stdout)
    result["module_policy"] = policy
    result["module_policy_sha256"] = digest(MODULE_POLICY.read_bytes())
    result["backend_artifacts"] = {p.name: digest(p.read_bytes()) for p in sorted(DLL.parent.iterdir())
                                   if p.suffix in (".dll", ".hpp", ".json")}
    result["host"] = {"platform": sys.platform, "machine": os.uname().machine,
                      "dotnet": subprocess.check_output(["dotnet", "--version"], text=True).strip()}
    return result


def generate(project, dispatch=False, raw_memory=False, linked_modules=None, require_translated_code=False):
    with locked(project):
        if linked_modules is None and (project / "link.json").exists():
            linked_modules = [Path(p) for p in load(project / "link.json")["projects"]]
        if linked_modules:
            from tools.recomp_link import generate_linked
            return generate_linked(project, linked_modules, dispatch, raw_memory, require_translated_code)
        initial = state(project)
        # Serialize exports as well as edits: the shared bridge output directory
        # must not be rebuilt while another generation is reading its assemblies.
        result = export(initial, dispatch, raw_memory)
        files = render(initial, result)
        if require_translated_code and any(i["policy"] == "translate" for i in result["imports"]):
            raise ValueError("translated imports require linked module projects")
        published = publish(project, initial, result, files)
        if linked_modules == []:
            (project / "link.json").unlink(missing_ok=True)
        return published


def render(initial, result):
    from tools import recomp_imports
    bindings = recomp_imports.read_bindings()
    recomp_imports.apply_contracts(result["imports"], bindings)
    result["native_bindings_sha256"] = digest(encoded(bindings))
    header = '#pragma once\n#include "runtime_api.hpp"\nnamespace recomp_generated {\n'
    api = '#pragma once\n#include "runtime.hpp"\n#include <span>\nnamespace recomp_generated {\n'
    for function in result["functions"]:
        header += (f"sharp_retro::Exit {function['name']}(sharp_retro::State&, "
                   "sharp_retro::Memory&, std::uint64_t);\n"
                   f"sharp_retro::Exit {function['name']}_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n")
    header += "}\n"
    api += ("using GuestFunction = sharp_retro::Exit(*)(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\n"
               "using GuestStep = sharp_retro::Exit(*)(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n"
               "struct CodeEntry { std::uint32_t address; GuestStep step; };\n"
               "std::span<const CodeEntry> compiled_code();\n"
               "inline GuestStep(*extra_guest_step)(std::uint32_t)=nullptr;\n"
               "inline GuestFunction(*extra_guest_function)(std::uint32_t)=nullptr;\n"
               "inline bool(*missing_guest_code)(std::uint32_t)=nullptr;\n"
               "struct FunctionEntry { std::uint32_t address; GuestFunction function; };\n"
               "struct ImportEntry { std::uint32_t address; const char* library; const char* symbol; bool translated_module; };\n"
               "using ImportHandler = void(*)(const ImportEntry&,sharp_retro::State&,sharp_retro::Memory&);\n"
               "std::span<const FunctionEntry> compiled_functions();\n"
               "std::span<const ImportEntry> declared_imports();\n"
               "GuestFunction resolve_guest(std::uint32_t address);\n"
               "sharp_retro::Exit invoke_guest(std::uint32_t,sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\n"
               "sharp_retro::Exit resume_guest(std::uint32_t,sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&,ImportHandler=nullptr);\n"
               "sharp_retro::Exit execute_guest(std::uint32_t,std::uint32_t,sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&,ImportHandler=nullptr);\n}\n")
    files = {"runtime.hpp": result.pop("runtime"), "functions.hpp": header,"runtime_api.hpp":api,
             "candidate_api.hpp": (RUNTIME / "candidate_api.hpp").read_text(),
             "native_imports.hpp": (RUNTIME / "native_imports.hpp").read_text(),
             "native_batch.hpp": (RUNTIME / "native_batch.hpp").read_text(),
             "native_files.hpp": (RUNTIME / "native_files.hpp").read_text(),
             "native_memory.hpp": (RUNTIME / "native_memory.hpp").read_text(),
             "native_abi.hpp": (RUNTIME / "native_abi.hpp").read_text(),
             "native_provider_identity.hpp": (RUNTIME / "native_provider_identity.hpp").read_text(),
             "static_code_lookup.hpp": (RUNTIME / "static_code_lookup.hpp").read_text(),
             "native_error.hpp": (RUNTIME / "native_error.hpp").read_text(),
             "native_abi_frame.hpp": (RUNTIME / "native_abi_frame.hpp").read_text(),
             "native_abi.cpp": (RUNTIME / "native_abi.cpp").read_text(),
             "native_cpu.cpp": (RUNTIME / "native_cpu.cpp").read_text(),
             "native_simd.cpp": (RUNTIME / "native_simd.cpp").read_text(),
             "native_abi_call.S": (RUNTIME / "native_abi_call.S").read_text(),
             "native_execution.hpp": (RUNTIME / "native_execution.hpp").read_text(),
             "process_memory.hpp": (RUNTIME / "process_memory.hpp").read_text(),
             "win32_memory.hpp": (RUNTIME / "win32_memory.hpp").read_text(),
             "native_bindings.generated.inc": recomp_imports.render_bindings(bindings),
             "native-bindings.json": encoded(bindings),
             "native_registry.hpp": (RUNTIME / "native_registry.hpp").read_text(),
             "native_registry_keys.hpp": (RUNTIME / "native_registry_keys.hpp").read_text(),
             "native_sync.hpp": (RUNTIME / "native_sync.hpp").read_text(),
             "native_resources.hpp": (RUNTIME / "native_resources.hpp").read_text(),
             "native_system_info.hpp": (RUNTIME / "native_system_info.hpp").read_text(),
             "image_memory.hpp": (RUNTIME / "image_memory.hpp").read_text(),
             "native_callbacks.hpp": (RUNTIME / "native_callbacks.hpp").read_text(),
             "native_floating.hpp": (RUNTIME / "native_floating.hpp").read_text(),
             "native_x87.hpp": (RUNTIME / "native_x87.hpp").read_text(),
             "native_access.hpp": (RUNTIME / "native_access.hpp").read_text()}
    for function in result["functions"]:
        files[function["name"] + ".cpp"] = function.pop("source")
        function["id"] = (f"{function.get('module',initial['module'])}:{function.get('module_sha256',initial['binary_sha256'])}:"
                          f"rva-{function['rva']:08x}")
    sources = "\n".join("  " + name for name in [*(f["name"]+".cpp" for f in result["functions"]), *result.get("extra_sources", [])])
    ordered_functions = sorted(result["functions"], key=lambda f: f.get("image_base",initial["image_base"])+f["rva"])
    entries = ",\n".join(f"    {{0x{f.get('image_base',initial['image_base'])+f['rva']:08x}u,{f['name']}}}" for f in ordered_functions)
    owners = {}
    for function in result["functions"]:
        for instruction in function["instructions"]:
            address = function.get("image_base",initial["image_base"]) + instruction["rva"]
            if address in owners:
                raise ValueError("ambiguous instruction ownership")
            owners[address] = function["name"] + "_step"
    code = ",\n".join(f"    {{0x{address:08x}u,{name}}}" for address, name in sorted(owners.items()))
    def cpp_string(value):
        return "".join(f'"\\x{byte:02x}"' for byte in value.encode("ascii"))
    if set(owners) & {i["address"] for i in result["imports"]}:
        raise ValueError("import token overlaps translated code")
    imports = ",\n".join(f"    {{0x{i['address']:08x}u,{cpp_string(i['library'])},{cpp_string(i['symbol'])},"
                          + ("true" if i["policy"] == "translate" else "false") + "}"
                          for i in sorted(result["imports"], key=lambda i: i["address"]))
    template = (RUNTIME / "registry.cpp.in").read_text()
    for token, value in {"FUNCTION_COUNT": len(result["functions"]), "ENTRIES": entries,
                         "CODE_COUNT": len(owners), "CODE": code, "IMPORT_COUNT": len(result["imports"]),
                         "IMPORTS": imports}.items():
        template = template.replace("@" + token + "@", str(value))
    files["registry.cpp"] = template
    files["image_main.cc"] = ('#include "functions.hpp"\n#include <cstdio>\n#include <cstring>\n'
                              'int main(int argc,char** argv) {\n'
                              '    if(argc!=2 || std::strcmp(argv[1],"--list")) {\n'
                              '        std::fputs("Translation bundle: use --list. Game startup is not implemented.\\n",stderr); return 2;\n    }\n'
                              '    for(const auto& entry:recomp_generated::compiled_functions()) std::printf("0x%08x\\n",unsigned(entry.address));\n'
                              '    return 0;\n}\n')
    files["CMakeLists.txt"] = ("cmake_minimum_required(VERSION 3.20)\n"
                              "project(recomp_generated LANGUAGES CXX)\n"
                              f"add_library(recomp_generated STATIC registry.cpp\n{sources}\n)\n"
                              "target_compile_features(recomp_generated PUBLIC cxx_std_20)\n"
                              "target_include_directories(recomp_generated PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})\n"
                              "if(WIN32)\n set(CMAKE_ASM_COMPILER ${CMAKE_CXX_COMPILER})\n enable_language(ASM)\n"
                              " option(RECOMP_NATIVE_EXECUTION \"Native x86 memory and ABI; OFF selects the strict validation backend\" ON)\n"
                              " if(RECOMP_NATIVE_EXECUTION)\n  target_compile_definitions(recomp_generated PUBLIC RECOMP_NATIVE_EXECUTION=1)\n endif()\n"
                              " target_sources(recomp_generated PRIVATE native_abi.cpp native_abi_call.S native_cpu.cpp native_simd.cpp)\n"
                              " target_link_libraries(recomp_generated PUBLIC advapi32 winmm user32 shell32 gdi32)\nendif()\n"
                              "if(MSVC)\n message(FATAL_ERROR \"Requires a supported unsigned 128-bit carrier\")\nendif()\n"
                              "add_executable(recomp_image image_main.cc)\n"
                              "target_link_libraries(recomp_image PRIVATE recomp_generated)\n"
                              "if(MINGW)\n target_link_options(recomp_image PRIVATE -static)\nendif()\n")
    return files

def publish(project, initial, result, files):
    """Publish a complete immutable view; binary blobs stay beside its source."""
    result["project_revision"] = initial["revision"]
    result["project_sha256"] = digest(encoded(initial))
    content_bytes = {name: content.encode() if isinstance(content, str) else content for name, content in files.items()}
    result["files"] = {name: digest(content) for name, content in content_bytes.items()}
    result["evidence_status"] = "generated_only; not behavioral validation"
    view_id = digest(encoded(result))
    view = project / "views" / view_id
    if not view.exists():
        view.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".view-", dir=view.parent) as temporary:
            staging = Path(temporary) / "view"
            staging.mkdir()
            for name, content in content_bytes.items():
                (staging / name).write_bytes(content)
            atomic_json(staging / "manifest.json", result)
            staging.rename(view)
    atomic_json(project / "current.json", {"view": view_id})
    return {"view": view_id, "directory": str(view), "functions": len(result["functions"]),
            "evidence_status": result["evidence_status"]}


def read_view(project, view_id):
    if len(view_id) != 64 or any(c not in "0123456789abcdef" for c in view_id):
        raise ValueError("expected a complete view hash")
    directory = project / "views" / view_id
    restore_view_manifest(directory, view_id)
    manifest = load(directory / "manifest.json")
    if digest(encoded(manifest)) != view_id:
        raise ValueError("view manifest changed")
    for name, expected in manifest["files"].items():
        if Path(name).name != name or digest((directory / name).read_bytes()) != expected:
            raise ValueError("generated view changed: " + name)
    return directory, manifest


def restore_view_manifest(directory, view_id):
    """Materialize losslessly packed historical metadata, preserving its identity.

    Executable/data/source files remain at their existing paths. A restored
    manifest undergoes the ordinary identity and complete file checks in read_view.
    Existing manifests are never repaired or replaced by this storage path.
    """
    manifest = directory / "manifest.json"
    packed = directory / "manifest.json.gz"
    if manifest.exists() or not packed.exists():
        return
    fd, temporary = tempfile.mkstemp(prefix=".manifest-restore-", dir=directory)
    try:
        checksum = hashlib.sha256()
        size = 0
        with os.fdopen(fd, "wb") as output, gzip.open(packed, "rb") as source:
            while chunk := source.read(1024 * 1024):
                size += len(chunk)
                if size > 1024 * 1024 * 1024:
                    raise ValueError("packed view manifest exceeds restoration budget")
                checksum.update(chunk)
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        if checksum.hexdigest() != view_id:
            raise ValueError("packed view manifest identity changed")
        # An exclusive link publishes a complete file; concurrent restorations
        # cannot truncate it or overwrite an existing, possibly changed manifest.
        try:
            os.link(temporary, manifest)
        except FileExistsError:
            if digest(manifest.read_bytes()) != view_id:
                raise ValueError("view manifest changed during restoration")
    except (OSError, EOFError) as error:
        raise ValueError("packed view manifest could not be restored: " + str(error)) from error
    finally:
        Path(temporary).unlink(missing_ok=True)


def select_function(view, rva, module=None):
    functions = [f for f in view["functions"] if f["rva"] == rva and
                 (module is None or f.get("module", "").lower() == module.lower())]
    if len(functions) != 1:
        raise ValueError("function is absent or ambiguous in this view; specify --module for linked views")
    return functions[0]


def owned_function(view, current, project, rva, module=None):
    function = select_function(view, rva, module)
    if function.get("owner_project", str(project.resolve())) != str(project.resolve()):
        raise ValueError("edit this function in its owning project: " + function["owner_project"] +
                         "; generate and inspect that project's own view first")
    return function


def annotate(project, view_id, rva, variable_name, new_name=None, new_type=None, module=None):
    if new_name is None and new_type is None:
        raise ValueError("supply --name and/or --type")
    with locked(project):
        current = state(project)
        _, view = read_view(project, view_id)
        if view["project_sha256"] != digest(encoded(current)):
            raise ValueError("stale view: regenerate and inspect before editing")
        selected = owned_function(view, current, project, rva, module)
        matches = [v for v in selected["variables"] if v["name"] == variable_name]
        if len(matches) != 1:
            raise ValueError("variable is absent or ambiguous in this view")
        variable = matches[0]
        function = next(f for f in current["functions"] if f["rva"] == rva)
        annotation = {"name": new_name if new_name is not None else variable["name"],
                      "type": new_type if new_type is not None else variable["type"]}
        function["annotations"][variable["origin"]] = annotation
        # Validate all names, types and origins with the real emitter before
        # committing the transaction. Failed edits do not change project state.
        export(current)
        current["revision"] += 1
        atomic_json(project / "project.json", current)
        return {"origin": variable["origin"], "annotation": annotation, "revision": current["revision"]}


def annotate_structure(project, view_id, rva, structure_name, new_name=None, field_name=None, new_type=None, module=None):
    if new_name is None and (field_name is None or new_type is None):
        raise ValueError("supply --name and/or a field --type")
    with locked(project):
        current = state(project)
        _, view = read_view(project, view_id)
        if view["project_sha256"] != digest(encoded(current)):
            raise ValueError("stale view: regenerate and inspect before editing")
        selected = owned_function(view, current, project, rva, module)
        matches = [s for s in selected.get("structures", []) if s["name"] == structure_name]
        if len(matches) != 1:
            raise ValueError("structure is absent or ambiguous in this view")
        structure = matches[0]
        function = next(f for f in current["functions"] if f["rva"] == rva)
        stored = function.setdefault("structures", {}).setdefault(
            structure["origin"], {"name": structure["name"], "fields": {}})
        origin = structure["origin"]
        if field_name is None:
            stored["name"] = new_name
            annotation = {"name": new_name}
        else:
            fields = [f for f in structure["fields"] if f["name"] == field_name]
            if len(fields) != 1:
                raise ValueError("field is absent or ambiguous in this view")
            field = fields[0]
            origin = field["origin"]
            annotation = {"name": new_name if new_name is not None else field["name"],
                          "type": new_type if new_type is not None else field["type"]}
            stored["fields"][origin] = annotation
        export(current)
        current["revision"] += 1
        atomic_json(project / "project.json", current)
        return {"origin": origin, "annotation": annotation, "revision": current["revision"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Iterative SharpRetro binary-to-C++ recovery")
    parser.add_argument("--project", type=Path, default=ROOT / "local/recomp/project")
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new")
    new.add_argument("binary", type=Path)
    new.add_argument("--sharp-retro", type=Path, default=ROOT.parent / "SharpRetro")
    add = commands.add_parser("add")
    add.add_argument("--rva", type=lambda s: int(s, 0), required=True)
    add.add_argument("--size", type=lambda s: int(s, 0), required=True)
    gen = commands.add_parser("generate")
    gen.add_argument("--dispatch", action="store_true")
    gen.add_argument("--raw-memory", action="store_true", help="inspect structure facts but emit original raw accesses")
    composition = gen.add_mutually_exclusive_group()
    composition.add_argument("--standalone", action="store_true", help="generate only this project and forget remembered composition")
    composition.add_argument("--with-module", type=Path, action="append", help="link another recovery project into this view; remember composition")
    gen.add_argument("--require-translated-code", action="store_true", help="refuse unresolved translated import code")
    show = commands.add_parser("show")
    show.add_argument("--view")
    show.add_argument("--module", help="module basename for a linked view")
    show.add_argument("--rva", type=lambda s: int(s, 0))
    edit = commands.add_parser("annotate")
    edit.add_argument("--view", required=True)
    edit.add_argument("--module")
    edit.add_argument("--rva", type=lambda s: int(s, 0), required=True)
    edit.add_argument("--variable", required=True)
    edit.add_argument("--name")
    edit.add_argument("--type", choices=("bits", "bool", "u8", "u16", "u32", "u64"))
    for command in ("annotate-structure", "annotate-field"):
        structure = commands.add_parser(command)
        structure.add_argument("--view", required=True)
        structure.add_argument("--module")
        structure.add_argument("--rva", type=lambda s: int(s, 0), required=True)
        structure.add_argument("--structure", required=True)
        structure.add_argument("--name", required=command == "annotate-structure")
        if command == "annotate-field":
            structure.add_argument("--field", required=True)
            structure.add_argument("--type", choices=("bits", "u8", "u16", "u32", "u64"))
    build = commands.add_parser("build")
    build.add_argument("--view")
    build.add_argument("--windows", action="store_true", help="cross-compile a Windows translation bundle")
    build.add_argument("--cxx", type=Path, help="compiler path, required with --windows")
    build.add_argument("--execution-profile", choices=("native", "strict"), default="native",
                       help="Windows defaults to native memory/ABI; strict is for explicit validation fixtures")
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        if args.command == "new":
            from tools.daodecomp.pe import fingerprint
            binary = args.binary.resolve()
            identity = fingerprint(binary)
            if identity["format"] != "PE32" or identity["architecture"] != "x86":
                raise ValueError("initial profile requires PE32 x86")
            with locked(project):
                if (project / "project.json").exists():
                    raise ValueError("project already exists")
                result = {"schema_version": 1, "revision": 0, "binary": str(binary),
                          "module": binary.name, "binary_sha256": identity["sha256"],
                          "image_base": identity["image_base"], "sharp_retro": str(args.sharp_retro.resolve()),
                          "functions": []}
                atomic_json(project / "project.json", result)
        elif args.command == "add":
            if args.rva < 0 or args.size <= 0 or args.rva + args.size > 2**32:
                raise ValueError("expected nonnegative RVA and nonempty 32-bit range")
            with locked(project):
                result = state(project)
                checked_binary(result)
                if any(args.rva < f["rva"] + f["size"] and f["rva"] < args.rva + args.size for f in result["functions"]):
                    raise ValueError("function ranges overlap")
                result["functions"].append({"rva": args.rva, "size": args.size, "annotations": {},
                                            "contract_status": "unreviewed machine-state boundary"})
                result["functions"].sort(key=lambda f: f["rva"])
                result["revision"] += 1
                atomic_json(project / "project.json", result)
        elif args.command == "generate":
            result = generate(project, args.dispatch, args.raw_memory, [] if args.standalone else args.with_module, args.require_translated_code)
        elif args.command == "annotate":
            result = annotate(project, args.view, args.rva, args.variable, args.name, args.type, args.module)
        elif args.command in ("annotate-structure", "annotate-field"):
            result = annotate_structure(project, args.view, args.rva, args.structure, args.name,
                                        getattr(args, "field", None), getattr(args, "type", None), args.module)
        else:
            view_id = args.view or load(project / "current.json")["view"]
            directory, result = read_view(project, view_id)
            if args.command == "show":
                if args.rva is not None:
                    result = select_function(result, args.rva, args.module)
                    result = dict(result, source=(directory / (result["name"] + ".cpp")).read_text(), view=view_id)
            else:
                options = []
                suffix = ""
                if args.windows and args.cxx is None:
                    raise ValueError("--windows requires --cxx pointing to a Windows cross-compiler")
                if args.cxx is not None:
                    compiler = args.cxx.absolute()  # Preserve llvm-mingw's argv[0] target wrapper.
                    if not compiler.is_file():
                        raise ValueError("compiler does not exist")
                    options.append(f"-DCMAKE_CXX_COMPILER={compiler}")
                    suffix = "-" + digest(str(compiler).encode())[:12]
                    if args.windows:
                        options.append("-DCMAKE_SYSTEM_NAME=Windows")
                        suffix += "-windows"
                        options.append("-DRECOMP_NATIVE_EXECUTION=" + ("ON" if args.execution_profile == "native" else "OFF"))
                        suffix += "-" + args.execution_profile
                        for variable, executable in (("AR", "llvm-ar"), ("RANLIB", "llvm-ranlib")):
                            tool = compiler.parent / executable
                            if tool.is_file():
                                options.append(f"-DCMAKE_{variable}={tool}")
                destination = project / "builds" / (view_id + suffix)
                subprocess.run(["cmake", "-S", str(directory), "-B", str(destination),
                                "-DCMAKE_BUILD_TYPE=RelWithDebInfo", *options], check=True, stdout=sys.stderr)
                subprocess.run(["cmake", "--build", str(destination), "--parallel", "2"],
                               check=True, stdout=sys.stderr)
                result = {"view": view_id, "build_directory": str(destination),
                          "executable": str(destination / ("recomp_image.exe" if args.windows else "recomp_image")),
                          "evidence_status": "compiled_only; diagnostic translation bundle, no game startup"}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, StopIteration, subprocess.SubprocessError) as error:
        print("recomp: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
