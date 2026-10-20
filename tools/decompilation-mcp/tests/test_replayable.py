"""Exercise the shared portable IR/frontier suite in the standalone .NET CI job."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_shared(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tests' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RecoveredIrTests = load_shared('test_replayable_ir').RecoveredIrTests
PipelineBoundaryTests = load_shared('test_replayable_pipeline').PipelineBoundaryTests
