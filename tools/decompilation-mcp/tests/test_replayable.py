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

TransportGuardTests = load_shared('test_replayable_transport').TransportGuardTests
TransportBoundaryTests = load_shared('test_replayable_transport').TransportBoundaryTests

# The open stack fixtures import the shared IR builders by their test module name.
import sys
sys.path.insert(0,str(ROOT / 'tests'))
StackArgumentTests = load_shared('test_replayable_stackargs').StackArgumentTests
StackIntegrationTests = load_shared('test_replayable_stackargs').StackIntegrationTests
StackDependencyTests = load_shared('test_replayable_stackargs').StackDependencyTests

ConditionalTests = load_shared('test_replayable_conditional').ConditionalTests
ConditionalDependencyTests = load_shared('test_replayable_conditional').ConditionalDependencyTests
ConditionalIntegrationTests = load_shared('test_replayable_conditional').ConditionalIntegrationTests
